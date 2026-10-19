#!/usr/bin/env python3
"""Offline deterministic historical targets and conditional live remainder; no probabilities."""
from pathlib import Path
import csv,gzip,io,json,math,argparse
D=Path(__file__).resolve().parent

def clip(x):return min(1.,max(0.,x))
def status(q,pool):
 if pool<=0:return 'no_positive_pool'
 if q<0:return 'already_secured'
 if q>1:return 'impossible'
 return 'feasible'
def solve_shift(weights,shares,target_net):
 total=sum(weights)
 if total<=0:return dict(status='no_positive_pool',unbounded_shift=None,bounded_shift=None,achieved_net=0,clipped_units=0)
 if any(s is None and w>0 for w,s in zip(weights,shares)):return dict(status='unknown_preference',unbounded_shift=None,bounded_shift=None,achieved_net=None,clipped_units=0)
 base=sum(w*(2*s-1)for w,s in zip(weights,shares)if w>0);unbounded=(target_net-base)/(2*total)
 if target_net < -total or target_net>total:return dict(status='impossible',unbounded_shift=unbounded,bounded_shift=None,achieved_net=None,clipped_units=0)
 lo,hi=-1.,1.
 for _ in range(75):
  mid=(lo+hi)/2;net=sum(w*(2*clip(s+mid)-1)for w,s in zip(weights,shares)if w>0)
  if net<target_net:lo=mid
  else:hi=mid
 delta=(lo+hi)/2;achieved=sum(w*(2*clip(s+delta)-1)for w,s in zip(weights,shares)if w>0)
 return dict(status='feasible',baseline_status='already_winning'if base>0 else 'tied'if base==0 else 'trailing',unbounded_shift=unbounded,bounded_shift=delta,achieved_net=achieved,clipped_units=sum(1 for w,s in zip(weights,shares)if w>0 and not 0<=s+delta<=1))
def selected_only(pool,other_net,target_net):
 if pool<=0:return dict(required_share=None,clipped_share=None,status='no_positive_pool',fixed_others_net=other_net,target_net=target_net)
 q=(pool+target_net-other_net)/(2*pool)
 return dict(required_share=q,clipped_share=clip(q),status=status(q,pool),fixed_others_net=other_net,target_net=target_net)
def live(x):
 """remaining_votes means ALL remaining valid candidate votes, not ballots issued or ballots received."""
 
 if 'remaining_units'in x:return live_units(x)
 counted=x['counted'];other=counted.get('other_candidates',{});
 if any(k in ('A','B')for k in other):return dict(status='invalid_other_candidate_identity',probability=None)
 out=dict(counted_fixed=counted,assumptions=x,probability=None)
 vals=[counted['A'],counted['B'],*other.values()]
 if any(not isinstance(v,(int,float))or not math.isfinite(v)or v<0 for v in vals):return dict(out,status='invalid_negative_or_nonfinite_counted')
 U=x.get('remaining_votes');op=x.get('remaining_other_share');q=x.get('remaining_A_pair_share');L=counted['A']-counted['B'];countedtotal=sum(vals)
 if U is None:return dict(out,status='unknown_remaining_pool',final_denominator=None)
 if not isinstance(U,(int,float))or not math.isfinite(U)or U<0:return dict(out,status='invalid_negative_or_nonfinite_pool',final_denominator=None)
 if U==0:
  names=dict(other,A=counted['A'],B=counted['B']);winner=max(names,key=names.get);lead=names[winner]-max(v for k,v in names.items()if k!=winner)
  return dict(out,status='no_pool',final_denominator=countedtotal,final_counts=names,pair_net=L,plurality_winner=winner if lead>0 else None,plurality_cushion_votes=lead)
 if op is None:return dict(out,status='unknown_other_participation',final_denominator=countedtotal+U)
 if not isinstance(op,(int,float))or not math.isfinite(op)or not 0<=op<=1:return dict(out,status='invalid_other_share',final_denominator=countedtotal+U)
 pair=U*(1-op);finalpair=counted['A']+counted['B']+pair;g=x.get('target_pair_margin_pp',0)/100;target=g*finalpair
 if not math.isfinite(g):return dict(out,status='invalid_target')
 req=selected_only(pair,L,target);out.update(remaining_pair_votes=pair,required_A_pair_share=req['required_share'],requirement_status=req['status'],target_pair_net=target,final_pair_denominator=finalpair,final_denominator=countedtotal+U)
 if pair==0:
  out['requirement_status']='no_positive_pair_pool'
 if q is None:return dict(out,status='unknown_remaining_preference',pair_net_bounds=[L-pair,L+pair])
 if not isinstance(q,(int,float))or not math.isfinite(q):return dict(out,status='invalid_pair_share')
 qc=clip(q);A=counted['A']+pair*qc;B=counted['B']+pair*(1-qc);remainingother=U*op
 allocation=x.get('other_allocation');names=dict(other,A=A,B=B);legal=None
 if remainingother==0:allocation={}
 if allocation is not None:
  if any(not isinstance(v,(int,float))or not math.isfinite(v)or v<0 for v in allocation.values())or (remainingother>0 and abs(sum(allocation.values())-1)>1e-10):return dict(out,status='invalid_named_other_allocation')
  for name,share in allocation.items():
   if name in ('A','B'):return dict(out,status='invalid_other_candidate_identity')
   names[name]=names.get(name,0)+remainingother*share
  winner=max(names,key=names.get);cushion=names[winner]-max(v for k,v in names.items()if k!=winner);legal=winner if cushion>0 else None
  out.update(final_named_counts=names,plurality_winner=legal,plurality_cushion_votes=cushion)
 else:
  # No invented distribution: bounds keep each counted other candidate fixed.
  out.update(plurality_winner=None,plurality_status='unknown_named_other_allocation',A_minimum_cushion_vs_any_other=A-max([*other.values(),0])-remainingother)
 return dict(out,status='calculated',input_share_clipped=qc!=q,used_A_pair_share=qc,final_A=A,final_B=B,final_other=sum(other.values())+remainingother,pair_net=A-B,pair_margin_pp=100*(A-B)/finalpair if finalpair else None,all_candidate_margin_pp=100*(A-B)/(countedtotal+U),pair_target_reached=A-B>=target-1e-10)
