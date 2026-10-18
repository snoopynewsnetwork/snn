#!/usr/bin/env python3
"""Offline independent conservation, source, bounds, calculator and complete-asset audit."""
import collections,csv,gzip,hashlib,json,math,pathlib,re
from calculate import R,csvread
S=R.parents[1];checks=[]
def ck(name,ok,detail=None):
 checks.append({'name':name,'pass':bool(ok),'detail':detail})
def close(x,y,tol=1e-6):return abs(float(x)-float(y))<=tol
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text())
B=csvread(R.parent/'county-baselines.csv');N=csvread(R/'native-baselines.csv.gz');L=csvread(R/'candidate-methods.csv.gz');SC=csvread(R/'state-scenarios.csv');CT=csvread(R/'county-targets.csv.gz');NT=csvread(R/'native-targets.csv.gz');MB=csvread(R/'method-baselines.csv.gz');MT=csvread(R/'method-targets.csv.gz');EC=load(R/'extraction-checks.json');PEER=load(R/'peer-reconciliation.json')
by={e:[x for x in B if x['election_key']==e] for e in {x['election_key'] for x in B}};expected={'2020NovGen':(2374519,2462617,115039),'2021JanFedRun':(2269923,2214979,0),'2022NovGen':(1946117,1908442,81365),'2022DecGenRun':(1820633,1721244,0),'2024NovGen':(2548017,2663117,38913)}
ck('five_elections_795_rows',len(by)==5 and len(B)==795)
keys={x['county_fips'] for x in B};ck('all159unique_counties_every_election',len(keys)==159 and all(len(v)==159 and len({x['county_fips'] for x in v})==159 for v in by.values()))
for e,vals in by.items():
 got=tuple(sum(int(x[k]) for x in vals) for k in ['A','B','other_named_valid_votes']);ck('primary_state_pair_other_'+e,got==expected[e],{'observed':got,'expected':expected[e]})
 ck('denominators_'+e,all(int(x['A'])+int(x['B'])==int(x['pair_votes']) and int(x['pair_votes'])+int(x['other_named_valid_votes'])==int(x['named_valid_option_votes']) and int(x['named_valid_option_votes'])+int(x['void_option_votes'])==int(x['source_alloption_votes']) for x in vals))
ck('every_raw_option_and_method_position',len(L)==76400 and len({(x['source_id'],x['unit_level'],x['native_GUID'],x['source_pointer']) for x in L})==76400)
ck('native_identity_coverage2701',len(N)==2701 and len({(x['county_fips'],x['native_GUID']) for x in N})==2701)
native_totals=[x for x in L if x['unit_level']=='native_precinct' and x['group_ordinal']=='-1'];native_methods=[x for x in L if x['unit_level']=='native_precinct' and x['group_ordinal']!='-1']
ck('native_nulls_preserved',sum(x['votes']=='' for x in native_totals)==40 and sum(x['votes']=='' for x in native_methods)==22416)
ck('native_candidate_and_method_row_counts',len(native_totals)==10812 and len(native_methods)==43248)
ck('native_ballots_registration',sum(float(x['ballots_cast']) for x in N)==5297264 and sum(float(x['registered_voters']) for x in N)==7219868)
ck('older_ballot_registration_unknown',all(x['ballots_cast']=='' and x['registered_voters']=='' for x in B if x['election_key']!='2024NovGen'))
ck('comparably_observed_extraction_balances',not EC['nonzero_differences'] and EC['checks']==33414 and EC['unverifiable_redacted_checks']==7706,{'unverifiable_redacted_checks':EC['unverifiable_redacted_checks']})
ck('all14statecandidate_controls',len(EC['state_candidate_controls'])==14 and all(x['difference']==0 for x in EC['state_candidate_controls']))
ck('18_raw_state_local_identity_differences_retained',len(load(R/'source/party-disagreements.json'))==18)
ck('independent_peer_all_fields_orders_and_residuals',not PEER['disagreements'] and PEER['check_count']>=1451108,{'checks':PEER['check_count'],'status':PEER['status']})
for f,pin in PEER['peer_artifact_pins'].items():
 b=(S/'data/turnout'/f).read_bytes();ck('immutable_peer_pin_'+f,sha(b)==pin['sha256'] and len(b)==pin['bytes'])
