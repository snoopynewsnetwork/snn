#!/usr/bin/env python3
"""All-native and county targets, historical volume/mix/preference sensitivity."""
import json,sys
sys.dont_write_bytecode=True
from build import HERE,STATE,CONTESTS,NAMES,native,geo,csvout,COUNTIES,PRES,S20,S22
from calculator import uniform,selected
from acquire import dump

def run():
    counties=json.loads((HERE/'county-controls.json').read_text());states=json.loads((HERE/'state-baselines.json').read_text());state={r['source_id']:r for r in states}
    states_out=[];native_out=[];county_out=[]
    # Same-contest scenarios use their original native leaves, never a guessed
    # cross-year town/ward join. Hybrid mixes transfer only county totals, then
    # explicitly preserve 2024 within-county pair weights and preferences.
    cases=[]
    for sid,m in CONTESTS.items():cases.append(dict(id=str(m['year'])+'-own-native-repeat',preference_source=sid,volume_source=sid,mix_source=sid,hybrid=False))
    cases += [dict(id='2024-preference-'+str(CONTESTS[sid]['year'])+'-county-mix-'+label+'-historical-volume',preference_source=PRES,volume_source=sid,mix_source=sid,hybrid=True) for sid,label in [(S22,'low'),(S20,'middle'),(PRES,'high')]]
    # Preference sensitivity uses actual 2020/2022 county shares on the 2024
    # native volume. This is explicitly a county anchor, not ward imputation.
    for sid in [S22,S20]:cases.append(dict(id=str(CONTESTS[sid]['year'])+'-county-preference-2024-native-volume',preference_source=sid,volume_source=PRES,mix_source=PRES,hybrid=False,county_preference=True))
    for case in cases:
        pref=case['preference_source'];m=CONTESTS[pref];src=PRES if case.get('hybrid') or case.get('county_preference') else pref
        ns=native(src);cmeta=CONTESTS[src];gs=[geo(r,cmeta['year']) for r in ns]
        weights=[];shares=[];totals=[]
        for r in ns:
            f=r['fields'];a=f[cmeta['A']];b=f[cmeta['B']];pair=sum(v for v in [a,b] if v is not None)
            q=a/pair if pair and a is not None and b is not None else None
            C=sum(f[k] for k in cmeta['candidates'] if f[k] is not None)
            if case.get('hybrid'):
                county=r['county'];mix=next(c for c in counties if c['source_id']==case['mix_source'] and c['county']==county);base=next(c for c in counties if c['source_id']==PRES and c['county']==county)
                scale=mix['pair_votes']/base['pair_votes'];pair=pair*scale
                # Preserve 2024 native pair participation when converting pool
                # size to total reported candidate/generic marks.
                C=C*scale
            if case.get('county_preference'):
                county=next(c for c in counties if c['source_id']==pref and c['county']==r['county']);q=county['A_pair_share'] if pair else None
            weights.append(pair);shares.append(q);totals.append(C)
        T=sum(weights);C=sum(totals)
        for target,margin in [('tie',0.),('A_plus_1_pair_margin',.01)]:
            solved=uniform(weights,shares,margin);assert solved['status']=='solved'
            flat={k:v for k,v in solved.items() if k not in ['target_shares','target_contributions']}
            states_out.append(dict(scenario=case['id'],target=target,**case,**flat,all_reported_candidate_generic_volume=C,target_all_reported_margin_pp=100*solved['target_net_votes']/C if C else None,preference_A=NAMES[m['A']][0],preference_B=NAMES[m['B']][0]))
            for i,(g,t,q,Ci,qt,net) in enumerate(zip(gs,weights,shares,totals,solved['target_shares'],solved['target_contributions'])):
                conditional=selected(weights,shares,i,margin,0)
                row=dict(scenario=case['id'],target=target,source_id=src,preference_source=pref,geography_key=g['geography_key'],county=g['county'],county_fips=g['county_fips'],native_label=g['native_label'],A_name=NAMES[m['A']][0],B_name=NAMES[m['B']][0],pair_volume=t,all_reported_volume=Ci,pair_weight=t/T,pair_participation=t/Ci if Ci else None,baseline_A_pair_share=q,baseline_net_votes=t*(2*q-1) if t else 0.,target_A_pair_share=qt,target_pair_margin_pp=100*(2*qt-1) if qt is not None else None,target_net_votes=net,required_change_share_pp=100*(qt-q) if q is not None and qt is not None else None,net_gain_votes=net-(t*(2*q-1) if t else 0.),net_votes_per_1pp_A_share=.02*t,selected_only_required_share_unbounded=conditional.get('required_share_unbounded'),selected_only_required_share_clipped=conditional.get('required_share_clipped'),selected_only_status=conditional['status'],every_other_unit_fixed='clipped historical preference (0pp shift); every native unit included',other_fixed_net_votes=conditional.get('other_fixed_net_votes'),unobserved_pair_fields=ns[i]['fields'][cmeta['A']] is None or ns[i]['fields'][cmeta['B']] is None)
                native_out.append(row)
            for county in COUNTIES:
                ix=[i for i,g in enumerate(gs) if g['county']==county];t=sum(weights[i] for i in ix);cc=sum(totals[i] for i in ix);base=sum(weights[i]*(2*shares[i]-1) for i in ix if weights[i]>0);net=sum(solved['target_contributions'][i] for i in ix);other=solved['baseline_net_votes']-base;qreq=(t+margin*T-other)/(2*t)
                county_out.append(dict(scenario=case['id'],target=target,county=county,county_fips=gs[ix[0]]['county_fips'],pair_volume=t,all_reported_volume=cc,pair_participation=t/cc,pair_weight=t/T,baseline_net_votes=base,target_net_votes=net,target_A_pair_share=(1+net/t)/2,target_pair_margin_pp=100*net/t,net_gain_votes=net-base,net_votes_per_1pp_A_share=.02*t,selected_county_only_required_share_unbounded=qreq,selected_county_only_status='already_secured_at_all_B' if qreq<0 else 'impossible_at_all_A' if qreq>1 else 'feasible',other_counties_fixed_net_votes=other,other_counties_fixed='all native units at historical baseline preference; 0pp shift'))
    csvout(HERE/'state-scenarios.csv',states_out);csvout(HERE/'native-targets.csv',native_out);csvout(HERE/'county-targets.csv',county_out)
    dump(HERE/'scenario-settings.json',dict(scenarios=cases,targets=dict(tie=0,A_plus_1_pair_margin=.01),historical_pair_volume_anchors={str(CONTESTS[k]['year']):v['pair_votes'] for k,v in state.items()},historical_volume_order='low2022; base/middle2020; high2024. Historical envelope, not2026 projection. Primary recent comparison remains2024.',historical_volume_labels=dict(low=608121,base_middle=777007,high=814011),hybrid_method='Historical source county pair totals; 2024 within-county native pair weights and native preferences. No cross-year native identity join.',other_candidate_method='Pair-only scenarios preserve candidate identities outside pair; own-repeat all-candidate denominator observed. Hybrids preserve 2024 native pair participation; county preference cases keep 2024 candidate volume.',zero_and_missing='Null raw candidates stay null. Numerical reported subtotal may be zero; an unknown/no-positive pair pool has no defined preference/target share. No unobserved counts are inferred.',state_includes_all_native_leaves=True,clipping='Explicit [0,1] share clipping; bisection solves bounded statewide target, retain unbounded delta and clipped-unit count.'))
    print(json.dumps(dict(state_scenarios=len(states_out),native_targets=len(native_out),county_targets=len(county_out))))
if __name__=='__main__':run()
