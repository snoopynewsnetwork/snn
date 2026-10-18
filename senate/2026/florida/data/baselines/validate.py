#!/usr/bin/env python3
"""Offline validation from retained original evidence and independently checkable arithmetic."""
import csv,gzip,hashlib,io,json,math,re,zipfile
from collections import Counter,defaultdict
from pathlib import Path
from urllib.parse import unquote
from parse_sources import D,FIELDS,sha,writejson
from build import readcsv
from calculate import bounded_shift,selected_threshold,clip
from live_remainder import calculate
S=D.parent.parent

def main():
 checks=[];metrics={}
 def check(name,condition,detail=None):
  if not condition:raise AssertionError((name,detail))
  checks.append({'check':name,'passed':True,**({'detail':detail} if detail is not None else {})})
 # Every fetch/reference resolves to exact retained bytes, including failed HTTP bodies.
 references=json.loads((D/'source/external-source-references.json').read_text());shared=json.loads((D/'source/shared-original-references.json').read_text());source_count=0
 for r in references:
  p=D/r['asset'];b=p.read_bytes();raw=gzip.decompress(b);check('shared_news_hash:'+r['id'],sha(b)==r['stored_sha256'] and sha(raw)==r['raw_sha256'] and len(b)<40000000);source_count+=1
 for r in shared:
  p=S/r['stored_path'];b=p.read_bytes();raw=gzip.decompress(b);check('shared_primary_hash:'+r['id'],sha(b)==r['stored_sha256'] and sha(raw)==r['raw_sha256'] and len(b)==r['stored_bytes']);source_count+=1
 for p in sorted((D/'source').glob('*.receipt.json')):
  r=json.loads(p.read_text());b=(D/r['asset']).read_bytes();raw=gzip.decompress(b);check('own_capture_hash:'+p.name,sha(b)==r['stored_sha256'] and sha(raw)==r['raw_sha256'] and len(b)==r['stored_bytes'] and len(raw)==r['raw_bytes']);source_count+=1
 metrics['verified_capture_references']=source_count
 # ZIP integrity, all208 members and every source row/19field shape, including unrelated offices.
 members=json.loads((D/'source/zip-member-inventory.json').read_text());member_map={(r['source_id'],r['source_member']):r for r in members};sourceids=['dos-2024-precinct-official-storage-alias','dos-2022-precinct-official-storage-alias','dos-2020-precinct-zip'];allrows=0;allmembers=0
 for sid in sourceids:
  ref=next(r for r in references if r['id']==sid);raw=gzip.decompress((D/ref['asset']).read_bytes());z=zipfile.ZipFile(io.BytesIO(raw));check('zip_crc:'+sid,z.testzip() is None)
  for info in z.infolist():
   b=z.read(info);r=member_map.pop((sid,info.filename));check('zip_member:'+info.filename,sha(b)==r['member_sha256'] and len(b)==r['member_bytes'] and f'{info.CRC:08x}'==r['member_crc32']);rows=b.decode(r['encoding']).splitlines();check('all19_fields:'+info.filename,all(len(line.split('\t'))==19 for line in rows) and len(rows)==r['source_rows']);allrows+=len(rows);allmembers+=1
 check('complete_original_inventory',not member_map and allrows==1707538 and allmembers==208);metrics.update(all_original_rows=allrows,original_members=allmembers)
 rawrows=readcsv(D/'native-source-rows.csv.gz');check('raw_position_uniqueness',len(rawrows)==211874 and len({(r['source_id'],r['source_member'],r['source_row_1based']) for r in rawrows})==len(rawrows));check('raw_19column_presence',all(all(k in r for k in FIELDS) for r in rawrows));check('no_recount_selected_contests',all(r['base_selected']=='True' for r in rawrows));metrics['selected_source_rows']=len(rawrows)
 # Full original native sums remain independent of primary valid-vote county counts.
 rawc=Counter()
 for r in rawrows:
  ctx=('2024' if '20241105' in r['source_member'] else '2022' if '20221108' in r['source_member'] else '2020','senate' if r['contest_code']=='120000' else 'president');rawc[(*ctx,r['county_code'],r['candidate_name'],r['candidate_party'],r['candidate_fvrs_id'],r['candidate_doe_id'])]+=int(r['votes'])
 compiled=readcsv(D/'compiled-county-candidates.csv');check('raw_to_compiled_every_candidate',rawc==Counter({(r['year'],r['contest'],r['county_code'],r['candidate_name'],r['party'],r['candidate_fvrs_id'],r['candidate_doe_id']):int(r['votes']) for r in compiled}))
 official=readcsv(D/'official-county-candidates.csv');check('official_complete_candidate_cells',len(official)==2479 and len({(r['year'],r['contest'],r['county'],r['candidate_position']) for r in official})==2479)
 counties=readcsv(D.parent/'county-baselines.csv');check('county_unique_coverage',len(counties)==268 and len({(r['year'],r['contest'],r['county_fips']) for r in counties})==268);states=readcsv(D/'state-baselines.csv')
 for st in states:
  rs=[r for r in counties if r['year']==st['year'] and r['contest']==st['contest']];check('all67:'+st['year']+st['contest'],len(rs)==67 and len({r['county_fips'] for r in rs})==67)
  for k in ['A_votes','B_votes','other_valid_votes','valid_named_writein_votes','all_candidate_votes','pair_votes']:check('state_balance:'+st['year']+st['contest']+k,sum(int(r[k]) for r in rs)==int(st[k]))
  check('weights:'+st['year']+st['contest'],abs(math.fsum(float(r['state_pair_weight']) for r in rs)-1)<1e-12 and abs(math.fsum(float(r['state_all_candidate_weight']) for r in rs)-1)<1e-12)
  check('valid_denominators:'+st['year']+st['contest'],all(int(r['A_votes'])+int(r['B_votes'])==int(r['pair_votes']) and int(r['pair_votes'])+int(r['other_valid_votes'])==int(r['all_candidate_votes']) and abs(float(r['pair_participation_of_valid'])-int(r['pair_votes'])/int(r['all_candidate_votes']))<1e-13 for r in rs))
 # Fifteen independent federal Clerk controls, extracted text provenance checked too.
 expected={('2024','Rick Scott'):5977706,('2024','Debbie Mucarsel-Powell'):4603077,('2024','Ben Everidge'):62683,('2024','Feena Bonoan'):57363,('2024','Tuan TQ Nguyen'):56586,('2024','Howard Knepper'):13,('2022','Marco Rubio'):4474847,('2022','Val Demings'):3201522,('2022','Dennis Misigoy'):32177,('2022','Steven B. Grant'):31816,('2022','Tuan TQ Nguyen'):17385,('2022','Uloma Uma Ekpete'):42,('2022','Edward A. Gray'):190,('2022','Howard Knepper'):2,('2022','Moses Quiles'):33}
 aliases={'Val Demings':'Val Butler Demings','Tuan TQ Nguyen':'Tuan'}
 for (y,name),n in expected.items():
  total=sum(int(r['votes']) for r in official if r['year']==y and r['contest']=='senate' and r['candidate_name']==name);text=(D/'source'/f'clerk-{y}.txt').read_text();lines=[line for line in text.splitlines() if aliases.get(name,name) in line and re.search(r'\b'+re.escape(f'{n:,}')+r'\s*$',line)];check('Clerk_control:'+y+name,total==n and bool(lines))
 check('NARA_2024_controls',sum(int(r['votes']) for r in official if r['year']=='2024' and r['contest']=='president' and r['candidate_name']=='Trump / Vance')==6110125 and sum(int(r['votes']) for r in official if r['year']=='2024' and r['contest']=='president' and r['party']=='WRI')==205)
 discrepancies=readcsv(D/'source-discrepancies.csv');different=[r for r in discrepancies if r['comparison_status']=='named_source_difference'];check('source_conflicts_retained',len(different)==8 and all(r['compiled_minus_official']!='0' for r in different));metrics['named_source_conflicts']=different
 native=readcsv(D/'native-units.csv.gz');check('native_unique',len(native)==23532 and len({r['native_key'] for r in native})==23532);counts=Counter((r['year'],r['contest']) for r in native);check('native_context_coverage',counts=={('2024','senate'):5710,('2024','president'):5712,('2022','senate'):6013,('2020','president'):6097});check('native_methods_not_invented',all(r['method']=='not_provided_in_19field_schema' for r in native));check('native_registration_unique_observation',all(r['registration_context_count']=='1' for r in native));metrics['native_contexts']=dict((y+'_'+c,n) for (y,c),n in counts.items())
 # Exact integer threshold and full order; all nonpriority counties remain accounted for.
 p=json.loads((D/'priority-contract.json').read_text());order=p['all67_order'];check('full_priority_order',len(order)==67 and order==sorted(order,key=lambda r:(-r['all_candidate_votes'],r['county_fips'])));check('integer_minimum80',p['minimum80_count']==22 and p['minimum80_total']==8734473 and p['prior_total']==8572752 and 5*p['prior_total']<4*p['total']<=5*p['minimum80_total'] and p['minimum80_total']+p['remainder_votes']==p['total']);check('top15',p['top15_total']==7373225)
 # Recompute every conditional target/contribution/denominator from its own declared input fields.
 cg=defaultdict(list)
 for r in readcsv(D/'county-scenarios.csv.gz'):cg[r['scenario_id']].append(r)
 ss=readcsv(D/'state-scenarios.csv');check('county_scenario_dimensions',len(ss)==144 and sum(map(len,cg.values()))==9648);maxerr=0
 for r in ss:
  us=cg.pop(r['scenario_id']);P=float(r['pair_volume']);F=float(r['all_candidate_volume']);target=float(r['target_A_minus_B']);delta=float(r['bounded_shift_share_pp'])/100;nets=[]
  check('scenario_67:'+r['scenario_id'],len(us)==67 and len({u['county_fips'] for u in us})==67)
  check('scenario_denominators:'+r['scenario_id'],abs(math.fsum(float(u['pair_volume']) for u in us)-P)<1e-6 and abs(math.fsum(float(u['all_volume']) for u in us)-F)<1e-6 and abs(math.fsum(float(u['pair_weight']) for u in us)-1)<1e-12)
  for u in us:
   t=float(u['pair_volume']);s=float(u['share']);q=clip(s+delta);net=t*(2*q-1);nets.append(net);req=(t+target-(float(r['baseline_A_minus_B'])-t*(2*s-1)))/(2*t)
   assert abs(q-float(u['target_A_pair_share']))<1e-12 and abs(net-float(u['target_net_votes']))<1e-7 and abs(req-float(u['selected_only_unbounded_A_pair_share']))<1e-11 and 0<=float(u['selected_only_clipped_A_pair_share'])<=1
   assert abs(.02*t-float(u['gain_net_votes_per_1pp_A_share']))<1e-9 and abs(float(u['pair_participation'])-t/float(u['all_volume']))<1e-12
  error=abs(math.fsum(nets)-target);maxerr=max(maxerr,error);check('county_target_sum:'+r['scenario_id'],error<1e-6 and r['A_exceeds_aggregate_other_upper_bound']=='True' and r['B_exceeds_aggregate_other_upper_bound']=='True')
 check('no_unmatched_county_scenarios',not cg)
 ng=defaultdict(list)
 for r in readcsv(D/'native-scenarios.csv.gz'):ng[r['scenario_id']].append(r)
 ns=readcsv(D/'native-state-scenarios.csv');check('native_scenario_dimensions',len(ns)==24 and sum(map(len,ng.values()))==141192)
 for st in ns:
  us=ng.pop(st['scenario_id']);P=float(st['pair_volume']);M=float(st['baseline_net']);target=float(st['target_net']);delta=float(st['bounded_shift_share_pp'])/100;nets=[]
  check('native_every_unit:'+st['scenario_id'],len(us)==int(st['native_units']) and len({r['native_key'] for r in us})==len(us))
  for r in us:
   t=float(r['native_pair_volume']);s=float(r['baseline_share']) if r['baseline_share'] else .5;q=clip(s+delta);net=t*(2*q-1);nets.append(net);assert abs(net-float(r['target_net_votes']))<1e-7 and r['all_valid_denominator']==''
   if t>0:
    req=(t+target-(M-t*(2*s-1)))/(2*t);assert abs(req-float(r['selected_only_unbounded_share']))<1e-8 and 0<=float(r['target_share'])<=1
   else:assert r['selected_only_status']=='no_positive_pool' and r['baseline_share']=='' and r['target_share']==''
  error=abs(math.fsum(nets)-target);maxerr=max(maxerr,error);check('native_target_sum:'+st['scenario_id'],error<1e-6 and abs(math.fsum(float(u['native_pair_weight']) for u in us)-1)<1e-12)
 check('no_unmatched_native_scenarios',not ng);metrics['target_rows']=150840;metrics['max_target_sum_error_votes']=maxerr
 # Bounded endpoint, already-winning, negative shift, zero and infeasible pools.
 stress={'clipping':bounded_shift([10,90],[.99,.1],0),'already_winning':bounded_shift([100],[.7],0),'impossible':bounded_shift([100],[.5],101),'no_positive':bounded_shift([0],[.5],0),'selected_secured':selected_threshold(10,20,0),'selected_impossible':selected_threshold(10,-20,0)}
 check('bounded_edge_cases',stress['clipping']['clipped_units']>0 and stress['already_winning']['bounded_shift']<0 and stress['already_winning']['baseline_already_above_target'] and stress['impossible']['status']=='impossible' and stress['no_positive']['status']=='no_positive_pool' and stress['selected_secured']['status'].startswith('already_secured') and stress['selected_impossible']['status'].startswith('impossible'));metrics['bounded_synthetic_cases']=stress
 inputs=json.loads((D/'synthetic-live-inputs.json').read_text());results=json.loads((D/'synthetic-live-results.json').read_text());check('synthetic_live_reproduction',len(inputs)==15 and [calculate(x) for x in inputs]==results)
 for x,r in zip(inputs,results):
  check('counted_immutable:'+x['id'],r['counted_fixed']==x['counted'])
  if r.get('projected_candidates') is not None:
   check('live_final_denominator:'+x['id'],abs(sum(r['projected_candidates'].values())-r['final_denominator'])<1e-9 and r['final_denominator']==sum(x['counted'].values())+sum(p['contest_votes'] for p in x['remaining']))
  if r.get('remaining_pools'):check('live_clipping_bounds:'+x['id'],all(p['A_pair_share_used'] is None or 0<=p['A_pair_share_used']<=1 for p in r['remaining_pools']))
 check('live_other_plurality',next(r for r in results if r['id']=='other_wins')['legal_plurality_outcome']=='Named independent');check('live_unknown_retained',next(r for r in results if r['id']=='unknown_pool')['status']=='unknown_remaining_pool');check('live_no_pool',next(r for r in results if r['id']=='no_pool_lost')['threshold_status']=='no_positive_pool')
 # Peer proof is immutable evidence, external acceptance is PATH ONLY (never reverse-hashed).
 witness=json.loads((D/'peer-agreement.json').read_text());check('peer_proof',witness['status']=='passed_read_only_independent_comparison' and witness['raw19_field_equalities']==4025606 and witness['native_contexts']==23532 and witness['shared_EAVS_field_equalities']==8375 and witness['bookclosing_exact_cells']==2412)
 for pin in witness['pinned_assets']:
  pth=S/pin['path'];check('peer_pin:'+pin['path'],pth.stat().st_size==pin['bytes'] and sha(pth.read_bytes())==pin['sha256'])
 accepted=S/'data/coordinator-priority-acceptance.json';authority=json.loads(accepted.read_text());check('external_historical_acceptance_exists',authority['accepted'] is True and authority['status']=='accepted_historical_dispatch_only' and authority['contract']['sha256']==witness['Gulf_clock_metadata_repair']['new_contract_sha256']);metrics['external_historical_acceptance_path']='data/coordinator-priority-acceptance.json';metrics['authority_note']='Historical dispatch only; coordinator-owned path-only reference, no reverse hash, no current geometry/reporting/candidate admission'
 # Current final-publication mapping, source identity and inspection evidence.
 mapping=json.loads((D/'source/current-ballot-mapping.json').read_text());receipt=json.loads((D/'source/broward-final-candidates.receipt.json').read_text());text=(D/'source/broward-final-candidates.txt').read_text();check('final_current_publication',mapping['raw_sha256']==receipt['raw_sha256'] and 'November 3, 2026 General Election' in text and all(c['name'] in text and c['current_official_result_candidate_id'] is None for c in mapping['candidates']))
 # Deterministic pins freeze all shared research outputs after deterministic gzip repair.
 for n,pin in json.loads((D/'deterministic-data-pins.json').read_text()).items():
  pth=D/n;check('deterministic_pin:'+n,pth.stat().st_size==pin['bytes'] and sha(pth.read_bytes())==pin['sha256'])
 # Relative Markdown links and path bounds, without browsing or outside writes.
 for pth in [S/'county-partisanship.md',D/'source/SCHEMA.md']:
  for target in re.findall(r'(?<!!)\[[^\]]*\]\(([^)]+)\)',pth.read_text()):
   if target.startswith(('http:','https:','#')):continue
   target=unquote(target.split('#')[0]);resolved=(pth.parent/target).resolve();check('relative_link:'+str(pth.relative_to(S))+':'+target,(resolved.exists() or resolved in [(D/'validation.json').resolve(),(D/'asset-manifest.json').resolve()]) and (resolved==S.resolve() or S.resolve() in resolved.parents))
 paths=[p for p in D.rglob('*') if p.is_file()]+[S/'county-partisanship.md',D.parent/'county-baselines.csv'];check('no_cache_dependencies',not any(any(part in ['__pycache__','node_modules','.venv'] for part in p.relative_to(S).parts) for p in paths));check('strict_asset_bounds',all(p.stat().st_size<40000000 for p in paths));metrics['owned_files_including_validation_manifest']=len(paths)+sum(not (D/n).exists() for n in ['validation.json','asset-manifest.json'])
 result={'status':'passed','research_snapshot_utc':'2026-10-18','calibrated_probabilities':False,'live_collector_implemented':False,'current_geometry_approved':False,'current_result_candidate_ids_verified':False,'checks_passed':len(checks),'checks':checks,'metrics':metrics,'material_gaps':['No native valid-writein/candidate-by-method allocation','Eight named source discrepancies retained without repair or explained chronology','No November native geometry/ballot-style crosswalk','Current result-candidate IDs and demonstrated live cadence unavailable','No sourced2026remaining pool or calibrated win probability'],'asset_manifest_path':'asset-manifest.json'}
 writejson(D/'validation.json',result)
 owned=[]
 for pth in sorted([p for p in D.rglob('*') if p.is_file() and p.name!='asset-manifest.json']+[S/'county-partisanship.md',D.parent/'county-baselines.csv']):
  b=pth.read_bytes();entry={'path':str(pth.relative_to(S)),'bytes':len(b),'sha256':sha(b),'kind':'owned_source_capture_or_analysis' if 'source' in pth.relative_to(D).parts else 'owned_derived_or_script'} if D in pth.parents else {'path':str(pth.relative_to(S)),'bytes':len(b),'sha256':sha(b),'kind':'owned_report_or_csv'}
  if pth.suffix=='.gz':raw=gzip.decompress(b);entry.update(uncompressed_bytes=len(raw),uncompressed_sha256=sha(raw),reconstruction='gzip.decompress restores exact stored payload; no truncation or splits')
  owned.append(entry)
 manifest={'scope':'county-partisanship.md,data/county-baselines.csv,data/baselines/** only','self_reference':'manifest lists every owned file except itself; validation included; no reverse coordinator/peer witness hash dependency','strict_stored_byte_limit_exclusive':40000000,'owned':owned,'shared_originals':references+shared,'shared_originals_read_only':True,'external_acceptance_path_only':'data/coordinator-priority-acceptance.json'};writejson(D/'asset-manifest.json',manifest)
 assert (D/'asset-manifest.json').stat().st_size<40000000 and (D/'validation.json').exists()
 print(json.dumps({'status':'passed','checks':len(checks),'metrics':{k:v for k,v in metrics.items() if k not in ['bounded_synthetic_cases','named_source_conflicts']},'largest_owned_asset':max(owned,key=lambda r:r['bytes'])},indent=2))
if __name__=='__main__':main()
