#!/usr/bin/env python3
"""Offline conditional arithmetic. JSON stdin/file -> strict JSON stdout.
No source downloads, implicit candidate coalitions, probabilities or calls.
"""
import argparse,json,math,sys
class Invalid(ValueError):pass
def require(test,message):
    if not test:raise Invalid(message)
def number(v,label,lo=0,hi=None):
    require(type(v) in (int,float) and math.isfinite(v),label+' must be finite numeric (not bool/null/text)')
    require(v>=lo and (hi is None or v<=hi),label+' outside permitted bounds')
    return v
def total(xs):
    try:v=math.fsum(xs)
    except (OverflowError,ValueError):raise Invalid('aggregate numeric overflow')
    require(math.isfinite(v),'aggregate numeric overflow');return v
def key(v,label):require(isinstance(v,str) and bool(v.strip()),label+' must be a nonblank string');return v
def fields(obj,allowed,label):require(isinstance(obj,dict),label+' must be an object');require(not(set(obj)-set(allowed)),label+' has unsupported fields')
def strict_pairs(pairs):
    d={}
    for k,v in pairs:
        require(k not in d,'duplicate object field: '+k);d[k]=v
    return d
def decode(text):
    def nonfinite(s):raise Invalid('nonfinite JSON token: '+s)
    return json.loads(text,object_pairs_hook=strict_pairs,parse_constant=nonfinite)
def clean_finite(obj):
    if isinstance(obj,float):require(math.isfinite(obj),'derived numeric overflow')
    elif isinstance(obj,dict):
        for x in obj.values():clean_finite(x)
    elif isinstance(obj,list):
        for x in obj:clean_finite(x)
def threshold(q):return 'secured' if q<0 else ('impossible' if q>1 else 'feasible')
def validate(data):
    fields(data,['mode','candidates','pair','units','target_pair_margin','selected_unit','assumptions','scope'],'input')
    require(data.get('mode') in ('historical','live'),'unsupported mode')
    target=number(data.get('target_pair_margin'),'target_pair_margin',-1,1)
    for x in ['assumptions','scope']:key(data.get(x),x)
    cs=data.get('candidates');require(isinstance(cs,list) and len(cs)>=2,'candidates must be a list of at least two identities')
    ids=[]
    for c in cs:
        fields(c,['id','name','party','scope'],'candidate')
        for k in ['id','name','party','scope']:key(c.get(k),'candidate '+k)
        require(c['scope'] in ('named','generic_write_in','unallocated_other'),'unsupported candidate scope');ids.append(c['id'])
    require(len(set(ids))==len(ids),'candidate identity collision')
    names=[c['name'] for c in cs];require(len(set(names))==len(names),'candidate names must be distinct')
    pair=data.get('pair');require(isinstance(pair,list) and len(pair)==2 and all(isinstance(i,str) for i in pair) and pair[0]!=pair[1] and all(i in ids for i in pair),'pair must name two distinct supplied candidate ids')
    ai,bi=[ids.index(i) for i in pair];others=[i for i in range(len(ids)) if i not in (ai,bi)]
    units=data.get('units');require(isinstance(units,list) and len(units)>0,'units must be a nonempty list')
    # Validate every identity and input before any arithmetic/unknown/no-pool branch.
    keys=[]
    for u in units:
        require(isinstance(u,dict),'unit must be an object');keys.append(key(u.get('key'),'unit key'))
    require(len(set(keys))==len(keys),'duplicate unit keys')
    selected=data.get('selected_unit')
    if selected is not None:key(selected,'selected_unit');require(selected in keys,'selected_unit does not exist')
    parsed=[]
    for u in units:
        allowed=['key','votes','volume'] if data['mode']=='historical' else ['key','counted','remaining','pair_participation','a_share','other_allocation']
        fields(u,allowed,'unit')
        vs=u.get('votes' if data['mode']=='historical' else 'counted');require(isinstance(vs,list) and len(vs)==len(ids),'vote vector must cover every candidate')
        for v in vs:number(v,'candidate count')
        vtotal=total(vs);pairtotal=total([vs[ai],vs[bi]])
        require(vtotal>=pairtotal,'all-candidate total smaller than pair counts')
        if data['mode']=='historical':
            volume=number(u.get('volume',vtotal),'historical volume')
            require(not(volume>0 and vtotal==0),'positive historical volume with undefined source participation')
            participation=pairtotal/vtotal if vtotal else 0
            q=vs[ai]/pairtotal if pairtotal else None
            other=total(vs[i] for i in others)
            allocation=[vs[i]/other for i in others] if other else [0 for i in others]
            counted=[0 for _ in ids];remaining=volume
        else:
            counted=vs;remaining=number(u.get('remaining'),'remaining')
            participation=number(u.get('pair_participation'),'pair_participation',0,1)
            q=u.get('a_share');require('a_share' in u,'a_share is required (null explicitly means unknown)')
            if q is not None:number(q,'a_share',0,1)
            allocation=u.get('other_allocation');require(isinstance(allocation,list) and len(allocation)==len(others),'other_allocation must cover supplied other identities')
            for v in allocation:number(v,'other allocation',0,1)
            s=total(allocation)
            if remaining*(1-participation)>0:require(abs(s-1)<=1e-12,'unbalanced supplied-other allocation')
            else:require(s==0 or abs(s-1)<=1e-12,'unbalanced supplied-other allocation')
        pool=remaining*participation;otherpool=remaining*(1-participation)
        clean_finite([pool,otherpool,volume if data['mode']=='historical' else 0])
        parsed.append({'key':u['key'],'counted':counted,'counted_full':total(counted),'remaining_full':remaining,'pair_pool':pool,'other_pool':otherpool,'a_share':q,'pair_participation':participation,'other_allocation':allocation,'source_votes':vs if data['mode']=='historical' else None})
    # Validate all aggregate/derived bounds before early returns.
    total([x['counted_full']+x['remaining_full'] for x in parsed]);total(x['pair_pool'] for x in parsed)
    return parsed,cs,ai,bi,others,target,selected
