"""Offline historical conditional arithmetic. No 2026 turnout/probability model."""
from extract import *
import argparse, math
def clip(x):return min(1.,max(0.,x))
def solve(weights,shares,target_margin):
    if any(w<0 for w in weights):return dict(status='negative_pool_invalid')
    T=sum(weights)
    if not T:return dict(status='no_positive_pool',pair_pool=T)
    if any(s is None and w>0 for w,s in zip(weights,shares)):return dict(status='unknown_preference',pair_pool=T)
    if not -1<=target_margin<=1:return dict(status='impossible_target_margin',pair_pool=T)
    shares=[s if s is not None else 0 for s in shares]
    net=sum(w*(2*s-1) for w,s in zip(weights,shares));target=target_margin*T
    delta=(target-net)/(2*T);lo,hi=-1.,1.
    for _ in range(80):
        mid=(lo+hi)/2
        if sum(w*(2*clip(s+mid)-1) for w,s in zip(weights,shares))<target:lo=mid
        else:hi=mid
    bounded=(lo+hi)/2
    return dict(status='bounded_clipping_solved' if any(w>0 and not 0<=s+delta<=1 for w,s in zip(weights,shares)) else 'unbounded_feasible',
                pair_pool=T,baseline_net=net,target_net=target,unbounded_shift_pp=100*delta,bounded_shift_pp=100*bounded,
                already_at_or_above_target=net>=target,achieved_net=sum(w*(2*clip(s+bounded)-1) for w,s in zip(weights,shares)),
                clipped_units=sum(w>0 and not 0<=s+bounded<=1 for w,s in zip(weights,shares)))
def conditional(w,own_net,net,total,target_margin):
    if w<=0:return dict(selected_required_share=None,selected_status='no_positive_pool',selected_unbounded_shift_pp=None)
    q=(w+target_margin*total-(net-own_net))/(2*w)
    return dict(selected_required_share=q,selected_status='already_secured' if q<0 else ('impossible' if q>1 else 'feasible_threshold'),selected_unbounded_shift_pp=100*(q-(own_net/w+1)/2))
def readnative():
    ns=list(csv.DictReader(gzip.open(BASE/'native-units.csv.gz','rt')))
    for r in ns:
        for k in ['A','B','other','pair_votes','candidate_votes']:r[k]=int(r[k])
        r['A_pair_share']=float(r['A_pair_share']) if r['A_pair_share'] else None
    return ns
def unitrow(r,w,s,O,sol,target,scenario,pref,volume):
    T=sol['pair_pool'];net=sol['baseline_net'];own=w*(2*s-1) if s is not None else 0
    shift=sol['bounded_shift_pp']/100;un=sol['unbounded_shift_pp']/100
    q=clip(s+shift) if s is not None else None;qa=s+un if s is not None else None
    return dict(scenario=scenario,preference_anchor=pref,volume_basis=volume,target='tie' if target==0 else 'A+1_pair_margin',target_pair_margin_pp=target*100,
                geography_key=r['geography_key'],county=r['county'],name=r['name'],native_type=r['native_type'],county_fips=r['county_fips'],
                A_name=r['A_name'],B_name=r['B_name'],historical_A=r['A'],historical_B=r['B'],historical_other=r['other'],
                pair_pool=w,other_pool=O,all_candidate_pool=w+O,pair_participation=w/(w+O) if w+O else None,weight=w/T,
                baseline_A_pair_share=s,baseline_net=own,baseline_margin_contribution_pp=100*own/T,
                other_units_fixed_net=net-own,other_units_share_shift_pp=0,
                local_tie_share=.5 if w else None,local_Aplus1_share=.505 if w else None,
                local_tie_shift_pp=100*(.5-s) if w and s is not None else None,local_Aplus1_shift_pp=100*(.505-s) if w and s is not None else None,
                unbounded_shift_pp=sol['unbounded_shift_pp'],unbounded_target_share=qa,bounded_shift_pp=sol['bounded_shift_pp'],bounded_target_share=q,
                clipped=qa is not None and not 0<=qa<=1,solver_status=sol['status'],
                target_net=w*(2*q-1) if q is not None else 0,target_all_margin_pp=100*w*(2*q-1)/(w+O) if w+O and q is not None else None,
                net_gain=w*2*(q-s) if s is not None else 0,share_pp1_unbounded_net_gain=.02*w,share_pp1_clipped_net_gain=2*w*(clip(s+.01)-s) if s is not None else 0,
                max_positive_net_gain=2*w*(1-s) if s is not None else 0,
                **conditional(w,own,net,T,target))
