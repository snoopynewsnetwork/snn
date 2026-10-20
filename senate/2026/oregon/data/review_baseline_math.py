"""Independent saturation-event audit; no producer solver imports or writes."""
from pathlib import Path
from collections import defaultdict
import csv, hashlib, json, math
D=Path(__file__).resolve().parent; R=D.parent; B=D/'baselines'
checks=0; maximum_shift=0.; maximum_net=0.

def check(value, reason):
 global checks
 checks+=1
 if not value:raise AssertionError(reason)

def close(x,y,reason,atol=1e-7):
 check(math.isfinite(x) and math.isfinite(y) and abs(x-y)<=atol+1e-12*max(abs(x),abs(y)),reason)

def rows(path):
 with path.open(newline='')as f:return list(csv.DictReader(f))

def root(units,margin):
 T=math.fsum(t for t,p in units);target=margin*T
 points=sorted({-1.,1.,*[-p for t,p in units if t>0],*[1-p for t,p in units if t>0]})
 def net(x):return math.fsum(t*(2*min(1,max(0,p+x))-1)for t,p in units)
 for left,right in zip(points,points[1:]):
  lower=net(left);upper=net(right)
  if lower<=target<=upper:
   return left if upper==lower else left+(target-lower)*(right-left)/(upper-lower)
 raise AssertionError('target outside finite event domain')

