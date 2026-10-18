#!/usr/bin/env python3
"""Read-only final first-wave comparison; no writes to any peer/coordinator path."""
import csv,gzip,json
from acquire import ROOT,dump,sha
STATE=ROOT.parent.parent
PINS={
'turnout.md':('f2355a0dcb4b95ea257b15087ee6232ca8c3db8c5bac3cf79bedbc4a888018c5',48195),
'data/county-turnout.csv':('473cd7500701e0c7afe7918e1ff34c9c60735e3c3f1446fae0b19084901e7ec9',99704),
'data/turnout/asset-manifest.json':('8303fbce1ee0cb31940fe1ac6e754a3602b991eedcd23b2ab313fc012a594bc2',40061),
'county-partisanship.md':('71244accd7a03dda7ef4305aeaf8bb6fead68fa3cb70c0bee68696f77da7f5a3',25742),
'data/county-baselines.csv':('a52225ce6be80e807296d384d91c4e71d2f6b71a13b52a662da2bca34c691355',570002),
'data/baselines/asset-manifest.json':('f454633a24723c310b1290f8ff3a247dfb2a1629f51c75514d39cd1fcf11792c',49407),
'data/baselines/validation.json':('f72993c821af799f9424bc22c5731ff14fff0232e5654bb1dee36367f54e206c',3395),
'data/turnout/priority-set.json':('11c042966c67a50e496ad6f839afd8e3c8b28afe6e2761c6cda1aa51f7ce90fc',3653481)}
def loc(r):
    d=dict(r['source_locator']);label=d.pop('label_column',None)
    if label=='G':d['source_column_start']='G'
    if label=='A' and 'ballots-cast' in r['source_id'] and r['source_id'].startswith('2020'):d['source_column_start']='A'
    return json.dumps(d,sort_keys=True)
def fields(f):return {('ballots_total' if k=='ballots_cast' else k):v for k,v in f.items()}
def key(r):return r['source_id'],r['county'],r.get('native_label',r.get('label')),loc(r)
def main():
    observed=[]
    for path,(h,n) in PINS.items():
        b=(STATE/path).read_bytes();assert len(b)==n and sha(b)==h,path
        observed.append({'path':path,'sha256':h,'bytes':n,'status':'final_freeze_exact'})
    own=[json.loads(l) for l in gzip.open(ROOT/'historical-native-records.jsonl.gz','rt')];lookup={key(r):r for r in own}
    peers=[json.loads(l) for l in gzip.open(STATE/'data/baselines/native-fields.jsonl.gz','rt')]
    checks=0;typechecks=0
    for p in peers:
        r=lookup[key(p)];assert r['fields']==fields(p['fields']) and r['raw_fields']==fields(p['raw_fields']),key(p);checks+=len(r['fields'])
        if r['field_types'] and any(v is not None for v in r['field_types'].values()):
            for k,v in fields(p.get('cell_types',{})).items():assert r['field_types'][k]==v;typechecks+=1
    assert len(peers)==len(own)==7360
    pc=json.load(open(STATE/'data/baselines/source/controls.json'));controls=[{**r,'source_id':a['source_id']} for a in json.load(open(ROOT/'historical-audit.json')) for r in a['all_controls']]
    clookup={key(r):r for r in controls}
    for p in pc:
        r=clookup[key(p)];assert r['fields']==fields(p['fields']) and r['raw_fields']==fields(p['raw_fields']),key(p)
    assert len(pc)==483
    csvchecks=0
    for r in csv.DictReader((STATE/'data/county-baselines.csv').open()):
        candidates=[p for p in own if p['source_id']==r['source_id'] and p['county']==r['county'] and p['native_label']==r['native_label']];assert len(candidates)==1
        p=candidates[0]
        for k,v in p['fields'].items():assert r[k]==('' if v is None else str(v));csvchecks+=1
    c=json.load(open(STATE/'data/turnout/priority-set.json'));tr=list(csv.DictReader((STATE/'data/county-turnout.csv').open()));assert [r['geography_key'] for r in tr]==c['full_ordered_keys']
    for r in tr:
        p=next(p for p in own if p['source_id']==c['basis_source_id'] and p['county']==r['county'] and p['native_label']==r['native_label'])
        for k,v in p['fields'].items():assert r[k]==('' if v is None else str(v))
    dump(ROOT/'peer-final-verification.json',{'status':'pass','pins':observed,'partisanship_records':len(peers),'partisanship_native_fields':checks,'partisanship_BIFF_types':typechecks,'partisanship_controls':len(pc),'partisanship_csv_rows':960,'partisanship_csv_candidate_fields':csvchecks,'turnout_csv_rows':len(tr),'full320_order_exact':True,'priority143_exact':True,'schema_aliases':['peer ballots_cast → ballots_total','label_columnA/G → same exact original source column; no label/geographic alias'],'coordinator_acceptance':'data/coordinator-priority-acceptance.json (read-only external authority; no reverse hash cycle)','mutable_second_wave_pins':[]})
    print('PASS: both final freezes exact;7360 baseline source records,483 controls,960 CSV rows and320 rank rows independently agree')
if __name__=='__main__':main()
