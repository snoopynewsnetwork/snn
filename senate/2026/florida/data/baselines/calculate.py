#!/usr/bin/env python3
"""Offline deterministic historical scenarios. A=the named Democrat; B=Republican.
County volume is ALL VALID candidate votes; pair participation comes from preference anchor.
Native calculations use COMPILED A+B only; no certified native write-in allocation exists.
"""
import argparse,csv,gzip,json,math
from collections import defaultdict
from pathlib import Path
from parse_sources import D,csvwrite,writejson
from build import readcsv

def clip(q):return min(1.,max(0.,q))
def bounded_shift(weights,shares,target_net):
 P=math.fsum(weights);M=math.fsum(t*(2*s-1) for t,s in zip(weights,shares))
 if P<=0:return {'status':'no_positive_pool','unbounded_shift':None,'bounded_shift':None,'net':M,'target_net':target_net,'clipped_units':0}
 unbounded=(target_net-M)/(2*P)
 if target_net < -P-1e-7 or target_net>P+1e-7:return {'status':'impossible','unbounded_shift':unbounded,'bounded_shift':None,'net':None,'target_net':target_net,'clipped_units':None}
 lo=-1.;hi=1.
 for _ in range(85):
  mid=(lo+hi)/2;net=math.fsum(t*(2*clip(s+mid)-1) for t,s in zip(weights,shares))
  if net<target_net:lo=mid
  else:hi=mid
 delta=(lo+hi)/2;net=math.fsum(t*(2*clip(s+delta)-1) for t,s in zip(weights,shares));clipped=sum(t>0 and (s+delta<0 or s+delta>1) for t,s in zip(weights,shares))
 return {'status':'feasible_with_clipping' if clipped else 'feasible','baseline_already_above_target':M>target_net,'unbounded_shift':unbounded,'bounded_shift':delta,'net':net,'target_net':target_net,'clipped_units':clipped,'unbounded_would_clip':sum(t>0 and (s+unbounded<0 or s+unbounded>1) for t,s in zip(weights,shares))}
def selected_threshold(t,other_net,target_net):
 if t<=0:return {'status':'no_positive_pool','required_share_unbounded':None,'clipped_share':None,'minimum_change_net':None}
 q=(t+target_net-other_net)/(2*t)
 return {'status':'already_secured_under_fixed_others' if q<0 else 'impossible_under_fixed_others' if q>1 else 'feasible','required_share_unbounded':q,'clipped_share':clip(q),'minimum_change_net':target_net-other_net}

