"""Offline deterministic arithmetic. No network, collector, probabilities or 2026 prior.
Usage: python -B calculate.py scenario.json
All target margins are fractions, so 0.01 is A+1 pair-margin point.
"""
import json,math,sys

def number(x,name,lo=None,hi=None):
    if type(x) not in (int,float) or not math.isfinite(x):raise ValueError(name+' must be finite numeric (not bool/null/text)')
    if lo is not None and x<lo or hi is not None and x>hi:raise ValueError(name+' outside supported range')
    return float(x)
def string(x,name):
    if not isinstance(x,str) or not x.strip():raise ValueError(name+' must be a nonempty string')
    return x
def obj(x,name):
    if not isinstance(x,dict):raise ValueError(name+' must be an object')
    return x
def counts(x,name):
    obj(x,name)
    return {string(k,name+' candidate'):number(v,name+' votes',0) for k,v in x.items()}
def share(x,name):return None if x is None else number(x,name,0,1)
def clip(x):return min(1.0,max(0.0,x))
def validate(data):
    obj(data,'scenario');mode=data.get('mode')
    if mode not in ['historical','live']:raise ValueError('unsupported mode')
    pair=obj(data.get('pair'),'pair');a=string(pair.get('A'),'pair.A');b=string(pair.get('B'),'pair.B')
    if a==b:raise ValueError('pair identities must differ')
    complete=data.get('candidate_universe_complete',False)
    if type(complete) is not bool:raise ValueError('candidate_universe_complete must be bool')
    margin=number(data.get('target_margin',0),'target_margin',-1,1)
    units=data.get('units')
    if not isinstance(units,list) or not units:raise ValueError('units must be a nonempty array')
    keys=[];out=[]
    # All rows validated before unknown/preference/no-pool arithmetic branches.
    for r in units:
        obj(r,'unit');key=string(r.get('key'),'unit key')
        if key in keys:raise ValueError('duplicate unit key')
        keys.append(key)
        if mode=='historical':
            t=number(r.get('pair_volume'),'pair_volume',0);f=number(r.get('all_volume'),'all_volume',0)
            if t>f:raise ValueError('pair_volume exceeds all_volume')
            q=share(r.get('a_share'),'a_share');other=counts(r.get('others',{}),'others')
            un=number(r.get('unallocated_other',0),'unallocated_other',0)
            if any(k in [a,b,'A','B'] for k in other):raise ValueError('others collide with pair identity')
            if not math.isclose(sum(other.values())+un,f-t,abs_tol=1e-7,rel_tol=1e-10):raise ValueError('other counts do not balance all_volume minus pair_volume')
            out.append(dict(key=key,t=t,f=f,q=q,other=other,un=un))
        else:
            c=obj(r.get('counted'),'counted');ca=number(c.get('A'),'counted.A',0);cb=number(c.get('B'),'counted.B',0)
            co=counts(c.get('others',{}),'counted.others');cu=number(c.get('unallocated_other',0),'counted.unallocated_other',0)
            remain=number(r.get('remaining'),'remaining',0);p=number(r.get('pair_participation'),'pair_participation',0,1)
            q=share(r.get('a_share'),'a_share');os=counts(r.get('other_shares',{}),'other_shares')
            us=number(r.get('unallocated_other_share',0),'unallocated_other_share',0,1)
            if any(v>1 for v in os.values()):raise ValueError('other share exceeds 1')
            if any(k in [a,b,'A','B'] for k in set(co)|set(os)):raise ValueError('others collide with pair identity')
            osum=sum(os.values())+us
            if osum>1+1e-12:raise ValueError('other shares exceed 1')
            if remain*(1-p)>0 and not math.isclose(osum,1,abs_tol=1e-12):raise ValueError('positive remaining other pool must be allocated or explicitly unallocated')
            out.append(dict(key=key,ca=ca,cb=cb,co=co,cu=cu,r=remain,p=p,q=q,os=os,us=us))
    selected=data.get('selected_unit')
    if selected is not None:
        string(selected,'selected_unit')
        if selected not in keys:raise ValueError('selected_unit absent')
    # Overflow can occur even when each individual input is finite.
    if mode=='historical':totals=[sum(r[v] for r in out) for v in ['t','f']]
    else:totals=[sum(r['ca']+r['cb']+sum(r['co'].values())+r['cu']+r['r'] for r in out),sum(r['ca']+r['cb']+r['r']*r['p'] for r in out)]
    if not all(math.isfinite(v) for v in totals):raise ValueError('final denominator overflow')
    if max(totals)<=0:raise ValueError('final all-candidate denominator must be positive')
    return mode,a,b,complete,margin,out,selected

