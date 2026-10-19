"""Source-native contributions and selected-unit-only historical arithmetic.

Every state denominator and fixed-other net contains all82 counties. A bounded
reviewed native set is never substituted for the complete state. Other-year
county volume mixes are explicitly conditional and use the source2024 native
within-parent pair weights; they do not claim a cross-year precinct identity.
"""
import argparse,csv,gzip,io,json,math
from collections import defaultdict
from sources import OUT,BASE,save,sha
from calculator import clip,status

ANCHORS=['2024-senate','2024-president','2020-senate','2018-special','2018-runoff']
def volume_scenarios(counties):
    total=sum(float(r['2024-senate_pair_votes']) for r in counties)
    settings=[('base-2024-Senate','2024-senate_pair_votes','2024 actual named Senate pair'),('low-2022-EAC-counted-ballots','eac_2022_F1a','2022 EAC F1a administrative sensitivity; illustrative pair participation=1, no observed2022Senate'),('high-2020-Senate','2020-senate_pair_votes','2020 actual named Senate pair'),('midterm-2018-special-pair','2018-special_pair_votes','2018Nov6 actual named Espy/Hyde-Smith pair, other candidates separate'),('midterm-2018-runoff-pair','2018-runoff_pair_votes','2018Nov27 actual runoff pair, distinct electorate')]
    for name,field,basis in settings:
        ws={r['fips']:float(r[field]) for r in counties};yield name,ws,basis
        if not name.startswith('base'):
            scale=total/sum(ws.values());yield name+'-normalized-to-2024-pair',{k:v*scale for k,v in ws.items()},basis+'; common statewide scale to2024pair isolates county mix'

def units(ledger,counties):
    result=[];parents={r['fips']:r for r in counties}
    for s in ledger['sources']:
        parent=parents[s['county_fips']];psum=0
        for p in s['pages']:
            for c in p['columns']:
                if c['role']!='source_native_reporting_constituent':continue
                a=c['fields']['Ty Pinkins']['value'];b=c['fields']['Roger F. Wicker']['value'];n=a+b;psum+=n
                result.append(dict(key=f'{s["county_fips"]}:{s["source_id"]}:p{p["page"]}:c{c["source_column"]}',county_fips=s['county_fips'],county=s['county'],source_id=s['source_id'],raw_sha256=s['raw_sha256'],page=p['page'],source_column=c['source_column'],header_bounds=json.dumps(c['header_bounds']),label_literal=c['label_literal'],printed_native_id=c['printed_native_id'],historical_A=a,historical_B=b,historical_pair=n,within_parent_pair_weight=n/float(parent['2024-senate_pair_votes']),historical_A_share=a/n if n else None,historical_A_minus_B=a-b))
        assert psum==int(parent['2024-senate_pair_votes']),(s['source_id'],psum)
    assert len({u['key'] for u in result})==len(result)
    return result