def county_scenarios():
 rows=readcsv(D.parent/'county-baselines.csv');contexts=['2024-senate','2022-senate','2024-president','2020-president'];by={c:{r['county_fips']:r for r in rows if f"{r['year']}-{r['contest']}"==c} for c in contexts};volumes={'low':sum(int(r['all_candidate_votes']) for r in by['2022-senate'].values()),'base':sum(int(r['all_candidate_votes']) for r in by['2024-senate'].values()),'high':sum(int(r['all_candidate_votes']) for r in by['2020-president'].values())};out=[];state=[]
 for pref in contexts:
  for mix in contexts:
   mix_total=sum(int(r['all_candidate_votes']) for r in by[mix].values())
   for vol,F in volumes.items():
    us=[]
    for fips,r in sorted(by[pref].items()):
     Fc=F*int(by[mix][fips]['all_candidate_votes'])/mix_total;participation=float(r['pair_participation_of_valid']);Tc=Fc*participation
     us.append({'county_fips':fips,'county':r['county'],'county_code':r['county_code'],'all_volume':Fc,'pair_volume':Tc,'pair_participation':participation,'share':float(r['A_pair_share']),'other_volume':Fc-Tc,'A_name':r['A_name'],'B_name':r['B_name'],'historical_A':int(r['A_votes']),'historical_B':int(r['B_votes'])})
    P=math.fsum(u['pair_volume'] for u in us);M=math.fsum(u['pair_volume']*(2*u['share']-1) for u in us)
    for target,g in [('tie',0.),('Aplus1_pair_margin',.01),('Aplus1_all_candidate_margin',.01*F/P)]:
     sid=f'pref-{pref}_mix-{mix}_volume-{vol}_{target}';solve=bounded_shift([u['pair_volume'] for u in us],[u['share'] for u in us],g*P);delta=solve['bounded_shift'];nets=[];av=[]
     for u in us:
      t=u['pair_volume'];q=clip(u['share']+delta);net=t*(2*q-1);cond=selected_threshold(t,M-t*(2*u['share']-1),g*P);nets.append(net);av.append(t*q)
      out.append({'scenario_id':sid,'preference_anchor':pref,'mix_anchor':mix,'historical_volume_label':vol,'historical_volume_basis':'2022-senate-valid' if vol=='low' else '2024-senate-valid' if vol=='base' else '2020-president-valid',**u,'pair_weight':t/P,'all_candidate_weight':u['all_volume']/F,'baseline_net':t*(2*u['share']-1),'baseline_state_margin_contribution_pp':100*t*(2*u['share']-1)/P,'target':target,'target_pair_margin_pp':100*g,'unbounded_shift_share_pp':100*solve['unbounded_shift'],'bounded_shift_share_pp':100*delta,'target_A_pair_share':q,'share_clipped':u['share']+delta!=q,'actual_share_change_pp':100*(q-u['share']),'target_pair_margin_unit_pp':100*(2*q-1),'target_A_all_share':q*t/u['all_volume'],'target_net_votes':net,'gain_net_votes':net-t*(2*u['share']-1),'gain_net_votes_per_1pp_A_share':.02*t,'selected_only_others_assumption':'every other county at anchor preference; same declared volume/mix/pair-participation, other candidates fixed','selected_only_status':cond['status'],'selected_only_unbounded_A_pair_share':cond['required_share_unbounded'],'selected_only_clipped_A_pair_share':cond['clipped_share'],'selected_only_change_share_pp':100*(cond['required_share_unbounded']-u['share']) if cond['required_share_unbounded'] is not None else None})
     net=math.fsum(nets);A=math.fsum(av);B=P-A
     # A must exceed each individual opponent. Aggregate other is an upper bound for largest other.
     O=F-P;state.append({'scenario_id':sid,'preference_anchor':pref,'mix_anchor':mix,'historical_volume_label':vol,'all_candidate_volume':F,'pair_volume':P,'other_valid_volume':O,'pair_participation':P/F,'baseline_A_minus_B':M,'baseline_pair_margin_pp':100*M/P,'baseline_all_candidate_margin_pp':100*M/F,'target':target,'target_A_minus_B':g*P,'target_pair_margin_pp':100*g,'target_all_candidate_margin_pp':100*g*P/F,'unbounded_shift_share_pp':100*solve['unbounded_shift'],'bounded_shift_share_pp':100*delta,'clipped_units':solve['clipped_units'],'unbounded_would_clip_units':solve['unbounded_would_clip'],'solve_status':solve['status'],'baseline_already_above_target':solve['baseline_already_above_target'],'computed_A_minus_B':net,'computed_A':A,'computed_B':B,'A_exceeds_aggregate_other_upper_bound':A>O,'B_exceeds_aggregate_other_upper_bound':B>O,'county_count':len(us),'weight_sum':math.fsum(u['pair_volume']/P for u in us),'net_residual':net-g*P})
 csvwrite(D/'county-scenarios.csv.gz',out);csvwrite(D/'state-scenarios.csv',state);writejson(D/'scenario-settings.json',{'version':1,'A':'named DEM anchor candidate, not assumed 2026 effect','B':'named REP anchor candidate','county_volume_basis':'all valid candidate votes including named valid write-ins','volumes':volumes,'preference_anchors':contexts,'mix_anchors':contexts,'pair_participation':'each county preference-anchor (A+B)/all-valid votes; no single statewide substitution','other_candidates':'held outside pair, at same county preference-anchor participation; aggregate upper bound used to check no other can beat tied A/B','targets':['tie','Aplus1_pair_margin','Aplus1_all_candidate_margin'],'native_no_crossyear_join':True,'not_a_2026_projection':True})
 return state

