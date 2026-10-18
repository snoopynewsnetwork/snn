"""Offline historical conditional arithmetic. All shares are fractions internally."""
import argparse, csv, gzip, json, math
from pathlib import Path
from build import H, SPECS, csvout, jdump
ANCHORS=['president_2024','senate_2022','senate_2020']
def clip(x): return max(0.,min(1.,x))
def solve(shares,weights,margin):
    if len(shares)!=len(weights): return dict(status='invalid_length',shift=None)
    if any(not math.isfinite(x) for x in shares+weights+[margin]) or any(w<0 for w in weights): return dict(status='invalid',shift=None)
    if any(s<0 or s>1 for s in shares): return dict(status='invalid_share',shift=None)
    T=sum(weights)
    if T<=0: return dict(status='no_positive_pool',shift=None,unbounded_shift=None)
    M=sum(w*(2*s-1) for w,s in zip(weights,shares)); target=margin*T
    unbounded=(target-M)/(2*T)
    if abs(margin)>1: return dict(status='impossible',shift=None,unbounded_shift=unbounded)
    lo,hi=-1.,1.
    for _ in range(90):
        mid=(lo+hi)/2; val=sum(w*(2*clip(s+mid)-1) for w,s in zip(weights,shares))
        if val<target: lo=mid
        else: hi=mid
    d=(lo+hi)/2
    return dict(status='feasible',shift=d,unbounded_shift=unbounded,baseline_already_at_or_above_target=M>=target,baseline_net=M,target_net=target,total_pair=T,clipped_units=sum(w>0 and not 0<=s+d<=1 for s,w in zip(shares,weights)))
def selected(Tc,Mother,T,margin):
    if Tc<=0: return dict(required_share_unbounded=None,required_share_clipped=None,status='no_positive_pool')
    q=(Tc+margin*T-Mother)/(2*Tc)
    status='already_secured_under_fixed_others' if q<0 else ('impossible_under_fixed_others' if q>1 else 'feasible_tie_or_cushion_threshold')
    return dict(required_share_unbounded=q,required_share_clipped=clip(q),status=status)
def county_inputs():
    return list(csv.DictReader((H.parent/'county-baselines.csv').open()))
def scenario(rows,anchor,volume,scale=1.,others_shift=0.,margin=0.):
    if not math.isfinite(scale) or scale<0 or not math.isfinite(others_shift): return dict(status='invalid_volume_or_preference_setting'),[]
    shares=[float(r[anchor+'_d_pair_share']) for r in rows]
    weights=[float(r[volume+'_pair_votes'])*scale for r in rows]
    total_named=sum(float(r[volume+'_named_votes'])*scale for r in rows)
    result=solve(shares,weights,margin)
    if result['status']!='feasible':
        result.update(preference_anchor=anchor,volume_basis=volume,scale=scale,goal_pair_margin_pp=margin*100,expected_named_votes=total_named)
        return result,[]
    T=sum(weights); d=result['shift']; M=result['baseline_net']; output=[]
    for r,s,w in zip(rows,shares,weights):
        base=w*(2*s-1); t=clip(s+d); others=sum(wj*(2*clip(sj+others_shift)-1) for sj,wj in zip(shares,weights))-w*(2*clip(s+others_shift)-1)
        single=selected(w,others,T,margin)
        named=float(r[volume+'_named_votes'])*scale
        output.append(dict(county=r['county'],county_fips=r['county_fips'],county_key=r['county_key'],preference_anchor=anchor,volume_basis=volume,scale=scale,pair_participation=float(r[volume+'_pair_participation']),historical_anchor_A_name=SPECS[anchor]['candidates'][0][1],historical_anchor_B_name=SPECS[anchor]['candidates'][1][1],baseline_A_share=s,baseline_net=base,expected_pair_votes=w,expected_named_votes=named,other_named_votes=named-w,pair_weight=w/T,named_weight=named/total_named,goal_pair_margin_pp=margin*100,uniform_shift_unbounded_share_pp=result['unbounded_shift']*100,uniform_shift_bounded_share_pp=d*100,target_A_share=t,target_pair_margin_pp=100*(2*t-1),target_net=w*(2*t-1),target_net_gain=2*w*(t-s),net_gain_per_1pp_A_share=2*w*.01,bounded_net_gain_from_plus1pp_A_share=2*w*(clip(s+.01)-s),unit_share_clipped=(s+d!=t),local_tie_share=.5,local_tie_change_share_pp=100*(.5-s),local_Aplus1_share=.505,local_Aplus1_change_share_pp=100*(.505-s),selected_only_others_share_shift_pp=others_shift*100,selected_only_others_net=others,selected_only_required_share_unbounded=single['required_share_unbounded'],selected_only_required_share_clipped=single['required_share_clipped'],selected_only_status=single['status']))
    finalA=sum(r['expected_pair_votes']*r['target_A_share'] for r in output); finalB=T-finalA
    # Keep each historical nonpair candidate distinct; no assumption about 2026 candidates.
    other_candidates={ck:sum(float(r[volume+'_'+ck+'_votes'])*scale for r in rows) for ck,_,_ in SPECS[volume]['candidates'][2:]}
    result.update(preference_anchor=anchor,volume_basis=volume,scale=scale,goal_pair_margin_pp=margin*100,expected_named_votes=total_named,expected_other_named_votes=total_named-T,pair_participation=T/total_named,final_A=finalA,final_B=finalB,final_other_candidates=other_candidates,final_pair_margin_pp=100*(finalA-finalB)/T,final_all_named_margin_pp=100*(finalA-finalB)/total_named,final_A_all_named_share=finalA/total_named,pair_cushion_net_votes=margin*T,all_named_1pp_net_votes=.01*total_named,plurality_comparison='A_clear_plurality' if finalA>max([finalB]+list(other_candidates.values()))+1e-7 else ('A_B_tie_for_first' if abs(finalA-finalB)<1e-7 and finalA>=max(other_candidates.values()) else 'A_not_clear_plurality'))
    return result,output
