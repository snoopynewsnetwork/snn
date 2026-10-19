"""Offline full-source Senate inventory/target/exception and2020TOTAL audit."""
import csv,gzip,io,json,math,re
from collections import Counter,defaultdict
from sources import OUT,BASE,original,sha,save
def near(a,b):assert abs(a-b)<1e-6,(a,b)
def main():
    p=OUT/'native-2024-senate-reviewed-84views.json';ledger=json.loads(p.read_text());controls=json.loads((OUT/'native-2024-senate-reviewed-controls-84views.json').read_text());roles=Counter();keys=set();preferred=Counter();pages=0
    assert len(ledger['sources'])==84
    for s in ledger['sources']:
        assert sha(original(s['source_id']))==s['raw_sha256'];sums=Counter();totals={}
        for p in s['pages']:
            pages+=1;w,h=p['render_size'];assert sha((BASE/p['raster_path']).read_bytes())==p['raster_sha256']
            for c in p['columns']:
                key=(s['county_fips'],s['source_id'],p['page'],c['source_column']);assert key not in keys;keys.add(key);roles[c['role']]+=1;assert c['role'] in ['source_native_reporting_constituent','parallel_native_observation','source_TOTAL','unused_template_column']
                boxes=[c['header_bounds']]+[f['source_box'] for f in c['fields'].values()]
                for b in boxes:assert 0<=b[0]<b[2]<=w and 0<=b[1]<b[3]<=h
                assert set(c['fields'])=={'Ty Pinkins','Roger F. Wicker'}
                for n,f in c['fields'].items():
                    v=f['value']
                    if c['role']=='unused_template_column':assert v is None
                    else:assert isinstance(v,int) and v>=0
                    if c['role']=='source_native_reporting_constituent':sums[n]+=v
                    if c['role']=='source_TOTAL':assert n not in totals;totals[n]=v
        assert dict(sums)==totals
        if s['use_in_preferred82_scope']:preferred.update(sums)
    assert pages==211 and len(keys)==2321 and roles=={'source_native_reporting_constituent':1779,'source_TOTAL':84,'unused_template_column':447,'parallel_native_observation':11};assert dict(preferred)=={'Ty Pinkins':451980,'Roger F. Wicker':763420};assert controls['candidate_numeric_or_null_positions']==4642
    assert {z['source_id'] for z in ledger['current_checkpoint_box_differences']}=={'sos-2024-county-itawamba'} and len(ledger['current_checkpoint_box_differences'])==58
    flat=list(csv.DictReader((OUT/'native-2024-senate-reviewed-84views.csv').open()));assert len(flat)==4642 and len({(r['key'],r['candidate']) for r in flat})==4642;assert sum(r['votes']=='' for r in flat)==894
    hint=json.loads(gzip.decompress((OUT/'source/native-reviewed-84views-positions.json.gz').read_bytes()))
    for s in hint['sources']:
        assert set(s)=={'source_id','raw_sha256','pages'}
        for p in s['pages']:
            assert set(p)=={'page','render_size','rotation_ccw','deskew_angle_ccw','columns'}
            for c in p['columns']:assert set(c)=={'source_column','header_bounds','candidate_bounds'}
    settings=json.loads((OUT/'native-source-calculator-settings.json').read_text());packed=(BASE/settings['stored_path']).read_bytes();assert len(packed)==settings['stored_bytes']<40000000 and sha(packed)==settings['stored_sha256'];raw=gzip.decompress(packed);assert len(raw)==settings['original_csv_bytes'] and sha(raw)==settings['original_csv_sha256'];groups=defaultdict(lambda:dict(keys=set(),counties=set(),pair=0.,weight=0.,base=0.,target=0.,gain=0.,clipped=0))
    n=0
    for r in csv.DictReader(io.StringIO(raw.decode())):
        k=(r['scenario'],r['preference_anchor'],r['target_pair_margin_pp']);g=groups[k];assert r['key'] not in g['keys'];g['keys'].add(r['key']);g['counties'].add(r['county_fips']);w=float(r['expected_unit_pair_votes']);q=float(r['target_A_share']);q0=float(r['baseline_A_share']);fixed=float(r['selected_only_fixed_other_net']);target=float(r['state_target_net']);base=float(r['state_baseline_net']);assert 0<=q<=1;near(w*(2*q-1),float(r['target_net']));near(.02*w,float(r['net_gain_for_one_A_share_pp']));near(fixed+w*(2*q0-1),base)
        if w>0:
            req=float(r['selected_only_required_A_share']);near(fixed+w*(2*req-1),target);near(float(r['local_A_plus_1_shift_pp'])-float(r['local_tie_shift_pp']),.5)
        else:assert r['selected_only_status']=='no_positive_pool'
        g['pair']+=w;g['weight']+=float(r['state_pair_weight']);g['base']+=float(r['baseline_unit_net']);g['target']+=float(r['target_net']);g['gain']+=float(r['net_gain']);g['clipped']+=r['share_clipped']=='True';n+=1
    state=list(csv.DictReader((OUT/'native-source-state-targets.csv').open()));assert len(groups)==len(state)==90 and n==156240
    for s in state:
        g=groups[(s['scenario'],s['preference_anchor'],s['target_pair_margin_pp'])];assert len(g['keys'])==1736 and len(g['counties'])==82;near(g['pair'],float(s['pair_votes']));near(g['weight'],1);near(g['base'],float(s['baseline_net']));near(g['target'],float(s['target_net']));near(g['target']-g['base'],g['gain']);assert g['clipped']==int(s['clipped_units']);near(g['target'],float(s['target_pair_margin_pp'])*g['pair']/100)
    counts=json.loads((OUT/'county-2020-publication-controls.json').read_text());assert counts['controls']['source_publications']==104 and counts['controls']['county_coverage']==82;assert len(counts['readings'])==104 and len({r['source_id'] for r in counts['readings']})==104
    for r in counts['readings']:assert sha(original(r['source_id']))==r['raw_sha256'] and sha((OUT/r['evidence_path']).read_bytes())==r['evidence_sha256']
    assert counts['controls']['all82_selected_publications_match_each_county_CSV'];assert {r['county_key'] for r in counts['controls']['changed_county_publications']}=={'adams','coahoma','prentiss'}
    exceptions=json.loads((OUT/'native-source-exception-readings.json').read_text());checked=0;nulls=0
    for s in exceptions['sources']:
        assert sha(original(s['source_id']))==s['raw_sha256'];sums=Counter();totals={}
        for p in s['pages']:
            assert sha((BASE/p['full_original_render_path']).read_bytes())==p['render_sha256'];assert len(p['fields'])==11
            for f in p['fields']:
                assert len(f['values'])==len(p['roles'])
                for role,v in zip(p['roles'],f['values']):
                    if role=='unused_template_column':assert v is None;nulls+=1;continue
                    assert isinstance(v,int) and v>=0;checked+=1
                    if role=='source_native_reporting_constituent':sums[f['candidate']]+=v
                    elif role=='source_TOTAL':totals[f['candidate']]=v
        assert dict(sums)==totals==s['printed_TOTAL']
    assert checked==429 and nulls==176
    winston=json.loads((OUT/'winston-native-allfield-readings.json').read_text());assert winston['controls']['all11_vectors_close'] and winston['controls']['native_constituents']==12 and winston['controls']['candidate_numeric_positions']==143 and winston['controls']['unused_null_positions']==99
    wn=0;wb=0;ws=Counter();wt={}
    for p in winston['pages']:
        assert sha((BASE/p['full_original_render_path']).read_bytes())==p['render_sha256']
        for f in p['fields']:
            assert len(f['values'])==len(p['roles'])==11
            for role,v in zip(p['roles'],f['values']):
                if role=='unused_template_column':assert v is None;wb+=1
                else:
                    assert isinstance(v,int) and v>=0;wn+=1
                    if role=='source_native_reporting_constituent':ws[f['candidate']]+=v
                    elif role=='source_TOTAL':wt[f['candidate']]=v
    assert wn==143 and wb==99 and dict(ws)==wt==winston['controls']['source_scoped_named_county_controls']
    allfield=json.loads((OUT/'native-allfield-coverage.json').read_text());assert len(allfield['all82_preferred_source_parent_status'])==82 and len({s['source_id'] for s in allfield['sources']})==allfield['counts']['source_views'];assert sum(p['source_native_constituents'] for p in allfield['all82_preferred_source_parent_status'])==1736;assert allfield['counts']['native_constituents']+allfield['counts']['preferred_unreviewed_native_constituents']==1736;assert allfield['complete_statewide_nine_presidential_native']==all(p['all11_original_review_complete'] for p in allfield['all82_preferred_source_parent_status'])
    for pin in allfield['inputs']:assert sha((BASE/pin['path']).read_bytes())==pin['sha256'] and (BASE/pin['path']).stat().st_size==pin['bytes']
    for s in allfield['sources']:assert s['all11_source_vectors_close_printed_TOTAL'] and sha(original(s['source_id']))==s['raw_sha256']
    histcoverage=json.loads((OUT/'native-2020-coverage.json').read_text());assert len(histcoverage['all104_publication_status'])==104 and not histcoverage['complete2020_native'];assert sum(r['selected_for_82_county_amended_where_explicit_control'] for r in histcoverage['all104_publication_status'])==82
    for pin in histcoverage['inputs']:assert sha((BASE/pin['path']).read_bytes())==pin['sha256'] and (BASE/pin['path']).stat().st_size==pin['bytes']
    for s in histcoverage['reviewed_sources']:assert sha(original(s['source_id']))==s['raw_sha256'] and s['all_three_native_vectors_close_source_TOTAL']
    histfields=json.loads((OUT/'native-2020-additional-readings.json').read_text())
    for s in histfields['sources']:
        ss=Counter();tt={}
        for pg in s['pages']:
            assert sha((BASE/pg['full_original_render_path']).read_bytes())==pg['render_sha256'];w,h=pg['render_size']
            for c in pg['columns']:
                l,t,r,b=c['header_bounds'];assert 0<=l<r<=w and 0<=t<b<=h
            for f in pg['fields']:
                assert len(f['values'])==len(pg['columns'])
                for c,v in zip(pg['columns'],f['values']):
                    if c['role'] in ['source_native_reporting_constituent','source_administrative_reporting_column']:assert isinstance(v,int) and v>=0;ss[f['candidate']]+=v
                    elif c['role']=='source_TOTAL':tt[f['candidate']]=v
                    else:assert v is None
        assert dict(ss)==tt==s['controls']['earlier_county_publication_control']
    named2024=json.loads((OUT/'native-2024-candidate-controls.json').read_text());assert named2024['county_candidate_controls']==902 and named2024['preferred_native_constituents']==1736 and len(named2024['differences'])==2;assert named2024['source_state_presidential_named_denominator']==1228007 and named2024['certified_state_presidential_named_denominator']==1228008
    altfields=json.loads((OUT/'native-alternative-allfield-readings.json').read_text());assert altfields['complete_two_alternative_views'] and altfields['counts']==dict(native_constituents=43,source_TOTAL_columns=2,unused_blank_columns=10,source_pages=5,numeric_positions=495,unused_null_positions=110,source_views=2)
    for s in altfields['sources']:
        assert sha(original(s['source_id']))==s['raw_sha256'] and s['controls']['all11_vectors_close'] and not s['additive_to_preferred82'];ss=Counter();tt={}
        for p in s['pages']:
            assert sha((BASE/p['full_original_render_path']).read_bytes())==p['render_sha256'] and len(p['fields'])==11
            for f in p['fields']:
                for role,v in zip(p['roles'],f['values']):
                    if role=='source_native_reporting_constituent':ss[f['candidate']]+=v
                    elif role=='source_TOTAL':tt[f['candidate']]=v
                    else:assert role=='unused_template_column' and v is None
        assert dict(ss)==tt==s['controls']['printed_TOTAL']
    for snapshotpath in sorted((OUT/'source').glob('native-allfield-*/snapshot.json')):
        fs=json.loads(snapshotpath.read_text());frozen={}
        for pin in fs['pins']:
            stored=(BASE/pin['frozen_path']).read_bytes();raw=gzip.decompress(stored);assert len(stored)==pin['stored_bytes'] and sha(stored)==pin['stored_sha256'] and len(raw)==pin['original_bytes'] and sha(raw)==pin['original_sha256'];frozen[pin['original_path']]=raw
        witness=json.loads(frozen['data/baselines/native-allfield-coverage.json']);assert witness['counts']==fs['counts']
        for pin in witness['inputs']:assert len(frozen[pin['path']])==pin['bytes'] and sha(frozen[pin['path']])==pin['sha256']
        assert not fs['complete_statewide_presidential'] and not fs['historical_native_complete'] and not fs['current2026_geography_approved']
    union=json.loads((OUT/'union-native-profile-readings.json').read_text());assert len(union['profiles'])==20 and union['controls']['required_numeric_fields']==380 and union['controls']['all18_count_field_vectors_match_county_summary'];assert union['controls']['contest_unallocated_arithmetic_residuals']=={'president':37,'senate':186}
    unionpeer=json.loads((OUT/'union-native-profile-peer-reconciliation.json').read_text());assert unionpeer['field_positions']==380 and not unionpeer['value_differences'] and not unionpeer['exact_text_layer_position_differences'] and not unionpeer['label_differences']
    pike=json.loads((OUT/'pike-native-profile-readings.json').read_text());assert len(pike['profiles'])==25 and pike['controls']['required_numeric_fields']==525 and pike['controls']['all19_available_count_vectors_match_original_county'];assert pike['controls']['profile_blank_sum']==1 and pike['controls']['county_blank_control'] is None;assert pike['controls']['contest_unallocated_arithmetic_residuals']=={'president':78,'senate':177}
    pikepeer=json.loads((OUT/'pike-native-profile-peer-reconciliation.json').read_text());assert pikepeer['field_positions']==525 and not pikepeer['value_differences'] and not pikepeer['label_differences']
    for p in pike['profiles']:
        assert len(p['fields'])==21
        for f in p['fields']:assert sha((BASE/f['full_original_render_path']).read_bytes())==f['render_sha256'] and sha((BASE/f['evidence_path']).read_bytes())==f['evidence_sha256']
    alternatives=list(csv.DictReader((OUT/'native-alternative-unit-targets.csv').open()));altstate=list(csv.DictReader((OUT/'native-alternative-state-targets.csv').open()));assert len(alternatives)==7920 and len(altstate)==360;assert len({r['key'] for r in alternatives})==88;assert all(int(r['state_counties'])==82 and int(r['state_source_unit_count'])==1736 for r in alternatives)
    for r in alternatives:
        w=float(r['expected_unit_pair_votes']);fixed=float(r['selected_only_fixed_other_net']);target=float(r['state_target_net']);req=float(r['selected_only_required_A_share']) if r['selected_only_required_A_share'] else None;near(float(r['state_target_net']),float(r['target_pair_margin_pp'])*float(r['state_pair_denominator'])/100)
        if req is not None:near(fixed+w*(2*req-1),target)
        else:assert r['selected_only_status']=='no_positive_pool'
    parallels=list(csv.DictReader((OUT/'native-parallel-observation-local-targets.csv').open()));assert len(parallels)==22 and len({r['key'] for r in parallels})==11;assert all('No independent disjoint pool' in r['selected_state_status'] for r in parallels)
    contract=json.loads((OUT/'native-priority-contract.json').read_text());orders=json.loads((OUT/'native-source-orders.json').read_text());recon=json.loads((OUT/'native-order-peer-reconciliation.json').read_text());pref=orders['preferred82_view'];assert contract['ordered_native_keys']==[r['key'] for r in pref['full_descending_order']];assert len(contract['ordered_native_keys'])==len(set(contract['ordered_native_keys']))==1736;assert len(contract['ordered_priority_native_keys'])==887 and len(contract['ordered_nonpriority_native_keys'])==849;assert contract['ordered_priority_native_keys']==contract['ordered_native_keys'][:887] and contract['ordered_nonpriority_native_keys']==contract['ordered_native_keys'][887:];assert len(contract['parent_all_native_keys'])==82 and sum(bool(v) for v in contract['parent_priority_native_keys'].values())==77;assert sum(map(len,contract['parent_all_native_keys'].values()))==1736 and sum(map(len,contract['parent_priority_native_keys'].values()))==887;assert pref['minimum80']['preceding_votes']==972157 and pref['minimum80']['votes']==972656 and pref['top15']['votes']==60019
    for D in [1215400,1215401]:assert 5*(972157+1)<4*D<=5*972656
    assert recon['compared_source_views']==84 and recon['compared_ordered_unit_positions']==3515 and recon['compared_candidate_fields']==7030 and recon['exact_order_key_candidate_parent_rank_cumulative_disagreements']==0 and recon['working_peer_ID_addition_unique_source_positions']==43
    snapshot=json.loads((OUT/'source/native-priority-v1/snapshot.json').read_text())
    for pin in snapshot['pins']:
        stored=(BASE/pin['frozen_path']).read_bytes();rawpin=gzip.decompress(stored);assert sha(stored)==pin['stored_sha256'] and sha(rawpin)==pin['original_sha256'] and rawpin==(BASE/pin['original_path']).read_bytes()
    assert not snapshot['coordinator_accepted'] and not snapshot['current2026_geography_approved']
    save(OUT/'native-final-validation.json',dict(status='pass_explicit_source_scopes',source_views=84,counties=82,source_pages=211,source_position_keys=2321,candidate_numeric_or_null_positions=4642,preferred82_native_constituents=1736,preferred82_candidate_sums=dict(preferred),native_named_pair_denominator=1215400,certified_named_pair_denominator=1215401,unallocated_source_disagreement={'Ty Pinkins':-1,'Roger F. Wicker':0},exact_all_target_bounds_agreement=False,Itawamba_target_metadata_differences=58,positions_only_hint_whitelist_pass=True,all84_original_and_render_hashes_verified=True,bounded_native_state_targets=90,native_unit_targets=n,all82_in_every_state=True,county2020_publications=104,county2020_original_read_candidate_fields=312,historical2020_native_review=histcoverage['counts'],additional_all11_original_candidate_positions=dict(numeric=429,unused_null=176,disjoint_native=26,parallel_native=11),bounded_all11_original_SEMS_coverage=allfield['counts'],all_candidate_native_complete=False,historical_native_complete=False,current2026_geography_approved=False))
    save(OUT/'native-alternative-validation.json',dict(status='pass_source_scope_arithmetic',Union_original_reviewed_profiles=20,Union_required_fields=380,Union_all18_count_vectors_close_primary_summary=True,Union_peer_numeric_position_label_differences=0,Pike_original_reviewed_profiles=25,Pike_required_fields=525,Pike_all19_available_count_vectors_close_original_county=True,Pike_blank1_county_unprinted=True,Pike_peer_numeric_label_differences=0,Pike_physical_reading_windows_not_claimed_exact_equal=True,complete_alternative_county_partitions=4,alternative_native_unit_observations=88,all82_in_every_alternative_state=True,alternative_state_targets=360,alternative_unit_targets=7920,Kemper_nonadditive_parallel_observations=11,Kemper_local_only_targets=22,parallel_selected_state_pool_not_inferred=True,complete_all_candidate_native_question=False,current_geography_approved=False))
    save(OUT/'native-priority-validation.json',dict(status='pass_independent_immutable887_proposal',all84_separate_source_orders=True,preferred_native_count=1736,preferred_named_pair_votes=1215400,certified_county_named_pair_votes=1215401,source_native_top15_votes=60019,minimum80_count=887,preceding886_votes=972157,crossing887_votes=972656,crossing_contribution=499,all849_nonpriority_units_retained=True,priority_parent_counties=77,zero_priority_parent_counties=5,all82_parent_child_maps_coherent=True,all3515_ordered_unit_positions_and7030candidate_fields_match_peer=True,working_peer_optional_ID_additions_separately_recorded=43,unallocated_Tunica_vote_preserved=True,unknown_vote_upper_bound_proof_pass=True,all4_immutable_original_and_stored_pins_verified=True,coordinator_accepted=False,current2026_geography_approved=False))
    print('PASS:84source scopes/4642Senatepositions;90state+156240unit bounded targets;104historicalcounty publications;sourceexceptions429numeric/176null;Union380/Pike525fields;alternative7920/parallel22targets')
if __name__=='__main__':main()
