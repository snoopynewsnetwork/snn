"""Independent complete original-page Senate readings for both2020 Coahoma files."""
from pathlib import Path
import csv
import gzip
import hashlib
import io
import json

DATA = Path(__file__).resolve().parent
ROOT = DATA.parent
NAMES = ['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards']
LABELS = {
    2:['Bobo','Cagle Crossing','Clarksdale\nCourthouse','Clarksdale #2','Clarksdale #3',
       'Clarksdale #4','Clarksdale #4 North','Clarksdale #5','Coahoma','Dublin','Farrell'],
    3:['Friars Point','Jonestown','Lula','Lyon','Rena Lara','Roundaway','Sasse Street Fire\nStation','TOTAL','','','']}
# Typed from the four complete coordinator Poppler renders, without OCR fitting.
READINGS = {
    'sos-2020-county-coahoma':{
        2:[[86,23,419,730,398,1082,110,1114,193,85,137],
           [33,33,202,488,63,47,61,159,9,80,27],
           [2,0,5,3,3,7,1,14,0,0,1]],
        3:[[458,557,133,373,43,46,465,6452,None,None,None],
           [35,11,125,582,168,27,11,2161,None,None,None],
           [0,0,2,4,1,0,3,46,None,None,None]]},
    'sos-2020-county-coahoma-amended':{
        2:[[86,22,419,730,383,1056,106,1065,193,83,137],
           [33,33,202,488,58,46,55,150,9,77,27],
           [2,0,5,3,3,7,1,14,0,0,1]],
        3:[[458,557,133,371,43,46,449,6337,None,None,None],
           [35,11,125,582,167,27,8,2133,None,None,None],
           [0,0,2,4,1,0,3,46,None,None,None]]}}
STATE = {'sos-2020-certified-sen-pdf':[578806,709539,23152],
         'sos-2020-amended-sen-pdf':[578691,709511,23152]}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    records = json.loads((DATA/'coordinator-qa/coahoma-2020-renders.json').read_bytes())
    assert len(records) == 6
    for record in records:
        b = (ROOT/record['path']).read_bytes()
        assert sha(b) == record['sha256'] and len(b) == record['bytes']
        source = record['source_pin']
        path = ROOT/source['path'] if 'path' in source else DATA/'news'/source['asset']
        stored = path.read_bytes()
        assert sha(stored) == source['stored_sha256']
        assert sha(gzip.decompress(stored)) == source['raw_sha256']
    peer_path = DATA/'baselines/coahoma-2020-amendment-readings.json'
    copy = DATA/'coordinator-qa/coahoma-2020-amendment-readings-snapshot.json.gz'
    if not copy.exists():
        raw = peer_path.read_bytes()
        assert peer_path.read_bytes() == raw
        copy.write_bytes(gzip.compress(raw,mtime=0))
    stored = copy.read_bytes()
    raw = gzip.decompress(stored)
    peer = json.loads(raw)
    assert {s['source_id'] for s in peer['sources']} == set(READINGS)
    numeric = nulls = 0
    county_totals = {}
    for source in peer['sources']:
        sid = source['source_id']
        expected_sha = next(r['source_pin']['raw_sha256'] for r in records if r['source_pin']['id'] == sid)
        assert source['raw_sha256'] == expected_sha
        assert [p['page'] for p in source['pages']] == [2,3]
        totals = []
        for page in source['pages']:
            number = page['page']
            assert [c['source_column'] for c in page['columns']] == list(range(1,12))
            assert [c['label_literal'] for c in page['columns']] == LABELS[number]
            assert [c['role'] for c in page['columns']] == (
                ['source_native_reporting_constituent']*11 if number == 2 else
                ['source_native_reporting_constituent']*7+['source_TOTAL']+['unused_template_column']*3)
            assert [f['candidate'] for f in page['fields']] == NAMES
            for index, field in enumerate(page['fields']):
                expected = READINGS[sid][number][index]
                assert field['values'] == expected
                numeric += sum(v is not None for v in expected)
                nulls += sum(v is None for v in expected)
                if number == 3:
                    assert sum(READINGS[sid][2][index]+expected[:7]) == expected[7]
                    totals.append(expected[7])
        county_totals[sid] = totals
    assert numeric == 114 and nulls == 18
    county_delta = [b-a for a,b in zip(county_totals['sos-2020-county-coahoma'],county_totals['sos-2020-county-coahoma-amended'])]
    state_delta = [b-a for a,b in zip(STATE['sos-2020-certified-sen-pdf'],STATE['sos-2020-amended-sen-pdf'])]
    assert county_delta == state_delta == [-115,-28,0]
    manifest = json.loads((DATA/'news/manifest.json').read_bytes())
    csv_source = next(s for s in manifest if s['id'] == 'sos-2020-recap-csv')
    csv_stored = (DATA/'news'/csv_source['asset']).read_bytes()
    csv_raw = gzip.decompress(csv_stored)
    assert sha(csv_raw) == csv_source['raw_sha256'] and sha(csv_stored) == csv_source['stored_sha256']
    csv_rows = [r for r in csv.DictReader(io.StringIO(csv_raw.decode('utf-8-sig')))
                if r['County'] == 'Coahoma' and r['Office'] == 'United States-Senate ']
    assert len(csv_rows) == 3
    csv_control = {r['Candidate']:int(r['County Total']) for r in csv_rows}
    assert [csv_control[n] for n in NAMES] == county_totals['sos-2020-county-coahoma-amended']
    output = {'status':'pass_explicit_primary_Coahoma_original_amended_vectors_match_state_difference_not_exhaustive',
        'source_pages_and_original_pins':records,'independent_manual_candidate_readings':READINGS,
        'independent_literal_headers':LABELS,'candidate_order':NAMES,
        'native_source_constituents_per_document':18,'numeric_positions_including_TOTAL':numeric,
        'unused_null_positions':nulls,'physical_TOTAL_column_each_document_page3':8,
        'county_printed_TOTAL_vectors':county_totals,'independent_state_printed_vectors':STATE,
        'amended_minus_original_candidate_delta':county_delta,'combined_delta':sum(county_delta),
        'CSV_Coahoma_source_rows':csv_rows,'CSV_source_pin':csv_source,
        'worker_reading_snapshot':{'path':str(copy.relative_to(ROOT)),'stored_bytes':len(stored),
            'stored_sha256':sha(stored),'original_bytes':len(raw),'original_sha256':sha(raw)},
        'source_clock_qualification':'State report prints December03,2020 12:12PM and December04,2020 03:13PM, zones unspecified; certificate signature dates, county file Last-Modified, retrieval clocks and release chronology remain distinct.',
        'scope':'Both original county documents explicitly supply18 constituents and three Senate fields plus TOTAL; all108 native cells,6 TOTAL cells and18 unused/null positions agree with the independently produced worker ledger. Physical page3 TOTAL is column8 in both; original machine-column7 merge is not an accepted locator. Replacing the original printed Coahoma vector with the amended printed vector gives the entire observed statewide candidate difference without fitting residuals. This equality does not prove no other county or office changed, that changes cannot offset, or any causal/certification/publication sequence. Presidential, complete104-source historical/native and current-geography gates remain open.'}
    (DATA/'coordinator-coahoma-2020-amendment-review.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({k:output[k] for k in ['status','numeric_positions_including_TOTAL','unused_null_positions','amended_minus_original_candidate_delta','combined_delta']}))


if __name__ == '__main__':
    main()
