#!/usr/bin/env python3
"""Offline deterministic, conditional arithmetic. Shares fractions; no probabilities."""
import math,json,argparse

def clip(q):return max(0.,min(1.,q))
def condition(q):
 if q is None:return 'no-positive-pool'
 if q<0:return 'secured-under-assumptions'
 if q>1:return 'impossible-under-assumptions'
 return 'feasible-boundary' if q in [0,1] else 'feasible'
def uniform(units,target_margin=0):
 if not math.isfinite(target_margin):raise ValueError('nonfinite target')
 if any(t<0 or not math.isfinite(t) or (t>0 and (s is None or not 0<=s<=1)) for t,s in units):raise ValueError('invalid weight/share')
 T=sum(t for t,s in units);M=sum(t*(2*s-1) for t,s in units if t>0)
 if T==0:return dict(status='no-positive-pool',pair_total=0,baseline_net=0,raw_shift=None,bounded_shift=None,target_net=0,raw_uniform_feasible=None,clipped_units=0)
 goal=target_margin*T;raw=(goal-M)/(2*T)
 if abs(target_margin)>1:return dict(status='impossible',pair_total=T,baseline_net=M,raw_shift=raw,bounded_shift=None,target_net=goal,raw_uniform_feasible=False,clipped_units=0)
 feasible=all(0<=s+raw<=1 for t,s in units if t>0)
 lo,hi=-1.,1.
 for _ in range(95):
  mid=(lo+hi)/2;v=sum(t*(2*clip(s+mid)-1) for t,s in units if t>0)
  if v<goal:lo=mid
  else:hi=mid
 delta=(lo+hi)/2
 # plateau at full saturation admits unbounded ray of shifts; record it explicitly.
 interval=None
 if target_margin==-1:delta=-max(s for t,s in units if t>0);interval=['-infinity',delta]
 if target_margin==1:delta=1-min(s for t,s in units if t>0);interval=[delta,'infinity']
 return dict(status='feasible-bounded' if not feasible else 'feasible-uniform',pair_total=T,baseline_net=M,raw_shift=raw,bounded_shift=delta,target_net=goal,raw_uniform_feasible=feasible,clipped_units=sum(not 0<=s+delta<=1 for t,s in units if t>0),solution_interval=interval,already_at_or_above_target=M>=goal)

def selected(pair_total,selected_T,other_net,target_margin=0):
 if selected_T<0:raise ValueError('negative pool')
 goal=target_margin*pair_total
 if selected_T==0:return dict(required_share_unbounded=None,required_share_clipped=None,status='no-positive-pool',fixed_other_net=other_net,already_at_target=other_net>=goal)
 q=(selected_T+goal-other_net)/(2*selected_T)
 return dict(required_share_unbounded=q,required_share_clipped=clip(q),status=condition(q),fixed_other_net=other_net,already_at_target=None)

