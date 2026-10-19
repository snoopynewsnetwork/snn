"""Independent visual readings of the two disputed 2018 special-election cells."""
from pathlib import Path
import gzip
import hashlib
import json

DATA = Path(__file__).resolve().parent
ROOT = DATA.parent
MANUAL = {
    'sos-2018-county-choctaw': {
        'page': 3, 'source_TOTAL_column': 3,
        'TOTAL': {'Tobey Bernard Bartee': 48, 'Mike Espy': 852,
                  'Cindy Hyde-Smith': 1550, 'Chris McDaniel': 573},
        'scope': 'Only the four printed special-election TOTAL cells are independently typed here. The two preceding columns are actual precincts, not the complete county partition.',
    },
    'sos-2018-county-quitman': {
        'page': 2, 'source_TOTAL_column': 11,
        'TOTAL': {'Tobey Bernard Bartee': 55, 'Mike Espy': 1643,
                  'Cindy Hyde-Smith': 601, 'Chris McDaniel': 141},
        'constituent_labels_literal': ['Crenshaw', 'Crowder', 'Darling', 'District 3 North',
            'District 3 South', 'Lambert', 'North West Marks', 'Sledge',
            'South West Marks', 'West Lambert'],
        'constituent_values': {
            'Tobey Bernard Bartee': [4,3,2,4,3,6,8,10,9,6],
            'Mike Espy': [72,35,92,181,174,206,284,239,183,177],
            'Cindy Hyde-Smith': [2,120,21,116,125,32,62,31,42,50],
            'Chris McDaniel': [1,33,10,25,17,4,20,11,6,14],
        },
        'scope': 'All ten displayed constituent values and four TOTAL cells were typed from the full original page. Their sums independently reproduce the printed totals; no statewide residual is used.',
    },
}


def main():
    pages = json.loads((DATA / 'coordinator-qa/2018-disputed-original-pages.json').read_bytes())
    assert len(pages) == 2
    for page in pages:
        source = page['source']
        manual = MANUAL[source['id']]
        assert page['page'] == manual['page']
        stored = (ROOT / source['path']).read_bytes()
        raw = gzip.decompress(stored)
        assert len(stored) == source['stored_bytes']
        assert len(raw) == source['bytes']
        assert hashlib.sha256(stored).hexdigest() == source['stored_sha256']
        assert hashlib.sha256(raw).hexdigest() == source['raw_sha256']
        assert raw.startswith(b'%PDF-')
        render = (ROOT / page['path']).read_bytes()
        assert len(render) == page['bytes']
        assert hashlib.sha256(render).hexdigest() == page['sha256']
        for candidate, values in manual.get('constituent_values', {}).items():
            assert len(values) == len(manual['constituent_labels_literal']) == 10
            assert sum(values) == manual['TOTAL'][candidate]
    result = {
        'status': 'pass_independent_complete_original_page_readings',
        'election_date': '2018-11-06', 'contest': 'United States-Senate Special',
        'originals_and_complete_render_pins': pages,
        'independent_manual_readings': MANUAL,
        'explicit_TOTAL_cells_read': 8,
        'explicit_Quitman_constituent_candidate_cells_read': 40,
        'resolved_readings': [
            {'source_id': 'sos-2018-county-choctaw', 'candidate': 'Cindy Hyde-Smith',
             'original_printed_value': 1550, 'competing_reading': 1650},
            {'source_id': 'sos-2018-county-quitman', 'candidate': 'Mike Espy',
             'original_printed_value': 1643, 'competing_reading': 1543},
        ],
        'qualification': 'The two earlier competing readings are transcription differences. This bounded original-cell review establishes neither a historical publication change nor whole-state native acceptance. No worker output is modified and no candidate, method, geographic or current reporting join is inferred.',
    }
    (DATA / 'coordinator-2018-disputed-cell-review.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['status', 'explicit_TOTAL_cells_read',
        'explicit_Quitman_constituent_candidate_cells_read', 'resolved_readings']}))


if __name__ == '__main__':
    main()
