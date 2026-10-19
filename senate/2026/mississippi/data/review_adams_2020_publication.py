"""Bounded direct-original Adams2020 publication comparison; no mixed-vintage rollup."""
from pathlib import Path
import csv
import gzip
import hashlib
import io
import json

DATA = Path(__file__).resolve().parent
ROOT = DATA.parent
NAMES = ['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards']
READINGS = {
    'sos-2020-county-adams': [[125,362,1069,369,192,831,586,205,7736],
                             [125,99,55,80,192,38,457,341,5416],
                             [1,2,6,3,3,5,9,6,152]],
    'sos-2020-county-adams-amended': [[287,362,1069,369,409,831,586,205,8190],
                                     [125,99,55,80,192,38,457,341,5416],
                                     [1,2,6,3,3,5,9,6,152]]}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    renders = json.loads((DATA/'coordinator-qa/adams-2020-original-renders.json').read_bytes())
    assert len(renders) == 2
    for r in renders:
        b = (ROOT/r['path']).read_bytes()
        assert sha(b) == r['sha256'] and len(b) == r['bytes']
        meta = r['source_pin']
        stored = (ROOT/meta['path']).read_bytes()
        assert sha(stored) == meta['stored_sha256']
        assert sha(gzip.decompress(stored)) == meta['raw_sha256']
    path = DATA/'coordinator-qa/adams-2020-reading-snapshot.json.gz'
    if not path.exists():
        p = DATA/'baselines/county-2020-repair-readings.json'
        b = p.read_bytes()
        x = json.loads(b)
        selected = [r for r in x['readings'] if r['source_id'] in READINGS]
        assert p.read_bytes() == b and len(selected) == 2
        path.write_bytes(gzip.compress((json.dumps({'reading_file_pin':{'path':str(p.relative_to(ROOT)),
            'bytes':len(b),'sha256':sha(b)},'selected_source_readings':selected},indent=2)+'\n').encode(),mtime=0))
    snapshot = json.loads(gzip.decompress(path.read_bytes()))
    for r in snapshot['selected_source_readings']:
        assert r['source_column_accepted'] == 9
        assert [r['candidate_values'][n] for n in NAMES] == [row[-1] for row in READINGS[r['source_id']]]
        assert r['raw_sha256'] == next(v['source_pin']['raw_sha256'] for v in renders if v['source_pin']['id']==r['source_id'])
    delta = [b[-1]-a[-1] for a,b in zip(READINGS['sos-2020-county-adams'],READINGS['sos-2020-county-adams-amended'])]
    assert delta == [454,0,0]
    manifest = json.loads((DATA/'news/manifest.json').read_bytes())
    source = next(r for r in manifest if r['id']=='sos-2020-recap-csv')
    stored = (DATA/'news'/source['asset']).read_bytes()
    raw = gzip.decompress(stored)
    assert sha(stored) == source['stored_sha256'] and sha(raw) == source['raw_sha256']
    rows = [r for r in csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
            if r['County']=='Adams' and r['Office']=='United States-Senate ']
    assert {r['Candidate']:int(r['County Total']) for r in rows} == dict(zip(NAMES,[8190,5416,152]))
    b = path.read_bytes()
    output = {'status':'pass_bounded_original_Adams_publication_difference_not_full_native_or_uniform_vintage',
        'complete_original_page_renders':renders,'candidate_order':NAMES,
        'independent_last8_constituent_and_TOTAL_column_readings':READINGS,
        'physical_TOTAL_column':9,'original_PDF_page':4,'amended_PDF_page':3,
        'printed_TOTAL_vectors':{sid:[row[-1] for row in values] for sid,values in READINGS.items()},
        'amended_minus_original_TOTAL':[454,0,0],'CSV_source_pin':source,'CSV_rows':rows,
        'worker_TOTAL_readings_compared':6,'original_numeric_positions_independently_read':54,
        'unused_blank_positions_preserved':12,
        'worker_reading_snapshot_pin':{'path':str(path.relative_to(ROOT)),'bytes':len(b),'sha256':sha(b)},
        'scope':'Both complete last-block pages visibly print TOTAL at physical9. Each also has8 actual constituent columns and2 unused columns, preserved separately. This bounded check reads54 numeric cells and12 unused/null positions, compares six county TOTAL fields to the independent worker ledger, and verifies CSV matches the amended total. Earlier Adams source pages/native sums are not reviewed here. The additional+454 Espy printed county difference makes concrete that Coahoma matching the statewide net does not prove it was the only county publication change. Do not roll up mixed current-index original/amended documents as a common statewide certificate vintage, allocate residuals, or infer source publication/certification/correction chronology.'}
    (DATA/'coordinator-adams-2020-publication-review.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'status':output['status'],'TOTAL_delta':delta,'compared_TOTAL_fields':6,
                      'bounded_original_numeric_positions':54}))


if __name__ == '__main__':
    main()
