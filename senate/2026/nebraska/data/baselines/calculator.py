#!/usr/bin/env python3
"""Offline deterministic arithmetic, not a forecast or probability model.
CLI: calculator.py live INPUT.json | targets INPUT.json
All shares are fractions internally. No observed count is ever scaled or shifted.
"""
import argparse,json,math
def clip(q):return min(1.0,max(0.0,q))
def finite(x):return isinstance(x,(int,float))and not isinstance(x,bool)and math.isfinite(x)
def threshold(q):
 if q is None:return 'unknown'
 if q<0:return 'secured_under_fixed_assumptions'
 if q>1:return 'impossible_under_fixed_assumptions'
 return 'feasible'
def targets(rows,margin=0.0):
 """T is final named-pair pool; q is its requested historical A share.
 Solve sum T(2 clip(q+delta)-1)=margin*sum T. Preserve unconstrained delta.
 """
 if not finite(margin):return dict(status='invalid_margin')
 if any(not finite(r.get('T'))or r['T']<0 for r in rows):return dict(status='invalid_negative_or_unknown_volume')
 T=sum(r['T']for r in rows)
 if T==0:return dict(status='no_positive_pool',pair_volume=0,unbounded_shift_share_pp=None,bounded_shift_share_pp=None,rows=[])
 if any(not finite(r.get('q'))for r in rows if r['T']>0):return dict(status='unknown_preference_anchor')
 if abs(margin)>1:return dict(status='impossible_target_margin',requested_margin=margin,pair_volume=T,unbounded_shift_share_pp=None,bounded_shift_share_pp=None,rows=[])
 prepared=[dict(r,q_requested=r.get('q'),q=clip(r['q'])if r.get('q')is not None else None)for r in rows]
 M=sum(r['T']*(2*r['q']-1)for r in prepared if r['T']>0)
 delta=(margin*T-M)/(2*T)
 def net(d):return sum(r['T']*(2*clip(r['q']+d)-1)for r in prepared if r['T']>0)
 lo=-1.0;hi=1.0
 for _ in range(100):
  mid=(lo+hi)/2
  if net(mid)<margin*T:lo=mid
  else:hi=mid
 bounded=(lo+hi)/2;out=[]
 for r in prepared:
  v=r['T'];q=r['q'];s=clip(q+bounded)if q is not None else None
  baseline=v*(2*q-1)if q is not None else 0
  needed=(margin*T-(M-baseline)+v)/(2*v)if v>0 else None
  out.append(dict(**r,weight=v/T,target_share=s,target_margin=2*s-1 if s is not None else None,
   target_net=v*(2*s-1)if s is not None else 0,baseline_net=baseline,
   target_gain=v*2*(s-q)if q is not None else 0,share_change_pp=100*(s-q)if q is not None else None,
   margin_change_pp=200*(s-q)if q is not None else None,
   net_gain_for_one_share_pp=.02*v,net_gain_for_one_share_pp_after_clipping=2*v*(clip(q+.01)-q)if q is not None else None,
   baseline_anchor_clipped=q!=r.get('q_requested'),unbounded_target_share=q+delta if q is not None else None,
   uniform_target_clipped=(q+bounded<0 or q+bounded>1)if q is not None else False,
   selected_only_required_share_unbounded=needed,selected_only_required_share_display=clip(needed)if needed is not None else None,
   selected_only_status=threshold(needed)if v>0 else'no_positive_pool',
   selected_only_other_units_net=M-baseline,selected_only_other_units_assumption='all other units fixed at this scenario historical baseline q,T',
   selected_only_share_change_pp=100*(needed-q)if needed is not None and q is not None else None))
 return dict(status='solved',pair_volume=T,baseline_net=M,baseline_already_A_leading=M>0,
  target_margin_fraction=margin,target_pair_margin_pp=100*margin,target_net=margin*T,
  unbounded_shift_share_pp=100*delta,bounded_shift_share_pp=100*bounded,
  unbounded_would_clip=sum(r['T']>0 and (r['q']+delta<0 or r['q']+delta>1)for r in prepared),
  bounded_clipped=sum(r['uniform_target_clipped']for r in out),
  achieved_net=sum(r['target_net']for r in out),rows=out,
  legal_outcome_qualification='named-pair scenario only; retain every other candidate and compare all individual candidate totals')