# Each complete state calculation includes all159 counties; no priority filter is used.
ck('scenario_matrix',len(SC)==50 and len(CT)==7950)
bad_finite=[]
for name,rows in [('county_baseline',B),('native_baseline',N),('state_scenarios',SC),('county_targets',CT),('native_targets',NT),('method_baselines',MB),('method_targets',MT)]:
 for i,r in enumerate(rows):
  for k,v in r.items():
   if v=='':continue
   try:
    if not math.isfinite(float(v)):bad_finite.append([name,i,k,v])
   except ValueError:pass
ck('all_numeric_outputs_finite',not bad_finite,bad_finite)
for state in SC:
 vals=[x for x in CT if x['scenario']==state['scenario']];P=float(state['pair_votes']);g=float(state['target_pair_margin_pp'])/100;net=sum(float(x['target_net']) for x in vals);weights=sum(float(x['pair_weight']) for x in vals);F=P+float(state['named_other_fixed'])+float(state['separate_state_qualified_writeins']);cushion=(g*P-(F-P))/2
 good=len(vals)==159 and {x['county_fips'] for x in vals}==keys and close(sum(float(x['expected_pair_votes']) for x in vals),P) and close(weights,1,1e-12) and close(net,g*P) and close(state['final_allcandidate_denominator'],F) and close(state['majority_cushion_votes'],cushion) and (state['A_strict_majority']=='True')==(cushion>0)
 for x in vals:
  T=float(x['expected_pair_votes']);q=float(x['target_A_pair_share']);baseline=float(x['baseline_A_pair_share']);raw=float(x['selected_raw_required_share']);outside=float(x['outside_fixed_net']);good=good and 0<=q<=1 and close(T*(2*q-1),x['target_net']) and close(T*(2*raw-1)+outside,g*P) and close(x['county_pair_participation_in_named_mix'],T/(T+float(x['named_other_fixed'])),1e-12) and close(x['gain_for_plus1_share_pp_net'],2*T*(min(1,baseline+.01)-baseline))
 ck('whole_state_scenario_'+state['scenario'],good)
# Native and method conditional ledgers include withheld volume explicitly.
NS=load(R/'native-state-scenarios.json');ck('native_targets_all2701_twice',len(NT)==5402)
for state in NS:
 g=state['target_pair_margin_pp'];vals=[x for x in NT if int(x['target_pair_margin_pp'])==g];known=[x for x in vals if x['target_net']!=''];net=sum(float(x['target_net']) for x in known)+state['unallocated_withheld_net_held_fixed'];weight=sum(float(x['pair_weight_in_complete_county_state']) for x in vals if x['pair_weight_in_complete_county_state']!='')+state['unallocated_withheld_pair_votes_held_fixed']/state['complete_county_state_pair_votes']
 ck('bounded_native_state_'+str(g),len(vals)==2701 and close(net,state['allstate_target_net']) and close(weight,1,1e-12) and all(0<=float(x['target_share'])<=1 for x in known) and state['clipped_unit_count']==(3 if g==0 else 4))
ck('all_county_native_method_units',len(MB)==13984 and len(MT)==27968 and collections.Counter(x['unit_level'] for x in MB)=={'county':3180,'native_precinct':10804})
for state in load(R/'method-state-scenarios.json'):
 vals=[x for x in MT if x['election_key']==state['election_key'] and x['unit_level']==state['unit_level'] and int(x['target_pair_margin_pp'])==state['target_pair_margin_pp']];net=sum(float(x['target_net']) for x in vals if x['target_net']!='')+state['unallocated_redacted_net_held_fixed'];ck('bounded_method_state_'+state['election_key']+'_'+state['unit_level']+'_'+str(state['target_pair_margin_pp']),close(net,state['allstate_target_net']) and all(0<=float(x['target_A_pair_share'])<=1 for x in vals if x['target_A_pair_share']!=''))
