"""Generate historical scenarios/targets from our independently parsed source tables."""
import csv,json,math,gzip
from collections import defaultdict
from calculator import historical,selected,solve,R
from county import js,csvout,SPECS

def main():
 scenarios=[];contributions=[];countyselected=[];local=[];native_selected=[]
 for pref in SPECS:
  for setting,volume in [('low','2022-senate'),('base','2024-president'),('high','2020-senate')]+([('actual-governor','2022-governor')] if pref=='2022-governor' else []):
   for margin in [0,.01]:
    arg={'mode':'county','preference':pref,'mix':{volume:1},'target_margin':margin,'denominator':'reported_all_choice'};o=historical(arg);sid=f'{pref}-{setting}-'+('tie' if margin==0 else 'Aplus1');o['scenario_id']=sid;o['input']=arg;scenarios.append(o)
    for r,field in zip(o['result']['units'],o['county_volume_and_full_field']):
     contributions.append({'scenario_id':sid,'county':r['key'],'preference':pref,'historical_volume_source':volume,'reported_all_choice_volume':field['reported_all_choice_volume'],'pair_participation':field['pair_participation'],**r})
    for field in o['county_volume_and_full_field']:
     sel=historical({**arg,'county':field['county']})['result'];countyselected.append({'scenario_id':sid,'county':field['county'],'target_margin':margin,'selected_pair_volume':sel['selected_pair_volume'],'other_net_votes_fixed':sel['other_net_votes_fixed'],'selected_baseline_share':sel['selected_baseline_share'],'unbounded_required_share':sel['unbounded_required_share'],'required_share':sel['required_share'],'status':sel['status']})
 # Standalone local pair ties/cushions are different from necessary statewide targets.
 wide=list(csv.DictReader((R.parent/'county-baselines.csv').open()));native=json.loads((R/'native-units.json').read_text());state={}
 for ct in SPECS:
  state[ct]={'pair':sum(int(r['pair_votes']) for r in wide if r['contest']==ct),'net':sum(int(r['A_minus_B_net_votes']) for r in wide if r['contest']==ct)}
 for r in wide:
  for m in [0,.01]:
   t=int(r['pair_votes']);p=float(r['A_pair_share']);local.append({'scope':'county standalone pair arithmetic','contest':r['contest'],'key':r['county'],'pair_votes':t,'source_share':p,'target_pair_margin':m,'target_A_share':(1+m)/2,'share_shift_points':100*((1+m)/2-p),'net_vote_change':t*((1+m)-(2*p)),'gain_per_A_share_point':.02*t,'status':'feasible_local_pair_target'})
 recon=json.loads((R/'native-reconciliation.json').read_text());closed={(r['source_key'],r['contest'],r['county']) for r in recon if r['column_closed']}
 for r in native:
  for m in [0,.01]:
   t=r['pair_votes'];p=r['A_pair_share'];local.append({'scope':'historical native source-local standalone pair arithmetic; not state','contest':r['contest'],'key':r['unit_key'],'pair_votes':t,'source_share':p,'target_pair_margin':m,'target_A_share':(1+m)/2 if t else None,'share_shift_points':100*((1+m)/2-p) if p is not None else None,'net_vote_change':t*((1+m)-2*p) if p is not None else None,'gain_per_A_share_point':.02*t if t is not None else None,'status':'unknown_source_pair' if t is None else 'no_positive_pool' if t==0 else 'feasible_local_pair_target'})
   ct=r['contest'];s=state[ct];eligible=(r['source_key'],ct,r['county']) in closed and t is not None
   othernet=s['net']-(t*(2*p-1) if p is not None else 0);q=(m*s['pair']-othernet+t)/(2*t) if eligible and t and p is not None else None
   native_selected.append({'contest':ct,'key':r['unit_key'],'state_pair_votes_from_all36_counties':s['pair'],'state_net_votes_from_all36_counties':s['net'],'target_pair_margin':m,'selected_pair_volume':t,'source_share':p,'all_other_votes_fixed_net':othernet if eligible else None,'unbounded_required_share':q,'bounded_required_share':min(1,max(0,q)) if q is not None else None,'status':'unknown_unclosed_native_scope' if not eligible else 'no_positive_pool' if not t else 'secured_even_at_zero' if q<0 else 'impossible_even_at_one' if q>1 else 'feasible','assumption':'same-contest all36 county candidate controls fixed; only this column-closed source-local native unit changes A/B split; all other units represented by explicit aggregate source controls, no residual assigned to a native identity'})
 js('historical-scenarios.json',scenarios);csvout('county-contributions.csv',contributions);csvout('county-selected-targets.csv',countyselected);csvout('local-pair-targets.csv',local);csvout('native-selected-state-targets.csv',native_selected)
 # Known-native all-scope scenarios deliberately unavailable outside modeled source pool.
 ns=[]
 for pref in SPECS:
  for m in [0,.01]:ns.append(historical({'mode':'native','preference':pref,'mix':{pref:1},'target_margin':m}))
 js('known-native-scenarios.json',ns)
 print(json.dumps({'state_scenarios':len(scenarios),'county_contributions':len(contributions),'selected_county_cases':len(countyselected),'local_cases':len(local),'native_selected_state_cases':len(native_selected)}))
if __name__=='__main__':main()
