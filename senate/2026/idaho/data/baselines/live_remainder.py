#!/usr/bin/env python3
"""Conditional arithmetic on a supplied remaining valid-candidate pool. No collector."""
import argparse,json,math
from calculate import clip,threshold,D,save
def evaluate(case):
 counted=case.get('counted',{});A=case.get('A','A');B=case.get('B','B');result=dict(id=case.get('id'),A=A,B=B,counted_fixed=dict(counted),probability=None,qualification='Synthetic conditional arithmetic, not a calibrated probability or measured outstanding pool')
 if A==B or A not in counted or B not in counted:return dict(result,status='invalid_candidate_mapping')
 if any(not isinstance(v,(int,float))or not math.isfinite(v)or v<0 for v in counted.values()):return dict(result,status='invalid_negative_or_nonfinite_counted_votes')
 units=case.get('remaining_units',[])
 if any(u.get('valid_candidate_pool')is None for u in units):return dict(result,status='unknown_remaining_pool',projected_final=None)
 if any(not isinstance(u['valid_candidate_pool'],(int,float))or not math.isfinite(u['valid_candidate_pool'])or u['valid_candidate_pool']<0 for u in units):return dict(result,status='invalid_negative_or_nonfinite_pool',projected_final=None)
 rem=[];errors=[]
 for u in units:
  U=u['valid_candidate_pool'];p=u.get('pair_fraction');q=u.get('A_share_of_pair');other=u.get('other_allocation',{})
  if U==0:rem.append(dict(id=u['id'],pool=0,pair_pool=0,q=None,raw_q=q,clipped=False,other={}));continue
  if p is None or q is None:return dict(result,status='unknown_remaining_preference_or_pair_fraction')
  if not all(isinstance(x,(int,float))and math.isfinite(x)for x in [p,q])or not 0<=p<=1:return dict(result,status='invalid_pair_fraction_or_preference')
  if any(n in [A,B]or n not in counted or not isinstance(v,(int,float))or not math.isfinite(v)or v<0 for n,v in other.items())or(U*(1-p)>0 and abs(sum(other.values())-1)>1e-9):return dict(result,status='invalid_other_candidate_allocation')
  rem.append(dict(id=u['id'],pool=U,pair_pool=U*p,q=clip(q),raw_q=q,clipped=q!=clip(q),other={n:U*(1-p)*s for n,s in other.items()}))
 if len({r['id']for r in rem})!=len(rem):return dict(result,status='invalid_duplicate_remaining_unit')
 totalU=sum(r['pool']for r in rem);pairU=sum(r['pair_pool']for r in rem);final=dict(counted)
 for r in rem:
  if r['pair_pool']:final[A]+=r['pair_pool']*r['q'];final[B]+=r['pair_pool']*(1-r['q'])
  for n,v in r['other'].items():final[n]+=v
 V=sum(counted.values())+totalU;T=counted[A]+counted[B]+pairU;lead=final[A]-final[B];maxvote=max(final.values())if final else 0;winners=[n for n,v in final.items()if abs(v-maxvote)<1e-9]
 result.update(status='no_positive_pair_pool'if pairU==0 else'conditional_arithmetic',remaining_assumptions=rem,remaining_valid_candidate_pool=totalU,remaining_pair_pool=pairU,final_all_candidate_denominator=V,final_pair_denominator=T,projected_final=final,projected_A_minus_B_net=lead,projected_pair_margin_pp=None if T==0 else 100*lead/T,projected_all_candidate_margin_pp=None if V==0 else 100*lead/V,full_field_plurality_leaders=winners,full_field_A_strict_plurality=final[A]>max(v for n,v in final.items()if n!=A),tie_resolution='Idaho state/federal tie determined by coin toss after canvass; arithmetic tie is not an elected winner')
 selected=case.get('selected_unit');rawtarget=case.get('target_margin_pp',0);denom=case.get('target_denominator','pair')
 if not isinstance(rawtarget,(int,float))or not math.isfinite(rawtarget):return dict(result,status='invalid_target_margin')
 target=rawtarget/100
 if denom not in ['pair','all_candidate']:return dict(result,status='invalid_target_denominator')
 if not isinstance(target,(int,float))or not math.isfinite(target):return dict(result,status='invalid_target_margin')
 targetnet=target*(T if denom=='pair'else V)
 if selected is None:chosen=rem;fixednet=counted[A]-counted[B];fixedA=counted[A]
 else:
  chosen=[r for r in rem if r['id']==selected]
  if len(chosen)!=1:return dict(result,status='invalid_selected_unit')
  other=[r for r in rem if r['id']!=selected];fixednet=counted[A]-counted[B]+sum(r['pair_pool']*(2*r['q']-1)for r in other if r['pair_pool']);fixedA=counted[A]+sum(r['pair_pool']*r['q']for r in other if r['pair_pool'])
 pool=sum(r['pair_pool']for r in chosen)
 if pool<=0:result['break_even']=dict(status='no_positive_pool',required_A_share=None,fixed_A_minus_B=fixednet,target_net=targetnet,target_denominator=denom,condition_met=fixednet>=targetnet);return result
 q=(pool+targetnet-fixednet)/(2*pool);anchor=sum(r['pair_pool']*r['q']for r in chosen if r['pair_pool'])/pool
 # Other candidates' full-field totals do not depend on q when pool/pair fraction fixed.
 otherreq={n:(v-fixedA)/pool for n,v in final.items()if n not in [A,B]};breq=(pool-fixednet)/(2*pool);legal=max([breq]+list(otherreq.values()))
 result['break_even']=dict(status=threshold(q,pool),required_A_share_unbounded=q,clipped_display_share=clip(q),required_share_pp=100*q,stated_remaining_A_share=anchor,required_change_from_stated_remaining_A_share_pp=100*(q-anchor),target_net=targetnet,target_denominator=denom,selected_unit=selected or'all_remaining_pair_units',fixed_other_assumption='all other remaining units at stated clipped shares; all counted candidate votes and other allocations fixed',fixed_A_minus_B=fixednet,legal_strict_plurality_requires_share_GREATER_THAN=legal,legal_status=threshold(legal,pool),other_candidate_thresholds=otherreq,legal_threshold_not_replaced_by_pair_margin=True)
 return result
