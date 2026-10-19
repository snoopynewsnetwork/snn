#!/usr/bin/env python3
"""Offline Colorado identity, arithmetic, source and asset audit; emits material gaps."""
from pathlib import Path
from collections import defaultdict,Counter
import json,csv,gzip,io,hashlib,re,math,sys
sys.dont_write_bytecode=True
from calculate import live,solve_shift
D=Path(__file__).resolve().parent;S=D.parent.parent
checks=Counter()
def check(ok,kind):
 assert ok,kind;checks[kind]+=1
def sha(b):return hashlib.sha256(b).hexdigest()
def readcsv(p):
 b=p.read_bytes();b=gzip.decompress(b)if p.suffix=='.gz'else b;return list(csv.DictReader(io.StringIO(b.decode())))
def jl(p):return [json.loads(x)for x in gzip.decompress(p.read_bytes()).splitlines()]
def close(a,b,tol=1e-6):return abs(float(a)-float(b))<=tol
def main():
 # Every retained original source entity and discovery/control chain is hash checked, including unsuccessful responses.
 refs=[]
 for name in ['reused-originals.json','discovery-evidence.json']:
  for a in json.loads((D/'source'/name).read_text()):
   p=D/a['path'];b=p.read_bytes();raw=gzip.decompress(b);check(sha(b)==a['stored_sha256'],'stored_source_hash');check(sha(raw)==a['raw_sha256'],'raw_source_hash');check(len(raw)==a.get('bytes',a.get('raw_bytes')),'raw_source_size');check(len(b)<40000000,'source_bound');refs.append(dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b),raw_bytes=len(raw),raw_sha256=sha(raw)))
 for a in json.loads((D/'source/acquisition.json').read_text()):
  if 'path'not in a:continue
  b=(D/a['path']).read_bytes();raw=gzip.decompress(b);check(sha(b)==a['stored_sha256']and len(b)==a['stored_bytes'],'acquired_stored');check(sha(raw)==a['sha256']and len(raw)==a['bytes'],'acquired_raw')
 rows=jl(D/'extracts/original-csv-records.jsonl.gz');check(len(rows)==9831,'original_record_count');native=readcsv(D/'native-baselines.csv.gz');county=readcsv(D.parent/'county-baselines.csv');check(len(native)==9636 and len(county)==192,'complete_rows')
 original={}
 for r in rows:
  key=(r['year'],r['record_ordinal']);check(key not in original,'source_row_identity');original[key]=r;v=list(map(int,r['raw_fields'][2:]));check(all(n>=0 for n in v),'source_nonnegative');check(sum(v[:-2])==v[-2]==v[-1],'source_totals')
 for year,n in [(2024,3199),(2022,3232),(2020,3205)]:
  rs=[r for r in native if int(r['year'])==year];cs=[r for r in county if int(r['year'])==year];check(len(rs)==n and len({r['county_literal']for r in rs})==64 and len(cs)==64,'native_county_coverage');check(len({r['key']for r in rs})==n,'native_unique')
  for r in rs:
   o=original[(year,int(r['source_record']))];check(r['key']==o['key']and r['county_literal']==o['county_literal']and r['native_id_literal']==o['native_id_literal'],'canonical_identity');check(int(r['A'])+int(r['B'])+int(r['other'])==int(r['candidate_votes']),'native_candidate_denominator');check(r['method']==r['administrative_ballots']==r['registered_voters']==r['undervotes']==r['overvotes']==r['blank_votes']=='','unknown_native_fields')
  for r in cs:
   check(len(r['county_fips'])==5 and r['county_fips'].startswith('08'),'county_fips');v=json.loads(r['candidate_vector_json']);check(sum(v.values())==int(r['candidate_votes']),'county_full_candidates');check(int(r['A'])+int(r['B'])==int(r['pair_votes']),'county_pair');check(close(r['pair_participation'],int(r['pair_votes'])/int(r['candidate_votes'])),'county_participation');check(int(r['administrative_ballots'])==int(r['turnout_table_ballots'])and int(r['registered_voters'])==int(r['turnout_registered_voters']),'county_admin_controls')
 # Full all-column reconstruction independent of saved preflight booleans.
 for year in [2024,2022,2020]:
  rr=[r for r in rows if r['year']==year];sr=next(r for r in rr if r['level_literal']=='State');cs=[r for r in rr if r['level_literal']=='County'];ns=[r for r in rr if r['level_literal']=='Precinct']
  for col in range(2,len(sr['raw_fields'])):
   check(sum(int(r['raw_fields'][col])for r in cs)==int(sr['raw_fields'][col]),'county_to_state_candidate_and_pseudo')
   for c in cs:check(sum(int(r['raw_fields'][col])for r in ns if r['county_literal']==c['county_literal'])==int(c['raw_fields'][col]),'native_to_county_candidate_and_pseudo')
 long=readcsv(D/'extracts/all-candidate-votes.csv.gz');check(len(long)==101529 and sum(r['level']=='Precinct'for r in long)==99514,'candidate_position_count');keys=set()
 for r in long:
  k=(r['year'],r['source_record'],r['source_column']);check(k not in keys,'candidate_position_unique');keys.add(k);o=original[(int(r['year']),int(r['source_record']))];c=int(r['source_column'])-1;check(int(r['votes'])==int(o['raw_fields'][c])and r['candidate_literal']==o['header_fields'][c]and r['party_literal']==o['party_fields'][c],'candidate_source_position')
 pages=json.loads((D/'source/historical-page-props.json').read_text());check(sum(len(x['contest']['candidates'])for x in pages.values())==37,'full_source_candidate_pseudo_objects')
 for p in pages.values():check(p['hasBallots']is False and p['contest']['hasVoteChannels']is False,'source_absence_flags')
 stats=jl(D/'extracts/turnout-original-cells.jsonl.gz');check(len(stats)==3183,'stats_coverage');check(sum(len(r['raw_cells'])for r in stats)==22281,'all_original_stats_cells');ann=[]
 for r in stats:
  for c in 'CDEF':
   raw=r['raw_cells'].get(c,{});t=raw.get('text')
   if t and t.endswith('*'):ann.append((r['source_row'],c,t));check(raw['attributes']['t']=='s'and raw['raw_v'].isdigit(),'annotated_shared_string_type')
 check([x[2]for x in ann]==['101*','9*','110*','194*','2868*','349*','3217*','1700*'],'exact_annotated_literals');check(sum(r['annotated_inclusive']['F']for r in stats)==3241155,'annotated_ballot_control');check(sum(r['plain_numeric']['F']or 0 for r in stats)==3239261,'numeric_ballot_lane');check(sum(r['annotated_inclusive']['D']is None for r in stats)==18,'missing_inactive_not_zero')
 lanes=json.loads((D/'extracts/turnout-lanes.json').read_text());check(sum(lanes['tail_counts'].values())==1043548,'cached_error_tail');check(any(r['source_row']==3185 for r in lanes['explanatory']),'footnote_retained')
 orders=json.loads((D/'historical-orders.json').read_text());hierarchy=json.loads((D/'native-hierarchy.json').read_text())
 for year,order in orders.items():
  check(order==sorted(order,key=lambda r:(-r['candidate_votes'],r['key'])),'full_descending_order');check(set(r['key']for r in order)=={k for keys in hierarchy[year].values()for k in keys},'full_native_map');check(len(hierarchy[year])==64,'all_parents');cum=0;cross=None
  for r in order:
   cum+=r['candidate_votes'];check(cum==r['cumulative_votes'],'rank_cumulative')
  total=cum
  for i,r in enumerate(order):
   if 5*r['cumulative_votes']>=4*total:cross=i;break
  check(cross is not None and (cross==0 or 5*order[cross-1]['cumulative_votes']<4*total),'exact_minimum80')
 contract=json.loads((D/'priority-contract.json').read_text());check(contract['denominator']==3192745 and contract['top15']==39005,'priority_denominator');check(contract['crossing']==dict(rank=1992,key='CO|2024|26499|Summit|2081359007',votes=870,cumulative=2554233,previous=2553363),'exact_priority_crossing');check(contract['ordered_keys']==[r['key']for r in orders['2024']],'contract_full_order');check(len(contract['priority_keys'])==1992 and contract['nonpriority_count']==1207 and contract['nonpriority_votes']==638512,'priority_remainder')
 # Every scenario retains its complete geography and exact settings, row contribution and fixed-others solve.
 settings={r['scenario']:r for r in json.loads((D/'scenario-settings.json').read_text())};st=readcsv(D/'state-scenarios.csv');ct=readcsv(D/'county-targets.csv');nt=readcsv(D/'native-targets.csv.gz');check(len(st)==36 and len(ct)==1152 and len(nt)==57816,'scenario_coverage');groups=defaultdict(list)
 for r in ct+nt:groups[(r['scenario'],r['target_pair_margin_pp'])].append(r)
 for r in st:
  s=settings[r['scenario']];rs=groups[(r['scenario'],r['target_pair_margin_pp'])];T=float(r['pair_total']);N=float(r['all_candidate_total']);target=float(r['target_net']);check(len(rs)==s['units']and len({x['key']for x in rs})==s['units'],'scenario_all_units');check(close(sum(float(x['scenario_pair_votes'])for x in rs),T)and close(T,s['pair_total']),'scenario_declared_volume');check(close(sum(float(x['scenario_all_candidate_votes'])for x in rs),N)and close(N,s['all_candidate_total']),'scenario_allcandidate_volume');check(close(sum(float(x['pair_weight'])for x in rs),1,1e-10)and close(sum(float(x['candidate_weight'])for x in rs),1,1e-10),'weights_sum_one');check(close(sum(float(x['target_net'])for x in rs),target)and close(r['achieved_net'],target),'bounded_target_sum');check(close(sum(float(x['baseline_net'])for x in rs),r['baseline_net']),'baseline_contributions');check(close(sum(float(x['net_gain'])for x in rs),target-float(r['baseline_net'])),'net_gains_sum');check(close(r['target_all_candidate_margin_pp'],100*target/N),'all_candidate_cushion');check(close(r['unbounded_share_shift_pp'],100*(target-float(r['baseline_net']))/(2*T)),'unbounded_formula');check(close(r['target_A'],(T+target)/2)and close(r['target_B'],(T-target)/2),'state_pair_targets')
  for x in rs:
   w=float(x['scenario_pair_votes']);q=float(x['target_share'])if x['target_share']else None
   if q is not None:check(0<=q<=1,'bounded_share');check(close(x['target_net'],w*(2*q-1)),'unit_target_net');check(close(x['target_A_votes'],w*q)and close(x['target_B_votes'],w*(1-q)),'unit_target_pair_counts')
   denom=float(x['scenario_all_candidate_votes'])
   if x['target_all_candidate_margin_pp']:check(close(x['target_all_candidate_margin_pp'],100*float(x['target_net'])/denom),'unit_all_candidate_margin')
   check(close(x['local_Aplus1_pair_net'],.01*w),'local_Aplus1_net')
   check(close(x['gain_per_A_share_pp'],.02*w),'share_margin_factor_two')
   if w>0:
    rawq=float(x['selected_only_required_share']);oth=float(x['others_fixed_net']);check(close(oth+w*(2*rawq-1),target),'selected_only_break_even');expected='already_secured'if rawq<0 else'impossible'if rawq>1 else'feasible';check(x['selected_only_status']==expected,'selected_only_status')
   else:check(x['selected_only_status']=='no_positive_pool'and x['selected_only_required_share']=='','no_positive_pool')
   if x['historical_pair_share']:
    baseline=float(x['historical_pair_share']);delta=float(x['uniform_bounded_shift_pp'])/100;check(close(q,min(1,max(0,baseline+delta))),'explicit_clipping')
 # Meaningful synthetic assertions, and counted votes never changed by forecast.
 cases={r['name']:r for r in json.loads((D/'live-scenarios.json').read_text())}
 for r in cases.values():
  check(live(r['input'])==r['result'],'saved_live_reproduction');check(r['result']['counted_fixed']==r['input']['counted'],'counted_votes_fixed')
 check(cases['unknown_pool']['result']['status']=='unknown_remaining_pool','unknown_case');check(cases['negative_pool']['result']['status']=='invalid_negative_or_nonfinite_pool','negative_case');check(cases['no_pool']['result']['final_denominator']==130,'no_pool_final_denominator');check(cases['secured']['result']['requirement_status']=='already_secured','secured_case');check(cases['impossible']['result']['requirement_status']=='impossible','impossible_case');check(cases['clipping_high']['result']['used_A_pair_share']==1 and cases['clipping_low']['result']['used_A_pair_share']==0,'clipping_cases');check(cases['third_candidate_wins']['result']['plurality_winner']=='Named Independent','full_field_legal_threshold');check(cases['unknown_other_allocation']['result']['plurality_winner']is None,'unknown_other_allocation')
 z=cases['final_denominator_cushion']['result'];check(z['final_denominator']==230 and z['final_pair_denominator']==210 and close(z['required_A_pair_share'],(90+2.1+20)/180),'final_denominator_cushion');check(cases['all_other_pool']['result']['requirement_status']=='no_positive_pair_pool','no_positive_pair_case')
 multi=cases['selected_multiunit_1'];q=multi['result']['selected_unit_requirement']['required_share'];inp=json.loads(json.dumps(multi['input']));inp['remaining_units'][0]['remaining_A_pair_share']=q;res=live(inp);check(close(res['pair_net'],.01*res['final_pair_denominator']),'multiunit_selected_final_denominator')
 bounded=json.loads((D/'bounded-scenarios.json').read_text())
 for r in bounded:check(solve_shift(r['weights'],r['shares'],r['target'])==r['result'],'bounded_saved_reproduction')
 check(bounded[1]['result']['status']=='impossible'and bounded[2]['result']['status']=='no_positive_pool'and bounded[3]['result']['status']=='unknown_preference'and bounded[4]['result']['baseline_status']=='already_winning','bounded_edge_statuses')
 check(bounded[0]['result']['clipped_units']>0 and close(bounded[0]['result']['achieved_net'],0),'bounded_synthetic_clip')
 check(cases['selected_unknown_preference']['result']['status']=='conditional_only_selected_preference_unknown'and cases['selected_unknown_preference']['result']['final_A']is None,'selected_unknown_preference_preserved')
 # Current final official HTML/XLSX roster independently agrees, flags preserved.
 roster=json.loads((D/'source/current-senate-roster.json').read_text());xls=json.loads((D/'source/current-senate-spreadsheet-rows.json').read_text());check(len(roster['rows'])==len(xls)==9,'current_roster_coverage')
 for a,b in zip(roster['rows'],xls):check(a['fields']==[c['decoded']for c in b['cells']],'current_final_roster_agreement')
 check(sum(r['fields'][-1]=='Y'for r in roster['rows'])==3,'current_writeins')
 # Frozen bodies checked, not current byte equality inferred after a later peer seal.
 peer=json.loads((D/'peer-comparison/reconciliation.json').read_text());check(peer['checks']==917624 and peer['exact_priority_equal'],'frozen_peer_semantic_pass')
 for e in json.loads((D/'peer-comparison/stable-v1/receipt.json').read_text())['entries']:
  b=(D/'peer-comparison/stable-v1'/e['snapshot']).read_bytes();check(sha(b)==e['stored_sha256']and len(b)==e['stored_bytes'],'frozen_peer_stored_hash');raw=gzip.decompress(b);check(sha(raw)==e['sha256']and len(raw)==e['bytes'],'frozen_peer_exact_body')
 # Readiness controls and relative report links. URLs have direct primary citations; no network needed for the offline audit.
 for p in [S/'county-partisanship.md',D/'source/SCHEMA.md']:
  for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   if re.match(r'https?://|#',target):continue
   target=target.split('#')[0];resolved=p.parent/target
   if resolved in [D/'validation.json',D/'asset-manifest.json']:continue
   check(resolved.exists(),'relative_links')
 check(not any(p.name in ['__pycache__','node_modules','.venv']for p in D.rglob('*')),'no_cache_dependencies')
 gaps=['Formal coordinator acceptance remains pending; current geography approval false.','No source method splits, generic/invalid write-in controls or extracted blank/under/over counts in selected historical originals.','Current final roster names/parties/write-ins verified; live vendor IDs and historical-to-current native joins unverified.','Actual remaining pool/candidate participation and electronic UOCAVA deadline presentation unresolved; calculator inputs explicit and synthetic.','No2026turnout forecast, candidate effects/lower preferences, live collector, measured cadence or calibrated probability.']
 output=dict(status='pass_offline_original_controls_calculators_and_asset_audit',checks=dict(checks),total_checks=sum(checks.values()),coverage=dict(counties_each=64,native2024=3199,native2022=3232,native2020=3205,original_CSV_records=9831,allcandidate_positions=101529,native_candidate_positions=99514,OOXML_native_rows=3183,OOXML_cells=22281,cached_tail=1043548,county_target_rows=len(ct),native_target_rows=len(nt),state_scenarios=len(st),synthetic_live_cases=len(cases)),priority=contract['crossing'],formal_acceptance=False,current_geography_approved=False,material_gaps=gaps)
 (D/'validation.json').write_text(json.dumps(output,indent=2)+'\n')
 # Every owned file including scripts/report/validation; only manifest excludes itself to avoid recursion.
 owned=[S/'county-partisanship.md',D.parent/'county-baselines.csv']+[p for p in D.rglob('*')if p.is_file()and p!=D/'asset-manifest.json'];assets=[]
 for p in sorted(owned):
  b=p.read_bytes();assert len(b)<40000000;entry=dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))
  if p.suffix=='.gz':
   raw=gzip.decompress(b);entry.update(reconstruction='gzip.decompress yields exact ordered derivative/original entity',decoded_bytes=len(raw),decoded_sha256=sha(raw))
  assets.append(entry)
 (D/'asset-manifest.json').write_text(json.dumps(dict(scope='only county-partisanship.md,data/county-baselines.csv,data/baselines/**',self_exclusion='asset-manifest.json only; prevents recursive hash; every other owned file included',assets=assets,referenced_originals=list({r['path']:r for r in refs}.values())),indent=2)+'\n')
 for p in [S/'county-partisanship.md',D/'source/SCHEMA.md']:
  for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   if not re.match(r'https?://|#',target):assert (p.parent/target.split('#')[0]).exists()
 # Immediate audit exact coverage and hashes, not a self-reported success flag alone.
 mf=json.loads((D/'asset-manifest.json').read_text());assert len(mf['assets'])==len(owned)
 for a in mf['assets']:b=(S/a['path']).read_bytes();assert sha(b)==a['sha256']and len(b)==a['bytes']and len(b)<40000000
 print(json.dumps(dict(status=output['status'],checks=output['total_checks'],assets=len(assets),maximum_asset_bytes=max(a['bytes']for a in assets),material_gaps=len(gaps))))
if __name__=='__main__':main()
