#!/usr/bin/env python3
"""Freeze reciprocal peer derivatives after independent original extraction.
Never edits peer files. Every comparison operates on immutable hash-named copies.
"""
from pathlib import Path
import csv,gzip,json,hashlib,datetime
from collections import Counter
D=Path(__file__).resolve().parent;B=D.parent/'baselines';P=D/'peer-captures';P.mkdir(exist_ok=True)
def sha(b):return hashlib.sha256(b).hexdigest()
def jlines(p):return[json.loads(s)for s in gzip.decompress(p.read_bytes()).decode().splitlines()]
def main():
    manifest=[];checks=0;errors=[]
    def capture(path):
        b=path.read_bytes();p=P/(sha(b)+('-'+path.name));
        if p.exists():assert p.read_bytes()==b
        else:p.write_bytes(b)
        manifest.append({'original_path':str(path.relative_to(D.parent.parent)),'snapshot_path':str(p.relative_to(D.parent.parent)),'sha256':sha(b),'bytes':len(b)})
        return b
    def ck(a,b,label):
        nonlocal checks;checks+=1
        if a!=b:errors.append({'label':label,'own':a if len(str(a))<1000 else {'sha256':sha(json.dumps(a,sort_keys=True).encode()),'items':len(a)},'peer':b if len(str(b))<1000 else {'sha256':sha(json.dumps(b,sort_keys=True).encode()),'items':len(b)}})
    def csvb(b):return list(csv.DictReader(io for io in b.decode().splitlines()))
    ownraw=jlines(D/'extract/original-native-records.jsonl.gz')
    for year in [2024,2022,2020]:
        peer=csvb(gzip.decompress(capture(B/f'extract/{year}-raw-rows.csv.gz')));own=[r for r in ownraw if r['year']==year];ck(len(own),len(peer),f'{year}raw count')
        for o,p in zip(own,peer):
            ck(o['record_position_1based']+1,int(p['csv_record_1based_including_header']),f'{year}record position')
            for k,v in o['fields'].items():ck(v,p[k],f'{year}:{o["record_position_1based"]}:{k}')
        pu=json.loads(capture(B/f'extract/{year}-units.json'));ou=jlines(D/f'extract/native-units-{year}.jsonl.gz');pd={(p['JurisdictionID'],p['PrecinctName']):p for p in pu};ck(len(ou),len(pd),f'{year}native count')
        for o in ou:
            p=pd[(o['authority_id'],o['precinct_name_literal'])]
            for n,k in [(p['A_name'],'A'),(p['B_name'],'B')]:ck(o['printed_candidate_votes'][n],p[k],f'{year}:{o["key"]}:{n}')
            ck(o['literal_categories'],p['literal_category_record_sums'],f'{year}:{o["key"]}:literal categories')
            ck([i+1 for i in o['source_records_1based']],p['source_positions'],f'{year}:{o["key"]}:source positions')
            ck([o['registration_literal']],p['registration_literals'],f'{year}:{o["key"]}:registration')
            ck(sorted([[c['container_id'],c['juris_name']]for c in o['source_contexts']]),sorted(p['presentation_contexts']),f'{year}:{o["key"]}:contexts')
            ck(o['generic_writein_marks'],p['generic_writein_marks'],f'{year}:{o["key"]}:generic observed')
            for raw,k in [('Under Votes','under_votes_observed'),('Over Votes','over_votes_observed'),('Blank Ballots','blank_ballots_observed')]:ck(o['literal_categories'].get(raw),p[k],f'{year}:{o["key"]}:{raw}')
    peer=csvb(capture(B/'extract/county-candidate-source-rows.csv'));own=csvb((D/'extract/county-candidate-source-rows.csv').read_bytes());pd={(p['year'],p['county_key'],p['candidate_literal']):p for p in peer};ck(len(own),len(pd),'county candidate count')
    for o in own:
        p=pd[o['year'],o['county_authority_id'],o['name']]
        for k,z in [('party','party_literal'),('votes','votes'),('votes_literal','votes_literal'),('percentage_literal','percentage_literal'),('href','href_literal'),('detail_url','detail_url'),('table_id','table_id')]:ck(o[k],p[z],f'county:{o["year"]}:{o["county_authority_id"]}:{o["name"]}:{k}')
        ck(int(o['tr_position_0based'])+1,int(p['table_row']),'county table row')
    peer=csvb(capture(D.parent/'county-baselines.csv'));pd={(p['year'],p['county_key']):p for p in peer};own=csvb((D/'extract/county-all-years.csv').read_bytes())
    for o in own:
        p=pd[o['year'],o['county_authority_id']]
        for k,z in [('all_named_votes','all_named_votes'),('printed_votes','native_printed_votes'),('native_generic_writein_marks','native_generic_marks'),('ballots_cast','ballots_cast'),('historical_Total_Voters','historical_Total_Voters')]:ck(o[k],p[z],f'county controls:{o["year"]}:{o["county_authority_id"]}:{k}')
    pc=json.loads(capture(B/'priority/contracts.json'))['contracts'];ours=json.loads((D/'extract/county-priorities.json').read_text())
    for year in [2024,2022,2020]:
        for field,pf in [('all_named_votes','all_named_votes'),('printed_votes','native_printed_votes'),('printed_plus_generic_marks','native_raw_mark_universe'),('ballots_cast','ballots_cast')]:
            p=pc[f'county-{year}-{pf}'];o=ours[f'{year}:{field}'];order=csvb((D/f'extract/county-{year}-order-{field}.csv').read_bytes())
            ck([r['county_authority_id']for r in order],p['full_order'],f'full county order:{year}:{field}')
            for k,z in [('denominator','denominator'),('minimum80_count','minimum_count'),('preceding_votes','before_votes'),('cumulative80_votes','crossing_votes')]:ck(o[k],p[z],f'county80:{year}:{field}:{k}')
    p=csvb(gzip.decompress(capture(B/'priority/native-2024-printed-observed.csv.gz')));o=jlines(D/'extract/native-2024-order-printed_observed_sum.jsonl.gz')
    unavailable={(r['authority_id'],r['precinct_name_literal'])for r in o if r['administrative_only']}
    # Peer table orders its explicitly defined empty recorded sum as0. Own
    # primary order places unavailable named pools after observed numeric0.
    # Canonicalize only these four documented cases; retain both raw orders.
    p=[r for r in p if(r['JurisdictionID'],r['PrecinctName'])not in unavailable]+sorted([r for r in p if(r['JurisdictionID'],r['PrecinctName'])in unavailable],key=lambda r:(r['JurisdictionID'],r['PrecinctName']))
    ck([(r['authority_id'],r['precinct_name_literal'])for r in o],[(r['JurisdictionID'],r['PrecinctName'])for r in p],'full native printed order after explicit unavailable-pool placement')
    for a,b in zip(o,p):ck(a['printed_known_recorded_sum'],int(b['printed_votes']),'native ranked recorded sum (empty sum explicitly not observed0)');ck(a['cumulative_votes'],int(b['cumulative_votes']),'native ranked cumulative')
    # All authority/category totals in every year.
    peer=csvb(capture(B/'extract/authority-candidate-category-totals.csv'));pd={(r['year'],r['JurisdictionID'],r['candidate_or_category_literal']):int(r['votes'])for r in peer}
    own={(str(y),a['authority_id'],n):v for y in [2024,2022,2020]for a in jlines(D/f'extract/authority-native-{y}.jsonl.gz')for n,v in a['literal_categories'].items()};ck(own,pd,'all authority candidate/category controls')
    result={'status':'pass'if not errors else'fail','peer_agent_id':'a7b49f02-905f-4208-b957-fffdb58615bf','own_original_first_build':'build_turnout.py','captured_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'errors':errors,'snapshots':manifest,'native_order_semantic_adapter':'Only four unavailable named pools are moved after observed numeric0 in peer recorded-sum order. Their source rows and empty recorded aggregates agree; no votes or other order changed. Both immutable raw orders retained.','scope':'independent historical arithmetic agreement only; not legal write-in allocation or geographic approval'}
    (D/'peer-reconciliation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'checks':checks,'error_count':len(errors),'first_errors':errors[:2]}))
    assert not errors
if __name__=='__main__':main()