def main():
 global maximum_shift,maximum_net
 county=rows(D/'county-baselines.csv');idx={(x['contest'],x['county']):x for x in county};check(len(idx)==144,'all county contexts')
 candidates=rows(B/'county-candidates.csv');check(len(candidates)==864,'all county candidate positions')
 for x in county:
  a=int(x['A_votes']);b=int(x['B_votes']);v=int(x['reported_all_choice_votes']);t=a+b
  own=[c for c in candidates if(c['contest'],c['county'])==(x['contest'],x['county'])]
  check(len(own) in (5,6,8),'full own candidate scope');check(sum(int(c['votes'])for c in own)==v,'county full-field source balance')
  close(float(x['pair_participation_in_reported_all_choice']),t/v,'pair participation')
  close(float(x['A_pair_share']),a/t,'county pair share')
  check(int(x['pair_votes'])==t and int(x['A_minus_B_net_votes'])==a-b,'integer pair source')
 scenarios=json.loads((B/'historical-scenarios.json').read_bytes());contrib=rows(B/'county-contributions.csv');selected=rows(B/'county-selected-targets.csv');check(len(scenarios)==26,'complete scenario settings')
 for s in scenarios:
  arg=s['input'];pref=arg['preference'];margin=arg['target_margin'];names=sorted(x['county']for x in county if x['contest']==pref);expected=[];volumes={};other=defaultdict(float)
  for name in names:
   x=idx[pref,name];a=int(x['A_votes']);b=int(x['B_votes']);allv=int(x['reported_all_choice_votes']);v=math.fsum(int(idx[ct,name]['reported_all_choice_votes'])*w for ct,w in arg['mix'].items());t=v*(a+b)/allv;p=a/(a+b);expected.append((t,p));volumes[name]=(v,t,p)
   for c in candidates:
    if(c['contest'],c['county'])==(pref,name) and c['candidate']not in (x['A'],x['B']):other[c['candidate']]+=v*int(c['votes'])/allv
  T=math.fsum(t for t,p in expected);net=math.fsum(t*(2*p-1)for t,p in expected);want=margin*T;shift=root(expected,margin);unbounded=(want-net)/(2*T);result=s['result'];maximum_shift=max(maximum_shift,abs(shift-result['bounded_share_shift']))
  close(result['pair_volume'],T,'scenario denominator');close(result['baseline_net_votes'],net,'scenario baseline net');close(result['unbounded_share_shift'],unbounded,'unbounded solve',1e-12);close(result['bounded_share_shift'],shift,'bounded event solve',1e-12)
  achieved=math.fsum(t*(2*min(1,max(0,p+shift))-1)for t,p in expected);maximum_net=max(maximum_net,abs(achieved-want));close(achieved,want,'event target net')
  rs={x['county']:x for x in contrib if x['scenario_id']==s['scenario_id']};sels={x['county']:x for x in selected if x['scenario_id']==s['scenario_id']};check(set(rs)==set(sels)==set(names),'all counties retained')
  for name in names:
   v,t,p=volumes[name];q=min(1,max(0,p+shift));r=rs[name];sel=sels[name]
   for field,value in [('reported_all_choice_volume',v),('pair_volume',t),('share',p),('weight',t/T),('target_share',q),('baseline_net_votes',t*(2*p-1)),('target_net_votes',t*(2*q-1)),('net_vote_gain',2*t*(q-p)),('gain_per_A_share_point',.02*t)]:close(float(r[field]),value,'county contribution '+field)
   othernet=net-t*(2*p-1);need=(want-othernet+t)/(2*t);close(float(sel['unbounded_required_share']),need,'selected unbounded share');close(float(sel['required_share']),min(1,max(0,need)),'selected clipped display')
   check(sel['status']==('secured_even_at_zero'if need<0 else'impossible_even_at_one'if need>1 else'feasible'),'selected feasible status')
  check(set(other)==set(s['other_final']),'full other field retained')
  for k,v in other.items():close(s['other_final'][k],v,'fixed named/generic other totals')
  V=math.fsum(v for v,t,p in volumes.values());close(s['historical_volume'],V,'all-choice volume');close(s['A_final'],(T+want)/2,'state final A');close(s['B_final'],(T-want)/2,'state final B');close(s['A_minus_B_all_choice_margin'],want/V,'all-choice margin distinct')
 native=json.loads((B/'native-units.json').read_bytes());ni={x['unit_key']:x for x in native};check(len(ni)==len(native),'native key uniqueness');recon=json.loads((B/'native-reconciliation.json').read_bytes());closed={(x['source_key'],x['contest'],x['county'])for x in recon if x['column_closed']}
 for r in rows(B/'local-pair-targets.csv'):
  ct=r['contest'];m=float(r['target_pair_margin'])
  if r['scope']=='county standalone pair arithmetic':x=idx[ct,r['key']];t=int(x['pair_votes']);p=float(x['A_pair_share'])
  else:x=ni[r['key']];t=x['pair_votes'];p=x['A_pair_share']
  if t is None:check(r['status']=='unknown_source_pair'and r['target_A_share']=='','unknown native stays unknown');continue
  if t==0:check(r['status']=='no_positive_pool','zero pool');continue
  close(float(r['target_A_share']),(1+m)/2,'local target');close(float(r['share_shift_points']),100*((1+m)/2-p),'local shift');close(float(r['net_vote_change']),t*(1+m-2*p),'local net')
 state={ct:(sum(int(x['pair_votes'])for x in county if x['contest']==ct),sum(int(x['A_minus_B_net_votes'])for x in county if x['contest']==ct))for ct in {x['contest']for x in county}}
 for r in rows(B/'native-selected-state-targets.csv'):
  x=ni[r['key']];t=x['pair_votes'];p=x['A_pair_share'];m=float(r['target_pair_margin']);T,N=state[x['contest']];eligible=(x['source_key'],x['contest'],x['county'])in closed and t is not None
  check(int(r['state_pair_votes_from_all36_counties'])==T and int(r['state_net_votes_from_all36_counties'])==N,'all-state controls fixed')
  if not eligible:check(r['status']=='unknown_unclosed_native_scope' and r['unbounded_required_share']=='','unclosed native target unmodeled');continue
  if not t:check(r['status']=='no_positive_pool','native selected zero pool');continue
  q=(m*T-(N-t*(2*p-1))+t)/(2*t);close(float(r['unbounded_required_share']),q,'native selected all-others-fixed');close(float(r['bounded_required_share']),min(1,max(0,q)),'native clipped display')
 for scenario in json.loads((B/'known-native-scenarios.json').read_bytes()):
  ct=scenario['preference'];choices={}
  for x in native:
   if x['contest']==ct and(x['source_key'],ct,x['county'])in closed:choices.setdefault(x['county'],x['source_key'])
  source=[x for x in native if x['contest']==ct and choices.get(x['county'])==x['source_key']];expected=[(x['pair_votes'],x['A_pair_share'])for x in source if x['pair_votes'] and x['A_pair_share']is not None];result=scenario['result'];check(len(source)==len(result['units']),'one closed publication per county')
  shift=root(expected,result['target_margin']);close(result['bounded_share_shift'],shift,'known-native clipped event root',1e-12);check(scenario['statewide_native_dispatch']is None,'no extrapolated native dispatch')
 output={'status':'pass_independent_historical_and_source_local_formula_review','checks':checks,'county_rows':len(county),'state_scenarios':len(scenarios),'county_contributions':len(contrib),'county_selected_targets':len(selected),'native_source_local_units':len(native),'local_target_rows':len(rows(B/'local-pair-targets.csv')),'native_selected_state_cases':len(rows(B/'native-selected-state-targets.csv')),'maximum_shift_difference':maximum_shift,'maximum_net_residual':maximum_net,'method':'Independent event-interval integration, no author solver imports','source_or_producer_bytes_written':False,'current_or_geographic_approvals':False,'source_inputs':[]}
 for path in [D/'county-baselines.csv',B/'county-candidates.csv',B/'native-units.json',B/'historical-scenarios.json',B/'county-contributions.csv',B/'county-selected-targets.csv',B/'local-pair-targets.csv',B/'native-selected-state-targets.csv',B/'known-native-scenarios.json']:
  raw=path.read_bytes();output['source_inputs'].append({'path':str(path.relative_to(R)),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
 (D/'coordinator-baseline-math-review.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps({k:v for k,v in output.items()if k!='source_inputs'}))

if __name__=='__main__':main()
