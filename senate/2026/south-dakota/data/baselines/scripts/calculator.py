#!/usr/bin/env python3
"""Offline deterministic arithmetic. No probabilities, turnout prediction or source collector."""
import argparse,json,math
def clip(x):return max(0.,min(1.,x))
def net(units,delta=0.):return sum(u['pair_volume']*(2*clip(u['a_share']+delta)-1)for u in units)
def bounded_shift(units,margin=0.,bounds=(-1.,1.)):
 for u in units:
  if not math.isfinite(u['pair_volume'])or u['pair_volume']<0 or not math.isfinite(u['a_share'])or not 0<=u['a_share']<=1:raise ValueError('invalid volume/share')
 T=sum(u['pair_volume']for u in units);base=net(units);target=margin*T
 if T<=0:return dict(status='no_positive_pool',pair_total=T,baseline_net=base,target_net=target,unbounded_shift=None,bounded_shift=None)
 unbounded=(target-base)/(2*T);lo,hi=bounds
 if not -1<=lo<=hi<=1:raise ValueError('shift bounds must lie in [-1,1]')
 minimum,maximum=net(units,lo),net(units,hi)
 result=dict(pair_total=T,baseline_net=base,target_net=target,unbounded_shift=unbounded,unbounded_shift_share_pp=100*unbounded,unbounded_target_has_clipping=any(not 0<=u['a_share']+unbounded<=1 for u in units),bounds=list(bounds),baseline_already_at_or_above_target=base>=target)
 if target<minimum-1e-8 or target>maximum+1e-8:return dict(result,status='impossible_with_shift_bounds',bounded_shift=None,feasible_net_min=minimum,feasible_net_max=maximum)
 for _ in range(90):
  mid=(lo+hi)/2
  if net(units,mid)<target:lo=mid
  else:hi=mid
 delta=(lo+hi)/2
 return dict(result,status='already_winning_baseline'if base>target else'feasible',bounded_shift=delta,bounded_shift_share_pp=100*delta,achieved_net=net(units,delta),clipped_units=sum(not 0<=u['a_share']+delta<=1 for u in units))
def selected_unit(units,key,margin=0.,elsewhere_shift=0.):
 selected=next(u for u in units if u['key']==key);T=sum(u['pair_volume']for u in units);other=net([u for u in units if u['key']!=key],elsewhere_shift);v=selected['pair_volume'];need=margin*T-other
 if v<=0:return dict(status='no_positive_pool',required_share=None,other_fixed_net=other,target_net=margin*T)
 q=(need/v+1)/2
 return dict(status='secured_even_at_zero'if q<0 else'impossible'if q>1 else'feasible',required_share=q,display_clipped_share=clip(q),selected_pair_volume=v,other_fixed_net=other,elsewhere_share_shift=elsewhere_shift,target_net=margin*T,required_net=need,required_share_change_pp=100*(q-selected['a_share']))
