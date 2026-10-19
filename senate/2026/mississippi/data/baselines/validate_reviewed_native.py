"""Validate exact source-native replay scope, weights and selected targets."""
import csv,gzip,io,json,math
from collections import defaultdict,Counter
from sources import OUT,BASE,original,sha,save
from native_calculator import volume_scenarios,ANCHORS
from calculator import status,clip
def close(a,b,tol=1e-6):assert abs(a-b)<tol,(a,b)
def main():
    path=OUT/'native-2024-senate-reviewed-40views.json';x=json.loads(path.read_text());county={r['fips']:r for r in csv.DictReader((BASE/'data/county-baselines.csv').open())};keys=set();units={};counts=Counter();wraps=x['explicit_wrap_representation_aliases']
    for s in x['sources']:
        assert sha(original(s['source_id']))==s['raw_sha256'];a=b=0;ta=tb=None
        for p in s['pages']:
            raster=(BASE/p['raster_path']).read_bytes();assert sha(raster)==p['raster_sha256'];w,h=p['render_size']
            for c in p['columns']:
                key=f'{s["county_fips"]}:{s["source_id"]}:p{p["page"]}:c{c["source_column"]}';assert key not in keys;keys.add(key);counts[c['role']]+=1
                hb=c['header_bounds'];assert 0<=hb[0]<hb[2]<=w+1 and 0<=hb[1]<hb[3]<=h+1
                for name,z in c['fields'].items():
                    box=z['source_box'];assert 0<=box[0]<box[2]<=w+1 and 0<=box[1]<box[3]<=h+1
                    if c['role']=='unused_template_column':assert z['value'] is None
                    else:assert isinstance(z['value'],int) and z['value']>=0
                va=c['fields']['Ty Pinkins']['value'];vb=c['fields']['Roger F. Wicker']['value']
                if c['role']=='source_TOTAL':assert ta is None;ta,tb=va,vb
                elif c['role']=='source_native_reporting_constituent':a+=va;b+=vb;units[key]=dict(county_fips=s['county_fips'],a=va,b=vb,n=va+vb)
        parent=county[s['county_fips']];assert a==ta==int(parent['2024-senate_A']);assert b==tb==int(parent['2024-senate_B'])
    assert counts=={'source_native_reporting_constituent':985,'source_TOTAL':40,'unused_template_column':196};assert len(keys)==1221
    settings=json.loads((OUT/'native-calculator-settings.json').read_text());assert settings['input_ledger_sha256']==sha(path.read_bytes());assert settings['native_units']==len(units) and settings['native_parent_counties']==40;assert settings['state_counties']==82;assert not settings['statewide_native_complete']
    stored=(BASE/settings['stored_path']).read_bytes();assert sha(stored)==settings['stored_sha256'];raw=gzip.decompress(stored);assert sha(raw)==settings['original_csv_sha256'];assert len(raw)==settings['original_csv_bytes'];volumes={k:w for k,w,_ in volume_scenarios(list(county.values()))};group=defaultdict(list);n=0;statuses=Counter()
    for r in csv.DictReader(io.StringIO(raw.decode())):
        n+=1;u=units[r['key']];parent=county[u['county_fips']];cw=volumes[r['scenario']];T=sum(cw.values());expectedw=cw[u['county_fips']]*u['n']/int(parent['2024-senate_pair_votes']);w=float(r['expected_unit_pair_votes']);close(w,expectedw);close(float(r['state_pair_votes']),T);close(float(r['state_pair_weight']),w/T);close(float(r['within_parent_pair_weight']),u['n']/int(parent['2024-senate_pair_votes']))
        anchor=r['preference_anchor'];q0=u['a']/u['n'] if anchor=='2024-senate' and u['n'] else float(parent[anchor+'_A_pair_share']) if anchor!='2024-senate' else None
        state=sum(cw[c['fips']]*(2*float(c[anchor+'_A_pair_share'])-1) for c in county.values());net=w*(2*q0-1) if q0 is not None else 0;fixed=state-net;target=float(r['target_pair_margin_pp'])*T/100;close(float(r['fixed_all_other_net']),fixed);close(float(r['state_baseline_net']),state);close(float(r['baseline_unit_net']),net)
        outsiders=sum(float(c[anchor+'_other']) for c in county.values());close(float(r['conditional_named_all_candidate_denominator']),T+outsiders)
        if w:
            q=float(r['selected_only_required_A_share']);close(fixed+w*(2*q-1),target);assert r['selected_only_status']==status(q);close(float(r['selected_only_clipped_display_share']),clip(q));close(float(r['selected_only_clipped_state_net']),fixed+w*(2*clip(q)-1));close(float(r['local_pair_tie_A_share']),.5);close(float(r['local_A_plus_1_pair_margin_A_share']),.505);close(float(r['local_A_plus_1_share_shift_pp'])-float(r['local_tie_share_shift_pp']),.5)
        else:assert r['selected_only_status']=='no_positive_pool' and not r['selected_only_required_A_share']
        statuses[r['selected_only_status']]+=1;group[(r['scenario'],anchor,r['target_pair_margin_pp'])].append(r)
    assert n==88650 and len(group)==90
    fips={u['county_fips'] for u in units.values()}
    for (scenario,anchor,margin),rs in group.items():
        assert len(rs)==985;close(sum(float(r['state_pair_weight']) for r in rs),sum(volumes[scenario][f] for f in fips)/sum(volumes[scenario].values()))
        parentweights=defaultdict(float)
        for r in rs:parentweights[r['county_fips']]+=float(r['within_parent_pair_weight'])
        assert set(parentweights)==fips
        for w in parentweights.values():close(w,1)
    save(OUT/'native-reviewed-validation.json',dict(status='pass_bounded40view_original_replay_and_all82_fixed_other_arithmetic',source_views=40,pages=sum(len(s['pages']) for s in x['sources']),source_columns=len(keys),native_constituents=985,native_candidate_positions=1970,TOTAL_candidate_positions=80,unused_null_candidate_positions=392,raw_originals_and_render_hashes_verified=True,all40_parent_candidate_controls_exact=True,explicit_wrap_representation_aliases=wraps,selected_target_rows=n,scenario_groups=len(group),every_state_assumption_contains_all82=True,selected_statuses=dict(statuses),native_weights_sum_to_covered_parent_fraction_not_assumed_statewide_one=True,statewide_native_complete=False,presidential_native_complete=False,current2026_geography_approved=False))
    print('pass bounded40views/985constituents;',n,'native target rows;',dict(statuses))
if __name__=='__main__':main()