def main():
    ns=readnative();county={lab:{r['county']:r for r in ns if r['contest_label']==lab and r['native_type']=='County'} for lab in LABELS}
    sensitivity=[];states=[];targets=[];native_targets=[];allcushions=[]
    mixes=LABELS+['low_historical_county_min','high_historical_county_max']
    for pref in LABELS:
        for mix in mixes:
            rs=list(county[pref].values());vol=[]
            for r in rs:
                choices=[county[x][r['county']] for x in LABELS]
                v=county[mix][r['county']] if mix in LABELS else (min(choices,key=lambda x:x['pair_votes']) if mix.startswith('low') else max(choices,key=lambda x:x['pair_votes']))
                vol.append(v)
            W=[v['pair_votes'] for v in vol];S=[r['A_pair_share'] for r in rs];O=[v['other'] for v in vol]
            sid=pref+'__'+mix;T=sum(W);N=T+sum(O)
            for target in [0,.01]:
                sol=solve(W,S,target)
                A=sum(w*clip(s+sol['bounded_shift_pp']/100) for w,s in zip(W,S));B=T-A
                states.append(dict(scenario=sid,preference_anchor=pref,volume_basis=mix,target='tie' if target==0 else 'A+1_pair_margin',all_candidate_pool=N,other_pool=sum(O),A=A,B=B,
                    achieved_pair_margin_pp=100*(A-B)/T,achieved_all_margin_pp=100*(A-B)/N,conservative_other_total_cushion=A-sum(O),**sol))
                for r,v,w,s,o in zip(rs,vol,W,S,O):
                    rr=unitrow(r,w,s,o,sol,target,sid,pref,mix);rr['volume_source_contest']=v['contest_label'];targets.append(rr)
            sensitivity.append(dict(scenario=sid,preference_anchor=pref,volume_basis=mix,pair_pool=T,other_pool=sum(O),all_candidate_pool=N,baseline_net=sum(w*(2*s-1) for w,s in zip(W,S)),source='direct observed county pair pools; envelopes choose minimum/maximum across four historical contests, no scaling'))
            acsol=solve(W,S,.01*N/T)
            allcushions.append(dict(scenario=sid,preference_anchor=pref,volume_basis=mix,all_candidate_pool=N,other_pool=sum(O),target_all_candidate_margin_pp=1,equivalent_pair_margin_pp=N/T,**acsol))
    # Every finer unit retains its own contest preferences/pools; never join years.
    for lab in LABELS:
        rs=[r for r in ns if r['contest_label']==lab and r['native_type']=='Precinct'];W=[r['pair_votes'] for r in rs];S=[r['A_pair_share'] for r in rs]
        for target in [0,.01]:
            sol=solve(W,S,target)
            for r,w,s in zip(rs,W,S):native_targets.append(unitrow(r,w,s,r['other'],sol,target,lab+'__native',lab,lab))
    rows(BASE/'county-targets.csv.gz',targets);rows(BASE/'native-targets.csv.gz',native_targets);rows(BASE/'state-scenarios.csv',states);rows(BASE/'sensitivity-settings.csv',sensitivity)
    rows(BASE/'all-candidate-cushions.csv',allcushions)
    # Local slice thresholds do not turn overlapping methods/hierarchies into independent state vectors.
    slices=[]
    for r in csv.DictReader(gzip.open(BASE/'method-baselines.csv.gz','rt')):
        a=int(r['A']) if r['A'] else None;b=int(r['B']) if r['B'] else None;w=a+b if a is not None and b is not None else None
        slices.append(dict(contest_label=r['contest_label'],geography_key=r['geography_key'],native_type=r['native_type'],method_id=r['method_id'],method_name=r['method_name'],A=a,B=b,pair_votes=w,
            combined_pair_weight=r['combined_pair_weight'],share_pp1_unbounded_net_gain=.02*w if w is not None else None,
            local_tie_A_share=.5 if w else None,local_Aplus1_share=.505 if w else None,local_tie_shift_pp=100*(.5-a/w) if w else None,local_Aplus1_shift_pp=100*(.505-a/w) if w else None,
            status='no_positive_pool' if w==0 else ('unknown_pool' if w is None else 'local conditional slice only'),state_use=r['method_scope_status']))
    rows(BASE/'method-local-targets.csv.gz',slices)
    # Synthetic solver edge evidence is separate from historical data.
    dump(BASE/'bounded-synthetic.json',[dict(name=n,weights=w,shares=s,target=t,result=solve(w,s,t)) for n,w,s,t in [
        ('clipping_requires_resolve',[1,9],[.99,.1],0),('already_winning',[3,2],[.8,.6],0),('zero_pool',[0],[None],0),
        ('negative_pool',[-1],[.5],0),('unknown',[1],[None],0),('impossible_target',[1],[.5],1.1)]])
    print(compact(dict(county_target_rows=len(targets),native_target_rows=len(native_targets),state_scenarios=len(states),method_local_rows=len(slices))))
if __name__=='__main__':main()