def live(s):
 """Counted A/B/other candidates fixed. Only stated remaining votes are forecast.
 Remaining pair U and each named-other remaining addition must be supplied explicitly.
 """
 if 'remaining_units'in s:return live_units(s)
 a=s.get('counted_A');b=s.get('counted_B');co=s.get('counted_others');u=s.get('remaining_pair');ro=s.get('remaining_others');q=s.get('remaining_A_share')
 result=dict(counted_A=a,counted_B=b,counted_others=co,remaining_pair=u,remaining_others=ro,
  remaining_A_share_requested=q,probability=None,synthetic=bool(s.get('synthetic',False)),
  assumptions=s.get('assumptions'),candidate_A=s.get('candidate_A'),candidate_B=s.get('candidate_B'))
 if not finite(a)or not finite(b)or a<0 or b<0 or not isinstance(co,dict)or any(not finite(v)or v<0 for v in co.values()):return dict(**result,status='invalid_counted_counts')
 if u is None:return dict(**result,status='unknown_remaining_pool',final_pair_denominator=None,final_all_candidate_denominator=None)
 if not finite(u)or u<0:return dict(**result,status='invalid_negative_or_nonfinite_remaining_pool',final_pair_denominator=None,final_all_candidate_denominator=None)
 if ro is not None and (not isinstance(ro,dict)or set(ro)!=set(co)or any(not finite(v)or v<0 for v in ro.values())):return dict(**result,status='invalid_other_candidate_pools')
 Fpair=a+b+u;Fall=Fpair+sum(co.values())+sum(ro.values())if ro is not None else None;lead=a-b
 result.update(final_pair_denominator=Fpair,final_all_candidate_denominator=Fall,counted_pair_lead=lead)
 if u==0:
  finalothers={k:co[k]+ro[k]for k in co}if ro is not None else None
  totals={s.get('candidate_A','A'):a,s.get('candidate_B','B'):b,**(finalothers or{})}
  high=max(totals.values());leaders=[k for k,v in totals.items()if v==high]
  return dict(**result,status='no_positive_pair_pool',pair_lead=lead,final_A=a,final_B=b,final_others=finalothers,
   unique_plurality_winner=leaders[0]if len(leaders)==1 and finalothers is not None else None,
   plurality_status='unknown_other_pools'if finalothers is None else'tied_highest_requires_statutory_process'if len(leaders)>1 else'unique_highest',
   tie_remaining_share=None,A_plus1_final_pair_share=None,A_plus1_final_all_share=None)
 tie=(u-lead)/(2*u);pairplus=(.01*Fpair-lead+u)/(2*u)
 allplus=(.01*Fall-lead+u)/(2*u)if Fall is not None else None
 finalothers={k:co[k]+ro[k]for k in co}if ro is not None else None
 plural=max([tie]+[(v-a)/u for v in finalothers.values()])if finalothers is not None else None
 result.update(tie_remaining_share=tie,tie_status=threshold(tie),A_plus1_final_pair_share=pairplus,A_plus1_final_pair_status=threshold(pairplus),
  A_plus1_final_all_share=allplus,A_plus1_final_all_status=threshold(allplus),
  plurality_remaining_share_boundary=plural,plurality_status=threshold(plural),
  plurality_boundary_rule='A must exceed boundary, not merely tie any highest rival; evaluate every named candidate separately',final_others=finalothers)
 if all(float(x).is_integer()for x in [u,a,b]):
  minimum=max([0,math.floor((b+u-a)/2)+1]+[math.floor(v-a)+1 for v in finalothers.values()])if finalothers is not None else None
  result.update(minimum_integer_remaining_A_for_unique_plurality=minimum,integer_plurality_feasible=(minimum<=u)if minimum is not None else None)
 if q is None:return dict(**result,status='thresholds_only_unknown_remaining_preference',final_A=None,final_B=None)
 if not finite(q):return dict(**result,status='invalid_remaining_share')
 qeff=clip(q);fa=a+u*qeff;fb=b+u*(1-qeff)
 totals={s.get('candidate_A','A'):fa,s.get('candidate_B','B'):fb,**(finalothers or{})};high=max(totals.values());leaders=[k for k,v in totals.items()if v==high]
 result.update(status='projected_conditional_arithmetic',remaining_A_share_used=qeff,share_clipped=qeff!=q,final_A=fa,final_B=fb,
  final_pair_lead=fa-fb,final_pair_margin_pp=100*(fa-fb)/Fpair if Fpair else None,
  final_all_margin_pp=100*(fa-fb)/Fall if Fall else None,
  unique_plurality_winner=leaders[0]if len(leaders)==1 and finalothers is not None else None,
  plurality_outcome='unknown_other_pools'if finalothers is None else'tied_highest_requires_statutory_process'if len(leaders)>1 else'unique_highest')
 return result