def native_scenarios():
 rows=readcsv(D/'native-units.csv.gz');contexts=['2024-senate','2022-senate','2024-president','2020-president'];totals={c:sum(int(r['pair_total']) for r in rows if f"{r['year']}-{r['contest']}"==c) for c in contexts};vols={'low':totals['2022-senate'],'base':totals['2024-senate'],'high':totals['2020-president']};out=[];states=[]
 for context in contexts:
  us=[r for r in rows if f"{r['year']}-{r['contest']}"==context];p0=totals[context];shares=[int(r['A'])/int(r['pair_total']) if int(r['pair_total']) else .5 for r in us]
  for vol,P in vols.items():
   weights=[P*int(r['pair_total'])/p0 for r in us];M=math.fsum(t*(2*s-1) for t,s in zip(weights,shares))
   for target,g in [('tie',0.),('Aplus1_pair_margin',.01)]:
    solve=bounded_shift(weights,shares,g*P);delta=solve['bounded_shift'];sid=f'native-{context}_volume-{vol}_{target}';net=0
    for r,t,s in zip(us,weights,shares):
     q=clip(s+delta);m=t*(2*q-1);net+=m;cond=selected_threshold(t,M-t*(2*s-1),g*P)
     out.append({'scenario_id':sid,'context':context,'volume_label':vol,'county_code':r['county_code'],'county':r['county'],'native_key':r['native_key'],'method':r['method'],'volume_basis':'compiled A+B only; all-valid-native denominator unavailable','native_pair_volume':t,'native_pair_weight':t/P,'historical_A':r['A'],'historical_B':r['B'],'baseline_share':s if int(r['pair_total']) else None,'zero_pair_share_convention':'.5 computational placeholder with zero weight' if not int(r['pair_total']) else '', 'baseline_net':t*(2*s-1),'target':target,'uniform_unbounded_shift_share_pp':100*solve['unbounded_shift'],'uniform_bounded_shift_share_pp':100*delta,'target_share':q if t>0 else None,'clipped':s+delta!=q if t>0 else False,'target_net_votes':m,'gain_net_votes':m-t*(2*s-1),'gain_net_votes_per_1pp':.02*t,'all_valid_denominator':None,'generic_writein_marks':r['generic_writein_marks'],'overvotes':r['overvotes'],'undervotes':r['undervotes'],'selected_only_others_assumption':'all other native contexts at compiled same-year preferences and stated volume scaling; no crossyear native match','selected_only_status':cond['status'],'selected_only_unbounded_share':cond['required_share_unbounded'],'selected_only_clipped_share':cond['clipped_share']})
    states.append({'scenario_id':sid,'context':context,'volume_label':vol,'pair_volume':P,'native_units':len(us),'positive_pool_units':sum(t>0 for t in weights),'baseline_net':M,'target_net':g*P,'unbounded_shift_share_pp':100*solve['unbounded_shift'],'bounded_shift_share_pp':100*delta,'clipped_units':solve['clipped_units'],'computed_net':net,'residual':net-g*P,'all_valid_denominator':None,'source_scope':'compiled, unadjusted; not certified native allocation'})
 csvwrite(D/'native-scenarios.csv.gz',out);csvwrite(D/'native-state-scenarios.csv',states)

def selected_cli(a):
 rs=readcsv(D.parent/'county-baselines.csv');rs=[r for r in rs if r['year']=='2024' and r['contest']=='senate'];chosen=[r for r in rs if r['county'].lower()==a.county.lower() or r['county_fips']==a.county];assert len(chosen)==1,'Use a county name or five-digit FIPS';r=chosen[0];P=sum(int(z['pair_votes']) for z in rs);F=sum(int(z['all_candidate_votes']) for z in rs);other=math.fsum(int(z['pair_votes'])*(2*clip(float(z['A_pair_share'])+a.others_share_shift_pp/100)-1) for z in rs if z!=r);target=a.target_margin_pp/100*(P if a.denominator=='pair' else F);print(json.dumps({'county':r['county'],'A':r['A_name'],'B':r['B_name'],'source_basis':'2024 Senate official all67 county results','pair_total':P,'all_candidate_total':F,'other_counties_net_assumed':other,'others_share_shift_pp':a.others_share_shift_pp,'target_net':target,**selected_threshold(int(r['pair_votes']),other,target)},indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--county');p.add_argument('--others-share-shift-pp',type=float,default=0);p.add_argument('--target-margin-pp',type=float,default=0);p.add_argument('--denominator',choices=['pair','all'],default='pair');a=p.parse_args()
 if a.county:selected_cli(a)
 else:county_scenarios();native_scenarios();print('Historical county/native scenarios built; no calibrated probabilities.')