def live_units(x):
 counted=x['counted'];units=x['remaining_units'];keys=[u['key']for u in units]
 if len(keys)!=len(set(keys)):return dict(status='duplicate_remaining_unit',probability=None)
 results=[];totalU=0;pair=0;addsA=0;addsB=0;otheradd=0;allocation={};allocation_known=True;selected_unknown=False
 for u in units:
  r=live(dict(u,counted=dict(A=0,B=0,other_candidates={}),target_pair_margin_pp=0));original_result=r
  if u['key']==x.get('selected_key')and u.get('remaining_A_pair_share')is None and r['status']=='unknown_remaining_preference':
   selected_unknown=True;r=live(dict(u,counted=dict(A=0,B=0,other_candidates={}),target_pair_margin_pp=0,remaining_A_pair_share=.5))
  results.append(dict(key=u['key'],result=original_result))
  if r['status']not in ('calculated','no_pool'):return dict(status='unknown_or_invalid_unit',unit_results=results,probability=None,final_denominator=None)
  U=u['remaining_votes'];totalU+=U
  if U==0:continue
  pair+=r['remaining_pair_votes'];addsA+=r['final_A'];addsB+=r['final_B'];otheradd+=r['final_other']
  if 'final_named_counts'not in r:allocation_known=False
  else:
   for k,v in r['final_named_counts'].items():
    if k not in ('A','B'):allocation[k]=allocation.get(k,0)+v
 aggregate=dict(x);aggregate.pop('remaining_units');aggregate.pop('selected_key',None);aggregate.update(remaining_votes=totalU,remaining_other_share=otheradd/totalU if totalU else 0,remaining_A_pair_share=addsA/pair if pair else 0,other_allocation={k:v/otheradd for k,v in allocation.items()}if otheradd and allocation_known else {}if not otheradd else None)
 result=live(aggregate);result['unit_results']=results
 selected=x.get('selected_key')
 if selected is not None:
  if selected not in keys:return dict(status='missing_selected_key',probability=None)
  u=units[keys.index(selected)];pool=u['remaining_votes']*(1-u['remaining_other_share'])if u['remaining_votes']else 0;ownnet=pool*(2*clip(u['remaining_A_pair_share']if u.get('remaining_A_pair_share')is not None else .5)-1)if pool else 0
  L=counted['A']-counted['B'];g=x.get('target_pair_margin_pp',0)/100;finalpair=counted['A']+counted['B']+pair
  result['selected_unit_requirement']=selected_only(pool,L+addsA-addsB-ownnet,g*finalpair);result['selected_key']=selected;result['other_units_assumption']='all other units fixed at supplied remaining pool, other participation and clipped pair preference; counted statewide votes fixed'
 if selected_unknown:
  result.update(status='conditional_only_selected_preference_unknown',assumptions=x,final_A=None,final_B=None,pair_net=None,pair_margin_pp=None,all_candidate_margin_pp=None,pair_target_reached=None,plurality_winner=None)
  for k in ['final_named_counts','plurality_cushion_votes','used_A_pair_share','input_share_clipped']:result.pop(k,None)
 return result