rank=load(R/'rankings.json')
for e,r in rank.items():
 vals=sorted(by[e],key=lambda x:(-int(x['named_valid_option_votes']),x['county_fips']));v=[int(x['named_valid_option_votes']) for x in vals];total=sum(v);k=r['minimum_count'];ck('complete_order_and_integer80_'+e,[x['county_fips'] for x in vals]==[x['county_fips'] for x in r['rows']] and r['denominator']==total and r['integer_80_threshold']==(4*total+4)//5 and 5*sum(v[:k-1])<4*total<=5*sum(v[:k]) and sum(v[:15])==r['top15'])
FEC=load(R/'source/fec-controls.json');bound=load(R/'source/priority-bounds.json');full=FEC['Georgia_total'];extra=full-rank['2024NovGen']['denominator'];rr=rank['2024NovGen'];inside=rr['rows'][:44];outside=rr['rows'][44:]
ck('FEC_complete_state_and_858_scope',full==5250905 and extra==858 and sum(x['votes'] for x in FEC['Georgia_controls'])==full)
ck('independent_minimum44_fullscope',5*(rr['first_k_minus_1']+extra)<4*full<=5*rr['first_k'])
ck('independent44membership_ballotbound',bound['Liberty_raw_app_ballots_match'] and bound['Liberty_ballots']==23258 and 23258<min(x['votes'] for x in inside) and max(x['votes'] for x in outside if x['county_fips']!='13179')+extra<min(x['votes'] for x in inside))
ck('independent_top15membership_and_sharebounds',rr['rows'][14]['votes']-rr['rows'][15]['votes']>extra and close(100*rr['top15']/full,55.98644424,1e-8) and close(100*(rr['top15']+extra)/full,56.00278428,1e-8) and close(100*rr['first_k']/full,80.41608066,1e-8) and close(100*(rr['first_k']+extra)/full,80.43242070,1e-8))
live={x['name']:x for x in load(R/'live-results.json')};a=live['known_denominators'];ck('live_handchecked_final_denominators',a['final_A']==70 and a['final_B']==60 and a['final_other']==15 and a['FINAL_pair_denominator']==130 and a['FINAL_allcandidate_denominator']==145 and a['required_remaining_A_pair_share_unbounded']==.25 and a['majority_remaining_A_share_boundary_strictly_exceed']==.625)
ck('live_Aplus1_uses_FINAL_pair',close(live['Aplus1_final_pair_denominator']['required_remaining_A_pair_share_unbounded'],.2825,1e-12))
statuses={'unknown':'unknown_remaining_assumptions','no_pool_tie':'no_positive_pair_pool','negative_pool':'invalid_negative_remaining','impossible':'impossible','secured':'already_secured','other_only_remaining':'no_positive_pair_pool','negative_counted':'invalid_negative_counted','duplicate_unit_rejected':'invalid_duplicate_unit'}
ck('live_unknown_no_pool_negative_impossible_secured',all(live[k]['status']==v for k,v in statuses.items()) and len(live)==13)
ck('live_clipping_preserves_counted',live['clip_high']['units'][0]['clipped_A_pair_share']==1 and live['clip_low']['units'][0]['clipped_A_pair_share']==0 and live['clip_high']['counted_A']==10 and live['clip_low']['counted_B']==20)
for x in live.values():
 if 'final_A' in x:ck('live_conservation_'+x['name'],close(x['final_A']+x['final_B']+x['final_other'],x['FINAL_allcandidate_denominator']) and close(x['final_A']+x['final_B'],x['FINAL_pair_denominator']))
edges={x['case']:x['result'] for x in load(R/'calculator-edge-tests.json')};ck('bounded_solver_clipping_already_winning_impossible_no_pool',edges['clipping_changes_solve']['status']=='feasible_clipped' and close(edges['clipping_changes_solve']['actual_net'],90) and edges['already_winning']['unbounded_shift_pp']<0 and edges['already_winning']['minimum_positive_improvement_pp']==0 and edges['impossible_margin']['status']=='impossible' and edges['no_positive_pool']['status']=='no_positive_pool' and edges['negative_volume']['status']=='invalid_negative_volume')
mapping=load(R/'source/current-ballot-mapping.json');ck('final_current_publication_mapping_not_oldIDs',[x['name'] for x in mapping['printed_candidates']]==['Mike Collins','Jon Ossoff'] and [x['name'] for x in mapping['qualified_writeins']]==['Elbert Arthur Bartell','Christina Clement','Cassandra Easton'] and mapping['current_result_election_id'] is None and mapping['runoff_configuration'] is None)
# Audit every shared original and owned request, including unsuccessful responses.
for name in ['shared-inputs.json','evidence-inputs.json']:
 for ref in load(R/'source'/name):
  p=S/ref['path'];z=p.read_bytes();b=z if ref.get('compression')=='none' else gzip.decompress(z);m=ref.get('acquisition') or ref;ck('source_pin_'+name+'_'+ref['path'],len(z)<40000000 and sha(z)==ref['stored_sha256'] and sha(b)==ref['raw_sha256'] and len(z)==ref.get('stored_bytes',len(z)),{'raw_bytes':len(b),'stored_bytes':len(z)})
for ref in load(R/'source/acquisitions.json'):
 if 'path' not in ref:continue
 z=(R/ref['path']).read_bytes();b=gzip.decompress(z);ck('owned_source_pin_'+ref['id']+'_'+ref['raw_sha256'][:8],sha(z)==ref['stored_sha256'] and sha(b)==ref['raw_sha256'] and len(z)==ref['stored_bytes'] and len(b)==ref['raw_bytes'])
owned=[S/'county-partisanship.md',R.parent/'county-baselines.csv']+sorted(p for p in R.rglob('*') if p.is_file() and p.name not in ['asset-manifest.json','validation.json'])
ck('all_owned_assets_strictly_under40MB',all(p.stat().st_size<40000000 for p in owned),{'largest_bytes':max(p.stat().st_size for p in owned),'files_before_generated_audit':len(owned)})
ck('no_dependency_or_cache_directories',not any(p.is_dir() and p.name in ['node_modules','__pycache__','.cache','.venv'] for p in R.rglob('*')))
missing=[]
for p in [S/'county-partisanship.md',R/'source/SCHEMA.md']:
 for dest in re.findall(r'\[[^\]]*\]\(([^\s)]+)\)',p.read_text()):
  if '://' in dest or dest.startswith('#'):continue
  q=(p.parent/dest.split('#')[0]).resolve()
  if not q.exists() and q not in [R/'validation.json',R/'asset-manifest.json']:missing.append({'document':str(p),'target':dest})
ck('all_relative_markdown_links',not missing,missing)
result={'status':'PASS_WITH_DOCUMENTED_COVERAGE_GAPS' if all(x['pass'] for x in checks) else 'FAIL','checks_run':len(checks),'failed_checks':[x for x in checks if not x['pass']],'coverage':{'counties_per_election':159,'elections':5,'county_rows':795,'candidate_total_method_rows':76400,'native_identities_2024':2701,'native_candidate_nulls':40,'native_method_nulls':22416,'county_target_rows':7950,'native_target_rows':5402,'county_native_method_baseline_rows':13984,'method_target_rows':27968,'peer_field_control_checks':PEER['check_count']},'material_gaps':['Full county/native qualified write-in allocations and exact full-candidate order/shares remain unknown; membership proof is separate.','Original SOS2024 write-in PDF403; original FEC corroboration acquired.','Older four county apps expose no finer native units and no usable ballot/registration controls.','Native candidate/method redactions; unallocated observed aggregates held fixed in conditional scenarios.','Current resultIDs/runoff configuration, approved boundaries/crosswalks, live cadence/remaining pool and calibrated probabilities unverified.'],'checks':checks,'asset_manifest_contract':'Generated after this report; inventories every owned file including validation.json, excludes only itself to avoid self-hash. Final tool verifies every manifest entry and exact path set.'}
(R/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
owned=owned+[R/'validation.json'];records=[{'path':str(p.relative_to(S)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in sorted(owned)];manifest={'schema_version':1,'scope':'owned county-partisanship.md,data/county-baselines.csv,data/baselines/**','self_exclusion':'asset-manifest.json only; impossible recursive self-hash','assets':records,'shared_original_references':'source/shared-inputs.json;source/evidence-inputs.json; original HTTP metadata pinned there'};(R/'asset-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
assert (R/'asset-manifest.json').stat().st_size<40000000
actual={str(p.relative_to(S)) for p in [S/'county-partisanship.md',R.parent/'county-baselines.csv']+list(p for p in R.rglob('*') if p.is_file() and p.name!='asset-manifest.json')};assert actual=={x['path'] for x in records}
for x in records:
 b=(S/x['path']).read_bytes();assert len(b)==x['bytes']<40000000 and sha(b)==x['sha256']
print(json.dumps({'status':result['status'],'checks':len(checks),'failures':result['failed_checks'],'manifest_assets':len(records),'manifest_exact_path_set':True},indent=2));assert not result['failed_checks']
