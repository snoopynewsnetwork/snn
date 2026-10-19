"""Independent complete-page readings of two eleven-candidate source views."""
from pathlib import Path
import csv
import gzip
import hashlib
import io
import json
import re

DATA = Path(__file__).resolve().parent
ROOT = DATA.parent
NAMES = ['Kamala D. Harris','Chase Oliver','Jill Stein','Randall Terry','Donald J. Trump',
         'Shiva Ayyadurai','Claudia De la Cruz','Robert F. Kennedy Jr.','Peter Sonski',
         'Ty Pinkins','Roger F. Wicker']
# Each list was typed from the complete coordinator original-page renders.
TUNICA7 = [
    [36,233,207,6,219,166,130,232,123,173,200],
    [0,0,0,0,0,0,0,1,0,1,0], [0,0,0,0,0,0,0,0,0,1,0],
    [0,1,0,0,0,1,0,0,0,0,0], [33,95,8,61,46,30,265,33,105,31,49],
    [0,0,0,0,0,0,0,0,0,0,1], [0,0,1,0,0,0,0,1,0,0,1],
    [0,5,1,0,2,1,1,0,5,4,0], [0,0,0,0,0,1,0,0,0,0,0],
    [30,226,202,7,225,168,129,212,126,169,195], [38,95,10,60,47,27,265,44,111,34,50]]
TUNICA8 = [[111,1836],[1,3],[0,1],[0,2],[43,799],[0,1],[0,3],[2,21],[0,1],[108,1797],[46,827]]
KEMPER67 = [
    [365,80,26,42,117,92,247,281,83,139,348], [0,0,0,0,0,1,1,0,0,1,0],
    [0,0,0,0,0,0,1,0,0,0,0], [1,0,0,0,0,0,0,0,0,0,0],
    [136,222,35,185,52,14,117,195,177,63,108], [0,0,0,0,0,0,0,1,0,0,0],
    [1,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,1,0,0,0,1],
    [0,0,0,0,0,0,0,1,0,0,0], [348,74,24,42,119,89,234,259,74,130,321],
    [153,228,36,183,57,17,126,208,182,73,123]]
KEMPER8 = [[166,226,169,2381],[0,1,1,5],[0,0,0,1],[0,0,0,1],[168,113,106,1691],
           [1,0,0,2],[0,0,0,1],[1,0,0,3],[0,0,0,1],[164,208,148,2234],[176,134,128,1824]]
READINGS = {'sos-2024-county-tunica':{7:TUNICA7,8:[r+[None]*9 for r in TUNICA8]},
            'sos-2024-county-kemper':{6:KEMPER67,7:KEMPER67,8:[r+[None]*7 for r in KEMPER8]}}
LABELS = {
    'sos-2024-county-tunica':{7:['Austin Park','Dundee Community\nCenter','Hambrick','Mhoon Landing',
        'New Sub Park','Robinsonville\nCommunity Center','Tunica','Tunica Auditorium',
        'Tunica Economic\nComplex','Verner Park','White Oak Rec.\nCenter'],8:['Workforce Center','TOTAL']},
    'sos-2024-county-kemper':{6:['Courthouse','Damascus','Farmers Market','Fort Stephens','Kellis Store',
        'Kemper Springs','Library','Little Rock Comm Ctr','Lynville','Mount Nebo','Porterville'],
        8:['Preston','Scooba A-L','Scooba M-Z','TOTAL']}}
LABELS['sos-2024-county-kemper'][7] = LABELS['sos-2024-county-kemper'][6]
SUMMARY = dict(zip(NAMES,[1837,3,1,2,799,1,3,21,1,1798,827]))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(path):
    b = path.read_bytes()
    return {'path':str(path.relative_to(ROOT)),'bytes':len(b),'sha256':sha(b)}