def live_units(s):
 """All counted totals fixed; solve a selected remaining unit with others fixed."""
 units=s['remaining_units'];keys=[r['key']for r in units]
 if len(keys)!=len(set(keys)):return dict(status='invalid_duplicate_remaining_unit')
 if any(r.get('remaining_pair')is None for r in units):return dict(status='unknown_remaining_unit_pool',counted_A=s.get('counted_A'),counted_B=s.get('counted_B'),counted_others=s.get('counted_others'))
 if any(not finite(r['remaining_pair'])or r['remaining_pair']<0 for r in units):return dict(status='invalid_negative_remaining_unit_pool')
 U=sum(r['remaining_pair']for r in units)
 known=all(finite(r.get('A_share'))for r in units if r['remaining_pair']>0)
 summary={k:v for k,v in s.items()if k not in ['remaining_units','selected_unit']}
 summary.update(remaining_pair=U,remaining_A_share=sum(r['remaining_pair']*clip(r['A_share'])for r in units if r['remaining_pair']>0)/U if U>0 and known else None)
 result=live(summary);result['remaining_units']=units;result['selected_unit']=s.get('selected_unit');result['remaining_shares_clipped']=[r['key']for r in units if finite(r.get('A_share'))and clip(r['A_share'])!=r['A_share']]
 chosen=next((r for r in units if r['key']==s.get('selected_unit')),None)
 if chosen is None:return dict(**result,selected_status='unknown_selected_unit')
 v=chosen['remaining_pair']
 if v==0:return dict(**result,selected_status='no_positive_pool',selected_required_share=None)
 other=[r for r in units if r is not chosen]
 if any(not finite(r.get('A_share'))for r in other if r['remaining_pair']>0):return dict(**result,selected_status='unknown_other_unit_preference',selected_required_share=None)
 L=s['counted_A']-s['counted_B'];M=sum(r['remaining_pair']*(2*clip(r['A_share'])-1)for r in other if r['remaining_pair']>0)
 req=(v-L-M)/(2*v);reqplus=(.01*result['final_pair_denominator']-L-M+v)/(2*v)
 reqall=(.01*result['final_all_candidate_denominator']-L-M+v)/(2*v)if result['final_all_candidate_denominator']is not None else None
 return dict(**result,selected_required_share=req,selected_status=threshold(req),selected_final_pair_Aplus1_share=reqplus,selected_final_all_Aplus1_share=reqall,
  selected_other_units_fixed_net=M,selected_assumption='Every other remaining unit held at its explicit remaining_pair and clipped A_share; counted totals fixed')
def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['live','targets']);p.add_argument('input');args=p.parse_args()
 with open(args.input)as f:s=json.load(f)
 result=live(s)if args.mode=='live'else targets(s['rows'],s.get('target_margin',0))
 print(json.dumps(result,indent=2,allow_nan=False))
if __name__=='__main__':main()