def requirement(raw,pool,fixed,target):
    if pool==0:
        return {'raw_required_share':None,'feasible_share':None,'status':'no_positive_pool',
                'fixed_target_status':'secured' if fixed>=target else 'impossible','unbounded':False}
    status='secured' if raw<0 else 'impossible' if raw>1 else 'feasible'
    return {'raw_required_share':raw,'feasible_share':raw if 0<=raw<=1 else None,'status':status,'unbounded':raw<0 or raw>1}

def fullfield(a,b,others,unallocated,complete):
    values={'A':a,'B':b,**others};top=max(values.values());winners=[k for k,v in values.items() if math.isclose(v,top,abs_tol=1e-8,rel_tol=0)]
    return {'supplied_candidate_totals':values,'supplied_plurality_leaders':winners,
            'supplied_A_strict_plurality':a>max([b]+list(others.values())),
            'unallocated_other':unallocated,'candidate_universe_complete':complete,
            'full_field_result':'A_strict_plurality' if complete and unallocated==0 and a>max([b]+list(others.values())) else
                                'A_not_strict_plurality' if complete and unallocated==0 else 'unknown_full_field',
            'legal_declaration':False}

def historical(data):
    _,a,b,complete,m,rows,selected=validate(data)
    T=sum(r['t'] for r in rows);F=sum(r['f'] for r in rows)
    unknown=[r['key'] for r in rows if r['t']>0 and r['q'] is None]
    result=dict(mode='historical',pair={'A':a,'B':b},target_pair_margin=m,pair_denominator=T,all_candidate_denominator=F,
                pair_participation=T/F,unknown_positive_pair_preferences=unknown,calibrated_probability=None)
    if unknown:return dict(result,status='unknown_preference',uniform_share_shift=None,units=None)
    base=sum(r['t']*(2*r['q']-1) for r in rows if r['t']>0);goal=m*T
    if not math.isfinite(base):raise ValueError('margin overflow')
    result.update(baseline_net_votes=base,baseline_pair_margin=base/T if T else None,
                  target_net_votes=goal,baseline_target_status='already_at_or_above_target' if base>=goal else 'below_target')
    if T==0:
        other={};un=0
        for row in rows:
            for k,v in row['other'].items():other[k]=other.get(k,0)+v
            un+=row['un']
        return dict(result,status='no_positive_pool',uniform_share_shift=None,unbounded_share_shift=None,
            units=[dict(key=row['key'],pair_volume=0,all_volume=row['f'],baseline_a_share=row['q'],target_a_share=None,
                        pair_weight=None,all_candidate_weight=row['f']/F,selected_only=requirement(None,0,0,0)) for row in rows],
            fullfield=fullfield(0,0,other,un,complete))
    raw=(m-base/T)/2
    def net(delta):return sum(r['t']*(2*clip(r['q']+delta)-1) for r in rows if r['t']>0)
    if goal<net(-1)-1e-7 or goal>net(1)+1e-7:return dict(result,status='impossible',unbounded_share_shift=raw,uniform_share_shift=None)
    lo,hi=-1.0,1.0
    for _ in range(90):
        mid=(lo+hi)/2
        if net(mid)<goal:lo=mid
        else:hi=mid
    delta=(lo+hi)/2
    unitrows=[];afinal=0.;bfinal=0.;others={};un=0.
    for r in rows:
        t,q=r['t'],r['q'];s=clip(q+delta) if q is not None else None
        own=t*(2*q-1) if t and q is not None else 0
        rest=base-own
        raw_selected=(goal/t-rest/t+1)/2 if t else None
        req=requirement(raw_selected,t,rest,goal)
        netr=t*(2*s-1) if t and s is not None else 0
        ar=t*s if s is not None else 0;br=t-ar;afinal+=ar;bfinal+=br
        for k,v in r['other'].items():others[k]=others.get(k,0)+v
        un+=r['un']
        unitrows.append(dict(key=r['key'],pair_volume=t,all_volume=r['f'],pair_participation=t/r['f'] if r['f'] else None,
            pair_weight=t/T,all_candidate_weight=r['f']/F,baseline_a_share=q,baseline_net_votes=own,
            target_a_share=s,target_pair_margin=(2*s-1) if s is not None else None,target_net_votes=netr,
            a_share_shift=(s-q) if s is not None else None,net_vote_gain=netr-own,plus1_share_point_net_vote_gain=0.02*t,
            clipped=(q is not None and (q+delta<0 or q+delta>1)),
            selected_only=dict(req,other_units_assumption='All other rows held at the supplied baseline preferences and volumes',other_units_net_votes=rest)))
    result.update(status='solved',uniform_share_shift=delta,unbounded_share_shift=raw,
        uniform_share_shift_points=100*delta,unbounded_share_shift_points=100*raw,
        final_net_votes=afinal-bfinal,final_pair_margin=(afinal-bfinal)/T,
        final_all_candidate_margin=(afinal-bfinal)/F,all_candidate_cushion_votes=goal,
        clipped_keys=[r['key'] for r in unitrows if r['clipped']],units=unitrows,
        fullfield=fullfield(afinal,bfinal,others,un,complete))
    if selected is not None:result['selected_unit']=next(r for r in unitrows if r['key']==selected)
    return result