def readcsv(p):
 b=p.read_bytes();b=gzip.decompress(b)if p.suffix=='.gz'else b;return list(csv.DictReader(io.StringIO(b.decode())))
def writecsv(p,rows):
 rows=list(rows);s=io.StringIO(newline='');w=csv.DictWriter(s,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows);b=s.getvalue().encode();p.write_bytes(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)
def build():
 counties=readcsv(D.parent/'county-baselines.csv');native=readcsv(D/'native-baselines.csv.gz');state=[];countyout=[];nativeout=[];settings=[]
 for r in counties+native:
  for k in ['year','A','B','other','pair_votes','candidate_votes']:r[k]=int(r[k])
  r['s']=r['A']/r['pair_votes']if r['pair_votes']else None
 # Complete county mix sensitivity: actual low2022/base2024/high2020 pair volumes, all64 weights.
 for prefyear in [2024,2022,2020]:
  prefs={r['county_literal']:r for r in counties if r['year']==prefyear}
  for label,volyear in [('low',2022),('base',2024),('high',2020)]:
   volume={r['county_literal']:r for r in counties if r['year']==volyear};keys=sorted(prefs);assert set(keys)==set(volume)and len(keys)==64
   rows=[prefs[k]for k in keys];weights=[volume[k]['pair_votes']for k in keys];shares=[r['s']for r in rows];others=[volume[k]['other']for k in keys];T=sum(weights);O=sum(others);base=sum(w*(2*s-1)for w,s in zip(weights,shares));sid=f'county-pref{prefyear}-{label}-volume{volyear}'
   settings.append(dict(scenario=sid,geography='county',preference_anchor=prefyear,volume_anchor=volyear,volume_lane=label,volume_basis='actual historical county A+B candidate votes; other held at same volume-year county counts',pair_total=T,all_candidate_total=T+O,units=64,other_units_assumption='historical preference-anchor shares at historical volume-anchor pair counts, zero added share shift'))
   for g in [0,.01]:
    sol=solve_shift(weights,shares,g*T);delta=sol['bounded_shift'];targetshares=[clip(s+delta)for s in shares];A=sum(w*s for w,s in zip(weights,targetshares));B=T-A
    state.append(dict(scenario=sid,geography='county',preference_year=prefyear,volume_year=volyear,volume_lane=label,units=64,pair_total=T,all_candidate_total=T+O,other_votes=O,baseline_net=base,baseline_pair_margin_pp=100*base/T,target_pair_margin_pp=100*g,target_net=g*T,unbounded_share_shift_pp=100*sol['unbounded_shift'],bounded_share_shift_pp=100*delta,clipped_units=sol['clipped_units'],achieved_net=sol['achieved_net'],target_all_candidate_margin_pp=100*g*T/(T+O),target_A=A,target_B=B,A_cushion_vs_all_other_combined=A-O,pair_baseline_status=sol['baseline_status'],status=sol['status']))
    for k,r,w,s,ts,o in zip(keys,rows,weights,shares,targetshares,others):
     ownbase=w*(2*s-1);selected=selected_only(w,base-ownbase,g*T)
     countyout.append(dict(scenario=sid,key=r['key'],county_literal=k,preference_year=prefyear,volume_year=volyear,A_name=r['A_name'],B_name=r['B_name'],historical_A=r['A'],historical_B=r['B'],historical_other=r['other'],historical_pair_share=s,scenario_pair_votes=w,scenario_other_votes=o,scenario_all_candidate_votes=w+o,pair_participation=w/(w+o)if w+o else None,pair_weight=w/T,candidate_weight=(w+o)/(T+O),baseline_net=ownbase,target_pair_margin_pp=100*g,target_share=ts,target_margin_pp=100*(2*ts-1),target_all_candidate_margin_pp=100*w*(2*ts-1)/(w+o)if w+o else None,target_A_votes=w*ts,target_B_votes=w*(1-ts),target_A_all_candidate_share=w*ts/(w+o)if w+o else None,local_Aplus1_pair_net=.01*w,target_net=w*(2*ts-1),net_gain=w*2*(ts-s),gain_per_A_share_pp=.02*w,share_shift_pp=100*(ts-s),uniform_unbounded_shift_pp=100*sol['unbounded_shift'],uniform_bounded_shift_pp=100*delta,clipped=not 0<=s+delta<=1,local_tie_share=.5,local_Aplus1_share=.505,local_tie_shift_pp=(.5-s)*100,local_Aplus1_shift_pp=(.505-s)*100,selected_only_required_share=selected['required_share'],selected_only_clipped_share=selected['clipped_share'],selected_only_status=selected['status'],others_fixed_net=selected['fixed_others_net']))
 # Every native universe retained; cross-year sensitivity uses county mix with explicitly fixed within-county native pair fractions, never native identity joins.
 for y in [2024,2022,2020]:
  for label,volyear in [('low',2022),('base',2024),('high',2020)]:
   rows=[r for r in native if r['year']==y];prefcounties={r['county_literal']:r for r in counties if r['year']==y};volcounties={r['county_literal']:r for r in counties if r['year']==volyear};weights=[r['pair_votes']/prefcounties[r['county_literal']]['pair_votes']*volcounties[r['county_literal']]['pair_votes']for r in rows];shares=[r['s']for r in rows];otherweights=[r['other']/prefcounties[r['county_literal']]['other']*volcounties[r['county_literal']]['other'] if prefcounties[r['county_literal']]['other'] else 0 for r in rows];T=sum(weights);O=sum(otherweights);base=sum(w*(2*s-1)for w,s in zip(weights,shares)if w);sid=f'native-pref{y}-{label}-countyvolume{volyear}'
   settings.append(dict(scenario=sid,geography='native',preference_anchor=y,volume_anchor=volyear,volume_lane=label,volume_basis='historical volume-year county A+B distributed by preference-year within-county native A+B fraction; other by own within-county other fraction; no crossyear native join',pair_total=T,all_candidate_total=T+O,units=len(rows),other_units_assumption='every other source-native unit at own-year A/B preference and explicitly rescaled county-mix weight; no added shift'))
   for g in [0,.01]:
    sol=solve_shift(weights,shares,g*T);delta=sol['bounded_shift'];A=sum(w*clip(s+delta)for w,s in zip(weights,shares)if w>0)
    state.append(dict(scenario=sid,geography='native',preference_year=y,volume_year=volyear,volume_lane=label,units=len(rows),pair_total=T,all_candidate_total=T+O,other_votes=O,baseline_net=base,baseline_pair_margin_pp=100*base/T,target_pair_margin_pp=100*g,target_net=g*T,unbounded_share_shift_pp=100*sol['unbounded_shift'],bounded_share_shift_pp=100*delta,clipped_units=sol['clipped_units'],achieved_net=sol['achieved_net'],target_all_candidate_margin_pp=100*g*T/(T+O),target_A=A,target_B=T-A,A_cushion_vs_all_other_combined=A-O,pair_baseline_status=sol['baseline_status'],status=sol['status']))
    for r,w,s,ow in zip(rows,weights,shares,otherweights):
     ts=clip(s+delta)if s is not None else None;ownnet=w*(2*s-1)if s is not None else 0;sel=selected_only(w,base-ownnet,g*T)
     nativeout.append(dict(scenario=sid,preference_year=y,volume_year=volyear,volume_lane=label,key=r['key'],county_literal=r['county_literal'],native_id_literal=r['native_id_literal'],source_id=r['source_id'],source_record=r['source_record'],A_name=r['A_name'],B_name=r['B_name'],A=r['A'],B=r['B'],other=r['other'],scenario_pair_votes=w,scenario_other_votes=ow,scenario_all_candidate_votes=w+ow,pair_participation=w/(w+ow)if w+ow else None,pair_weight=w/T,candidate_weight=(w+ow)/(T+O),historical_pair_share=s,baseline_net=ownnet,target_pair_margin_pp=g*100,target_share=ts,target_margin_pp=(2*ts-1)*100 if ts is not None else None,target_all_candidate_margin_pp=100*w*(2*ts-1)/(w+ow)if ts is not None and w+ow else None,target_A_votes=w*ts if ts is not None else 0,target_B_votes=w*(1-ts)if ts is not None else 0,target_A_all_candidate_share=w*ts/(w+ow)if ts is not None and w+ow else None,local_Aplus1_pair_net=.01*w,target_net=w*(2*ts-1)if ts is not None else 0,net_gain=2*w*(ts-s)if ts is not None else 0,gain_per_A_share_pp=.02*w,share_shift_pp=(ts-s)*100 if ts is not None else None,uniform_unbounded_shift_pp=sol['unbounded_shift']*100,uniform_bounded_shift_pp=delta*100,clipped=s is not None and not 0<=s+delta<=1,local_tie_share=.5 if w else None,local_Aplus1_share=.505 if w else None,local_tie_shift_pp=(.5-s)*100 if s is not None else None,local_Aplus1_shift_pp=(.505-s)*100 if s is not None else None,selected_only_required_share=sel['required_share'],selected_only_clipped_share=sel['clipped_share'],selected_only_status=sel['status'],others_fixed_net=sel['fixed_others_net'],pool_status='positive'if w else 'no_positive_pool'))
 writecsv(D/'county-targets.csv',countyout);writecsv(D/'native-targets.csv.gz',nativeout);writecsv(D/'state-scenarios.csv',state);(D/'scenario-settings.json').write_text(json.dumps(settings,indent=2)+'\n')
 cases=[('unknown_pool',dict(remaining_votes=None)),('no_pool',dict(remaining_votes=0)),('negative_pool',dict(remaining_votes=-1)),('unknown_other',dict(remaining_votes=100,remaining_other_share=None)),('unknown_preference',dict(remaining_votes=100,remaining_A_pair_share=None)),('secured',dict(counted=dict(A=200,B=0,other_candidates={'Named Independent':50}),remaining_votes=50)),('impossible',dict(counted=dict(A=0,B=200,other_candidates={'Named Independent':50}),remaining_votes=50)),('clipping_high',dict(remaining_votes=100,remaining_A_pair_share=1.4)),('clipping_low',dict(remaining_votes=100,remaining_A_pair_share=-.3)),('all_other_pool',dict(remaining_votes=100,remaining_other_share=1)),('third_candidate_wins',dict(counted=dict(A=10,B=5,other_candidates={'Named Independent':100}),remaining_votes=10)),('unknown_other_allocation',dict(remaining_votes=100,other_allocation=None)),('final_denominator_cushion',dict(remaining_votes=100,target_pair_margin_pp=1))]
 examples=[]
 for name,patch in cases:
  x=dict(counted=dict(A=50,B=70,other_candidates={'Named Independent':10}),remaining_votes=100,remaining_other_share=.1,remaining_A_pair_share=.6,other_allocation={'Named Independent':1},target_pair_margin_pp=0);x.update(patch);examples.append(dict(name=name,input=x,result=live(x)))
 units=[dict(key='synthetic-mail',remaining_votes=80,remaining_other_share=.1,remaining_A_pair_share=.7,other_allocation={'Named Independent':1}),dict(key='synthetic-inperson',remaining_votes=20,remaining_other_share=.2,remaining_A_pair_share=.3,other_allocation={'Named Independent':1}),dict(key='synthetic-no-pool',remaining_votes=0,remaining_other_share=None,remaining_A_pair_share=None)]
 for target in [0,1]:
  x=dict(counted=dict(A=50,B=70,other_candidates={'Named Independent':10}),remaining_units=units,selected_key='synthetic-mail',target_pair_margin_pp=target);examples.append(dict(name='selected_multiunit_'+str(target),input=x,result=live(x)))
 x=json.loads(json.dumps(examples[-1]['input']));x['remaining_units'][0]['remaining_A_pair_share']=None;examples.append(dict(name='selected_unknown_preference',input=x,result=live(x)))
 (D/'live-scenarios.json').write_text(json.dumps(examples,indent=2,allow_nan=False)+'\n')
 checks=[dict(name='bounded_clipping',weights=[90,10],shares=[.99,.01],target=0),dict(name='impossible',weights=[100],shares=[.5],target=101),dict(name='no_pool',weights=[0],shares=[None],target=0),dict(name='unknown_positive_preference',weights=[1],shares=[None],target=0),dict(name='already_winning',weights=[100],shares=[.7],target=0)]
 for c in checks:c['result']=solve_shift(c['weights'],c['shares'],c['target'])
 (D/'bounded-scenarios.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(dict(county_target_rows=len(countyout),native_target_rows=len(nativeout),state_scenarios=len(state),live_cases=len(examples))))
def main():
 p=argparse.ArgumentParser();p.add_argument('--live',type=Path);p.add_argument('--selected-key');p.add_argument('--target-margin-pp',type=float,default=0);a=p.parse_args()
 if a.live:print(json.dumps(live(json.loads(a.live.read_text())),indent=2,allow_nan=False));return
 if a.selected_key:
  rs=readcsv(D/'native-baselines.csv.gz'if a.selected_key.count('|')==4 and a.selected_key.rsplit('|',1)[1]else D.parent/'county-baselines.csv');r=next(r for r in rs if r['key']==a.selected_key);rs=[x for x in rs if x['year']==r['year']];T=sum(int(x['pair_votes'])for x in rs);other=sum(int(x['A'])-int(x['B'])for x in rs if x['key']!=r['key']);print(json.dumps(selected_only(int(r['pair_votes']),other,a.target_margin_pp/100*T),indent=2));return
 build()
if __name__=='__main__':main()
