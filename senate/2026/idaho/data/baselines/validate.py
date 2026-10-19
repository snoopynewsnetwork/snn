#!/usr/bin/env python3
"""Offline original/source/control/denominator/calculator/coverage/asset QA."""
import argparse,collections,csv,gzip,io,json,math,re,zipfile
from pathlib import Path
from extract import D,STATE,NEWS,sha,save,workbook,v
from calculate import solve,selected,clip
from live_remainder import evaluate
def load(n):
 p=D/n;b=p.read_bytes();return json.loads(gzip.decompress(b)if n.endswith('.gz')else b)
def readcsv(p):
 b=p.read_bytes();return list(csv.DictReader(io.StringIO((gzip.decompress(b)if p.suffix=='.gz'else b).decode())))
def main():
 arg=argparse.ArgumentParser();arg.add_argument('--verify-assets',action='store_true');args=arg.parse_args();counts=collections.Counter();details={}
 def check(kind,test):counts[kind]+=1;assert test,kind
 if args.verify_assets:
  m=load('asset-manifest.json');actual={str(p.relative_to(STATE))for p in D.rglob('*')if p.is_file()and p.name!='asset-manifest.json'and'__pycache__'not in p.parts}|{'county-partisanship.md','data/county-baselines.csv'};check('manifest_complete_owned_set',actual=={r['path']for r in m['owned']})
  for r in m['owned']:
   p=STATE/r['path'];b=p.read_bytes();check('owned_hash_size_bound',sha(b)==r['sha256']and len(b)==r['bytes']and len(b)<40000000)
   if p.suffix=='.gz':raw=gzip.decompress(b);check('owned_reconstructed_hash',sha(raw)==r['reconstructed_sha256']and len(raw)==r['reconstructed_bytes'])
  for r in m['read_only_references']:
   b=(D/r['path']).read_bytes();check('reference_hash_size',sha(b)==r['stored_sha256']and len(b)==r['stored_bytes'])
   if r.get('raw_sha256'):raw=gzip.decompress(b);check('reference_reconstruction',sha(raw)==r['raw_sha256']and len(raw)==r['raw_bytes'])
  print('sealed asset verification PASS',sum(counts.values()));return
 refs=load('source/reused-originals.json');raw={}
 for a in refs:
  b=(D/a['relative_path']).read_bytes();raw[a['id']]=gzip.decompress(b);check('source_hashes',sha(b)==a['stored_sha256']and sha(raw[a['id']])==a['raw_sha256']and len(raw[a['id']])==a['raw_bytes'])
 for a in load('source/acquisition.json'):
  b=(D/a['stored_path']).read_bytes();rr=gzip.decompress(b);check('HTTP_response_hashes',sha(b)==a['stored_sha256']and sha(rr)==a['raw_sha256']and len(rr)==a['raw_bytes'])
 for r in load('source/archive-members.json'):
  z=zipfile.ZipFile(io.BytesIO(raw[r['source_id']]));b=z.read(r['member']);check('ZIP_member_CRC_hash_size',z.testzip()is None and sha(b)==r['sha256']and len(b)==r['bytes']and f'{z.getinfo(r["member"]).CRC:08x}'==r['crc32'])
 races=workbook(raw['sos-2024-all-races-xlsx']);check('no_2024_federal_senate',not any(v(r,'C')=='Federal'and'Senat'in(v(r,'D')or'')for sh in races.values()for r in sh['rows']))
 units=load('source/native-units.json.gz');controls=load('source/controls.json.gz');positions=load('source/candidate-positions.json.gz');stats=load('source/statistics-positions.json.gz');expected={'2024-president':985,'2020-senate-II':974,'2020-president':974,'2022-senate-III':999,'2022-governor':999};check('all_native_counts',dict(collections.Counter(u['contest']for u in units))==expected);check('native_source_keys_unique',len({u['unit_id']for u in units})==len(units))
 for contest,n in expected.items():
  uu=[u for u in units if u['contest']==contest];cc=[u for u in controls if u['contest']==contest and u['scope']=='county'];check('all44_county_native_and_controls',len({u['county']for u in uu})==len(cc)==44)
  for c in cc:
   # Explicit county-only suffix representation, not a native alias.
   children=[u for u in uu if u['county']==c['county']]
   for candidate in c['candidates']:
    name=candidate['name'];known=sum(q['votes']for u in children for q in u['candidates']if q['name']==name and q['votes']is not None);check('native_known_candidate_sum_to_county',known==candidate['votes'])
  states=[u for u in controls if u['contest']==contest and u['scope']=='state']
  for state in states:
   for cand in state['candidates']:check('county_to_state_candidate',sum(c['votes']for u in cc for c in u['candidates']if c['name']==cand['name'])==cand['votes'])
 check('candidate_source_positions_complete_unique',len(positions)==36565 and len({(r['contest'],r['source_id'],r['archive_member'],r['worksheet'],r['row'],r['column'])for r in positions})==36565)
 nulls={t:sum(c['votes']is None for u in units if u['contest']==t for c in u['candidates'])for t in expected};check('native_nulls_preserved',nulls=={'2024-president':0,'2020-senate-II':8,'2020-president':42,'2022-senate-III':0,'2022-governor':0});details['native_candidate_nulls']=nulls
 for year in [2020,2024]:
  st=[s for s in stats if s['year']==year];n=[s for s in st if s['role']=='native'];foot=[s for s in st if s['role']=='overlapping_county_footer'];check('stats_county_coverage',len(foot)==44)
  for f in foot:
   for field in ['cutoff','day','registered','ballots']:check('stats_native_known_to_footer',sum(s[field]for s in n if s['county']==f['county']and s[field]is not None)==f[field])
  for s in st:
   if None not in [s['cutoff'],s['day'],s['registered']]:check('cutoff_plus_day',s['cutoff']+s['day']==s['registered'])
 st20=[s for s in stats if s['year']==2020 and s['role']=='native'];check('stats2020_nulls',[sum(s[f]is None for s in st20)for f in ['cutoff','day','registered','ballots']]==[32,35,33,9])
 st24=[s for s in stats if s['year']==2024 and s['role']=='native'];check('stats986',len(st24)==986);check('stats2024_controls',[sum(s[f]for s in st24)for f in ['cutoff','day','registered','ballots']]==[1057735,121015,1178750,917469])
 dis=load('source/2024-statistics-disagreements.json');check('Boundary7',len(dis['nonzero'])==7 and{r['county']for r in dis['nonzero']}=={'Boundary County'}and sum(r['ballots_minus_all_category']for r in dis['nonzero'])==3);check('Bingham_stats_only_zero',len(dis['stats_only'])==1 and dis['stats_only'][0]['county']=='Bingham County'and dis['stats_only'][0]['label']=='BONNEVILLE 27'and all(dis['stats_only'][0][f]==0 for f in ['cutoff','day','registered','ballots']))
 pdf=load('source/2024-pdf-reconciliation.json');check('independent_PDF_all985',pdf['matched']==985 and not pdf['unmatched_pdf_rows']and pdf['state_values_match']);national=load('source/national-control-reconciliation.json');check('national_denominator_difference',national['HouseClerk_total']-national['FEC_valid_total']==national['noncandidate_over']+national['noncandidate_under']==12409)
 html=load('source/2022-statistics-tables.json')
 for kind,fields in [('registration',['cutoff','day','registered','ballots']),('method',['ballots','absentee','early'])]:
  rr=[r for r in html if r['kind']==kind and r.get('county')and r['county']!='GRAND TOTAL'];total=next(r for r in html if r['kind']==kind and r.get('county')=='GRAND TOTAL');check('HTML2022_all44',len(rr)==44)
  for f in fields:check('HTML2022_known_numeric_control',sum(r[f]for r in rr if r[f]is not None)==total[f])
 scope=load('source/2022-writein-scope-disagreement.json');check('writein_disagreement_not_repaired',scope['HTML_votes']==46 and scope['general_workbook_votes']==67 and scope['primary_candidates']=={'Ryan Cole':22,'David Reilly':21,'Shelby Rognstad':6712}and'unexplained'in scope['HTML_scope'].lower())
 order=readcsv(D/'native-priority-order.csv');contract=load('priority-contract.json');check('full985_order_keys',len(order)==985 and[r['key']for r in order]==contract['ordered_keys']);cumulative=0
 for i,r in enumerate(order,1):
  previous=cumulative;cumulative+=int(r['candidate_votes']);check('priority_integer_order_fields',int(r['rank'])==i and int(r['cumulative'])==cumulative and(r['priority_minimum80']=='True')==(previous*5<905057*4))
  if i>1:check('canonical_sort',(-int(order[i-2]['candidate_votes']),order[i-2]['key'])<=(-int(r['candidate_votes']),r['key']))
 check('exact80_crossing',cumulative==905057 and int(order[526]['cumulative'])==723753 and int(order[527]['cumulative'])==724515 and len(contract['ordered_priority_keys'])==528 and len(contract['ordered_remainder_keys'])==457)
 for field,keys in [('ordered_child_keys_by_parent',contract['ordered_keys']),('ordered_priority_child_keys_by_parent',contract['ordered_priority_keys']),('ordered_remainder_child_keys_by_parent',contract['ordered_remainder_keys'])]:check('all44_child_arrays',len(contract[field])==44 and sorted(k for vv in contract[field].values()for k in vv)==sorted(keys))
 peer=load('qa/peer-comparison.json');check('reciprocal_QA',not peer['unresolved_differences']and len(peer['reordered_tie_ranks'])==12 and len(peer['lexical_method_differences'])==5 and len(peer['extra_peer_statistics_headings'])==2);details['peer_comparisons']=peer['total_field_comparisons']
 for p in peer['peer_pins']:
  b=(D/p['path']).read_bytes();check('compared_peer_pin_current',sha(b)==p['sha256']and len(b)==p['bytes'])
 county=readcsv(D.parent/'county-baselines.csv');native=readcsv(D/'native-baselines.csv.gz');check('baseline_rows',len(county)==440 and len(native)==9859);check('pair_row_uniqueness',len({(r['pair_id'],r['unit_id'])for r in county+native})==len(county)+len(native))
 for r in county+native:
  if r['pair_votes']:
   T=float(r['pair_votes']);A=float(r['anchor_A_votes']);B=float(r['anchor_B_votes']);check('pair_count_and_share',abs(T-A-B)<1e-9 and(T==0 or abs(float(r['A_share'])-A/T)<1e-12))
  if r['pair_participation']:check('county_native_participation',abs(float(r['pair_participation'])-float(r['pair_votes'])/float(r['all_candidate_votes']))<1e-12)
 scen=readcsv(D/'state-scenarios.csv');target=readcsv(D/'unit-targets.csv.gz');by=collections.defaultdict(list)
 for r in target:by[r['scenario']].append(r)
 check('scenario_counts',len(scen)==160 and len(target)==63518)
 maxres=0
 for s in scen:
  rr=by[s['scenario']];check('complete_scenario_scope',len(rr)==int(s['units'])and(s['scope']!='county'or len(rr)==44));check('scenario_units_unique',len({r['unit_id']for r in rr})==len(rr))
  if s['status']!='feasible':continue
  T=float(s['pair_volume_known_sum']);V=float(s['all_candidate_volume_basis']);check('pair_weights',abs(sum(float(r['pair_weight'])for r in rr)-1)<1e-10);check('all_candidate_weights',abs(sum(float(r['all_candidate_weight'])for r in rr)-1)<1e-10);check('declared_volume',abs(sum(float(r['pair_volume'])for r in rr)-T)<1e-7 and abs(sum(float(r['valid_volume'])for r in rr)-V)<1e-7)
  achieved=sum(float(r['target_net'])for r in rr if r['target_net']);target_expected=float(s['target_pair_margin_pp'])/100*T;maxres=max(maxres,abs(achieved-target_expected));check('tie_cushion_reconciles',abs(achieved-target_expected)<1e-6)
  for r in rr:
   t=float(r['pair_volume']);check('gain_scale',abs(float(r['net_gain_per_1pp_share'])-.02*t)<1e-9)
   if r['bounded_target_share']:
    q=float(r['bounded_target_share']);check('shares_bounded',0<=q<=1);check('unit_target_contribution',abs(float(r['target_net'])-t*(2*q-1))<1e-8)
   if r['bounded_gain_for_1pp_share']:
    base=float(r['baseline_A_share']);check('bounded_local_gain',abs(float(r['bounded_gain_for_1pp_share'])-2*t*(clip(base+.01)-base))<1e-9)
   if r['selected_only_required_share']:
    q=float(r['selected_only_required_share']);other=float(r['fixed_other_net']);check('selected_unit_conditional_equation',abs(other+t*(2*q-1)-target_expected)<1e-6)
  if s['legal_A_status']!='unknown_full_field':check('full_field_denominator',abs(float(s['target_A_votes'])+float(s['target_B_votes'])+sum(json.loads(s['other_candidate_totals_json']).values())-V)<1e-7)
 details['maximum_state_target_residual_votes']=maxres
 check('historical_other_candidate_can_beat_pair_target',all(s['legal_A_status']=='not_plurality'for s in scen if s['pair_id']=='2020-Fleming-Risch'and s['volume_setting']=='anchor_observed_county_repeat'and s['scope']=='county'))
 # Independent arithmetic witnesses, including empty and bounded/unknown cases.
 tests={};simple=[dict(pair_votes=100,share=.3)];a=solve(simple,0);b=solve(simple,.01);check('factor_of_two',abs(a['shift']-.2)<1e-12 and abs(b['shift']-.205)<1e-12);tests['fixed_pair_factor_two']=[a,b]
 clipped=solve([dict(pair_votes=1,share=.99),dict(pair_votes=9,share=0)],0);check('bounded_root',clipped['clipped_units']==1 and abs(clipped['achieved_net'])<1e-10 and clipped['shift']!=clipped['unbounded_shift']);tests['clipping']=clipped
 winning=solve([dict(pair_votes=100,share=.7)],0);check('negative_already_winning',winning['shift']<0 and winning['baseline_already_wins']and winning['minimum_nonnegative_improvement']==0);tests['already_winning']=winning
 check('no_positive_pool',solve([dict(pair_votes=0,share=None)],0)['status']=='no_positive_pool');check('unknown_pool',solve([dict(pair_votes=None,share=.4)],0)['status']=='unknown_preference_or_pair_pool');check('impossible_bounded',solve(simple,1.1)['status']=='impossible_bounded_target');check('selected_no_pool',selected([dict(pair_votes=0,share=None)],0)['status']=='no_positive_pool')
 cases=load('live-synthetic-inputs.json');saved=load('live-synthetic-results.json');actual=[evaluate(c)for c in cases];check('live_replay',actual==saved and len(saved)==14)
 for c,r in zip(cases,actual):
  check('counted_immutable',r['counted_fixed']==c['counted'])
  if r.get('projected_final')is None:continue
  check('live_final_denominator',abs(sum(r['projected_final'].values())-r['final_all_candidate_denominator'])<1e-8)
  for n,vv in c['counted'].items():check('counted_not_reforecast',r['projected_final'][n]>=vv)
 pair=next(r for r in saved if r['id']=='pair-plus1');allc=next(r for r in saved if r['id']=='all-candidate-plus1');check('final_pair_vs_all_denom',pair['break_even']['target_net']==.01*pair['final_pair_denominator']and allc['break_even']['target_net']==.01*allc['final_all_candidate_denominator']and pair['break_even']['required_A_share_unbounded']!=allc['break_even']['required_A_share_unbounded']);check('full_field_opponent_test',next(r for r in saved if r['id']=='other-candidate-wins')['break_even']['legal_status']=='impossible_under_fixed_assumptions')
 details['arithmetic_witnesses']=tests
 check('live_already_winning_negative_required_change',next(r for r in saved if r['id']=='already-winning-negative-tie-shift')['break_even']['required_change_from_stated_remaining_A_share_pp']<0)
 # Local links and owned-byte audit. Links into read-only evidence must also resolve.
 for p in [STATE/'county-partisanship.md',D/'source/SCHEMA.md']:
  for targetlink in re.findall(r'\[[^\]]+\]\(([^)]+)\)',p.read_text()):
   if not targetlink.startswith(('https://','http://','#')):check('relative_links_exist',(p.parent/targetlink.split('#')[0]).exists()or targetlink.endswith(('validation.json','asset-manifest.json')))
 for p in D.rglob('*'):
  if p.is_file():check('asset_byte_bound',p.stat().st_size<40000000)
 check('no_dependency_or_cache_directories',not any(p.name in ['node_modules','__pycache__','.pytest_cache']for p in D.rglob('*')))
 check('coverage_metadata_type_and_sum',isinstance(expected,dict)and sum(expected.values())==4931)
 details['source_scope_note']='source/2022-writein-scope-disagreement.json; HTML46 is not attributed to primary; actual primary PDF22/21/6712 remains separate'
 save('validation.json',dict(status='PASS',checks=dict(counts),total_checks=sum(counts.values()),details=details,coverage=expected,county_parents=44,canonical985=True,priority528=True,all_remainder457_included=True,gaps=['Boundary seven context source scopes/net3 unexplained','2020 native candidate/statistic nulls retained','2022 LisaMarieHTML46 versus general67 unexplained','statewide/later eligible writeins and result IDs not certified by bounded sample','no current geometry join, measured remaining pool, November cadence or calibration','turnout unsupported stage attribution queued for separate coordinator correction'],coordinator_acceptance=False))
 print('validation PASS',sum(counts.values()),'max target residual',maxres)
if __name__=='__main__':main()
