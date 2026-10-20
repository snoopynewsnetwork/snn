"""Offline deterministic historical or counted-plus-remainder pair scenarios.

Input/output contract: source/SCHEMA.md. CLI JSON errors are expected results.
"""
import json,math,sys
class Invalid(ValueError):pass
def number(x,name,lo=None,hi=None):
    if type(x) not in (int,float):raise Invalid(name+' must be a finite number, not bool/null/text')
    try: finite=math.isfinite(x)
    except OverflowError:finite=False
    if not finite or (lo is not None and x<lo) or (hi is not None and x>hi):raise Invalid(name+' outside finite supported bounds')
    return x
def total(xs,name):
    try:x=math.fsum(xs)
    except (OverflowError,ValueError):raise Invalid(name+' numeric overflow')
    return number(x,name)
def identity(s):
    if type(s)!=str or not s.strip():raise Invalid('identities and unit keys must be nonblank strings')
    return s
def clip(x):return min(1,max(0,x))
def validate(d):
    if type(d)!=dict:raise Invalid('input must be an object')
    if d.get('mode') not in ('historical','live'):raise Invalid('unsupported mode')
    g=number(d.get('target_pair_margin'),'target_pair_margin fraction',-1,1)
    if type(d.get('pair'))!=list or len(d['pair'])!=2:raise Invalid('pair must name two candidates')
    if type(d.get('other_candidates'))!=list:raise Invalid('other_candidates must be a list')
    names=[identity(x) for x in d['pair']+d['other_candidates']]
    if len(names)!=len(set(names)):raise Invalid('candidate identity collision')
    if d.get('candidate_universe') not in ('supplied','full'):raise Invalid('candidate_universe must be supplied or full')
    if type(d.get('unallocated_generic'))!=bool:raise Invalid('unallocated_generic must be boolean')
    if type(d.get('assumptions'))!=str or not d['assumptions'].strip():raise Invalid('assumptions label required')
    units=d.get('units')
    if type(units)!=list or not units:raise Invalid('nonempty units array required')
    keys=[]
    # Every key is validated globally before any unknown/zero-pool branch.
    for u in units:
        if type(u)!=dict:raise Invalid('unit must be an object')
        keys.append(identity(u.get('key')))
    if len(keys)!=len(set(keys)):raise Invalid('duplicate unit key')
    if 'selected_unit' in d:
        identity(d['selected_unit'])
        if d['selected_unit'] not in keys:raise Invalid('selected_unit absent')
    prepared=[]
    for u in units:
        k=u['key'];volume=number(u.get('volume' if d['mode']=='historical' else 'remaining'),k+' volume',0)
        p=number(u.get('pair_participation'),k+' pair_participation',0,1)
        q=u.get('share')
        if q is not None:number(q,k+' share',0,1)
        allocations=u.get('other_allocations')
        if type(allocations)!=dict or set(allocations)!=set(d['other_candidates']):raise Invalid(k+' other allocation identities mismatch')
        for n,v in allocations.items():number(v,k+' allocation '+n,0,1)
        allocsum=total(allocations.values(),k+' allocation sum')
        other=number(volume*(1-p),k+' other volume',0)
        if allocations and abs(allocsum-1)>1e-12:raise Invalid(k+' other allocations must sum to one')
        if other>0 and not allocations:raise Invalid(k+' positive other pool requires allocation')
        if d['mode']=='live':
            c=u.get('counted')
            if type(c)!=dict or set(c)!=set(names):raise Invalid(k+' counted candidate identities mismatch')
            for n,v in c.items():number(v,k+' counted '+n,0)
            supplied=number(u.get('counted_all_candidate_total'),k+' counted_all_candidate_total',0)
            countsum=total(c.values(),k+' counted sum')
            if supplied!=countsum:raise Invalid(k+' counted all-candidate total does not balance full supplied field')
        else:c={n:0 for n in names};countsum=0
        pool=number(volume*p,k+' pair pool',0)
        number(countsum+volume,k+' final all-candidate denominator',0)
        prepared.append(dict(key=k,counted=c,counted_all=countsum,volume=volume,pool=pool,share=q,participation=p,allocations=allocations))
    # Aggregate overflow validation also precedes unknown/no-positive-pool returns.
    for n in names:total([u['counted'][n] for u in prepared],'aggregate counted '+n)
    total([u['counted_all']+u['volume'] for u in prepared],'final all-candidate denominator')
    total([u['counted'][names[0]]+u['counted'][names[1]]+u['pool'] for u in prepared],'final pair denominator')
    return names,prepared,g
def requirement(raw):
    return {'raw_required_share':raw,'status':'secured' if raw<0 else 'impossible' if raw>1 else 'feasible','feasible_share':raw if 0<=raw<=1 else None}