def build(ledger_path):
    ledger=json.loads(ledger_path.read_text());counties=list(csv.DictReader((BASE/'data/county-baselines.csv').open()));parents={r['fips']:r for r in counties};uu=units(ledger,counties);buffers=io.StringIO();writer=None;observations=0;groups=[];source_fips={u['county_fips'] for u in uu}
    for scenario,county_w,basis in volume_scenarios(counties):
        T=sum(county_w.values())
        for anchor in ANCHORS:
            state_net=sum(county_w[r['fips']]*(2*float(r[anchor+'_A_pair_share'])-1) for r in counties);outsiders=sum(float(r[anchor+'_other']) for r in counties)
            for margin in [0,.01]:
                target=margin*T;groups.append(dict(scenario=scenario,preference_anchor=anchor,target_pair_margin_pp=100*margin,state_pair_votes=T,state_baseline_net=state_net,conditional_named_all_candidate_denominator=T+outsiders,all82_counties_in_fixed_other_assumptions=True,reviewed_native_counties=len(source_fips),reviewed_native_units=len(uu)))
                for u in uu:
                    parent=parents[u['county_fips']];w=county_w[u['county_fips']]*u['within_parent_pair_weight'];q0=u['historical_A_share'] if anchor=='2024-senate' else float(parent[anchor+'_A_pair_share']);net=w*(2*q0-1) if q0 is not None else 0.;fixed=state_net-net;required=(w+target-fixed)/(2*w) if w>0 else None;clipped=clip(required) if required is not None else None;achieved=fixed+w*(2*clipped-1) if clipped is not None else fixed;shift=required-q0 if required is not None and q0 is not None else None
                    r=u|dict(scenario=scenario,volume_basis=basis,within_parent_volume_assumption='Source2024 named pair weights fixed within this same historical parent; other-year volumes are conditional mixes, no historical native crosswalk asserted',preference_anchor=anchor,preference_scope='Actual own source-native2024 Senate pair preference' if anchor=='2024-senate' else 'Historical county pair preference applied uniformly to its source2024 native pool; illustrative assumption, no inferred native cross-year preference',expected_unit_pair_votes=w,state_pair_votes=T,state_pair_weight=w/T,state_baseline_net=state_net,baseline_unit_A_share=q0,baseline_unit_net=net,target_pair_margin_pp=margin*100,state_target_net=target,conditional_named_all_candidate_denominator=T+outsiders,historical_named_others_state_pool_held_fixed=outsiders,generic_write_in_marks='unresolved_not_zero',fixed_all_other_net=fixed,other_units_assumption='Every other reviewed native unit and all other82county geography held at the stated historical anchor preferences under this same county volume mix; counted historical reference is not a2026forecast',selected_only_required_A_share=required,selected_only_required_share_shift_pp=100*shift if shift is not None else None,selected_only_status=status(required) if required is not None else 'no_positive_pool',selected_only_clipped_display_share=clipped,selected_only_clipped_state_net=achieved,selected_only_clipped_target_gap=achieved-target,selected_only_required_net_gain=target-state_net,net_gain_for_one_A_share_pp=.02*w,local_pair_tie_A_share=.5 if w>0 else None,local_A_plus_1_pair_margin_A_share=.505 if w>0 else None,local_tie_share_shift_pp=100*(.5-q0) if q0 is not None else None,local_A_plus_1_share_shift_pp=100*(.505-q0) if q0 is not None else None,local_unbounded_tie_shift_formula='(B-A)/(2*(A+B))',local_net_gain_to_tie=-net,local_net_gain_to_A_plus_1=.01*w-net)
                    if writer is None:writer=csv.DictWriter(buffers,fieldnames=list(r));writer.writeheader()
                    writer.writerow(r);observations+=1
                    if required is not None:assert abs(fixed+w*(2*required-1)-target)<1e-6
    raw=buffers.getvalue().encode();path=OUT/'native-selected-targets.csv.gz';path.write_bytes(gzip.compress(raw,mtime=0))
    save(OUT/'native-calculator-settings.json',dict(qualification='Bounded reviewed native units only, all82counties included in every state calculation. Complete native statewide clipping surface remains pending; this file reports local pair targets and selected-unit-only break-even with every other geography fixed explicitly. Deterministic pair targets are not legal plurality/majority thresholds.',input_ledger=str(ledger_path.relative_to(BASE)),input_ledger_sha256=sha(ledger_path.read_bytes()),native_units=len(uu),native_parent_counties=len(source_fips),state_counties=82,scenario_groups=len(groups),target_rows=observations,settings=groups,stored_path=str(path.relative_to(BASE)),stored_bytes=path.stat().st_size,stored_sha256=sha(path.read_bytes()),original_csv_bytes=len(raw),original_csv_sha256=sha(raw),compression='Lossless gzip; decompress to exact ordered CSV bytes. No row split/normalization.',statewide_native_complete=False,formula='Selected q=(unit_pair+target_state_net-fixed_all_other_net)/(2*unit_pair); local tie shift=(B-A)/(2*(A+B)); A+1 adds0.005 share=0.5percentagepoints. Clipped display does not turn impossible requirements feasible.',current2026_identity_claim=False))
    print(len(uu),'native units;',observations,'selected/local target rows;',path.stat().st_size,'stored bytes')

def main():
    p=argparse.ArgumentParser();p.add_argument('--ledger',default='native-2024-senate-reviewed-40views.json');p.add_argument('--unit');p.add_argument('--target-pair-margin-pp',type=float,default=0);a=p.parse_args();path=OUT/a.ledger
    if not a.unit:build(path);return
    ledger=json.loads(path.read_text());cc=list(csv.DictReader((BASE/'data/county-baselines.csv').open()));u=next(x for x in units(ledger,cc) if x['key']==a.unit);T=sum(int(r['2024-senate_pair_votes']) for r in cc);net=sum(int(r['2024-senate_net_A_minus_B']) for r in cc);w=u['historical_pair'];target=a.target_pair_margin_pp*T/100;fixed=net-u['historical_A_minus_B'];q=(w+target-fixed)/(2*w) if w else None
    print(json.dumps(u|dict(state_pair_votes=T,state_counties=82,fixed_all_other_net=fixed,other_units_assumption='All other2024 named Senate source votes unchanged, every county included',target_pair_margin_pp=a.target_pair_margin_pp,required_A_share=q,clipped_display_share=clip(q) if q is not None else None,status=status(q) if q is not None else 'no_positive_pool'),indent=2))
if __name__=='__main__':main()