def samples():
 def c(id,counts=None,pool=100,q=.5,p=.9,**kw):
  return dict(id=id,A='Todd Achilles',B='Jim Risch',counted=counts or{'Todd Achilles':40,'Jim Risch':60,'Natalie M Fleming':5,'Matt Loesby':5},remaining_units=[dict(id='synthetic_native_unit',valid_candidate_pool=pool,pair_fraction=p,A_share_of_pair=q,other_allocation={'Natalie M Fleming':.5,'Matt Loesby':.5})],**kw)
 cases=[c('unknown',pool=None),c('no-pool',pool=0),c('negative-pool',pool=-1),c('impossible',pool=10),c('secured',counts={'Todd Achilles':200,'Jim Risch':50,'Natalie M Fleming':5,'Matt Loesby':5},pool=10),c('preference-clipping-high',q=1.2),c('preference-clipping-low',q=-.2),c('pair-plus1',target_margin_pp=1),c('all-candidate-plus1',target_margin_pp=1,target_denominator='all_candidate'),c('no-pair-pool',p=0),c('other-candidate-wins',counts={'Todd Achilles':20,'Jim Risch':20,'Natalie M Fleming':500,'Matt Loesby':5},pool=10),c('already-winning-negative-tie-shift',counts={'Todd Achilles':75,'Jim Risch':25,'Natalie M Fleming':5,'Matt Loesby':5},pool=100),c('negative-counted',counts={'Todd Achilles':-1,'Jim Risch':25,'Natalie M Fleming':5,'Matt Loesby':5})]
 cases.append(dict(id='selected-unit-with-others-fixed',A='Todd Achilles',B='Jim Risch',counted={'Todd Achilles':40,'Jim Risch':60,'Natalie M Fleming':5,'Matt Loesby':5},remaining_units=[dict(id='selected',valid_candidate_pool=100,pair_fraction=.8,A_share_of_pair=.6,other_allocation={'Natalie M Fleming':.7,'Matt Loesby':.3}),dict(id='other',valid_candidate_pool=200,pair_fraction=.9,A_share_of_pair=.5,other_allocation={'Natalie M Fleming':.5,'Matt Loesby':.5})],selected_unit='selected',target_margin_pp=1))
 save('live-synthetic-inputs.json',cases);save('live-synthetic-results.json',[evaluate(c)for c in cases]);return cases
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',nargs='?');p.add_argument('--samples',action='store_true');a=p.parse_args()
 if a.samples:samples();return
 if not a.input:p.error('Supply a JSON case or use --samples')
 print(json.dumps(evaluate(json.loads(Path(a.input).read_text())),indent=2))
if __name__=='__main__':main()