def main():
    source_path = DATA / 'baselines/native-source-exception-readings.json'
    snapshot = DATA / 'coordinator-qa/tunica-kemper-allfield-readings-snapshot.json.gz'
    if not snapshot.exists():
        b = source_path.read_bytes()
        assert source_path.read_bytes() == b
        snapshot.write_bytes(gzip.compress(b,mtime=0))
    worker = json.loads(gzip.decompress(snapshot.read_bytes()))
    originals = json.loads((DATA / 'coordinator-qa/tunica-kemper-2024-renders.json').read_bytes())
    upright = json.loads((DATA / 'coordinator-qa/tunica-kemper-allfield-upright-renders.json').read_bytes())
    for r in originals:
        assert pin(ROOT / r['path'])['sha256'] == r['sha256']
        meta = r['source_pin']
        stored = (ROOT / meta['path']).read_bytes()
        assert sha(stored) == meta['stored_sha256'] and sha(gzip.decompress(stored)) == meta['raw_sha256']
    for r in upright:
        assert pin(ROOT / r['path'])['sha256'] == r['sha256']
    numeric = nulls = 0
    totals = {}
    for source in worker['sources']:
        sid = source['source_id']
        assert source['raw_sha256'] == next(r['source_pin']['raw_sha256'] for r in originals if r['source_pin']['id'] == sid)
        assert [p['page'] for p in source['pages']] == list(READINGS[sid])
        for page in source['pages']:
            number = page['page']
            assert [f['candidate'] for f in page['fields']] == NAMES
            assert [f['printed_row_index'] for f in page['fields']] == list(range(1,12))
            assert [re.sub(r'\s','',s) for s in page['labels_literal']] == [re.sub(r'\s','',s) for s in LABELS[sid][number]]
            assert len(page['roles']) == 11
            worker_raster = ROOT / page['full_original_render_path']
            assert pin(worker_raster)['sha256'] == page['render_sha256']
            assert [f['values'] for f in page['fields']] == READINGS[sid][number]
            numeric += sum(v is not None for row in READINGS[sid][number] for v in row)
            nulls += sum(v is None for row in READINGS[sid][number] for v in row)
            if sid.endswith('kemper') and number == 6:
                assert page['roles'] == ['parallel_native_observation']*11
        first = 7
        first_rows = READINGS[sid][first]
        final_rows = READINGS[sid][8]
        # The TOTAL is physical column2 (Tunica) or4 (Kemper), followed by nulls.
        total_index = 1 if sid.endswith('tunica') else 3
        sums = {name:sum(first_rows[i])+sum(final_rows[i][:total_index]) for i,name in enumerate(NAMES)}
        printed = {name:final_rows[i][total_index] for i,name in enumerate(NAMES)}
        assert sums == printed == source['native_sums'] == source['printed_TOTAL']
        totals[sid] = printed
    assert numeric == 429 and nulls == 176
    assert totals['sos-2024-county-tunica']['Kamala D. Harris'] == 1836
    assert totals['sos-2024-county-tunica']['Ty Pinkins'] == 1797
    summary = worker['tunica_summary']
    assert summary['summary_named_candidates'] == SUMMARY
    assert summary['Senate_generic_write_in_totals'] == 3
    assert summary['President_generic_write_in_totals'] == 4
    assert summary['Senate_total_votes_cast'] == 2628 and summary['President_total_votes_cast'] == 2672
    assert summary['Senate_contest_totals'] == summary['President_contest_totals'] == 2745
    assert summary['timezone'] is None
    manifest = json.loads((DATA / 'news/manifest.json').read_bytes())
    csv_source = next(r for r in manifest if r['id'] == 'sos-2024-recap-csv')
    stored = (DATA / 'news' / csv_source['asset']).read_bytes()
    raw = gzip.decompress(stored)
    assert sha(stored) == csv_source['stored_sha256'] and sha(raw) == csv_source['raw_sha256']
    rows = list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
    county_controls = {}
    for county in ['Tunica','Kemper']:
        selected = [r for r in rows if r['County'] == county and r['Office'] in ['United States-President','United States-Senate']]
        assert len(selected) == 11
        by_name = {}
        for name in NAMES:
            matching = [r for r in selected if r['Candidate'] == name or r['Candidate'].startswith('Presidential Electors for '+name+' for President')]
            assert len(matching) == 1
            by_name[name] = int(matching[0]['County Total'])
        county_controls[county] = by_name
    assert county_controls['Tunica'] == SUMMARY
    assert county_controls['Kemper'] == totals['sos-2024-county-kemper']
    delta = {n:totals['sos-2024-county-tunica'][n]-SUMMARY[n] for n in NAMES}
    assert {n:d for n,d in delta.items() if d} == {'Kamala D. Harris':-1,'Ty Pinkins':-1}
    output = {
        'status':'pass_bounded_two_source_all11_fields_with_Tunica_primary_disagreements',
        'worker_readings_snapshot':pin(snapshot),'coordinator_original_complete_renders':originals,
        'coordinator_orthogonal_full_page_views':upright,'candidate_order':NAMES,
        'independent_manual_numeric_readings':READINGS,'independent_manual_header_readings':LABELS,
        'native_constituents':26,'nonadditive_Kemper_parallel_columns':11,
        'native_candidate_positions':286,'source_TOTAL_positions':22,
        'nonadditive_parallel_candidate_positions':121,'numeric_positions':429,'unused_null_positions':176,
        'all22_native_vectors_close_their_printed_TOTAL':True,'source_TOTAL_vectors':totals,
        'independent_Tunica_summary_named_readings':SUMMARY,'Tunica_SEMS_minus_ESandS_and_CSV':delta,
        'Tunica_Senate_generic_marks':3,'Tunica_presidential_generic_marks':4,
        'Tunica_summary_clock_literal':'11/15/2024 3:18 PM','Tunica_summary_clock_zone':None,
        'historical_CSV_source_pin':csv_source,'county_controls':county_controls,
        'scope':'Coordinator read all eleven candidate rows from complete original Tunica PDF7/8 and Kemper PDF6/7/8, with orthogonal rotations only.429 numeric and176 unused/null positions match the independent worker ledger. Kemper unofficial PDF6 repeats the eleven official PDF7 columns in every candidate field and remains non-additive; PDF8 adds3 native columns and TOTAL. Tunica named Harris1836 and Pinkins1797 disagree by1 each with ES&S PDF3 and county CSV; generic marks4/3 are separate, not residual allocations or validated named write-ins. Other county full-candidate/native fields, historical native/method and current geographic/reporting approval remain open.'}
    (DATA / 'coordinator-tunica-kemper-allfield-review.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({k:output[k] for k in ['status','native_constituents','numeric_positions','unused_null_positions','Tunica_SEMS_minus_ESandS_and_CSV']}))


if __name__ == '__main__':
    main()
