#!/usr/bin/env python3
"""Independent read-only peer comparison. Peer values never build this worker's data."""
import collections,csv,gzip,hashlib,json
from pathlib import Path
D=Path(__file__).resolve().parent;P=D.parent/'baselines'
FIELDS=['county_code','county_name','election_number','election_date','election_name','precinct_id','polling_location','registered_total','registered_rep','registered_dem','registered_other','contest_name','district','contest_code','candidate_name','candidate_party','candidate_fvrs_id','candidate_doe_id','votes']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    paths=['official-county-candidates.csv','compiled-county-candidates.csv','native-source-rows.csv.gz','native-units.csv.gz','source/zip-member-inventory.json'];witness={p:dict(sha256=sha(P/p),bytes=(P/p).stat().st_size) for p in paths}
    ours={}
    for y in ['2024','2022','2020']:
        for line in gzip.open(D/'extracts'/f'native-source-rows-{y}.jsonl.gz','rt'):
            r=json.loads(line);k=(r['source_id'],r['source_member'],str(r['source_row_1based']));assert k not in ours;ours[k]=(r['fields'],not r['recount_overlap_excluded'])
    peer={}
    for r in csv.DictReader(gzip.open(P/'native-source-rows.csv.gz','rt')):
        k=(r['source_id'],r['source_member'],r['source_row_1based']);assert k not in peer;peer[k]=([r[f] for f in FIELDS],r['base_selected']=='True')
    assert ours.keys()==peer.keys();assert ours==peer
    a={(r['context'],r['county'],r['candidate_party']):int(r['votes']) for r in csv.DictReader((D/'extracts'/'primary-county-candidates.csv').open())}
    b={(r['year']+'_'+r['contest'],r['county'],r['candidate_name']+' ('+r['party']+')'):int(r['votes']) for r in csv.DictReader((P/'official-county-candidates.csv').open())};assert a==b
    apos={(r['context'],r['county'],r['candidate_party']):(int(r['source_tr']),int(r['source_td_1based'])) for r in csv.DictReader((D/'extracts/primary-county-candidates.csv').open())}
    bpos={(r['year']+'_'+r['contest'],r['county'],r['candidate_name']+' ('+r['party']+')'):(int(r['source_tr_1based']),int(r['source_column_1based'])) for r in csv.DictReader((P/'official-county-candidates.csv').open())};assert apos==bpos
    aggregate=collections.Counter()
    for fields,base in ours.values():
        if not base:continue
        category={'900':'generic_writein_marks','901':'overvotes','902':'undervotes'}.get(fields[17],'named_candidate')
        aggregate[(fields[3].split('/')[-1],'senate' if fields[13]=='120000' else 'president',fields[0],fields[1],*fields[14:18],category)]+=int(fields[18])
    names=['year','contest','county_code','county','candidate_name','party','candidate_fvrs_id','candidate_doe_id','category']
    pcounty={tuple(r[k] for k in names):int(r['votes']) for r in csv.DictReader((P/'compiled-county-candidates.csv').open())};assert dict(aggregate)==pcounty
    units={}
    for line in gzip.open(D/'extracts'/'native-units.jsonl.gz','rt'):
        r=json.loads(line);y,contest=r['context'].split('_');key=json.dumps([y,contest,r['county_code'],r['election_number'],r['precinct_id'],r['polling_location']],ensure_ascii=False,separators=(',',':'));units[key]=r
    peerunits={r['native_key']:r for r in csv.DictReader(gzip.open(P/'native-units.csv.gz','rt'))};assert units.keys()==peerunits.keys()
    for k,u in units.items():
        p=peerunits[k];assert u['county_code']==p['county_code'];assert sorted(u['registration_observations'])==json.loads(p['registration_contexts']);assert sorted([r['candidate_label'],r['party'],r['fvrs_id'],r['doe_candidate_id']] for r in u['candidate_category_rows'])==json.loads(p['candidate_keys'])
        assert str(u['source_label_method_hint_only'])==p['native_label_method_hint']
        expected={'A':0,'B':0,'other_printed_candidates':0,'generic_writein_marks':0,'overvotes':0,'undervotes':0}
        for r in u['candidate_category_rows']:
            key={'900':'generic_writein_marks','901':'overvotes','902':'undervotes'}.get(r['doe_candidate_id'],'A' if r['party']=='DEM' else 'B' if r['party']=='REP' else 'other_printed_candidates');expected[key]+=r['votes']
        assert all(v==int(p[k]) for k,v in expected.items());assert [[u['source_member'],r['source_row_1based']] for r in u['candidate_category_rows']]==json.loads(p['source_positions'])
        assert p['method']=='not_provided_in_19field_schema'
    contract=json.loads((D/'priority-set.json').read_text());ranks={}
    for r in csv.DictReader((P/'official-county-candidates.csv').open()):
        if (r['year'],r['contest'])==('2024','senate'):ranks[r['county']]=ranks.get(r['county'],0)+int(r['votes'])
    order=sorted(ranks,key=lambda c:(-ranks[c],c));assert [(r['name'],r['votes']) for r in contract['all_unit_order']]==[(c,ranks[c]) for c in order]
    total=sum(ranks.values());cum=0
    for i,c in enumerate(order,1):
        prev=cum;cum+=ranks[c]
        if 5*cum>=4*total:break
    assert i==contract['minimum80']['count'] and prev==contract['minimum80']['preceding_votes'] and cum==contract['minimum80']['votes']
    ec=0;bc=0
    pe={(r['year'],r['county_fips']):r for r in json.loads((P/'eavs-controls.json').read_text())}
    for line in gzip.open(D/'extracts/eavs-controls.jsonl.gz','rt'):
        r=json.loads(line);p=pe[(r['context'],r['fips'])];assert r['source_csv_row_1based']==p['source_csv_row_1based'] and r['source_member']==p['source_member']
        for k,v in r['fields'].items():assert p['fields'][k]==v;ec+=1
    pb={(r['year'],r['county_fips']):r for r in json.loads((P/'bookclosing-controls.json').read_text())}
    for line in gzip.open(D/'extracts/bookclosing-controls.jsonl.gz','rt'):
        r=json.loads(line);p=pb[(r['context'],r['fips'])];assert r['row']==p['row'] and r['sheet']==p['sheet'];assert r['cells']==p['cells'];bc+=len(r['cells'])
    for name in ['eavs-controls.json','bookclosing-controls.json']:witness[name]=dict(sha256=sha(P/name),bytes=(P/name).stat().st_size)
    result=dict(status='pass',comparison='read-only; independent primary and raw19 extracts; no peer values used as inputs',peer_agent_id='1df5579b-5d40-46b9-a7af-17fdb1a2398d',peer_files=witness,raw19_source_positions=len(ours),raw_fields_compared=len(ours)*19,primary_county_candidate_cells=len(a),primary_TR_TD_positions=len(apos),compiled_county_candidate_category_controls=len(pcounty),native_contexts=len(units),eavs_shared_fields=ec,bookclosing_exact_cells=bc,all_county_order=67,minimum80=contract['minimum80'],candidate_method_scope='both original19 absent; source labels retained without method allocation',coordinator_accepted=False)
    (D/'peer-agreement.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
