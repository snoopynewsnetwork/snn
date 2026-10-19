"""Coordinator read-only worker review and independent original/target arithmetic.

No worker modules are imported. Original-position hints locate text only; votes
are reparsed from original PDF bytes before producer comparisons. The solver
integrates saturation breakpoints, independently of the producer's bisection.
Only coordinator-owned evidence is written.
"""
from pathlib import Path
from collections import defaultdict
import ast,csv,gzip,hashlib,json,math,re,subprocess
D=Path(__file__).resolve().parent;S=D.parent;B=D/'baselines';T=D/'turnout'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))
def load(p):return json.loads(p.read_bytes())
def jl(p):return [json.loads(x)for x in gzip.decompress(p.read_bytes()).splitlines()]
def freeze(p,b):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():assert p.read_bytes()==b,str(p)
 else:p.write_bytes(b)
def close(a,b,tol=2e-6):assert math.isfinite(a)and math.isfinite(b)and abs(a-b)<=tol,(a,b)
def clip(q):return max(0,min(1,q))
def invert(rows,margin):
 total=sum(v for v,q in rows);target=(1+margin)*total/2;events=defaultdict(float)
 for v,q in rows:
  if v:events[-q]+=v;events[1-q]-=v
 points=sorted(events);area=0.;slope=0.;previous=points[0]
 for x in points:
  end=area+slope*(x-previous)
  if slope>0 and area-1e-9<=target<=end+1e-9:return previous+(target-area)/slope
  area=end;slope+=events[x];previous=x
 assert abs(target-area)<1e-6
 return points[-1]
