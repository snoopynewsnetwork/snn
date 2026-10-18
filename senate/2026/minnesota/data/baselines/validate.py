"""Meaningful offline validation and complete owned asset audit. No Git access."""
import collections,datetime,gzip,hashlib,json,math,re,zipfile,io
from pathlib import Path
from extract import H,S,N,readcsv,dump
from definitions import CONTESTS
from calculator import live,bounded
STATE=H.parent.parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def near(a,b,tol=1e-7):assert abs(a-b)<=tol,(a,b,abs(a-b))
def files():return sorted([p for p in H.rglob('*') if p.is_file() and p.name!='asset-manifest.json']+[STATE/'county-partisanship.md',H.parent/'county-baselines.csv'])
def asset_manifest():
 entries=[]
 for p in files():
  b=p.read_bytes();assert len(b)<40000000
  entries.append(dict(path=str(p.relative_to(STATE)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
 refs=json.loads((S/'shared-originals.json').read_text())
 dump(H/'asset-manifest.json',dict(schema='mn-owned-assets/1.0',scope='Every assigned file, excluding this recursively unhashable manifest itself; no dependency/cache directories',owned_files=entries,source_references=[dict(path=str((H/r['reference_path']).resolve().relative_to(STATE)),stored_bytes=(H/r['reference_path']).stat().st_size,stored_sha256=r['stored_sha256'],original_bytes=r['bytes'],original_sha256=r['raw_sha256']) for r in refs]))
 for r in entries:
  p=STATE/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
 return len(entries)

def main():
 checks={};gaps=[]
 for m in json.loads((S/'shared-originals.json').read_text()):
  p=H/m['reference_path'];assert sha(p)==m['stored_sha256'];raw=gzip.decompress(p.read_bytes());assert hashlib.sha256(raw).hexdigest()==m['raw_sha256'] and len(raw)==m['bytes']
  if 'precinct-original' in m['id']:assert zipfile.ZipFile(io.BytesIO(raw)).testzip() is None
 checks['shared_source_hashes_and_XLSX_CRC']='pass'
 for m in json.loads((S/'acquisition.json').read_text()):
  if 'stored_path' not in m:continue
  p=H/m['stored_path'];assert sha(p)==m['stored_sha256'];b=gzip.decompress(p.read_bytes());assert len(b)==m['raw_bytes'] and hashlib.sha256(b).hexdigest()==m['raw_sha256']
 checks['fresh_capture_hashes']='pass'
 controls=json.loads((S/'extraction-controls.json').read_text());context=json.loads((S/'workbook-context.json').read_text())
 for year,n in [(2024,4103),(2022,4103),(2020,4110)]:
  rr=readcsv(H/f'native-{year}.csv.gz');assert len(rr)==n and len({r['native_key'] for r in rr})==n and len({r['county_fips'] for r in rr})==87
  assert all(r['VTDID']==r['county_fips']+r['PCTCODE'] for r in rr);assert len({(r['county_fips'],r['PCTCODE']) for r in rr})==n
  for field,total in controls[str(year)]['sums'].items():assert sum(int(r[field]) for r in rr)==total
 aggregate_cells=0
 for y in [2024,2022,2020]:
  nr=readcsv(H/f'native-{y}.csv.gz')
  for level,rows,keys in [('county',readcsv(H/f'county-controls-{y}.csv'),['county_fips']),('municipal',readcsv(H/f'municipal-controls-{y}.csv.gz'),['county_fips','MCDNAME'])]:
   grouped=collections.defaultdict(list)
   for r in nr:grouped[tuple(r[k] for k in keys)].append(r)
   for r in rows:
    leaves=grouped[tuple(r[k] for k in keys)];assert len(leaves)==int(r['native_units'])
    for f in controls[str(y)]['sums']:
     assert sum(int(x[f]) for x in leaves)==int(r[f]);aggregate_cells+=1
 checks['native_to_county_and_municipal_candidate_method_aggregations']=dict(status='pass',cells=aggregate_cells)
 assert context['2020']['columns']['G']=='TABMODEL__G' and context['2020']['columns']['R']=='TABMODEL__R'
 checks['complete_native_FIPS_source_rows_duplicates_controls']='pass'
 anomalies=[]
 for cid,c in CONTESTS.items():
  rr=readcsv(H/f"native-{c['year']}.csv.gz")
  for r in rr:
   if int(r[c['prefix']+'TOTAL'])>int(r['TOTVOTING']):anomalies.append(dict(contest=cid,native_key=r['native_key'],PCTNAME=r['PCTNAME'],COUNTYNAME=r['COUNTYNAME'],contest_votes=int(r[c['prefix']+'TOTAL']),TOTVOTING=int(r['TOTVOTING']),source_row=r['source_row']))
 assert len(anomalies)==2
 checks['preserved_contest_ballot_anomalies']=anomalies
 allbases={}
 for level,path in [('county',H.parent/'county-baselines.csv'),('native',H/'native-baselines.csv.gz'),('municipal',H/'municipal-baselines.csv.gz')]:
  bases=readcsv(path);allbases[level]=bases;assert len({(r['contest'],r['unit_key']) for r in bases})==len(bases)
  for cid,c in CONTESTS.items():
   rows=[r for r in bases if r['contest']==cid];assert len(rows)==(87 if level=='county' else 4103 if level=='native' and c['year']!=2020 else 4110 if level=='native' else controls[str(c['year'])]['municipal_source_groups'])
   near(sum(float(r['pair_weight']) for r in rows),1);near(sum(float(r['all_candidate_weight']) for r in rows),1)
   for r in rows:
    a,b,o,allv,t=map(int,[r['A'],r['B'],r['other'],r['all_candidate_votes'],r['pair_votes']]);assert a+b+o==allv and a+b==t
    if t:near(float(r['A_pair_share']),a/t,1e-14);near(float(r['pair_margin_pp']),100*(a-b)/t,1e-12)
   assert sum(int(r['A']) for r in rows)==next(v[3] for v in c['candidates'] if v[0]==c['A_field'])
 checks['baseline_all_levels_denominators_weights_and_coverage']='pass'
 cv=readcsv(H/'candidate-votes.csv.gz');assert len(cv)==sum((87+controls[str(c['year'])]['native_rows']+controls[str(c['year'])]['municipal_source_groups'])*len(c['candidates']) for c in CONTESTS.values()) and len({(r['contest'],r['level'],r['unit_key'],r['candidate_key']) for r in cv})==len(cv)
 for cid,c in CONTESTS.items():
  for level in allbases:
   for f,_,_,n in c['candidates']:assert sum(int(r['votes']) for r in cv if r['contest']==cid and r['level']==level and r['source_field']==f)==n
 sources={}
 for y in [2024,2022,2020]:
  for level,pp,keyfn in [('native',H/f'native-{y}.csv.gz',lambda r:r['native_key']),('county',H/f'county-controls-{y}.csv',lambda r:r['county_key']),('municipal',H/f'municipal-controls-{y}.csv.gz',lambda r:json.dumps([y,r['county_fips'],r['MCDNAME']],ensure_ascii=False,separators=(',',':')))]:
   for r in readcsv(pp):sources[(y,level,keyfn(r))]=r
 for r in cv:assert int(r['votes'])==int(sources[(CONTESTS[r['contest']]['year'],r['level'],r['unit_key'])][r['source_field']])
 checks['all_candidate_fields_primary_statewide_balances']=dict(status='pass',candidate_rows=len(cv))
 rank=json.loads((H/'priority-contract.json').read_text())
 for k,r in rank.items():
  if not isinstance(r,dict):continue
  yr,level=k.split('-');yr=int(yr);field=('MNGOV' if yr==2022 else 'USSEN')+'TOTAL'
  raw=readcsv(H/f'native-{yr}.csv.gz') if level=='native' else readcsv(H/f'county-controls-{yr}.csv') if level=='county' else readcsv(H/f'municipal-controls-{yr}.csv.gz')
  keyfn=(lambda x:x['native_key']) if level=='native' else (lambda x:x['county_key']) if level=='county' else (lambda x:json.dumps([yr,x['county_fips'],x['MCDNAME']],ensure_ascii=False,separators=(',',':')))
  ordered=sorted(raw,key=lambda x:(-int(x[field]),keyfn(x)));rr=readcsv(H/f'{level}-{yr}-ranked.csv.gz');assert [x['unit_key'] for x in rr]==[keyfn(x) for x in ordered];cum=0
  for x,rawrow in zip(rr,ordered):
   assert int(x['contest_votes'])==int(rawrow[field]);cum+=int(x['contest_votes']);assert int(x['cumulative_votes'])==cum
  near(r['total'],cum,0)
  assert r['previous_votes']*5<r['total']*4<=r['minimum80_votes']*5
 assert rank['2024-county']['minimum80_count']==24 and rank['2024-county']['outside_votes']==621346
 acceptance=json.loads((H.parent/'coordinator-priority-acceptance.json').read_text());assert acceptance['accepted'] and acceptance['ordered_priority_keys']==rank['2024-county']['priority_keys']
 assert sha(H.parent/'turnout/priority-set.json')==acceptance['contract_sha256'] and (H.parent/'turnout/priority-set.json').stat().st_size==acceptance['contract_bytes']
 checks['full_orders_exact_integer80_external_acceptance']='pass';checks['coordinator_acceptance_path']='data/coordinator-priority-acceptance.json'
 peer=json.loads((H/'peer-reconciliation.json').read_text());assert peer['status']=='pass';checks['actual_peer_readonly_audit']='pass'
 scenarios=json.loads((H/'state-scenarios.json').read_text());assert len(scenarios)==64
 max_error=0.;target_rowcounts={}
 for level in allbases:
  targetrows=readcsv(H/(level+'-targets.csv.gz'));target_rowcounts[level]=len(targetrows);groups=collections.defaultdict(list)
  for r in targetrows:groups[(r['scenario'],r['contest'],r['target'])].append(r)
  for key,rr in groups.items():
   ss=next(s for s in scenarios if (s['scenario'],s['contest'],s['target'],s['level'])==key+(level,));expected={r['unit_key'] for r in allbases[level] if r['contest']==key[1]};assert {r['unit_key'] for r in rr}==expected and len(rr)==len(expected)
   near(sum(float(r['pair_weight']) for r in rr),1);near(sum(float(r['all_vote_weight']) for r in rr),1)
   net=sum(float(r['target_net']) for r in rr);err=abs(net-ss['target_net']);max_error=max(max_error,err);near(net,ss['target_net'])
   near(sum(float(r['scenario_pair_votes']) for r in rr),ss['pair_volume']);near(sum(float(r['scenario_all_votes']) for r in rr),ss['all_candidate_volume'])
   for r in rr:
    w=float(r['scenario_pair_votes']);v=float(r['scenario_all_votes']);near(w+float(r['scenario_other_votes']),v)
    if w:
     q=float(r['target_share']);assert 0<=q<=1;near(float(r['target_net']),w*(2*q-1));near(float(r['gain_net']),2*w*(q-float(r['baseline_share'])))
     raw=float(r['selected_required_raw_share']);near(float(r['selected_others_net'])+w*(2*raw-1),ss['target_net']);near(float(r['selected_clipped_share']),max(0,min(1,raw)))
 checks['all_unit_bounded_targets_and_selected_only_solves']=dict(status='pass',rows=target_rowcounts,state_scenarios=64,max_target_net_error=max_error)
 csc=readcsv(H/'state-candidate-scenarios.csv')
 for s in scenarios:
  rr=[r for r in csc if (r['scenario'],r['contest'],r['target'],r['level'])==(s['scenario'],s['contest'],s['target'],s['level'])];near(sum(float(r['scenario_votes']) for r in rr),s['all_candidate_volume'])
 checks['full_candidate_scenario_denominators']='pass'
 inputs=json.loads((H/'live-scenarios-input.json').read_text());outputs=json.loads((H/'live-scenarios-output.json').read_text());assert [live(x) for x in inputs]==outputs
 for o in outputs:
  if o['status'] in ['unknown_remaining_pool','invalid_negative_or_nonfinite_pool']:assert o['final_denominator'] is None;continue
  near(sum(o['final_candidate_totals'].values()),o['final_all_candidate_denominator']);spec=o['input'];a=spec['A'];b=spec['B'];near(o['final_candidate_totals'][a]+o['final_candidate_totals'][b],o['final_pair_denominator'])
  for r in o['units']:
   assert r['counted']==next(x['counted'] for x in spec['units'] if x['key']==r['key']);near(sum(r['forecast_only_remaining'].values()),r['remaining_all'])
  u=o['remaining_pair_pool'];lead=o['counted_totals'][a]-o['counted_totals'][b]
  if u:
   for req in o['targets'].values():near(lead+u*(2*req['raw_share']-1),req['target_net'])
 assert next(x for x in outputs if x['id']=='impossible-even-all-remaining-A')['targets']['tie']['status']=='impossible'
 assert next(x for x in outputs if x['id']=='secured-even-all-remaining-B')['targets']['tie']['status']=='already_secured'
 assert not next(x for x in outputs if x['id']=='strong-named-other-can-win')['A_strictly_exceeds_every_supplied_opponent']
 edge=json.loads((H/'bounded-solver-cases.json').read_text())
 for r in edge:assert bounded(r['input']['shares'],r['input']['weights'],r['input']['target'])==r['output']
 clipped=next(r['output'] for r in edge if r['input']['id']=='clipping-required');assert clipped['status']=='feasible_with_clipping' and clipped['clipped_units']>0;near(clipped['bounded_shift'],-.35);near(clipped['net'],0)
 checks['live_fixed_counted_final_denominators_edge_cases_and_true_clipping']='pass'
 named=readcsv(S/'named-writeins-2020.csv');assert len(named)==522 and sum(int(r['votes']) for r in named)==32;assert json.loads((S/'canvass-2020-check.json').read_text())['county_fields']==957
 checks['named_writeins_overlap_and_957_canvass_controls']='pass'
 ballot=json.loads((S/'current-ballot.json').read_text());assert [r['name'] for r in ballot['candidates']]==['Marisa Simonetti','Rebecca Whiting','Peggy Flanagan','Michele Tafoya'];assert all(r['live_candidate_id'] is None for r in ballot['candidates'])
 for name,ref in ballot['source_ballots'].items():
  receipt=next(r for r in json.loads((S/'acquisition.json').read_text()) if r['id']==name+'-general-ballot-2026');assert receipt['raw_sha256']==ref['raw_sha256'] and receipt['raw_bytes']==ref['raw_bytes'];assert gzip.decompress((H/receipt['stored_path']).read_bytes()).startswith(b'%PDF');assert (S/(name+'-general-ballot-2026-page1.png')).read_bytes().startswith(b'\x89PNG')
 checks['current_general_ballot_visual_scope']='two official November sample styles; liveIDs/writein roster unverified'
 links=0
 for p in [STATE/'county-partisanship.md',S/'SCHEMA.md']:
  for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   if re.match(r'https?://|#',target):continue
   dest=(p.parent/target.split('#')[0]).resolve();assert dest.exists() or dest in [H/'validation.json',H/'asset-manifest.json'],(p,target);links+=1
 checks['relative_markdown_links']=dict(status='pass',checked=links)
 assert not any(p.name in ['__pycache__','node_modules','.venv'] for p in H.rglob('*'))
 gaps=['No2022/2024 independently downloaded county canvassPDF/named-writein annex; official workbooks and state controls retained.','Blank/under/over and candidate-method/native named-writein allocations unavailable.','Historical warning/discrepancy rows retained without adjustment.','Current general printed candidates verified on2officialsamplePDFs; livecandidateIDs/full eligiblewritein roster/currentnativecrosswalk unverified.','SomeHTTP200sourcepages are challenges; intermediate redirect responseheaders unavailable from historical/urllibcaptures.','No2026turnoutprojection/livecollector/knownlivecadence/calibratedprobability/currentgeometryapproval.']
 checks['owned_asset_hashes_sizes_and_no_cache']=dict(status='pass_generated_and_immediately_verified',owned_files=len(files()),max_stored_bytes=max(p.stat().st_size for p in files()),bound_exclusive=40000000,self_hash_scope='manifest excludes its own recursive hash')
 dump(H/'validation.json',dict(schema='mn-validation/1.0',status='pass',checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),checks=checks,material_gaps=gaps))
 n=asset_manifest();print(json.dumps(dict(status='pass',owned_assets=n,target_rows=target_rowcounts,relative_links=links,max_target_net_error=max_error)))
if __name__=='__main__':main()
