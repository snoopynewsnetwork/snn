"""Direct complete-original Coahoma 2020 Senate grids, two publications.

All numbers and literal headers below were transcribed while viewing the four
complete original county recap pages. No peer or residual supplied a value.
"""
import csv
import gzip
import io
from PIL import Image
import fitz
from acquire_sources import BASE, OUT, receipts, sha, savejson

NAMES = ['Mike Espy', 'Cindy Hyde-Smith', 'Jimmy L. Edwards']
PARTIES = {'Mike Espy': 'Democrat', 'Cindy Hyde-Smith': 'Republican',
           'Jimmy L. Edwards': 'Libertarian'}
HEADERS = {
    2: ['Bobo', 'Cagle Crossing', 'Clarksdale\nCourthouse', 'Clarksdale #2',
        'Clarksdale #3', 'Clarksdale #4', 'Clarksdale #4 North',
        'Clarksdale #5', 'Coahoma', 'Dublin', 'Farrell'],
    3: ['Friars Point', 'Jonestown', 'Lula', 'Lyon', 'Rena Lara', 'Roundaway',
        'Sasse Street Fire\nStation', 'TOTAL', '', '', ''],
}
ORIGINAL = {
    'Mike Espy': {
        2: [86, 23, 419, 730, 398, 1082, 110, 1114, 193, 85, 137],
        3: [458, 557, 133, 373, 43, 46, 465, 6452, None, None, None]},
    'Cindy Hyde-Smith': {
        2: [33, 33, 202, 488, 63, 47, 61, 159, 9, 80, 27],
        3: [35, 11, 125, 582, 168, 27, 11, 2161, None, None, None]},
    'Jimmy L. Edwards': {
        2: [2, 0, 5, 3, 3, 7, 1, 14, 0, 0, 1],
        3: [0, 0, 2, 4, 1, 0, 3, 46, None, None, None]},
}
AMENDED = {
    'Mike Espy': {
        2: [86, 22, 419, 730, 383, 1056, 106, 1065, 193, 83, 137],
        3: [458, 557, 133, 371, 43, 46, 449, 6337, None, None, None]},
    'Cindy Hyde-Smith': {
        2: [33, 33, 202, 488, 58, 46, 55, 150, 9, 77, 27],
        3: [35, 11, 125, 582, 167, 27, 8, 2133, None, None, None]},
    'Jimmy L. Edwards': ORIGINAL['Jimmy L. Edwards'],
}


def main():
    controls = list(csv.DictReader((OUT / '2020-publication-original-total-candidate-votes.csv').open()))
    sources = []
    flat = []
    for suffix, candidate_values in (('', ORIGINAL), ('-amended', AMENDED)):
        sid = 'sos-2020-county-coahoma' + suffix
        receipt = next(r for r in receipts if r['id'] == sid)
        raw = gzip.decompress((BASE / receipt['path']).read_bytes())
        assert sha(raw) == receipt['raw_sha256']
        doc = fitz.open(stream=raw, filetype='pdf')
        pages = {}
        for number in (2, 3):
            im = Image.open(io.BytesIO(doc[number-1].get_pixmap(
                matrix=fitz.Matrix(2.2, 2.2), colorspace=fitz.csGRAY).tobytes('png')))
            raster = OUT / f'qa/2020-coahoma-complete-original/{sid}/p{number:04d}-original.png'
            raster.parent.mkdir(parents=True, exist_ok=True)
            im.save(raster)
            pages[number] = dict(source_pdf_page=number,
                                 original_raster=str(raster.relative_to(BASE)),
                                 raster_sha256=sha(raster.read_bytes()),
                                 render_size=list(im.size))
        rows = []
        checks = {}
        for candidate in NAMES:
            native_sum = 0
            printed = []
            for number in (2, 3):
                values = candidate_values[candidate][number]
                assert len(values) == len(HEADERS[number]) == 11
                for physical_column, (header, vote) in enumerate(zip(HEADERS[number], values), 1):
                    role = ('source_TOTAL' if number == 3 and physical_column == 8
                            else 'unused_template_column' if header == ''
                            else 'source_native_reporting_constituent')
                    if role == 'source_TOTAL':
                        assert header == 'TOTAL' and isinstance(vote, int)
                        printed.append(vote)
                    elif role == 'unused_template_column':
                        assert vote is None
                    else:
                        assert isinstance(vote, int) and vote >= 0
                        native_sum += vote
                    rows.append(dict(source_id=sid, county='Coahoma', county_fips='28027',
                                     election_date='2020-11-03', source_raw_sha256=receipt['raw_sha256'],
                                     source_pdf_page=number, physical_source_column=physical_column,
                                     source_native_key=f'28027:{sid}:p{number}:c{physical_column}',
                                     literal_source_header=header, role=role,
                                     office_context_literal='United States-Senate',
                                     candidate=candidate, party_field_literal=PARTIES[candidate],
                                     votes=vote, original_raster=pages[number]['original_raster'],
                                     reading_basis='direct_complete_original_page_visual' if vote is not None
                                                   else 'visibly_unprinted_template_cell'))
            assert len(printed) == 1 and native_sum == printed[0]
            ctl = next(x for x in controls if x['source_id'] == sid and x['candidate'] == candidate)
            assert int(ctl['votes']) == printed[0] and ctl['source_raw_sha256'] == receipt['raw_sha256']
            assert int(ctl['source_page']) == 3
            checks[candidate] = dict(native_sum=native_sum, printed_TOTAL=printed[0],
                                     county_control=int(ctl['votes']), passes=True)
        assert len(rows) == 66 and sum(r['role'] == 'source_native_reporting_constituent' for r in rows) == 54
        sources.append(dict(source_id=sid, source_raw_sha256=receipt['raw_sha256'],
                            source_original_path=receipt['path'], source_pdf_page_count=len(doc),
                            pages=[pages[n] for n in (2, 3)], native_constituents=18,
                            physical_TOTAL_page=3, physical_TOTAL_column=8,
                            candidate_checks=checks, rows=rows,
                            scope='Separate 2020 original or amended county publication; no cross-publication identity join.'))
        flat.extend(rows)
    assert len(flat) == 132
    out = dict(scope='Two separate complete-original Coahoma 2020 Senate3 county publication grids, each direct read before peer comparison.',
               sources=sources, total_candidate_positions=len(flat),
               native_constituents_per_publication=18)
    savejson(OUT / '2020-coahoma-two-publication-native-original-readings.json', out)
    with (OUT / '2020-coahoma-two-publication-native-original-cells.csv').open('w', newline='') as f:
        fields = list(flat[0]); writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader(); writer.writerows(flat)
    print('Coahoma two distinct publications:', len(flat), 'positions, all six candidate vectors close')


if __name__ == '__main__':
    main()
