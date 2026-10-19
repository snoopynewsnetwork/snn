"""Offline bounded pair targets and fixed-counted, named-candidate remainder arithmetic.

Expectations may be fractional. No probability model or implicit remaining pool.
"""
import argparse,csv,json,math
from sources import *
def clip(x):return max(0.0,min(1.0,x))
def status(q):
    return 'already_above_target_at_zero_share' if q<0 else 'impossible' if q>1 else 'feasible'
def bounded_shift(weights,shares,target):
    total=sum(weights)
    if total<=0:return dict(status='no_positive_pool',unbounded_shift=None,bounded_shift=None)
    if abs(target)>total+1e-8:return dict(status='impossible',unbounded_shift=None,bounded_shift=None)
    base=sum(w*(2*s-1) for w,s in zip(weights,shares));raw=(target-base)/(2*total)
    lo,hi=-1.,1.
    for _ in range(100):
        mid=(lo+hi)/2;m=sum(w*(2*clip(s+mid)-1) for w,s in zip(weights,shares))
        if m<target:lo=mid
        else:hi=mid
    shift=(lo+hi)/2;values=[clip(s+shift) for s in shares]
    return dict(status='feasible_bounded',baseline_net=base,target_net=target,unbounded_shift=raw,bounded_shift=shift,
                unbounded_feasible=all(0<=s+raw<=1 for s in shares),clipped_units=sum(s+shift<0 or s+shift>1 for s in shares),shares=values,
                achieved_net=sum(w*(2*s-1) for w,s in zip(weights,values)),baseline_already_above_target=base>target)
def selected(weights,shares,index,target):
    w=weights[index];fixed=sum(t*(2*s-1) for j,(t,s) in enumerate(zip(weights,shares)) if j!=index)
    if w<=0:return dict(status='no_positive_pool',required_share=None,fixed_other_net=fixed)
    q=(w+target-fixed)/(2*w)
    return dict(status=status(q),required_share=q,clipped_display_share=clip(q),fixed_other_net=fixed)
def live(case):
    counted=case['counted'];remain=case.get('remaining');a=case['A'];b=case['B']
    if any(v is None or not isinstance(v,(int,float)) or not math.isfinite(v) or v<0 for v in counted.values()):return dict(status='invalid_negative_or_unknown_counted')
    if remain is None:return dict(status='unknown_remaining_pool',counted_fixed=counted)
    final=dict(counted);unknown=False;clipped=[];all_pool=0
    for u in remain:
        pool=u.get('pool');mix=u.get('shares')
        if pool is None or mix is None:unknown=True;continue
        if pool<0 or not math.isfinite(pool):return dict(status='invalid_negative_pool',unit=u.get('unit'))
        if any(v is None for v in mix.values()):unknown=True;continue
        if any(not isinstance(v,(int,float)) or not math.isfinite(v) for v in mix.values()):return dict(status='invalid_nonfinite_forecast_share',unit=u.get('unit'))
        # Explicit clip then normalize only forecast preference inputs, never votes.
        m={k:clip(v) for k,v in mix.items()}
        if m!=mix:clipped.append(u.get('unit'))
        if abs(sum(m.values())-1)>1e-9:return dict(status='invalid_forecast_share_sum_after_clipping',unit=u.get('unit'),clipped_shares=m)
        all_pool+=pool
        for k,q in m.items():final[k]=final.get(k,0)+pool*q
    if unknown:return dict(status='unknown_remaining_pool_or_mix',counted_fixed=counted)
    denom=sum(final.values());pair=final.get(a,0)+final.get(b,0);net=final.get(a,0)-final.get(b,0)
    named_rivals={k:v for k,v in final.items() if k!=a}
    # generic_other is a conservative unresolved pool, never a named Democratic candidate.
    winner=max(final,key=final.get) if final else None;maximum=max(final.values()) if final else 0
    tied=[k for k,v in final.items() if v==maximum]
    unit_targets=[]
    for u in remain:
        U=u['pool']*(clip(u['shares'].get(a,0))+clip(u['shares'].get(b,0)))
        ua=u['pool']*clip(u['shares'].get(a,0));ub=u['pool']*clip(u['shares'].get(b,0))
        fixedA=final.get(a,0)-ua;fixedB=final.get(b,0)-ub
        fixed_net=fixedA-fixedB
        if U<=0:unit_targets.append(dict(unit=u.get('unit'),status='no_positive_pair_pool'));continue
        tie=(U-fixed_net)/(2*U);cushion=(U+.01*pair-fixed_net)/(2*U)
        rival_thresholds={k:(v-fixedA)/U for k,v in final.items() if k not in [a,b]}
        plurality=max([tie]+list(rival_thresholds.values()))
        unit_targets.append(dict(unit=u.get('unit'),remaining_pair_pool=U,fixed_A_elsewhere=fixedA,fixed_B_elsewhere=fixedB,
           all_other_remaining_assumption='input forecast shares unchanged; counted candidates fixed',pair_tie_required_A_share=tie,pair_tie_status=status(tie),
           A_plus_1_final_pair_margin_required_A_share=cushion,A_plus_1_status=status(cushion),
           strict_plurality_requires_share_greater_than=plurality,plurality_status='impossible_strict' if plurality>=1 else 'secured_at_zero' if plurality<0 else 'feasible_strict',other_rival_share_thresholds=rival_thresholds))
    return dict(status='no_pool_final' if all_pool==0 else 'conditional_arithmetic',outcome_scope='Conditional on supplied candidate universe; unresolved valid write-ins not inferred absent',counted_fixed=counted,remaining_pool=all_pool,final_votes=final,
       final_all_candidate_denominator=denom,final_pair_denominator=pair,A_minus_B_votes=net,A_minus_B_pair_margin_pp=100*net/pair if pair else None,
       A_minus_B_all_candidate_margin_pp=100*net/denom if denom else None,plurality_leader=winner if len(tied)==1 else None,tied_leaders=tied,
       A_strict_plurality=final.get(a,0)>0 and all(final.get(a,0)>v for v in named_rivals.values()),A_cushion_vs_each_rival={k:final.get(a,0)-v for k,v in named_rivals.items()},clipped_forecast_units=clipped,selected_unit_targets=unit_targets)