def live(x):
 """Counted A/B/other fixed; remaining total includes assumed other-candidate counts.
 Each unit supplies remaining_total, remaining_other mapping and pair_share.
 Unknown is explicit; blank pool is never zero. Final denominator includes counted+remainder.
 """
 try:
  a=x['counted']['A'];b=x['counted']['B'];co=x['counted'].get('other',{});units=x['remaining'];g=x.get('target_pair_margin',0)
  if isinstance(g,bool) or not isinstance(g,(int,float)) or not math.isfinite(g):return {'status':'invalid-nonfinite-or-nonnumeric-target','counted_fixed':x['counted']}
  if abs(g)>1:return {'status':'invalid-target-out-of-bounds','counted_fixed':x['counted']}
  keys=[u.get('unit') for u in units]
  if any(not isinstance(k,str) or not k.strip() for k in keys):return {'status':'invalid-remaining-unit-key','counted_fixed':x['counted']}
  if len(set(keys))!=len(keys):return {'status':'invalid-duplicate-remaining-unit','counted_fixed':x['counted']}
  nums=[a,b,*co.values()]
  if any(not isinstance(v,(int,float)) or not math.isfinite(v) or v<0 for v in nums):return {'status':'invalid-negative-or-nonfinite-counted'}
  if any(u.get('remaining_total') is None or u.get('remaining_other') is None for u in units):return {'status':'unknown-remainder','counted_fixed':x['counted']}
  parsed=[];ro={};cliplog=[]
  for u in units:
   total=u['remaining_total'];other=u['remaining_other'];vals=[total,*other.values()]
   if any(not isinstance(v,(int,float)) or not math.isfinite(v) or v<0 for v in vals):return {'status':'invalid-negative-or-nonfinite-remainder','counted_fixed':x['counted']}
   U=total-sum(other.values())
   if U<0:return {'status':'invalid-other-exceeds-pool','counted_fixed':x['counted']}
   q=u.get('pair_share')
   if q is not None and (not isinstance(q,(int,float)) or not math.isfinite(q)):return {'status':'invalid-nonfinite-share'}
   if q is not None and clip(q)!=q:cliplog.append({'unit':u['unit'],'input':q,'clipped':clip(q)})
   parsed.append((u['unit'],U,None if q is None else clip(q),total,other))
   for k,v in other.items():ro[k]=ro.get(k,0)+v
  U=sum(r[1] for r in parsed);final_pair=a+b+U;final_all=a+b+sum(co.values())+sum(r[3] for r in parsed);L=a-b
  fo={k:co.get(k,0)+ro.get(k,0) for k in set(co)|set(ro)}
  threshold=None if U==0 else (g*final_pair-L+U)/(2*U)
  # For A to be plurality winner it must beat B AND each individual named other.
  tqb=None if U==0 else (U-L)/(2*U)
  tqother={k:(v-a)/U for k,v in fo.items()} if U>0 else {}
  plurality=max([tqb,*tqother.values()]) if U>0 else None
  r=dict(status='no-positive-pool' if U==0 else condition(threshold),counted_fixed=x['counted'],remaining_pair_pool=U,final_pair_denominator=final_pair,final_all_candidate_denominator=final_all,final_other=fo,target_pair_margin=g,required_remaining_A_share_unbounded=threshold,required_remaining_A_share_clipped=None if threshold is None else clip(threshold),pair_tie_required_share=tqb,plurality_strictly_exceeds_share=plurality,plurality_status='no-positive-pool' if U==0 else condition(plurality),other_candidate_thresholds=tqother,share_clipping=cliplog,calibration='Arithmetic only; no calibrated probability')
  if U==0:
   r.update(final_A=a,final_B=b,final_pair_net=L,final_pair_margin=None if final_pair==0 else L/final_pair,final_all_margin=None if final_all==0 else L/final_all,plurality_A_secured=a>max([b,*fo.values()]))
  elif all(q is not None or u==0 for name,u,q,total,other in parsed):
   fa=a+sum(u*q for name,u,q,total,other in parsed if u>0);fb=b+sum(u*(1-q) for name,u,q,total,other in parsed if u>0);net=fa-fb
   r.update(final_A=fa,final_B=fb,final_pair_net=net,final_pair_margin=net/final_pair,final_all_margin=net/final_all,plurality_A_secured=fa>max([fb,*fo.values()]))
  if x.get('selected_unit') is not None:
   name=x['selected_unit'];chosen=[z for z in parsed if z[0]==name]
   if len(chosen)!=1:r['selected']={'status':'missing-or-duplicate-selected-unit'}
   elif any(q is None and u>0 for n,u,q,total,other in parsed if n!=name):r['selected']={'status':'unknown-other-unit-preference'}
   else:
    sn=chosen[0][1];other=L+sum(u*(2*q-1) for n,u,q,total,o in parsed if n!=name and u>0)
    r['selected']=selected(final_pair,sn,other,g)
  return r
 except (KeyError,TypeError,AttributeError):return {'status':'invalid-schema'}

def main():
 p=argparse.ArgumentParser();p.add_argument('input',help='JSON object or list of scenarios');args=p.parse_args();x=json.load(open(args.input));print(json.dumps([dict(name=i.get('name'),result=live(i)) for i in x] if isinstance(x,list) else live(x),indent=2,allow_nan=False))
if __name__=='__main__':main()
