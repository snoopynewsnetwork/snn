"""Direct original reading of three nonadditive county E-013 summaries.

All nine presidential and two Senate named rows plus printed percentages are
read from complete original pages. Other offices remain in the original PDFs.
"""
import csv
import json

import fitz

from acquire_sources import BASE, OUT, receipts, savejson, sha, source


PRES = ['Kamala D. Harris / Tim Walz', 'Chase Oliver / Mike ter Maat',
        'Jill Stein / Rudolph Ware', 'Randall Terry / Stephen E. Broden',
        'Donald J. Trump / JD Vance', 'Shiva Ayyadurai / Crystal Ellis',
        'Claudia De la Cruz / Karina Garcia',
        'Robert F. Kennedy Jr. / Nicole Shanahan', 'Peter Sonski / Lauren Onak']
SEN = ['Ty Pinkins', 'Roger F. Wicker']
DATA = {
    'bolivar': {'page': 4, 'report_date': '11/14/2024', 'last_updated': 'November 14, 2024 - 08:51 AM',
                'raster_sha256': 'd24427aff779cbf7991ff2757a17c0768f99c3d29373f210a62115a019bcd927',
                'pres': [6419, 9, 12, 4, 3943, 3, 9, 30, 6],
                'pres_pct': ['61.51 %', '0.09 %', '0.11 %', '0.04 %', '37.79 %', '0.03 %', '0.09 %', '0.29 %', '0.06 %'],
                'pres_total': 10435, 'sen': [6200, 4101], 'sen_pct': ['60.19 %', '39.81 %'], 'sen_total': 10301},
    'grenada': {'page': 9, 'report_date': '11/15/2024', 'last_updated': 'November 15, 2024 - 02:56 PM',
                'raster_sha256': '703988035069c45afacaa53a6fdb936b0e3c7ad2d598007eaf38c055184ac17f',
                'pres': [4060, 8, 11, 2, 5651, 2, 4, 28, 0],
                'pres_pct': ['41.57 %', '0.08 %', '0.11 %', '0.02 %', '57.86 %', '0.02 %', '0.04 %', '0.29 %', '0.00 %'],
                'pres_total': 9766, 'sen': [3989, 5689], 'sen_pct': ['41.22 %', '58.78 %'], 'sen_total': 9678},
    'itawamba': {'page': 12, 'report_date': '11/18/2024', 'last_updated': 'November 18, 2024 - 11:20 AM',
                'raster_sha256': '1daba6b34582e34ff09561173034026586058b5658cde0ff9f51512c9a5ad118',
                'pres': [1027, 16, 7, 7, 9523, 2, 5, 29, 5],
                'pres_pct': ['9.67 %', '0.15 %', '0.07 %', '0.07 %', '89.66 %', '0.02 %', '0.05 %', '0.27 %', '0.05 %'],
                'pres_total': 10621, 'sen': [1114, 9337], 'sen_pct': ['10.66 %', '89.34 %'], 'sen_total': 10451},
}


def main():
    county = {r['county'].lower(): r for r in csv.DictReader((BASE / 'data/county-turnout.csv').open())}
    sources = []
    for name, x in DATA.items():
        sid = 'sos-2024-county-' + name
        receipt = next(r for r in receipts if r['id'] == sid)
        raw = source(sid)
        assert sha(raw) == receipt['raw_sha256']
        doc = fitz.open(stream=raw, filetype='pdf')
        pix = doc[x['page'] - 1].get_pixmap(matrix=fitz.Matrix(3, 3), colorspace=fitz.csGRAY)
        png = pix.tobytes('png')
        assert sha(png) == x['raster_sha256']
        path = OUT / f'qa/2024-extra-e013-original-summaries/{name}-p{x["page"]}-original.png'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(png)
        assert len(x['pres']) == len(x['pres_pct']) == 9 and len(x['sen']) == len(x['sen_pct']) == 2
        assert sum(x['pres']) == x['pres_total'] == int(county[name]['2024_president_candidate_votes'])
        assert sum(x['sen']) == x['sen_total']
        assert x['sen'] == [int(county[name]['2024_senate_pinkins']), int(county[name]['2024_senate_wicker'])]
        rows = []
        for office, labels, values, percentages in [('United States, President', PRES, x['pres'], x['pres_pct']),
                                                      ('United States, Senate', SEN, x['sen'], x['sen_pct'])]:
            for ordinal, (label, votes, pct) in enumerate(zip(labels, values, percentages), 1):
                rows.append({'office_literal': office, 'source_row_ordinal_in_office': ordinal,
                             'candidate_identity_short_label': label,
                             'source_full_label_available_in_original_pdf': True,
                             'reported_votes': votes, 'printed_percentage_of_current_total_reported_votes': pct,
                             'source_pdf_page': x['page'], 'source_id': sid,
                             'role': 'nonadditive_county_E013_named_candidate_summary'})
        sources.append({'source_id': sid, 'source_raw_sha256': receipt['raw_sha256'],
                        'source_original_path': receipt['path'], 'pdf_page': x['page'],
                        'original_render_path': str(path.relative_to(BASE)),
                        'original_render_sha256': x['raster_sha256'],
                        'original_render_size': [pix.width, pix.height],
                        'report_literal': 'Election Summary Report', 'report_number_literal': 'E-013',
                        'report_date_literal': x['report_date'], 'last_updated_literal': x['last_updated'],
                        'election_date_literal': '11/05/2024', 'district_type_literal': 'All',
                        'number_of_counties_reporting_results_for_each_requested_office_literal': '1 of 1',
                        'status_literal': None,
                        'candidate_rows': rows,
                        'printed_president_TOTAL': x['pres_total'],
                        'printed_senate_TOTAL': x['sen_total'],
                        'generic_write_in_available': False,
                        'ballots_cast_available': False,
                        'registered_voters_available': False,
                        'voting_method_available': False,
                        'qualification': 'E-013 named-candidate county aggregate; exact native SEMS and SOS CSV controls agree. Unrelated offices remain in complete original PDF. No generic/ballot/method value or candidate allocation to native units appears on this page.'})
    assert len(sources) == 3 and sum(len(s['candidate_rows']) for s in sources) == 33
    savejson(OUT / '2024-extra-e013-original-summary-readings.json', {
        'scope': 'Three original county E-013 pages, each9president+2Senate named rows and printed percentages. Nonadditive county summary controls; no source-native candidate assignment.',
        'source_views': 3, 'named_candidate_rows': 33, 'sources': sources})
    print('Three original E-013 county summaries: 33 named fields, all candidate and printed TOTAL controls close')


if __name__ == '__main__':
    main()
