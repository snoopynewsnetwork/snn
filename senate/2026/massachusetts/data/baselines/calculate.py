#!/usr/bin/env python3
"""Offline conditional arithmetic. No probabilities or inferred remaining pools.

CLI: python calculate.py historical|live input.json
Shares and target margins are fractions; outputs label pp explicitly.
"""
import argparse,gzip,json,math,sys

def number(x,label,lo=0,hi=None):
    if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x):raise ValueError(label+' must be a finite number')
    if x<lo or (hi is not None and x>hi):raise ValueError(label+' outside allowed range')
    return x
def keys(xs,label):
    if not isinstance(xs,list) or not xs or any(not isinstance(x,str) or not x.strip() for x in xs) or len(set(xs))!=len(xs):raise ValueError(label+' requires nonempty unique string keys')
def keyed_units(units):
    if not isinstance(units,list) or not units or any(not isinstance(x,dict) for x in units):raise ValueError('units must be a nonempty list of objects')
    keys([u.get('key') for u in units],'global source-unit keys')
def clip(x):return max(0.,min(1.,x))
def requirement(raw,pool,achieved_without=None):
    if pool==0:return dict(raw_share=None,clipped_share=None,status='no_positive_pool',fixed_net=achieved_without)
    return dict(raw_share=raw,clipped_share=clip(raw),status='already_secured' if raw<0 else 'impossible' if raw>1 else 'feasible')
def historical(units,target_margin=0,selected_key=None):
    keyed_units(units);number(target_margin,'target_margin',-1,1)
    for u in units:
        number(u.get('T'),'T');number(u.get('share'),'share',0,1)
        number(u.get('other_votes',0),'other_votes')
    if selected_key is not None and (not isinstance(selected_key,str) or selected_key not in [u['key'] for u in units]):raise ValueError('unknown selected_key')
    T=sum(u['T'] for u in units);M=sum(u['T']*(2*u['share']-1) for u in units)
    if T==0:return dict(status='no_positive_pool',pair_total=0,baseline_net_votes=0,unbounded_share_shift=None,bounded_share_shift=None,units=[dict(u,weight=None) for u in units])
    wanted=target_margin*T;delta=(wanted-M)/(2*T)
    def net(d):return sum(u['T']*(2*clip(u['share']+d)-1) for u in units)
    lo,hi=-1.,1.
    for _ in range(90):
        mid=(lo+hi)/2
        if net(mid)<wanted:lo=mid
        else:hi=mid
    shift=(lo+hi)/2;out=[]
    for u in units:
        s=clip(u['share']+shift);other_net=M-u['T']*(2*u['share']-1)
        req=(wanted-other_net+u['T'])/(2*u['T']) if u['T'] else None
        out.append(dict(u,weight=u['T']/T,unbounded_target_share=u['share']+delta,target_share=s,target_pair_margin=2*s-1,target_net_votes=u['T']*(2*s-1),gain_net_votes=2*u['T']*(s-u['share']),gain_net_per_A_share_pp=.02*u['T'],clipped=s!=u['share']+shift,selected_unit_only=requirement(req,u['T'],other_net),other_units_fixed_net=other_net))
    return dict(status='solved',pair_total=T,reported_final_denominator=T+sum(u.get('other_votes',0) for u in units),baseline_net_votes=M,baseline_pair_margin=M/T,already_winning_baseline=M>0,target_pair_margin=target_margin,target_net_votes=wanted,unbounded_share_shift=delta,unbounded_share_shift_pp=100*delta,bounded_share_shift=shift,bounded_share_shift_pp=100*shift,positive_improvement_needed_pp=max(0,100*shift),achieved_net_votes=net(shift),clipped_units=sum(u['clipped'] for u in out),units=out,selected=next((u for u in out if u['key']==selected_key),None))
