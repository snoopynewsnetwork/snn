#!/usr/bin/env python3
"""Offline deterministic arithmetic. No probabilities or live source adapter.

python3 calculator.py --live synthetic-inputs.json
python3 calculator.py --selected nh-2024-pres:33015:Salem --others-share-shift-pp 0
"""
import argparse,json,math,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def clip(q):return min(1.0,max(0.0,q))
def finite(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
def status_q(q):return 'already_secured_at_all_B' if q<0 else 'impossible_at_all_A' if q>1 else 'feasible_boundary_tie_at_all_A' if q==1 else 'feasible'
def uniform(weights,shares,margin=0):
    if len(weights)!=len(shares) or any(not finite(t) or t<0 for t in weights):return dict(status='invalid_weights')
    T=sum(weights)
    if T<=0:return dict(status='no_positive_pool',total_pair_votes=T,unbounded_shift_share_pp=None,bounded_shift_share_pp=None)
    if any(t>0 and (q is None or not finite(q) or not 0<=q<=1) for t,q in zip(weights,shares)):return dict(status='unknown_preference_for_positive_pool')
    if not finite(margin):return dict(status='invalid_margin')
    M=sum(t*(2*q-1) for t,q in zip(weights,shares) if t>0)
    target=margin*T;delta=(target-M)/(2*T)
    out=dict(total_pair_votes=T,baseline_net_votes=M,baseline_pair_margin_pp=100*M/T,target_net_votes=target,target_pair_margin_pp=100*margin,unbounded_shift_share_pp=100*delta,baseline_meets_target=M>=target,positive_improvement_share_pp=max(0,100*delta))
    if abs(target)>T:
        return dict(out,status='impossible_bounded_target',bounded_shift_share_pp=None)
    def net(d):return sum(t*(2*clip(q+d)-1) for t,q in zip(weights,shares) if t>0)
    lo=-1.;hi=1.
    for _ in range(100):
        mid=(lo+hi)/2
        if net(mid)<target:lo=mid
        else:hi=mid
    bounded=(lo+hi)/2;qs=[clip(q+bounded) if t>0 else None for t,q in zip(weights,shares)]
    nets=[t*(2*q-1) if t>0 else 0. for t,q in zip(weights,qs)]
    out.update(status='solved',bounded_shift_share_pp=100*bounded,target_shares=qs,target_contributions=nets,achieved_net_votes=sum(nets),clipped_units=sum(t>0 and not 0<=q+delta<=1 for t,q in zip(weights,shares)),unbounded_would_clip=any(t>0 and not 0<=q+delta<=1 for t,q in zip(weights,shares)))
    return out

def selected(weights,shares,index,margin=0,others_shift_pp=0):
    if not 0<=index<len(weights):return dict(status='unknown_selected_unit')
    T=sum(weights);t=weights[index]
    if any(w>0 and (s is None or not finite(s)) for w,s in zip(weights,shares)):return dict(status='unknown_preference')
    fixed=sum(w*(2*clip(s+others_shift_pp/100)-1) for i,(w,s) in enumerate(zip(weights,shares)) if i!=index and w>0)
    target=margin*T
    if t<=0:return dict(status='no_positive_pool',required_share_unbounded=None,other_fixed_net_votes=fixed,target_net_votes=target,meets_target_without_selected=fixed>=target)
    q=(t+target-fixed)/(2*t)
    return dict(status=status_q(q),required_share_unbounded=q,required_share_clipped=clip(q),required_change_share_pp=100*(q-shares[index]),other_fixed_net_votes=fixed,others_shift_share_pp=others_shift_pp,others_shares_clipped=True,target_net_votes=target,selected_pair_votes=t,all_pair_votes=T)

def remainder(doc):
    """Hold counted votes fixed; each pool states total, pair participation,
    A pair preference, and optional named allocation of nonpair votes.
    None total is unknown. A preference is explicitly clipped; invalid volumes
    and participation are rejected. No anonymous other bucket becomes a D vote.
    """
    counted=doc.get('counted',{});A=counted.get('A');B=counted.get('B');others=counted.get('others',{})
    base=dict(label=doc.get('label'),counted_fixed=counted,calibrated_probability=None)
    if not isinstance(others,dict) or any(not finite(v) or v<0 for v in [A,B]+list(others.values())):return dict(base,status='invalid_counted_votes')
    pools=doc.get('remaining',[])
    keys=[r.get('key') for r in pools if r.get('key') is not None]
    if len(set(keys))!=len(keys):return dict(base,status='invalid_duplicate_remaining_unit_key')
    if any(r.get('total_candidate_votes') is None for r in pools):return dict(base,status='unknown_remaining_pool',final_candidate_denominator=None)
    if any(not finite(r.get('total_candidate_votes')) or r['total_candidate_votes']<0 for r in pools):return dict(base,status='invalid_negative_or_nonfinite_pool')
    U=0.;O=0.;forecast=[];future_other={k:0. for k in others};unknown_other=False
    for r in pools:
        n=r['total_candidate_votes'];p=r.get('pair_fraction');q=r.get('A_pair_share')
        if not finite(p) or not 0<=p<=1:return dict(base,status='invalid_pair_participation')
        if n*p>0 and not finite(q):return dict(base,status='unknown_remaining_preference')
        used=clip(q) if finite(q) else None;u=n*p;o=n-u;allocation=r.get('other_allocation',{})
        if o>0:
            if not allocation:unknown_other=True
            elif any(not finite(v) or v<0 for v in allocation.values()) or not math.isclose(sum(allocation.values()),1.,abs_tol=1e-12):return dict(base,status='invalid_other_allocation')
            else:
                for k,v in allocation.items():future_other[k]=future_other.get(k,0.)+o*v
        forecast.append(dict(key=r.get('key'),total_candidate_votes=n,pair_votes=u,other_votes=o,requested_A_pair_share=q,used_A_pair_share=used,share_was_clipped=finite(q) and q!=used,A_votes=u*used if u else 0.,B_votes=u*(1-used) if u else 0.))
        U+=u;O+=o
    L=A-B;counted_pair=A+B;C0=A+B+sum(others.values());C=C0+U+O;T=counted_pair+U
    fa=A+sum(r['A_votes'] for r in forecast);fb=B+sum(r['B_votes'] for r in forecast);fo={k:others.get(k,0)+future_other.get(k,0) for k in set(others)|set(future_other)}
    target_mode=doc.get('target_mode','pair_margin');g=doc.get('target_fraction',0.)
    if target_mode not in ['pair_margin','all_candidate_margin'] or not finite(g):return dict(base,status='invalid_target')
    goal=g*(T if target_mode=='pair_margin' else C)
    required=(U+goal-L)/(2*U) if U>0 else None
    qstatus=status_q(required) if U>0 else ('no_positive_pair_pool_target_met' if L>=goal else 'no_positive_pair_pool_target_impossible')
    legal='unresolved_named_other_allocation' if unknown_other else ('A_leads_every_named_opponent' if fa>max([fb]+list(fo.values())) else 'A_tied_or_behind_a_named_opponent')
    out=dict(base,status='calculated',remaining_forecast=forecast,remaining_pair_votes=U,remaining_other_votes=O,final_pair_denominator=T,final_candidate_denominator=C,final_A=fa,final_B=fb,final_named_others=fo,final_A_minus_B_net_votes=fa-fb,final_pair_margin_pp=100*(fa-fb)/T if T else None,final_all_candidate_margin_pp=100*(fa-fb)/C if C else None,target_mode=target_mode,target_fraction=g,target_net_votes=goal,required_remaining_A_pair_share_unbounded=required,required_remaining_A_pair_share_clipped=clip(required) if required is not None else None,requirement_status=qstatus,conditional_plurality_status=legal,unknown_other_allocation=unknown_other)
    if doc.get('selected_key') is not None:
        rs=[r for r in forecast if r['key']==doc['selected_key']]
        if len(rs)!=1:out['selected_requirement']=dict(status='selected_key_missing_or_duplicate')
        else:
            r=rs[0];u=r['pair_votes'];fixed=L+sum(x['A_votes']-x['B_votes'] for x in forecast if x is not r)
            if u<=0:sel=dict(status='no_positive_pool',required_share_unbounded=None,other_fixed_net_votes=fixed)
            else:
                q=(u+goal-fixed)/(2*u);sel=dict(status=status_q(q),required_share_unbounded=q,required_share_clipped=clip(q),other_fixed_net_votes=fixed,selected_pair_votes=u)
            out['selected_requirement']=sel
    if not unknown_other and float(U).is_integer():
        # Strict integer plurality over B and each named other. Pair A+1 is a
        # separate illustrative target; it is never substituted for this rule.
        needed=max(math.floor((U-L)/2)+1,math.floor(max(list(fo.values())+[0])-A)+1,0)
        out['strict_plurality_minimum_integer_A_votes_from_remaining_pair']=needed
        out['strict_plurality_possible_under_pool']=needed<=U
    return out

def main():
    a=argparse.ArgumentParser();a.add_argument('--live',type=Path);a.add_argument('--selected');a.add_argument('--others-share-shift-pp',type=float,default=0);a.add_argument('--target-margin-pp',type=float,default=0);args=a.parse_args()
    if args.live:
        d=json.loads(args.live.read_text());out=[remainder(x) for x in d] if isinstance(d,list) else remainder(d)
    else:
        p=json.loads((HERE/'priority-set.json').read_text());ls=p['all_units'];weights=[(r['harris_walz'] or 0)+(r['trump_vance'] or 0) for r in ls];shares=[r['harris_walz']/t if t else None for r,t in zip(ls,weights)]
        if args.selected:
            idx=next((i for i,r in enumerate(ls) if r['geography_key']==args.selected),-1);out=selected(weights,shares,idx,args.target_margin_pp/100,args.others_share_shift_pp)
        else:out=uniform(weights,shares,args.target_margin_pp/100)
    print(json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False))
if __name__=='__main__':main()