def native_targets():
    units=[json.loads(l) for l in gzip.open(H/'native-units.jsonl.gz','rt')]; counties=county_inputs(); out=[]; states=[]
    # The full broad 2024 native family has complete numeric controls. Other native families have suppression gaps.
    broad=[u for u in units if u['source_id']=='sos-2024-president-county']
    positive=[u for u in broad if u['pair_votes'] and u['pair_votes']>0]
    shares=[u['A_votes']/u['pair_votes'] for u in positive]; weights=[u['pair_votes'] for u in positive]
    broadsol={m:solve(shares,weights,m) for m in [0.,.01]}
    for m,sol in broadsol.items(): states.append(dict(scope='complete_2024_broad_native_contexts',goal_pair_margin_pp=m*100,**sol))
    for u in units:
        pref=u['baseline']; primary='primary' in pref
        for margin in [0.,.01]:
            fields=dict(unit_key=u['unit_key'],source_id=u['source_id'],sheet=u['sheet'],county=u['county'],county_fips=u['county_fips'],goal_pair_margin_pp=margin*100,pair_votes=u['pair_votes'],named_votes=u['named_votes'],known_named_votes=u['known_named_votes'])
            if primary:
                fields.update(status='separate_party_primary_not_a_general_A_B_electorate',baseline_A_share=None,local_tie_share=None,local_Aplus1_share=None,statewide_uniform_target_share=None,selected_only_required_share_unbounded=None,selected_only_status='not_applicable')
            elif u['pair_votes'] is None:
                fields.update(status='unavailable_native_pair_cells_not_zero',baseline_A_share=None,local_tie_share=None,local_Aplus1_share=None,statewide_uniform_target_share=None,selected_only_required_share_unbounded=None,selected_only_status='unknown')
            elif u['pair_votes']==0:
                fields.update(status='no_positive_pair_pool',baseline_A_share=None,local_tie_share=None,local_Aplus1_share=None,statewide_uniform_target_share=None,selected_only_required_share_unbounded=None,selected_only_status='no_positive_pool')
            else:
                w=u['pair_votes']; s=u['A_votes']/w
                stateT=sum(float(r[pref+'_pair_votes']) for r in counties); stateM=sum(float(r[pref+'_d_minus_r_net_votes']) for r in counties)
                if u['source_id']=='sos-2024-president-county':
                    sol=broadsol[margin]; target=clip(s+sol['shift']); scope='complete_broad_native_uniform_shift'
                    fields.update(native_uniform_shift_unbounded_share_pp=100*sol['unbounded_shift'],native_uniform_shift_bounded_share_pp=100*sol['shift'],uniform_share_clipped=not 0<=s+sol['shift']<=1)
                else:
                    target=None; scope='unavailable_full_family_bounded_solve_due_to_missing_cells'
                single=selected(w,stateM-(u['A_votes']-u['B_votes']),stateT,margin)
                fields.update(status='published_numeric_pair',baseline_A_share=s,local_tie_share=.5,local_Aplus1_share=.505,statewide_uniform_target_share=target,selected_only_required_share_unbounded=single['required_share_unbounded'],selected_only_status=single['status'])
                fields.update(local_tie_net=0,local_Aplus1_net=.01*w,local_tie_net_gain=-(u['A_votes']-u['B_votes']),local_Aplus1_net_gain=.01*w-(u['A_votes']-u['B_votes']))
                fields.update(local_tie_change_share_pp=100*(.5-s),local_Aplus1_change_share_pp=100*(.505-s),baseline_net=u['A_votes']-u['B_votes'],pair_weight_of_complete_county_controls=w/stateT,net_gain_per_1pp_A_share=.02*w,bounded_net_gain_from_plus1pp_A_share=2*w*(clip(s+.01)-s),statewide_solve_scope=scope,statewide_target_net=w*(2*target-1) if target is not None else None,statewide_target_gain=2*w*(target-s) if target is not None else None,selected_only_other_net=stateM-(u['A_votes']-u['B_votes']),selected_only_required_share_clipped=single['required_share_clipped'])
            # Uniform CSV schema across unavailable/primary/zero rows.
            out.append(fields)
    cols=list(dict.fromkeys(k for r in out for k in r)); out=[{k:r.get(k) for k in cols} for r in out]
    csvout('native-targets.csv.gz',out); jdump('native-state-scenarios.json',states)