def live(config):
    if not isinstance(config,dict):raise ValueError('input must be object')
    candidates=config.get('candidates');keys(candidates,'candidate field')
    A=config.get('A');B=config.get('B')
    if A not in candidates or B not in candidates or A==B:raise ValueError('A and B must be distinct supplied candidates')
    units=config.get('units');keyed_units(units)
    target=config.get('target_margin',0);number(target,'target_margin',-1,1)
    selected=config.get('selected_key')
    if selected is not None and (not isinstance(selected,str) or selected not in [u['key'] for u in units]):raise ValueError('unknown selected_key')
    counted={c:0 for c in candidates};expected={c:0 for c in candidates};unknown=[];pools=[]
    for u in units:
        cv=u.get('counted');alloc=u.get('allocation');p=u.get('remaining_pool')
        if not isinstance(cv,dict) or set(cv)!=set(candidates):raise ValueError('counted requires complete candidate field')
        if not isinstance(alloc,dict) or set(alloc)!=set(candidates):raise ValueError('allocation requires complete candidate field')
        for c in candidates:number(cv[c],'counted '+c);number(alloc[c],'allocation '+c,0,1)
        if not math.isclose(sum(alloc.values()),1,abs_tol=1e-12,rel_tol=0):raise ValueError('allocation must sum to one')
        if not isinstance(p,dict) or p.get('status') not in ['known','unknown']:raise ValueError('explicit known/unknown remaining_pool required')
        if p['status']=='known':
            if set(p)!={'status','votes'}:raise ValueError('known remaining_pool needs votes only')
            number(p['votes'],'remaining pool');v=p['votes']
        else:
            if set(p)!={'status'}:raise ValueError('unknown pool cannot contain numeric guesses')
            unknown.append(u['key']);v=None
        for c in candidates:
            counted[c]+=cv[c]
            if v is not None:expected[c]+=v*alloc[c]
        pools.append(dict(key=u['key'],votes=v,allocation=alloc))
    if unknown:return dict(status='unknown_remaining_pool',unknown_units=unknown,counted=counted,counted_denominator=sum(counted.values()),final=None,final_denominator=None,pair_requirement=None)
    final={c:counted[c]+expected[c] for c in candidates};F=sum(final.values());Cpair=counted[A]+counted[B];L=counted[A]-counted[B]
    U=sum(p['votes']*(p['allocation'][A]+p['allocation'][B]) for p in pools)
    active=[p for p in pools if selected is None or p['key']==selected]
    R=sum(p['votes']*(p['allocation'][A]+p['allocation'][B]) for p in active)
    fixedNet=sum(p['votes']*(p['allocation'][A]-p['allocation'][B]) for p in pools if p not in active)
    raw=(target*(Cpair+U)-L-fixedNet+R)/(2*R) if R else None
    req=requirement(raw,R,L+fixedNet)
    # Full-field A plurality requires strict inequality against EACH supplied rival.
    # Variable pool reallocates A/B only; all other candidate votes stay fixed.
    fixedA=counted[A]+sum(p['votes']*p['allocation'][A] for p in pools if p not in active)
    fixedB=counted[B]+sum(p['votes']*p['allocation'][B] for p in pools if p not in active)
    hurdles={B:(fixedB+R-fixedA)/(2*R)} if R else {}
    if R:
        for c in candidates:
            if c not in [A,B]:hurdles[c]=(final[c]-fixedA)/R
    plurality_threshold=max(hurdles.values()) if hurdles else None
    largest=max(final.values());leaders=[c for c in candidates if math.isclose(final[c],largest,rel_tol=0,abs_tol=1e-9)]
    return dict(status='known_scenario',counted=counted,counted_denominator=sum(counted.values()),remaining_candidate_pool=sum(p['votes'] for p in pools),remaining_pair_pool=U,variable_pair_pool=R,final=final,final_denominator=F,final_pair_denominator=Cpair+U,A_final_all_candidate_share=final[A]/F if F else None,A_minus_B_final_pair_margin=(final[A]-final[B])/(Cpair+U) if Cpair+U else None,A_minus_B_final_all_candidate_margin=(final[A]-final[B])/F if F else None,target_pair_margin=target,pair_requirement=req,full_field_A_strict_plurality_share_threshold=plurality_threshold,full_field_rival_thresholds=hurdles,full_field_status='no_votes' if F==0 else 'tie_unresolved' if len(leaders)>1 else 'unique_leader',leaders=leaders if F else [],qualification='Arithmetic conditional on supplied complete candidate field and remaining candidate-vote pool; no blanks, eligibility, lower preferences or probabilities inferred. A pair target does not establish full-field plurality; ties unresolved.')
def strict_json(text):
    def pairs(xs):
        d={}
        for k,v in xs:
            if k in d:raise ValueError('duplicate JSON key: '+k)
            d[k]=v
        return d
    return json.loads(text,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('nonfinite JSON number')),object_pairs_hook=pairs)
def checked(fn):
    def wrapped(*args,**kwargs):
        try:
            result=fn(*args,**kwargs)
            def finite(x):
                if isinstance(x,float) and not math.isfinite(x):raise ValueError('arithmetic exceeds finite numeric range')
                if isinstance(x,dict):
                    for v in x.values():finite(v)
                if isinstance(x,list):
                    for v in x:finite(v)
            finite(result);return result
        except (OverflowError,ZeroDivisionError) as e:raise ValueError('arithmetic exceeds finite numeric range') from e
    return wrapped
historical=checked(historical)
live=checked(live)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['historical','live']);ap.add_argument('input');a=ap.parse_args()
    try:
        with (gzip.open(a.input,'rt') if a.input.endswith('.gz') else open(a.input)) as f:x=strict_json(f.read())
        if not isinstance(x,dict):raise ValueError('input must be object')
        out=live(x) if a.mode=='live' else historical(x.get('units'),x.get('target_margin',0),x.get('selected_key'))
        print(json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False))
    except (ValueError,TypeError,KeyError,OverflowError,OSError) as e:
        print(json.dumps({'status':'invalid_input','error':str(e)},allow_nan=False));return 2
    return 0
if __name__=='__main__':sys.exit(main())
