#!/usr/bin/env python3
"""Read-only comparison AFTER sealed independent original-first witness."""
import csv,gzip,json,hashlib,tarfile,datetime
from pathlib import Path
from urllib.parse import quote
from build import groups,county_groups
from extract import P,js,save,sha
PEER=P.parent/'turnout'
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def main():
 assert (P/'history/original-first/snapshot.json').exists()
 priority=read(PEER/'priority-set.json');assert sha((PEER/'priority-set.json').read_bytes())=='6b945a43a1f47f3dda1c072cd240f692633b00371ef93c4778e37a67afc93355'
 assert sha((PEER/'asset-manifest.json').read_bytes())=='d1558ec667c3e91f3727e24b5e1898b35d9c19208f3e55056517f310fbcb5693'
 files=[PEER/'priority-set.json',PEER/'asset-manifest.json',PEER/'final-seal.json',PEER/'source/SCHEMA.md',PEER.parent/'county-turnout.csv']+sorted((PEER/'orders').glob('*'))+sorted((PEER/'extracted').glob('*'))
 evidence=P/'history/peer-frozen';evidence.mkdir(parents=True,exist_ok=True)
 with tarfile.open(evidence/'reviewed-bodies.tar.gz','w:gz') as t:
  for p in files:t.add(p,arcname=str(p.relative_to(PEER.parent)))
 save('history/peer-frozen/receipts.json',{'retrieved_local_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'peer_phase':'read only after original-first snapshot','paths':[{'path':str(f),'sha256':sha(f.read_bytes()),'bytes':f.stat().st_size} for f in files]})
 units=[u for u in groups() if not(u['year']=='2020' and u['contest']!='U.S. Senate')];scopes={}
 for lane in sorted({u['lane'] for u in units}):scopes[lane]=[u for u in units if u['lane']==lane]
 errors=[];checks={};orders={}
 def eq(label,a,b):
  checks[label]=a==b
  if a!=b:errors.append({'scope':label,'independent':a,'peer':b})
 def order(label,rs):
  rs=sorted(rs,key=lambda u:(-u['votes'],u['key']));den=sum(u['votes'] for u in rs);cum=0;out=[]
  for i,u in enumerate(rs,1):
   cum+=u['votes'];out.append({'key':u['key'],'votes':u['votes'],'rank':i,'cumulative_votes':cum,'share_numerator':u['votes'],'share_denominator':den,'cumulative_share_numerator':cum})
  orders[label]=out;peer=list(csv.DictReader((PEER/'orders'/f'{label}.csv').open()));eq(label+' full numeric order',out,[{k:r[k] if k=='key' else int(r[k]) for k in out[0]} for r in peer])
 for lane,us in scopes.items():order(lane,us)
 primary=scopes['2024-xlsx']
 for method,suffix in [('Election Day','election-day'),('Early Vote','early-vote'),('Absentee','absentee'),('Provisional','provisional')]:order('2024-xlsx-'+suffix,[dict(u,votes=sum(u['methods'][method].values())) for u in primary])
 for year in ['2020','2022','2024']:
  info=js(year+'-info')['response'];co=county_groups(scopes[year+'-api']);order(year+'-county-contest',[{'key':f"AR:{year}-api-county:{c['county_fips']}:{quote(c['county_name'],safe='')}",'votes':c['votes']} for c in co])
  full=js(year+'-full')
  byname={v['locationName']:k for k,v in info['locations'].items()}
  for field in ['VotesCast','RegisteredVoters']:
   order(year+'-county-'+field,[{'key':f"AR:{year}-full-{field}:{byname[c['CountyName'].upper()]}:{quote(c['CountyName'],safe='')}",'votes':c[field]} for c in full['Turnout']['CountyTurnout']])
  # Whole raw parsed state, metadata, county response equality; source positions/types/nulls survive.
  ap=read(PEER/'extracted'/f'{year}-api-original-relevant-records.json.gz');tu=read(PEER/'extracted'/f'{year}-turnout-original-records.json.gz')
  cid={'2020':'560','2022':'1123','2024':'366'}[year]
  eq(year+' selected raw metadata',js(year+'-metadata')['response']['contests'][cid],ap['metadata'])
  eq(year+' county raw scope size',len(ap['counties']),75)
  for v in ap['counties']:
   ci=v['county_fips'];raw=js(f'{year}-federal-{ci}')['response']['contests'][cid]
   eq(f'{year} federal {ci} full raw contest',raw,v['raw_contest'])
   eq(f'{year} federal {ci} raw pointer',f'/response/contests/{cid}',v['source_contest_pointer'])
  for v in ap['native_inventory']:
   ci=v['county_fips'];ni=v['native_id'];eq(f'{year} full native raw descriptor {ci} {ni}',info['locations'][ci]['locations'][ni],v['raw_location'])
  fp=read(PEER/'extracted'/f'{year}-full-original-relevant-records.json.gz');fullbody=js(year+'-full');original=fullbody['ContestData'][fp['contest_position']]
  eq(year+' FullData complete state fields without separately compared Counties',{k:v for k,v in original.items() if k!='Counties'},fp['state'])
  eq(year+' FullData raw wrapper count',len(original['Counties']),len(fp['wrappers']))
  eq(year+' FullData whole turnout raw',fullbody['Turnout'],fp['turnout'])
  eq(year+' FullData election metadata raw',fullbody['ElectionInfo'],fp['election_info'])
  for i,w in enumerate(fp['wrappers']):eq(f'{year} FullData raw wrapper {i}',original['Counties'][i],w['raw'])
  eq(year+' full federal state raw',js(year+'-federal-state'),ap['state'])
  eq(year+' full turnout state raw',js(year+'-turnout-state'),tu['state'])
  # Peer county records are dictionaries with their exact response and source metadata.
  for label,d in [('api',ap),('turnout',tu)]:
   cc=d['counties']
   if isinstance(cc,dict):
    for ci,v in cc.items():
     raw=js(f'{year}-'+('federal' if label=='api' else 'turnout')+'-'+ci)
     # The peer stores the exact parsed body under raw when wrapped.
     if v==raw:eq(f'{year} {label} {ci} full raw',raw,v)
     elif isinstance(v,dict) and 'raw' in v:eq(f'{year} {label} {ci} full raw',raw,v['raw'])
     else:eq(f'{year} {label} {ci} representation',list(v) if isinstance(v,dict) else type(v).__name__,'expected raw body wrapper')
 # Compare each shared native full field independently reconstructed.
 universes=read(PEER/'extracted/source-native-universes.json.gz')
 for lane,us in scopes.items():
  peer={u['key']:u for u in universes[lane]};eq(lane+' key coverage',setstr(u['key'] for u in us),setstr(peer))
  for u in us:
   v=peer[u['key']]
   for f in ['county_fips','county_name','native_id','native_name','votes','candidates']:
    eq(lane+' '+u['key']+' '+f,u[f],v[f])
   if lane=='2024-xlsx':
    eq(u['key']+' parties',u['party_literals'],v['party_literals']);eq(u['key']+' methods',{m:sum(c.values()) for m,c in u['methods'].items()},v['methods']);eq(u['key']+' source rows',[int(p['position'].split('/')[-1][1:]) for p in u['source_positions']],v['source_rows'])
 match_result=read(P/'source/native-name-vector-matches.json');matchids={r['xlsx_key']:r['api_key'] for r in match_result['matched']}
 for v in universes['2024-xlsx']:
  eq(v['key']+' exact matched API key',matchids.get(v['key']),v['matched_api_key'])
  eq(v['key']+' exact matched API native ID',matchids[v['key']].split(':')[-1] if v['key'] in matchids else None,v['matched_api_native_id'])
 raw_peer=read(PEER/'extracted/2024-xlsx-president-raw-rows.json.gz')
 raw_own=[json.loads(line) for line in gzip.decompress((P/'source/xlsx-president-rows.jsonl.gz').read_bytes()).decode().splitlines()]
 eq('XLSX raw complete ordered row count',len(raw_own),len(raw_peer['rows']))
 for own,other in zip(raw_own,raw_peer['rows']):
  eq('XLSX raw row '+str(own['row']),{'source_row':own['row'],'source_cells':[{'ref':c['position'],'type':c['type'],'v':c['raw_value'],'value':c['value']} for c in own['cells']]},{'source_row':other['source_row'],'source_cells':other['source_cells']})
 primary_order=orders['2024-xlsx'];total=sum(u['votes'] for u in primary);threshold=(4*total+4)//5;n=next(i for i,r in enumerate(primary_order,1) if r['cumulative_votes']>=threshold)
 eq('2841 full primary order',[r['key'] for r in primary_order],[r['key'] for r in priority['full_order']]);eq('1056 priority',[r['key'] for r in primary_order[:n]],priority['ordered_priority_keys']);eq('1785 remainder',[r['key'] for r in primary_order[n:]],priority['remainder_keys']);eq('75 parents',sorted({u['county_fips'] for u in primary}),sorted(p['county_fips'] for p in priority['all75parents']))
 for parent in priority['all75parents']:
  for lane,children in parent['source_native_constituents'].items():
   ours=[u for u in scopes[lane] if u['county_fips']==parent['county_fips']]
   eq(parent['county_fips']+' '+lane+' full constituents',[(u['key'],u['native_name'],u['votes']) for u in ours],[(u['key'],u['native_name'],u['votes']) for u in children])
 save('peer-reconciliation.json',{'status':'pass' if not errors else 'differences','checks':len(checks),'passing':sum(checks.values()),'errors':errors,'orders_compared':len(orders),'priority':{'units':len(primary),'total':total,'minimum80_count':n,'threshold':threshold,'before':primary_order[n-2]['cumulative_votes'],'crossing':primary_order[n-1]['cumulative_votes'],'remainder':len(primary)-n},'acceptance':'historical numeric/source comparison only; coordinator geographic/legal approval pending','representations':'own source path position is candidate-cell/list address; peer source_pointer is contest node/worksheet address; these are distinct representations and not altered'})
 save('independent-complete-orders.json',orders)
 print('checks',len(checks),'errors',len(errors),'orders',len(orders));print(str(errors[:3])[:2000])
def setstr(xs):return sorted(xs)
if __name__=='__main__':main()