def run(d):
    names,units,g=validate(d);A,B=names[:2];counted={n:total([u['counted'][n] for u in units],n) for n in names}
    cp=counted[A]+counted[B];L=counted[A]-counted[B];U=total([u['pool'] for u in units],'remaining pair');T=cp+U;F=total([u['counted_all']+u['volume'] for u in units],'final all');unknown=[u['key'] for u in units if u['pool']>0 and u['share'] is None]
    out=dict(status='ok',mode=d['mode'],pair=d['pair'],assumptions=d['assumptions'],candidate_universe=d['candidate_universe'],unallocated_generic=d['unallocated_generic'],counted_fixed=counted,counted_pair_denominator=cp,counted_all_candidate_denominator=sum(counted.values()),remaining_all_candidate_pool=total([u['volume'] for u in units],'remaining all'),remaining_pair_pool=U,final_pair_denominator=T,final_all_candidate_denominator=F,target_pair_margin=g,target_pair_net=g*T,target_all_candidate_margin=None if F==0 else g*T/F,unknown_positive_pair_preferences=unknown)
    target=g*T
    out['aggregate_remaining_requirement']=requirement((U+target-L)/(2*U)) if U>0 else dict(status='no-positive-pool',fixed_target_status='above' if L>target else 'equal' if L==target else 'below',raw_required_share=None)
    def net(delta=0):return L+total([u['pool']*(2*clip(u['share']+delta)-1) for u in units if u['pool']>0],'modeled net')
    base=None if unknown else net()
    out['baseline_pair_net']=base;out['baseline_pair_margin']=None if T==0 or base is None else base/T
    if T==0:out['uniform']={'status':'no-positive-pair-denominator','unbounded_share_shift':None,'bounded_share_shift':None}
    elif unknown:out['uniform']={'status':'unknown-preference','unbounded_share_shift':None,'bounded_share_shift':None}
    elif U==0:out['uniform']={'status':'no-positive-pool','fixed_target_status':'above' if base>target else 'equal' if base==target else 'below','unbounded_share_shift':None,'bounded_share_shift':None}
    else:
        delta=(target-base)/(2*U);low=L-U;high=L+U
        if target<low:uniform={'status':'secured','unbounded_share_shift':delta,'bounded_share_shift':None}
        elif target>high:uniform={'status':'impossible','unbounded_share_shift':delta,'bounded_share_shift':None}
        else:
            # Monotone common additive shift; all endpoints explicitly clipped.
            l,r=-1.0,1.0
            for _ in range(90):
                mid=(l+r)/2
                if net(mid)<target:l=mid
                else:r=mid
            root=(l+r)/2;unclipped=all(0<=u['share']+delta<=1 for u in units if u['pool']>0)
            uniform={'status':'feasible','unbounded_share_shift':delta,'unbounded_all_shares_feasible':unclipped,'bounded_share_shift':root,'bounded_net':net(root),'residual_net':net(root)-target,'endpoint_clipped_units':[u['key'] for u in units if u['pool']>0 and (u['share']+root<0 or u['share']+root>1)]}
        out['uniform']=uniform
    known_remaining_net=total([v['pool']*(2*v['share']-1) for v in units if v['pool']>0 and v['share'] is not None],'known remaining net')
    for u in units:
        q=u['share'];pool=u['pool'];u['pair_weight']=None if T==0 else pool/T;u['all_candidate_weight']=None if F==0 else u['volume']/F;u['gain_net_for_one_share_pp']=0.02*pool;u['baseline_remaining_net']=None if pool>0 and q is None else 0 if pool==0 else pool*(2*q-1)
        if pool==0:u['selected_only']={'status':'no-positive-pool','raw_required_share':None,'fixed_target_status':'unknown-other-preference' if unknown else 'above' if base>target else 'equal' if base==target else 'below'}
        elif len(unknown)-(1 if pool>0 and q is None else 0)>0:u['selected_only']={'status':'unknown-other-preference','raw_required_share':None}
        else:
            others=L+known_remaining_net-(pool*(2*q-1) if q is not None else 0)
            u['selected_only']=requirement((pool+target-others)/(2*pool))
        shift=out['uniform'].get('bounded_share_shift');u['bounded_target_share']=None if pool==0 or q is None or shift is None else clip(q+shift);u['bounded_remaining_net']=None if u['bounded_target_share'] is None else pool*(2*u['bounded_target_share']-1)
    out['units']=units
    if 'selected_unit' in d:out['selected_unit_requirement']=next(u['selected_only'] for u in units if u['key']==d['selected_unit'])
    if unknown:out['projected_candidates']=None;out['plurality']={'status':'unknown-preference'}
    else:
        final=counted.copy()
        for u in units:
            if u['pool']>0:final[A]+=u['pool']*u['share'];final[B]+=u['pool']*(1-u['share'])
            for n,f in u['allocations'].items():final[n]+=u['volume']*(1-u['participation'])*f
        for n,v in final.items():number(v,'projected '+n,0)
        out['projected_candidates']=final;leaders=[n for n,v in final.items() if v==max(final.values())];out['plurality']={'status':'conditional-full-field' if d['candidate_universe']=='full' and not d['unallocated_generic'] else 'supplied-universe-only','leaders':leaders,'pair_A_leads':final[A]>final[B],'A_leads_every_supplied_other':all(final[A]>v for n,v in final.items() if n!=A),'legal_declaration':False}
    return out
def pairs(items):
    d={}
    for k,v in items:
        if k in d:raise Invalid('duplicate JSON object field: '+k)
        d[k]=v
    return d
def constant(x):raise Invalid('nonfinite JSON token: '+x)
def main():
    try:
        raw=open(sys.argv[1]).read() if len(sys.argv)==2 else sys.stdin.read()
        d=json.loads(raw,object_pairs_hook=pairs,parse_constant=constant);result=run(d)
        # Serialization guards all derived overflow, including values absent from early summaries.
        result=json.dumps(result,allow_nan=False,separators=(',',':'));print(result);return 0
    except (Invalid,ValueError,OverflowError,TypeError,KeyError) as e:
        print(json.dumps({'status':'invalid-input','error':str(e)},allow_nan=False));return 2
if __name__=='__main__':sys.exit(main())