def live(data):
    _,a,b,complete,m,rows,selected=validate(data)
    ca=sum(r['ca'] for r in rows);cb=sum(r['cb'] for r in rows);L=ca-cb
    U=sum(r['r']*r['p'] for r in rows);P=ca+cb+U;F=sum(r['ca']+r['cb']+sum(r['co'].values())+r['cu']+r['r'] for r in rows)
    goal=m*P;required=(goal/U-L/U+1)/2 if U else None
    unknown=[r['key'] for r in rows if r['r']*r['p']>0 and r['q'] is None]
    co={};un=0.;fixed=[]
    for r in rows:
        for k in set(r['co'])|set(r['os']):co[k]=co.get(k,0)+r['co'].get(k,0)+r['r']*(1-r['p'])*r['os'].get(k,0)
        un+=r['cu']+r['r']*(1-r['p'])*r['us']
        fixed.append({'key':r['key'],'counted_A':r['ca'],'counted_B':r['cb'],'counted_others':r['co'],
                      'counted_unallocated_other':r['cu'],'remaining_all':r['r'],'remaining_pair':r['r']*r['p'],
                      'pair_participation':r['p'],'a_share':r['q'],'remaining_other_shares':r['os'],
                      'remaining_unallocated_other_share':r['us']})
    result={'mode':'live','pair':{'A':a,'B':b},'counted_A':ca,'counted_B':cb,'counted_pair_lead':L,
            'remaining_pair_pool':U,'final_pair_denominator':P,'final_all_candidate_denominator':F,
            'target_pair_margin':m,'target_net_votes':goal,'counted_fixed_units':fixed,
            'pooled_tie_or_margin_requirement':requirement(required,U,L,goal),
            'possible_final_net_votes':[L-U,L+U],'unknown_positive_pair_preferences':unknown,
            'calibrated_probability':None,'is_synthetic_arithmetic':data.get('is_synthetic_arithmetic',False)}
    if selected is not None:
        chosen=next(r for r in rows if r['key']==selected);uc=chosen['r']*chosen['p']
        other_unknown=[r['key'] for r in rows if r['key']!=selected and r['r']*r['p']>0 and r['q'] is None]
        if other_unknown:result['selected_only']={'status':'unknown_other_unit_preference','unknown_keys':other_unknown}
        else:
            rest=L+sum(r['r']*r['p']*(2*r['q']-1) for r in rows if r['key']!=selected and r['r']*r['p']>0)
            req=(goal/uc-rest/uc+1)/2 if uc else None
            result['selected_only']=dict(requirement(req,uc,rest,goal),key=selected,other_units_net_votes=rest,
                other_units_assumption='Counted votes fixed; all other remaining pair votes use the supplied shares')
    if unknown:result.update(status='unknown_preference',forecast_A=None,forecast_B=None,forecast_pair_margin=None,fullfield=None)
    else:
        fa=ca+sum(r['r']*r['p']*r['q'] for r in rows if r['r']*r['p']>0);fb=cb+U-(fa-ca)
        result.update(status='no_positive_pool' if U==0 else 'calculated',forecast_A=fa,forecast_B=fb,
            forecast_net_votes=fa-fb,forecast_pair_margin=(fa-fb)/P if P else None,
            forecast_all_candidate_margin=(fa-fb)/F,fullfield=fullfield(fa,fb,co,un,complete))
    return result

def calculate(data):return historical(data) if data.get('mode')=='historical' else live(data)
def reject_constant(s):raise ValueError('non-JSON numeric constant '+s)
def pairs_hook(pairs):
    out={}
    for k,v in pairs:
        if k in out:raise ValueError('duplicate JSON object key '+k)
        out[k]=v
    return out
def main():
    try:
        if len(sys.argv)!=2:raise ValueError('Usage: calculate.py input.json')
        with open(sys.argv[1]) as f:data=json.load(f,parse_constant=reject_constant,object_pairs_hook=pairs_hook)
        obj(data,'scenario');result=calculate(data)
        print(json.dumps(result,indent=2,allow_nan=False))
    except (ValueError,TypeError,KeyError,OverflowError,ZeroDivisionError) as e:
        print(json.dumps({'status':'invalid_input','error':str(e)},allow_nan=False));raise SystemExit(2)
if __name__=='__main__':main()