def live(data):
 """Counted votes fixed. remaining_total includes A, B and each named other candidate."""
 counted=data['counted'];A=data['a'];B=data['b'];units=data['remaining'];margin=data.get('target_pair_margin',0.)
 if A==B or A not in counted or B not in counted:raise ValueError('distinct named A/B must be counted keys')
 if any(not isinstance(v,(int,float))or not math.isfinite(v)or v<0 for v in counted.values()):return dict(status='invalid_negative_or_nonfinite_counted')
 if any(u.get('remaining_total')is None for u in units):return dict(status='unknown_remaining_pool',counted_fixed=counted)
 if any(not math.isfinite(u['remaining_total'])or u['remaining_total']<0 for u in units):return dict(status='invalid_negative_or_nonfinite_remaining',counted_fixed=counted)
 final=dict(counted);contributions=[];pool=0.;flags=[]
 for u in units:
  other=u.get('other_shares',{})
  if any(k in[A,B]or k not in counted for k in other):raise ValueError('other keys must be distinct declared counted candidates')
  if any(not math.isfinite(s)or not 0<=s<=1 for s in other.values())or sum(other.values())>1:return dict(status='invalid_other_shares')
  p=1-sum(other.values());v=u['remaining_total']*p;pool+=v
  if u.get('a_pair_share')is None and v>0:return dict(status='unknown_remaining_preference',counted_fixed=counted)
  requested=u.get('a_pair_share')or 0.
  if not math.isfinite(requested):return dict(status='invalid_nonfinite_share')
  q=clip(requested);flags.append(q!=requested)
  gains={A:v*q,B:v*(1-q),**{k:u['remaining_total']*s for k,s in other.items()}}
  for k,x in gains.items():final[k]=final.get(k,0)+x
  contributions.append(dict(key=u['key'],remaining_total=u['remaining_total'],pair_pool=v,requested_a_pair_share=requested,clipped_a_pair_share=q,was_clipped=q!=requested,gains=gains))
 L=counted[A]-counted[B];finalpair=counted[A]+counted[B]+pool;finalall=sum(final.values());target=margin*finalpair
 qreq=(target-L+pool)/(2*pool)if pool>0 else None
 status=('secured_no_pair_pool'if L>target else'impossible_no_pair_pool'if L<target else'tied_no_pair_pool')if pool==0 else('secured_even_at_zero'if qreq<0 else'impossible'if qreq>1 else'feasible')
 winners=[k for k,x in final.items()if abs(x-max(final.values()))<1e-9]
 return dict(status=status,counted_fixed=counted,remaining_contributions=contributions,remaining_pair_pool=pool,remaining_all_candidate_pool=sum(u['remaining_total']for u in units),required_remaining_a_pair_share=qreq,display_clipped_required_share=clip(qreq)if qreq is not None else None,target_pair_margin=margin,target_net_uses_FINAL_pair_denominator=target,final_candidate_votes=final,final_pair_denominator=finalpair,final_all_candidate_denominator=finalall,final_a_minus_b_net=final[A]-final[B],final_pair_margin_pp=100*(final[A]-final[B])/finalpair if finalpair else None,final_all_candidate_margin_pp=100*(final[A]-final[B])/finalall if finalall else None,plurality_winners=winners,unique_plurality_winner=winners[0]if len(winners)==1 else None,any_preference_clipped=any(flags),probability=None)
def live_selected(data,key):
 """Only selected remaining preference is free; every other remaining unit fixed."""
 result=live(data)
 if 'remaining_contributions'not in result:return result
 u=next(u for u in result['remaining_contributions']if u['key']==key);v=u['pair_pool'];A=data['a'];B=data['b']
 other=sum(x['gains'][A]-x['gains'][B]for x in result['remaining_contributions']if x['key']!=key)
 L=data['counted'][A]-data['counted'][B];target=result['target_net_uses_FINAL_pair_denominator']
 q=(target-L-other+v)/(2*v)if v>0 else None
 return dict(status='no_positive_pool'if v<=0 else'secured_even_at_zero'if q<0 else'impossible'if q>1 else'feasible',selected_key=key,required_share=q,display_clipped_share=clip(q)if q is not None else None,counted_net_fixed=L,other_remaining_net_fixed=other,selected_pair_pool=v,final_pair_denominator=result['final_pair_denominator'],target_net=target)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('--selected');p.add_argument('--historical',action='store_true');p.add_argument('--elsewhere-shift',type=float,default=0.);args=p.parse_args();data=json.load(open(args.input))
 if args.historical:
  result=selected_unit(data['units'],args.selected,data.get('target_pair_margin',0.),args.elsewhere_shift)if args.selected else bounded_shift(data['units'],data.get('target_pair_margin',0.),tuple(data.get('shift_bounds',[-1,1])))
 else:result=live_selected(data,args.selected)if args.selected else live(data)
 print(json.dumps(result,indent=2,allow_nan=False))