def pair_remainder(counted_A,counted_B,pool,target_margin=0,final_pair_fixed=None):
    if pool is None:return dict(status='unknown_pool',required_share=None)
    if pool<0:return dict(status='invalid_negative_pool',required_share=None)
    lead=counted_A-counted_B
    final_den=final_pair_fixed if final_pair_fixed is not None else counted_A+counted_B+pool
    target=target_margin*final_den
    if pool==0:return dict(status='no_positive_pool',required_share=None,counted_lead=lead,target_net=target,secured=lead>target,impossible=lead<target,exact_tie=lead==target)
    q=(pool+target-lead)/(2*pool)
    return dict(status=status(q),required_share=q,clipped_display_share=clip(q),final_pair_denominator=final_den,target_net=target)
def historical():
    from build_counties import writecsv
    rows=list(csv.DictReader((BASE/'data/county-baselines.csv').open()));T=sum(float(r['2024-senate_pair_votes']) for r in rows)
    # EAC administrative counts are a separate vintage/universe, with eight 2024
    # counties below the signed named pair. Never treat their ratio as participation.
    mixes=[('base-2024-Senate', [float(r['2024-senate_pair_votes']) for r in rows], '2024 named Senate pair'),
       ('low-2022-EAC-counted-ballots', [float(r['eac_2022_F1a']) for r in rows], '2022 EAC F1a county volume; illustrative pair participation=1 in every county, not observed Senate participation; administrative sensitivity'),
       ('high-2020-Senate', [float(r['2020-senate_pair_votes']) for r in rows], '2020 actual named Senate pair volume'),
       ('midterm-2018-special-pair', [float(r['2018-special_pair_votes']) for r in rows], '2018 November6 actual Espy/Hyde-Smith pair only; Bartee and McDaniel remain separate named candidates'),
       ('midterm-2018-runoff-pair', [float(r['2018-runoff_pair_votes']) for r in rows], '2018 November27 actual Espy/Hyde-Smith runoff pair; separate electorate')]
    anchors=['2024-senate','2024-president','2020-senate','2018-special','2018-runoff'];out=[];states=[]
    for anchor in anchors:
        shares=[float(r[anchor+'_A_pair_share']) for r in rows]
        # A separate conditional denominator holds the anchor's actual named
        # outsiders fixed. This is not a 2026 third-candidate or ballot forecast.
        outsiders=[float(r[anchor+'_other']) for r in rows]
        for mix,volumes,description in mixes:
            # Additional normalized mix isolates composition from common statewide scaling.
            variants=[(mix,volumes,description)]
            if not mix.startswith('base'):variants.append((mix+'-normalized-to-2024-pair',[v*T/sum(volumes) for v in volumes],description+'; normalize statewide pair volume to 2024'))
            for scenario,w,desc in variants:
                for margin in [0,.01]:
                    target=margin*sum(w);sol=bounded_shift(w,shares,target)
                    states.append(dict(scenario=scenario,preference_anchor=anchor,target_pair_margin_pp=margin*100,volume_basis=desc,pair_votes=sum(w),historical_named_other_votes_held_fixed=sum(outsiders),conditional_named_all_candidate_denominator=sum(w)+sum(outsiders),conditional_A_minus_B_all_candidate_margin_pp=100*target/(sum(w)+sum(outsiders)),generic_write_in_pool='unresolved_not_inferred_zero',**{k:v for k,v in sol.items() if k!='shares'}))
                    for i,r in enumerate(rows):
                        sel=selected(w,shares,i,target);q=sol['shares'][i]
                        out.append(dict(scenario=scenario,preference_anchor=anchor,target_pair_margin_pp=margin*100,county=r['county'],fips=r['fips'],expected_pair_votes=w[i],historical_named_other_votes_held_fixed=outsiders[i],conditional_named_all_candidate_denominator=w[i]+outsiders[i],conditional_pair_participation=w[i]/(w[i]+outsiders[i]),conditional_A_minus_B_all_candidate_margin_pp=100*w[i]*(2*q-1)/(w[i]+outsiders[i]),state_pair_weight=w[i]/sum(w),baseline_A_share=shares[i],baseline_net=w[i]*(2*shares[i]-1),target_A_share=q,target_margin_pp=100*(2*q-1),target_net=w[i]*(2*q-1),net_gain=w[i]*2*(q-shares[i]),net_gain_for_one_share_pp=.02*w[i],unbounded_shift_share_pp=100*sol['unbounded_shift'],bounded_shift_share_pp=100*sol['bounded_shift'],selected_only_required_A_share=sel['required_share'],selected_only_status=sel['status'],all_other_units_assumption='unchanged named anchor shares under this same scenario pair volume; historical named outsiders fixed, generic marks unresolved',fixed_other_net=sel['fixed_other_net']))
    writecsv(OUT/'county-targets.csv',out);writecsv(OUT/'state-targets.csv',states)
    # Meaningful arithmetic fixtures, including every path required by the assignment.
    cases=[dict(id='unknown',A='Colom',B='Hyde-Smith',counted={'Colom':100,'Hyde-Smith':120,'Pinkins':15},remaining=None),
      dict(id='no-pool',A='Colom',B='Hyde-Smith',counted={'Colom':100,'Hyde-Smith':120,'Pinkins':15},remaining=[]),
      dict(id='empty-counted-no-pool',A='Colom',B='Hyde-Smith',counted={'Colom':0,'Hyde-Smith':0,'Pinkins':0},remaining=[]),
      dict(id='negative-pool',A='Colom',B='Hyde-Smith',counted={'Colom':100,'Hyde-Smith':120,'Pinkins':15},remaining=[dict(unit='synthetic',pool=-1,shares={'Colom':.5,'Hyde-Smith':.4,'Pinkins':.1})]),
      dict(id='third-candidate-leads-despite-pair-win',A='Colom',B='Hyde-Smith',counted={'Colom':100,'Hyde-Smith':80,'Pinkins':200},remaining=[dict(unit='synthetic',pool=100,shares={'Colom':.6,'Hyde-Smith':.3,'Pinkins':.1})]),
      dict(id='clipped-preferences',A='Colom',B='Hyde-Smith',counted={'Colom':100,'Hyde-Smith':120,'Pinkins':15},remaining=[dict(unit='synthetic',pool=10,shares={'Colom':1.2,'Hyde-Smith':-.2,'Pinkins':0})])]
    cases.append(dict(id='Independent-Pinkins-named-pair',A='Pinkins',B='Hyde-Smith',counted={'Colom':100,'Hyde-Smith':120,'Pinkins':15},remaining=[dict(unit='synthetic',pool=300,shares={'Colom':.1,'Hyde-Smith':.2,'Pinkins':.7})]))
    paircases=[dict(id=n,counted_A=a,counted_B=b,pool=u,target_margin=m) for n,a,b,u,m in [('secured',200,10,20,0),('impossible',10,200,20,0),('tie-threshold',100,120,100,0),('final-denominator-A+1',100,120,100,.01),('no-pool',100,120,0,0),('negative',100,120,-1,0),('unknown',100,120,None,0)]]
    save(OUT/'synthetic-scenarios.json',dict(qualification='Synthetic conditional arithmetic, no calibrated probabilities or 2026 turnout assumptions',live=[dict(input=c,output=live(c)) for c in cases],pair=[dict(input=c,output=pair_remainder(**{k:v for k,v in c.items() if k!='id'})) for c in paircases],bounded=[dict(input=dict(weights=[10,90],shares=[.99,.1],target=1),output=bounded_shift([10,90],[.99,.1],1)),dict(input=dict(weights=[0],shares=[.3],target=0),output=bounded_shift([0],[.3],0)),dict(input=dict(weights=[10],shares=[.3],target=11),output=bounded_shift([10],[.3],11))]))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--live-json');p.add_argument('--county');p.add_argument('--others-shift-pp',type=float,default=0);p.add_argument('--target-pair-margin-pp',type=float,default=0);args=p.parse_args()
    if args.live_json:print(json.dumps(live(json.loads(Path(args.live_json).read_text())),indent=2))
    elif args.county:
        r=list(csv.DictReader((BASE/'data/county-baselines.csv').open()));w=[float(x['2024-senate_pair_votes']) for x in r];s=[clip(float(x['2024-senate_A_pair_share'])+args.others_shift_pp/100) for x in r];i=next(i for i,x in enumerate(r) if x['county']==args.county);answer=selected(w,s,i,args.target_pair_margin_pp*sum(w)/100);answer.update(county=args.county,volume_basis='2024 named Senate pair, all 82 counties',state_pair_votes=sum(w),selected_pair_votes=w[i],others_share_shift_pp=args.others_shift_pp,target_pair_margin_pp=args.target_pair_margin_pp,other_share_clipping='explicit clip to [0,1] before fixed-other net');print(json.dumps(answer,indent=2))
    else:historical()