def solve(data):
    units,cs,ai,bi,others,target,selected=validate(data)
    counted=[total(u['counted'][i] for u in units) for i in range(len(cs))]
    fixed=total([counted[ai],-counted[bi]]);pool=total(u['pair_pool'] for u in units)
    pairden=total([counted[ai],counted[bi],pool]);fullden=total(u['counted_full']+u['remaining_full'] for u in units)
    targetnet=target*pairden;clean_finite([fixed,targetnet])
    clean_finite([2*pool,2*pairden])
    unknown=[u['key'] for u in units if u['pair_pool']>0 and u['a_share'] is None]
    answer={'status':'ok','mode':data['mode'],'scope':data['scope'],'assumptions':data['assumptions'],'pair':[cs[ai],cs[bi]],'target_pair_margin_fraction':target,'final_pair_denominator':pairden,'final_full_candidate_denominator':fullden,'target_pair_net_votes':targetnet,'same_net_full_candidate_margin_fraction':targetnet/fullden if fullden else None,'counted_candidates_fixed':[{'candidate':cs[i],'votes':v} for i,v in enumerate(counted)],'remaining_full_pool':total(u['remaining_full'] for u in units),'remaining_pair_pool':pool,'unknown_positive_pair_pool_keys':unknown,'units':units,'legal_outcome_declared':False,'probability':None}
    if pool:
        raw=(targetnet-fixed+pool)/(2*pool)
        answer['all_remaining_required_a_share']={'raw':raw,'status':threshold(raw),'pool':'remaining pair votes only','target':'final pair margin'}
    else:answer['all_remaining_required_a_share']={'raw':None,'status':'no-positive-pool','fixed_target_status':'secured' if fixed>targetnet else ('tie-at-target' if fixed==targetnet else 'impossible')}
    if selected is not None:
        s=next(u for u in units if u['key']==selected);unknown_other=[k for k in unknown if k!=selected]
        if unknown_other:sr={'status':'unknown','raw':None,'unknown_other_keys':unknown_other}
        else:
            om=total(u['pair_pool']*(2*u['a_share']-1) for u in units if u['key']!=selected and u['pair_pool'])
            if s['pair_pool']:
                raw=(targetnet-fixed-om+s['pair_pool'])/(2*s['pair_pool']);sr={'status':threshold(raw),'raw':raw}
            else:sr={'status':'no-positive-pool','raw':None,'fixed_target_status':'secured' if fixed+om>targetnet else ('tie-at-target' if fixed+om==targetnet else 'impossible')}
        answer['selected_only']={'key':selected,**sr,'others_assumption':'every other supplied unit held at its explicit counted/remaining/pair_participation/a_share/other allocation'}
    if unknown:
        answer['common_shift']={'status':'unknown','unbounded_share_shift':None,'bounded_share_shift':None}
        answer['projected_candidates']=None
    else:
        base=total([fixed]+[u['pair_pool']*(2*u['a_share']-1) for u in units if u['pair_pool']])
        answer['baseline_pair_net_votes']=base;answer['baseline_pair_margin_fraction']=base/pairden if pairden else None
        if not pool:shift={'status':'no-positive-pool','unbounded_share_shift':None,'bounded_share_shift':None}
        else:
            raw=(targetnet-base)/(2*pool)
            def net(d):return total([fixed]+[u['pair_pool']*(2*max(0,min(1,u['a_share']+d))-1) for u in units if u['pair_pool']])
            lo,hi=-1.0,1.0;minnet,maxnet=net(lo),net(hi)
            if targetnet<minnet or targetnet>maxnet:shift={'status':'secured' if targetnet<minnet else 'impossible','unbounded_share_shift':raw,'bounded_share_shift':None,'minimum_net':minnet,'maximum_net':maxnet}
            else:
                for _ in range(90):
                    mid=(lo+hi)/2
                    if net(mid)<targetnet:lo=mid
                    else:hi=mid
                delta=(lo+hi)/2;shift={'status':'feasible','unbounded_share_shift':raw,'bounded_share_shift':delta,'clipping_applied':any(u['a_share'] is not None and not 0<=u['a_share']+raw<=1 for u in units if u['pair_pool']),'residual_net_votes':net(delta)-targetnet,'baseline_already_ahead_of_target':base>targetnet}
        answer['common_shift']=shift
        projected=counted[:]
        for u in units:
            if u['pair_pool']:
                projected[ai]+=u['pair_pool']*u['a_share'];projected[bi]+=u['pair_pool']*(1-u['a_share'])
            for i,alloc in zip(others,u['other_allocation']):projected[i]+=u['other_pool']*alloc
        answer['projected_candidates']=[{'candidate':c,'votes':v,'full_candidate_share':v/fullden if fullden else None} for c,v in zip(cs,projected)]
        named_other=[projected[i] for i,c in enumerate(cs) if i!=ai and c['scope']=='named']
        answer['a_net_over_highest_other_named']=projected[ai]-max(named_other) if named_other else None
        answer['unallocated_choices_preclude_full_legal_claim']=any(c['scope']!='named' for c in cs)
        d=shift.get('bounded_share_shift')
        if d is not None:
            target_candidates=counted[:]
            for u in units:
                if u['pair_pool']:
                    q=max(0,min(1,u['a_share']+d));target_candidates[ai]+=u['pair_pool']*q;target_candidates[bi]+=u['pair_pool']*(1-q)
                for i,alloc in zip(others,u['other_allocation']):target_candidates[i]+=u['other_pool']*alloc
            answer['target_candidates']=[{'candidate':c,'votes':v,'full_candidate_share':v/fullden if fullden else None} for c,v in zip(cs,target_candidates)]
            answer['target_a_net_over_highest_other_named']=target_candidates[ai]-max(target_candidates[i] for i,c in enumerate(cs) if i!=ai and c['scope']=='named')
        for u in units:
            v=u['pair_pool'];q=u['a_share'];u['remaining_pair_weight']=v/pool if pool else None;u['final_pair_weight']=v/pairden if pairden else None
            u['baseline_remaining_pair_net']=v*(2*q-1) if v and q is not None else (0 if v==0 else None)
            u['one_share_point_net_gain']=.02*v
            u['target_a_share']=max(0,min(1,q+d)) if q is not None and d is not None else None
            u['target_remaining_pair_net']=v*(2*u['target_a_share']-1) if u['target_a_share'] is not None else (0 if v==0 else None)
            u['net_gain_to_target']=u['target_remaining_pair_net']-u['baseline_remaining_pair_net'] if u['target_remaining_pair_net'] is not None and u['baseline_remaining_pair_net'] is not None else None
            # Every selected-only threshold, with every other unit at baseline.
            if v and q is not None:
                raw=(targetnet-(base-u['baseline_remaining_pair_net'])+v)/(2*v);u['selected_only_required_a_share_raw']=raw;u['selected_only_status']=threshold(raw)
            else:u['selected_only_required_a_share_raw']=None;u['selected_only_status']='no-positive-pool'
    clean_finite(answer);return answer
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('input',nargs='?',default='-');args=parser.parse_args()
    try:
        source=sys.stdin.read() if args.input=='-' else open(args.input).read()
        result=solve(decode(source));print(json.dumps(result,allow_nan=False,separators=(',',':')))
    except (Invalid,json.JSONDecodeError,OverflowError,ZeroDivisionError,TypeError,KeyError) as e:
        print(json.dumps({'status':'invalid-input','error':str(e)},allow_nan=False,separators=(',',':')));return 2
    return 0
if __name__=='__main__':sys.exit(main())
