"""Conditional targets for original alternatives and Union vendor profiles.

Replace the ENTIRE selected county's source partition, never join units by
name or add duplicate views. All other81county source partitions remain fixed.
Kemper unofficial parallels receive local arithmetic only: no independently
disjoint selected pool is asserted for a repeated page observation.
"""
import csv,gzip,io,json
from collections import Counter
from sources import OUT,BASE,save,sha
from calculator import bounded_shift,clip,status
from native_state_calculator import load_units,scenarios
from native_calculator import ANCHORS
from build_counties import writecsv
def main():
    _,preferred,parents=load_units();cc={r['fips']:r for r in csv.DictReader((BASE/'data/county-baselines.csv').open())};ledger=json.loads((OUT/'native-2024-senate-reviewed-84views.json').read_text());variants=[];parallel=[]
    for s in ledger['sources']:
        if s['source_id'] not in ['sos-2024-county-coahoma','sos-2024-county-pike','sos-2024-county-kemper']:continue
        units=[]
        for p in s['pages']:
            for c in p['columns']:
                if c['role'] not in ['source_native_reporting_constituent','parallel_native_observation']:continue
                a=c['fields']['Ty Pinkins']['value'];b=c['fields']['Roger F. Wicker']['value'];u=dict(key=f'{s["county_fips"]}:{s["source_id"]}:p{p["page"]}:c{c["source_column"]}',county_fips=s['county_fips'],source_id=s['source_id'],raw_sha256=s['raw_sha256'],source_page=p['page'],source_column=c['source_column'],label_literal=c['label_literal'],historical_A=a,historical_B=b,historical_pair=a+b,source_native_A_share=a/(a+b) if a+b else None)
                if c['role']=='parallel_native_observation':parallel.append(u)
                else:units.append(u)
        if s['source_id'].endswith('-kemper'):continue
        variants.append((s['source_id'],s['county_fips'],units,'Original explicitly separate county-index packet; substitute complete county source partition, no unit-level crosswalk'))
    for county,fips in [('union','28145'),('pike','28113')]:
        source=json.loads((OUT/f'{county}-native-profile-readings.json').read_text());uu=[]
        for p in source['profiles']:
            fs={f['field']:f['value'] for f in p['fields']};a=fs['sen_Pinkins'];b=fs['sen_Wicker'];page=p['source_page'] if 'source_page' in p else p['source_pages'][0];uu.append(dict(key=f'{fips}:{source["source_id"]}:p{page}:vendor-profile',county_fips=fips,source_id=source['source_id'],raw_sha256=source['raw_sha256'],source_page=page,source_column='',label_literal=p['native_label_literal'],historical_A=a,historical_B=b,historical_pair=a+b,source_native_A_share=a/(a+b) if a+b else None,Senate_generic_marks_source=fs['sen_generic_write_in'],Senate_contest_opportunities_source=fs['sen_contest_total']))
        variants.append((f'{county.title()}-ES&S-vendor-profiles',fips,uu,'Disjoint vendor profiles form a separate complete county partition; substitute WHOLE county view, no SEMS/current unit crosswalk or updated-vintage splicing'))
    output=[];states=[]
    for variant,fips,units,qualification in variants:
        pool=[u for u in preferred if u['county_fips']!=fips]+units;parentcopy={f:dict(v) for f,v in parents.items()};parentcopy[fips]={'A':sum(u['historical_A'] for u in units),'B':sum(u['historical_B'] for u in units),'pair':sum(u['historical_pair'] for u in units)};assert len({u['county_fips'] for u in pool})==82
        for scenario,cw,basis in scenarios(cc,parentcopy):
            weights=[cw[u['county_fips']]*u['historical_pair']/parentcopy[u['county_fips']]['pair'] for u in pool];T=sum(weights)
            for anchor in ANCHORS:
                shares=[u['source_native_A_share'] if anchor=='2024-senate' else float(cc[u['county_fips']][anchor+'_A_pair_share']) for u in pool];shares=[q if q is not None else .5 for q in shares];base=sum(w*(2*q-1) for w,q in zip(weights,shares));others=sum(float(r[anchor+'_other']) for r in cc.values())
                for margin in [0,.01]:
                    target=margin*T;sol=bounded_shift(weights,shares,target);states.append(dict(alternative_source_partition=variant,county_fips=fips,source_partition_scope=qualification,scenario=scenario,preference_anchor=anchor,target_pair_margin_pp=100*margin,state_counties=82,disjoint_source_units=len(pool),pair_votes=T,**{k:v for k,v in sol.items() if k!='shares'}))
                    for u,w,q0,q in zip(pool,weights,shares,sol['shares']):
                        if u not in units:continue
                        net=w*(2*q0-1);fixed=base-net;req=(w+target-fixed)/(2*w) if w else None;row=u|dict(alternative_source_partition=variant,source_partition_scope=qualification,scenario=scenario,volume_basis=basis,preference_anchor=anchor,preference_scope='Actual selected historical native Senate pair' if anchor=='2024-senate' else 'Historical county pair preference uniformly applied inside this source2024 parent; expressly conditional, no cross-year native identity',expected_unit_pair_votes=w,within_selected_parent_pair_weight=u['historical_pair']/parentcopy[fips]['pair'],state_pair_denominator=T,state_pair_weight=w/T,state_counties=82,state_source_unit_count=len(pool),baseline_A_share=q0,baseline_unit_net=net,state_baseline_net=base,target_pair_margin_pp=100*margin,state_target_net=target,target_A_share=q,target_unit_net=w*(2*q-1),unit_net_gain=2*w*(q-q0),uniform_unbounded_shift_share_pp=100*sol['unbounded_shift'],uniform_bounded_shift_share_pp=100*sol['bounded_shift'],conditional_named_all_candidate_denominator=T+others,historical_named_others_state_held_fixed=others,generic_write_in_scope='Not treated as valid named candidates; absent elsewhere is unresolved, not zero',selected_only_fixed_other_net=fixed,selected_only_other_units_assumption='Every other source-native constituent in this explicit disjoint82county source mixture fixed at stated anchor preference and county volume; alternative county partition replaces rather than adds to preferred view',selected_only_required_A_share=req,selected_only_status=status(req) if req is not None else 'no_positive_pool',selected_only_clipped_display_share=clip(req) if req is not None else None,local_pair_tie_A_share=.5 if w else None,local_A_plus_1_pair_margin_A_share=.505 if w else None,local_tie_shift_share_pp=100*(.5-q0) if w else None,local_A_plus_1_shift_share_pp=100*(.505-q0) if w else None,net_gain_for_one_A_share_pp=.02*w)
                        if req is not None:assert abs(fixed+w*(2*req-1)-target)<1e-6
                        output.append(row)
    assert len(output)==7920 and len(states)==360
    local=[]
    for u in parallel:
        n=u['historical_pair'];q=u['source_native_A_share']
        for margin in [0,.01]:local.append(u|dict(source_role='parallel_native_observation',target_pair_margin_pp=100*margin,local_target_A_share=(1+margin)/2 if n else None,local_shift_share_pp=100*((1+margin)/2-q) if n else None,local_target_net=margin*n,local_net_gain=margin*n-u['historical_A']+u['historical_B'],net_gain_for_one_A_share_pp=.02*n,selected_state_status='No independent disjoint pool asserted for this nonadditive repeated source observation; local arithmetic only',current_geometry_approved=False))
    writecsv(OUT/'native-alternative-unit-targets.csv',output);writecsv(OUT/'native-alternative-state-targets.csv',states);writecsv(OUT/'native-parallel-observation-local-targets.csv',local);save(OUT/'native-alternative-calculator-settings.json',dict(qualification='Supplemental observed source views, never additive to preferred native scope. Each complete alternative county partition replaces the whole preferred county source view while all other81counties remain. No unit name/ordinal crosswalk is used. Nonadditive Kemper parallels have local arithmetic only; no independent state-moving pool inferred.',alternative_native_units=88,alternative_source_partitions=4,state_counties=82,state_target_groups=360,alternative_unit_targets=7920,parallel_observations=11,parallel_local_targets=22,preferred_scope_native_denominator=1215400,original_Pike_alternative_native_denominator=1212682,unallocated_Tunica_source_disagreement_remains=True,historical_volumes_and_preferences='Same9countyvolume/mix sensitivities and5anchors as native_state_calculator.py. Base is actual named pair of the specified source mixture, normalized variants use its own base total. Other-year native volumes/preferences are conditional assumptions.',all_candidate_native_question_complete=False,current2026_geography_approved=False));print('88alternative native observations/7920targets;360all82statecases;11parallel/22local-onlytargets')
if __name__=='__main__':main()