def main():
    p=argparse.ArgumentParser(); p.add_argument('--county'); p.add_argument('--anchor',choices=ANCHORS,default='president_2024'); p.add_argument('--volume',choices=ANCHORS,default='president_2024'); p.add_argument('--scale',type=float,default=1.); p.add_argument('--target-margin-pp',type=float,default=0.); p.add_argument('--others-share-shift-pp',type=float,default=0.); a=p.parse_args()
    rows=county_inputs()
    if a.county:
        result,detail=scenario(rows,a.anchor,a.volume,a.scale,a.others_share_shift_pp/100,a.target_margin_pp/100)
        print(json.dumps(dict(state=result,selected=next((r for r in detail if r['county']==a.county),None)),indent=2,allow_nan=False)); return
    settings=dict(volume_bases=dict(low=dict(source='senate_2022',named_votes=1004956,pair_votes=975190),base=dict(source='president_2024',named_votes=1327591,pair_votes=1303655),high=dict(source='senate_2020',named_votes=1367755,pair_votes=1299492)),definition='low/base/high order is historical named contest volume; pair participation and county mix are source-specific, not a2026 projection',preference_anchors=ANCHORS,goals_pair_margin_pp=[0,1],scale=1,others_share_shift_pp=0,pair_weight_definition='historical county pair votes in selected volume source divided by all105 county pair votes',other_candidate_handling='retain nonpair historical candidate counts from volume source separately; no transfers or2026 ballot mapping',composition_only='additional 2022/2020 pair mixes rescaled to2024 statewide pair total; every county retained')
    jdump('scenario-settings.json',settings)
    results=[]; allrows=[]
    for anchor in ANCHORS:
        for volume in ANCHORS:
            for margin in [0.,.01]:
                state,detail=scenario(rows,anchor,volume,1,0,margin); name=anchor+'__'+volume+'__raw'
                state['scenario']=name; results.append(state)
                allrows.extend(dict(scenario=name,**r) for r in detail)
    for volume in ['senate_2022','senate_2020']:
        scale=1303655/sum(float(r[volume+'_pair_votes']) for r in rows)
        for margin in [0.,.01]:
            state,detail=scenario(rows,'president_2024',volume,scale,0,margin); name='president_2024__'+volume+'__pair_total_normalized'
            state['scenario']=name; results.append(state); allrows.extend(dict(scenario=name,**r) for r in detail)
    jdump('state-scenarios.json',results); csvout('county-targets.csv',allrows); native_targets()
    print(json.dumps(dict(state_scenarios=len(results),county_target_rows=len(allrows),native_target_rows=44062)))
if __name__=='__main__': main()