def main():
 checks={};qa=D/'coordinator-qa/final-first-pair-v1';owned=set();refs=set();manifest_results={}
 for directory,mkey,rkey in [(T,'owned_artifacts','shared_original_references'),(B,'assets','references')]:
  mf=load(directory/'asset-manifest.json');entries=mf[mkey];paths=set()
  for r in entries+mf[rkey]:
   p=S/r['path'];b=p.read_bytes();assert len(b)==r['bytes']and sha(b)==r['sha256'],r['path'];assert len(b)<40_000_000
   if r in entries:assert r['path']not in paths;paths.add(r['path'])
   else:refs.add(r['path'])
  rootpaths=[S/('turnout.md'if directory==T else'county-partisanship.md'),D/('county-turnout.csv'if directory==T else'county-baselines.csv')]
  actual={str(p.relative_to(S))for p in [*directory.rglob('*'),*rootpaths]if p.is_file()}
  exclusions={'data/turnout/asset-manifest.json','data/turnout/validation.json'}if directory==T else{'data/baselines/asset-manifest.json'}
  assert actual==paths|exclusions,(actual-paths-exclusions,paths-actual)
  assert not owned.intersection(paths);owned.update(paths)
  assert not any(p.name in('__pycache__','node_modules','.venv')for p in directory.rglob('*'))
  for p in directory.rglob('*.py'):ast.parse(p.read_bytes(),filename=str(p))
  manifest_results[directory.name]=dict(owned_entries=len(entries),reference_entries=len(mf[rkey]),exact_membership=True,explicit_exclusions=sorted(exclusions),manifest=pin(directory/'asset-manifest.json'),validation=pin(directory/'validation.json'))
  for p in rootpaths+[directory/'asset-manifest.json',directory/'validation.json']:freeze(qa/'frozen'/str(p.relative_to(S)),p.read_bytes())
 # Three baseline-owned primary originals referenced by turnout are checked apart.
 for r in load(T/'asset-manifest.json')['peer_primary_original_references']:
  p=S/r['reference_path'];z=p.read_bytes();raw=gzip.decompress(z);a=r['receipt']
  assert sha(z)==a['stored_sha256']and sha(raw)==a['raw_sha256']and len(raw)==a['raw_bytes']
 checks['frozen_assets']=manifest_results
 # Independently reparse all eleven county/state tables at original PDF positions.
 receipts={a['id']:a for a in load(T/'source/shared-news-ledger.json')};pages={};originals=[]
 for year in [2024,2022,2020]:
  a=receipts[f'sos-{year}-canvass'];z=(D/'news'/a['asset']).read_bytes();raw=gzip.decompress(z)
  assert sha(z)==a['stored_sha256']and sha(raw)==a['raw_sha256']and len(raw)==a['bytes']
  pages[year]=subprocess.run(['pdftotext','-layout','-','-'],input=raw,capture_output=True,check=True).stdout.decode().split('\f');originals.append(a)
 hints=load(T/'extracts/state-controls.json');tables={};numeric=0
 for key,table in hints.items():
  def parse(r):
   nonlocal numeric
   text=pages[int(key[:4])][r['actual_pdf_page']-1].splitlines()[r['source_line_1based']-1];tail=text[r['source_column_0based']:]
   n=len(r['values']);m=re.match(re.escape(r['county_literal'])+r'\s+('+r'\s+'.join([r'\d[\d,]*']*n)+r')',tail);assert m
   vals=[int(v.replace(',',''))for v in m[1].split()];assert vals==r['values']and text==r['raw_line'];numeric+=len(vals);return vals
  tablec={c:parse(r)for c,r in table['counties'].items()};state=parse(table['statewide']);assert len(tablec)==93
  assert [sum(v[j]for v in tablec.values())for j in range(len(state))]==state
  tables[key]=dict(county=tablec,state=state)
 bt=load(B/'extracts/state-controls.json');aliases={'senate2024special':'2024-senate-special','senate2024regular':'2024-senate-regular','president2024':'2024-president','governor2022':'2022-governor','senate2020':'2020-senate'}
 for year in [2024,2022,2020]:aliases[f'registration{year}']=f'{year}-registration';aliases[f'votingmethod{year}']=f'{year}-voting-method'
 for k,a in aliases.items():assert bt[k]['county']==tables[a]['county']and bt[k]['state']==tables[a]['state']
 freeze(qa/'original-derived-eleven-tables.json.gz',gzip.compress((json.dumps(tables,indent=2)+'\n').encode(),mtime=0))
 checks['original_canvass_tables']=dict(tables=11,county_vectors=1023,original_numeric_fields=numeric,source_receipts=originals,independent_baseline_and_turnout_match=True)
 # Full original-derived native order was parsed separately with no worker input.
 nr=load(D/'coordinator-initial-native-named-order-review.json');p=S/nr['original_derived_transcript']['path'];assert pin(p)==nr['original_derived_transcript'];native=load_gzip(p);ni={r['key']:r for r in native}
 c=load(T/'priority-set.json');assert len(c['constituents'])==1326 and c['ordered_full_keys']==[r['key']for r in native]
 assert len(c['all93_parents'])==93
 for r in c['constituents']:
  a=ni[r['key']];assert r['candidate_values']==a['R_L']and r['county']==a['county']and r['generic_writeins']==a['generic_marks']
 assert not c['coordinator_acceptance']and not c['current_geography_approval'];assert len(c['administrative_and_partial_alternates'])==329
 assert len(c['additional_native_source_contexts'])==14 and len(c['unavailable_cases'])==2 and len(c['additional_administrative_contexts'])==2
 for parent in c['all93_parents']:
  rr=[r for r in c['constituents']if r['county']==parent['county']];assert parent['full_child_keys']==[r['key']for r in rr]
  assert parent['priority_child_keys']==[r['key']for r in rr if r['rank']<=765]
  assert parent['full_child_keys']==c['parent_full_child_map'][parent['parent_key']]
  assert parent['priority_child_keys']==c['parent_priority_child_map'][parent['parent_key']]
  for r in rr:assert c['child_parent_map'][r['key']]==parent['parent_key']
 checks['full_native_contract']=dict(full=1326,priority=765,remainder=561,parents=93,priority_parents=sum(bool(p['priority_child_keys'])for p in c['all93_parents']),all_parent_child_arrays_exact=True,complete_alternatives=329,additional_native_PDF_contexts=14,resident_unavailable=2,school_attachments=2)
 # Every reciprocal pin must still identify an exact final body.
 peer=[]
 for path,key in [(T/'peer-agreement.json','peer_inputs'),(B/'peer-reconciliation.json','pins')]:
  o=load(path)
  for r in o[key]:assert pin(S/r['path'])==r
  peer.append(pin(path))
 assert load(B/'peer-reconciliation.json')['presentation_differences']==[]
 checks['reciprocal_final_pins']=peer
 # Independent source-based scenario inputs and piecewise-linear target solution.
 def pair(anchor,county):v=tables[aliases[anchor]]['county'][county];return v[1],v[0]
 def volume(mix,county):
  year={'low_2022_voting_mix':2022,'base_2024_voting_mix':2024,'high_2020_voting_mix':2020}[mix]
  pairc=sum(tables['2024-senate-special']['county'][county]);return pairc*tables[f'{year}-voting-method']['county'][county][-1]/tables['2024-voting-method']['county'][county][-1]
 def expected(row,anchor,mix,geo):
  county=row['county'];a,b=pair(anchor,county)
  if geo=='county':return(a+b if mix=='own_historical_pair'else volume(mix,county)),a/(a+b)
  n=ni[row['key']];v=sum(n['R_L']);return v*volume(mix,county)/sum(tables['2024-senate-special']['county'][county]),n['R_L'][1]/v
 details=jl(B/'scenarios/unit-targets.jsonl.gz');groups=defaultdict(list)
 for r in details:groups[r['scenario'],r['target']].append(r)
 max_shift_error=0.;max_net_error=0.;formulas=0
 def verify_rows(rows,anchor,mix,geo,margin):
  nonlocal max_shift_error,max_net_error,formulas
  assert len(rows)==(93 if geo=='county' else 1326)and len({r['key']for r in rows})==len(rows)
  inputs=[]
  for r in rows:
   v,q=expected(r,anchor,mix,geo);close(r['T'],v);close(r['q'],q,1e-12);inputs.append((v,q))
  V=sum(v for v,q in inputs);M=sum(v*(2*q-1)for v,q in inputs);shift=invert(inputs,margin);net=0
  for r,(v,q)in zip(rows,inputs):
   qs=clip(q+shift);n=v*(2*qs-1);net+=n
   close(r['target_share'],qs,2e-12);close(r['target_net'],n);close(r['weight'],v/V,1e-12);close(r['baseline_net'],v*(2*q-1));close(r['target_gain'],n-v*(2*q-1));close(r['net_gain_for_one_share_pp'],.02*v)
   req=(margin*V-(M-v*(2*q-1))+v)/(2*v)if v else None
   if req is not None:close(r['selected_only_required_share_unbounded'],req)
   else:assert r['selected_only_required_share_unbounded']is None
   formulas+=10
  max_net_error=max(max_net_error,abs(net-margin*V));close(net,margin*V)
  return V,M,shift
 for s in load(B/'scenarios/state-targets.json'):
  V,M,shift=verify_rows(groups[s['scenario'],s['target']],s['anchor'],s['mix'],s['geography'],s['target_margin_fraction'])
  close(s['pair_volume'],V);close(s['baseline_net'],M);close(s['bounded_shift_share_pp'],100*shift,2e-10)
  max_shift_error=max(max_shift_error,abs(s['bounded_shift_share_pp']/100-shift))
 current=load(B/'scenarios/current-five-choice.json');cg=defaultdict(list)
 for r in jl(B/'scenarios/current-five-choice-units.jsonl.gz'):cg[r['scenario']].append(r)
 for s in current:
  frac=sum(s['other_final_share_assumptions'].values());margin={'tie_Ricketts':0,'Osborn_plus1_pair':.01,'Osborn_plus1_all_candidate':.01/(1-frac)}[s['target']]
  V,M,shift=verify_rows(cg[s['scenario']],s['historical_preference_anchor'],s['mix'],s['geography'],margin);allV=V/(1-frac);close(s['final_all_candidate_denominator'],allV)
  A=sum(r['T']*clip(r['q']+shift)for r in cg[s['scenario']]);scores={'Dan Osborn':A,'Pete Ricketts':V-A,**{k:allV*v for k,v in s['other_final_share_assumptions'].items()}}
  assert set(scores)==set(s['candidate_totals'])
  for k,v in scores.items():close(s['candidate_totals'][k],v)
  close(s['pair_margin_pp'],100*(A-(V-A))/V);close(s['all_candidate_margin_pp'],100*(A-(V-A))/allV)
  close(s['legal_pair_share_boundary'],max(V/2,max(scores[k]for k in s['other_final_share_assumptions']))/V)
  if s['legal_pair_share_boundary']>1:assert s['legal_bounded_shift']['status']=='impossible_target_margin'
 checks['independent_targets']=dict(historical_state_groups=46,historical_unit_rows=len(details),five_choice_state_groups=len(current),five_choice_unit_rows=sum(map(len,cg.values())),formula_checks=formulas,solver='Original-source weights/preferences; exact saturation-breakpoint integration, no producer imports/bisection',maximum_shift_fraction_error=max_shift_error,maximum_net_vote_error=max_net_error)
 # Independent live-remainder equations use final counted+remaining denominator.
 live=load(B/'scenarios/live-results.json');numbers=0
 for case in live:
  x=case['input'];o=case['output'];a=x['counted_A'];b=x['counted_B'];u=x['remaining_pair'];other=x['remaining_others']
  assert o.get('probability')is None
  if 'remaining_units'in x:
   if any(r['remaining_pair']is None for r in x['remaining_units']):assert o['status']=='unknown_remaining_unit_pool';continue
   u=sum(r['remaining_pair']for r in x['remaining_units'])
  if u is None:assert o['status']=='unknown_remaining_pool';continue
  if u<0:assert o['status']=='invalid_negative_or_nonfinite_remaining_pool';continue
  assert o['counted_A']==a and o['counted_B']==b and o['counted_others']==x['counted_others']
  P=a+b+u;close(o['final_pair_denominator'],P)
  F=P+sum(x['counted_others'].values())+sum(other.values())if other is not None else None
  if F is not None:close(o['final_all_candidate_denominator'],F)
  else:assert o['final_all_candidate_denominator']is None
  if u:
   close(o['tie_remaining_share'],(u-a+b)/(2*u));close(o['A_plus1_final_pair_share'],(.01*P-a+b+u)/(2*u))
   if F is not None:close(o['A_plus1_final_all_share'],(.01*F-a+b+u)/(2*u))
  if o.get('final_A')is not None:
   close(o['final_A']+o['final_B'],P)
   if o.get('final_others')is not None:close(o['final_A']+o['final_B']+sum(o['final_others'].values()),F)
  numbers+=1
 checks['independent_live']=dict(synthetic_cases=len(live),numeric_or_status_cases=len(live),non_unknown_equation_cases=numbers,counted_fixed=True,final_denominator_verified=True,no_probability=True)
 reg=load(B/'extracts/registration-source-disagreements.json');assert {r['county']:r['difference']for r in reg['observations']}==dict(Nemaha=-4,Clay=12,Nance=3,Gosper=-1,Lancaster=164,Deuel=1)
 checks['qualified_source_gaps']=dict(registration_differences=reg['observations'],generic_nine_counties=1117,generic_selected431=1078,generic_unavailable895=True,eligible_writein_universe_complete=False,eligible_priority_robustness_proven=False,partial_scenario_membership_swap=nr['partial_scenario'],current_geography_approved=False,source_volume_disagreements_unallocated=True)
 frozen=[pin(S/p)for p in sorted(owned)];out=dict(status='pass_frozen_first_pair_named_historical_scope_only',checks=checks,frozen_owned_entries=frozen,review_input_contract=pin(T/'priority-set.json'),formal_dispatch_acceptance=False,qualification='This review accepts no eligible-writein completeness, current geography, later legal/candidate universe, live counts or probability. Source discrepancies stay explicit. Turnout validation/self manifest are separately pinned external exclusions; baseline manifest self only.')
 p=D/'coordinator-finished-first-pair-review.json';freeze(p,(json.dumps(out,indent=2)+'\n').encode());print(json.dumps(pin(p)))
def load_gzip(p):return json.loads(gzip.decompress(p.read_bytes()))
if __name__=='__main__':main()
