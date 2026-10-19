"""Record the incompatible Montgomery statistics panel from its original PDF.

The 885 printed ballots are a source-scoped observation. They cannot replace
the county candidate controls or be apportioned to a voting method.
"""
import gzip
import json

import fitz

from acquire_sources import BASE, OUT, receipts, savejson, sha, source


SID = 'sos-2024-county-montgomery'
RASTERS = {
    1: '26eab9650ff8df7f95c84efc8f19b0d483e9fdf18a2ffe095a120c1183ed4fd4',
    3: '988298e22df0533649906870ca7cb07d8a773e03712b34e1845ae89aaf4225cb',
}


def prior_pin(path):
    folder = OUT / 'source/canvass-pre-montgomery-statistics-v1'
    folder.mkdir(parents=True, exist_ok=True)
    stored_path = folder / 'canvass-statistics-readings.json.gz'
    current = path.read_bytes()
    current_rows = json.loads(current)
    assert len(current_rows) in (13, 14)
    before = [r for r in current_rows if r['source_id'] != SID]
    assert len(before) == 13
    if not stored_path.exists():
        assert len(current_rows) == 13
        stored_path.write_bytes(gzip.compress(current, compresslevel=9, mtime=0))
    old = gzip.decompress(stored_path.read_bytes())
    assert json.loads(old) == before
    return {'path': str(stored_path.relative_to(BASE)),
            'raw_sha256': sha(old), 'raw_bytes': len(old),
            'stored_sha256': sha(stored_path.read_bytes()),
            'stored_bytes': stored_path.stat().st_size}


def main():
    receipt = next(r for r in receipts if r['id'] == SID)
    raw = source(SID)
    assert sha(raw) == receipt['raw_sha256'] == 'dc1a44fd5ea6fa3021a44f3df38f028cd3b272ba92a90fb151536caa599bfc9d'
    doc = fitz.open(stream=raw, filetype='pdf')
    assert len(doc) == 11
    pages = []
    folder = OUT / 'qa/2024-montgomery-original-panels'
    folder.mkdir(parents=True, exist_ok=True)
    for page, expected in RASTERS.items():
        pix = doc[page - 1].get_pixmap(matrix=fitz.Matrix(3, 3), colorspace=fitz.csGRAY)
        png = pix.tobytes('png')
        assert sha(png) == expected
        path = folder / f'p{page}-original.png'
        path.write_bytes(png)
        pages.append({'pdf_page': page, 'render_path': str(path.relative_to(BASE)),
                      'render_sha256': expected, 'render_size': [pix.width, pix.height]})
    summary = next(s for s in json.loads((OUT / 'canvass-summary-readings.json').read_text())['sources'] if s['source_id'] == SID)
    assert summary['page'] == 1 and summary['source_status_literal'] == 'Official Results'
    assert summary['source_clock_literal'] == '11/15/2024 10:25 AM'
    senate = summary['senate']
    president = summary['president']
    senate_named = senate['Ty Pinkins'][0] + senate['Roger F. Wicker'][0]
    president_named = sum(v[0] for k, v in president.items() if k not in ('Write-In Totals', 'Contest Totals'))
    assert (senate_named, senate['Write-In Totals'][0], president_named, president['Write-In Totals'][0]) == (4349, 13, 4424, 3)
    stats = {'source_id': SID, 'page': 3, 'election_date': '2024-11-05',
             'report_status_literal': 'Official Results',
             'source_clock_literal': '11/15/2024 10:24 AM',
             'source_clock_timezone': None,
             'reading_basis': 'Independent direct visual reading of complete hash-checked original PDF page3; OCR locator not numeric authority',
             'preview': 'data/turnout/qa/2024-montgomery-original-panels/p3-original.png',
             'registered_voters_total': 6291, 'ballots_cast_total': 885,
             'ballots_cast_blank': 1, 'source_turnout_percent_literal': '14.07%',
             'precincts_reporting_literal': '14 of 14', 'methods_literal': None,
             'ballots_cast_by_method': None, 'blank_by_method': None,
             'other_source_fields': {'printed_page_number_literal': '1 of 3',
                                     'statistics_clock_scope': 'PDF page3; summary PDF page1 prints 2 of 3 and 10:25 AM',
                                     'registration_status_date': None},
             'qualification': 'Printed ballots 885 are incompatible with the same PDF packet\'s named Senate 4349 and presidential 4424 votes. Preserve both panel clocks and values; no ballot denominator, voting-method allocation, residual, or cause is inferred. Registration snapshot/status beyond the printed report is unavailable.'}
    assert round(100 * 885 / 6291, 2) == 14.07
    comparison = {'statistics_ballots_cast': 885, 'statistics_registered_voters': 6291,
                  'statistics_blank': 1, 'statistics_turnout_percent_literal': '14.07%',
                  'named_senate_votes': senate_named, 'senate_generic_write_in_marks': 13,
                  'named_president_votes': president_named, 'president_generic_write_in_marks': 3,
                  'senate_named_exceeds_statistics_ballots_by': senate_named - 885,
                  'president_named_exceeds_statistics_ballots_by': president_named - 885,
                  'status': 'incompatible_source_panel_no_denominator_substitution'}
    assert comparison['senate_named_exceeds_statistics_ballots_by'] == 3464
    assert comparison['president_named_exceeds_statistics_ballots_by'] == 3539
    stats_path = OUT / 'canvass-statistics-readings.json'
    pin = prior_pin(stats_path)
    savejson(OUT / 'source/canvass-pre-montgomery-statistics-v1/pin.json', pin)
    rows = [s for s in json.loads(stats_path.read_text()) if s['source_id'] != SID] + [stats]
    savejson(stats_path, rows)
    savejson(OUT / '2024-montgomery-original-statistics-reading.json', {
        'source_id': SID, 'source_raw_sha256': receipt['raw_sha256'],
        'source_original_path': receipt['path'], 'source_status': 'Official Results',
        'source_pages': pages, 'statistics': stats,
        'summary_reference': {'pdf_page': 1, 'clock_literal': summary['source_clock_literal'],
                              'source_reading_path': 'data/turnout/canvass-summary-readings.json'},
        'source_arithmetic': comparison,
        'prior_statistics_ledger_pin': pin,
        'scope': 'Same original PDF packet, separate page and report clock. Direct printed statistics retained despite incompatibility with named candidate votes.'})
    print('Montgomery original PDF3: registration6291, ballots885, blank1, 14.07%; incompatible with PDF1 candidate votes')


if __name__ == '__main__':
    main()
