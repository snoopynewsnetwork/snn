"""Offline identity, controls, arithmetic, source/asset and coverage audit."""
import collections,csv,gzip,io,json,math,re
from pathlib import Path
from sources import *
from calculator import bounded_shift,live,pair_remainder
def close(a,b,tol=1e-6):assert abs(a-b)<tol,(a,b)
def main():
    checks={};gaps=[];rows=list(csv.DictReader((BASE/'data/county-baselines.csv').open()));assert len(rows)==82;assert len({r['fips'] for r in rows})==82
    assert all(re.fullmatch(r'28\d{3}',r['fips']) for r in rows);checks['county_identities_unique']=82
    candidates=list(csv.DictReader((OUT/'candidate-votes.csv').open()));keys=[(r['contest'],r['fips'],r['office_literal'],r['candidate_literal'],r['party_literal']) for r in candidates];assert len(keys)==len(set(keys))==1640
    assert collections.Counter(r['contest'] for r in candidates)=={'2024-senate':164,'2024-president':738,'2020-senate':246,'2018-special':328,'2018-runoff':164}
    primary=json.loads((OUT/'source/primary-state-readings.json').read_text())
    contests=['2024-senate','2024-president','2020-senate','2018-special','2018-runoff']
    for contest in contests:
        counts=collections.Counter()
        for r in candidates:
            if r['contest']==contest:
                name=r['candidate_literal'];name=re.match(r'Presidential Electors for (.*?) for President',name).group(1) if contest.endswith('president') else name
                counts[name]+=int(r['votes'])
        assert dict(counts)==primary[contest]['candidates'],(contest,counts)
        assert sum(counts.values())==primary[contest]['total']
    checks['primary_candidate_controls']='all20 named candidate totals across five distinct contests/stages match independent primary originals'
    for r in rows:
        for contest in contests:
            a,b,o=[int(r[contest+'_'+k]) for k in ['A','B','other']];assert a+b==int(r[contest+'_pair_votes']);assert a+b+o==int(r[contest+'_named_candidate_votes']);close(float(r[contest+'_A_pair_share']),a/(a+b))
        for y in [2022,2024]:assert int(r[f'eac_{y}_A1a'])==int(r[f'eac_{y}_A1b'])+int(r[f'eac_{y}_A1c'])
    ordered=sorted(rows,key=lambda r:(-int(r['2024-senate_named_candidate_votes']),r['fips']));assert [r['fips'] for r in rows]==[r['fips'] for r in ordered]
    T=sum(int(r['2024-senate_pair_votes']) for r in rows);cum=0;cross=None
    for i,r in enumerate(rows,1):
        cum+=int(r['2024-senate_pair_votes']);assert cum==int(r['cumulative_named_votes']);assert i==int(r['rank'])
        if cross is None and 5*cum>=4*T:cross=i
    assert T==1215401 and cross==41 and rows[40]['county']=='Newton';assert sum(int(r['2024-senate_pair_votes']) for r in rows[:15])==653846
    assert sum(int(r['2024-senate_pair_votes']) for r in rows[:40])==970209;assert sum(int(r['2024-senate_pair_votes']) for r in rows[:41])==979428
    checks['exact_integer_80_percent']='41 Newton; 40 below threshold; full 82 order'
    targets=list(csv.DictReader((OUT/'county-targets.csv').open()));states=list(csv.DictReader((OUT/'state-targets.csv').open()));groups=collections.defaultdict(list)
    for r in targets:groups[(r['scenario'],r['preference_anchor'],r['target_pair_margin_pp'])].append(r)
    assert len(groups)==len(states)==90
    for s in states:
        rr=groups[(s['scenario'],s['preference_anchor'],s['target_pair_margin_pp'])];assert len(rr)==82;assert {r['fips'] for r in rr}=={r['fips'] for r in rows}
        pair=sum(float(r['expected_pair_votes']) for r in rr);close(pair,float(s['pair_votes']));close(sum(float(r['state_pair_weight']) for r in rr),1)
        net=sum(float(r['target_net']) for r in rr);close(net,float(s['target_pair_margin_pp'])*pair/100)
        alln=sum(float(r['conditional_named_all_candidate_denominator']) for r in rr);close(alln,float(s['conditional_named_all_candidate_denominator']));close(100*net/alln,float(s['conditional_A_minus_B_all_candidate_margin_pp']))
        for r in rr:
            w=float(r['expected_pair_votes']);q=float(r['target_A_share']);assert 0<=q<=1;close(float(r['target_net']),w*(2*q-1));close(float(r['net_gain_for_one_share_pp']),.02*w)
            unbounded=float(r['selected_only_required_A_share']);other=float(r['fixed_other_net']);close(w*(2*unbounded-1)+other,float(s['target_pair_margin_pp'])*pair/100)
    checks['historical_scenarios']=dict(state_targets=len(states),county_targets=len(targets),all_82_in_every_state=True,tolerance_votes=1e-6)
    close(pair_remainder(100,120,100)['required_share'],.6);close(pair_remainder(100,120,100,.01)['required_share'],.616)
    assert pair_remainder(200,10,20)['status']=='already_above_target_at_zero_share';assert pair_remainder(10,200,20)['status']=='impossible';assert pair_remainder(10,20,None)['status']=='unknown_pool';assert pair_remainder(10,20,-1)['status']=='invalid_negative_pool';assert pair_remainder(10,20,0)['status']=='no_positive_pool'
    bound=bounded_shift([10,90],[.99,.1],1);assert not bound['unbounded_feasible'];assert bound['clipped_units']==1;close(bound['achieved_net'],1);assert bound['shares'][0]==1
    assert bounded_shift([0],[.3],0)['status']=='no_positive_pool';assert bounded_shift([10],[.3],11)['status']=='impossible';assert bounded_shift([10],[.8],0)['baseline_already_above_target']
    cases=json.loads((OUT/'synthetic-scenarios.json').read_text());testcases={c['input']['id']:c for c in cases['live']}
    for case in cases['live']:
        actual=live(case['input']);assert actual==case['output'];assert actual.get('counted_fixed',case['input']['counted'])==case['input']['counted']
        if 'final_votes' in actual:
            close(actual['final_all_candidate_denominator'],sum(case['input']['counted'].values())+actual['remaining_pool']);assert all(actual['final_votes'][k]>=v for k,v in case['input']['counted'].items())
    loser=testcases['third-candidate-leads-despite-pair-win']['output'];assert loser['A_minus_B_votes']>0 and not loser['A_strict_plurality'];assert loser['plurality_leader']=='Pinkins';assert testcases['clipped-preferences']['output']['clipped_forecast_units']==['synthetic']
    assert not testcases['empty-counted-no-pool']['output']['A_strict_plurality']
    checks['offline_live_and_bounded_edges']='unknown/no/negative pools; secured/impossible; final-denominator A+1; clipping; named third-candidate plurality; Independent Pinkins'
    peer=json.loads((OUT/'peer-reconciliation.json').read_text());assert not peer['candidate_differences'] and not peer['historical_differences'];assert peer['all_82_order_match'] and peer['priority_order_match'];metadata=peer.get('historical_physical_column_differences',[]);assert all(r['matches_documented_prior_merged_machine_ordinal'] and r['source_id']=='sos-2018-county-issaquena' and r['owned_fresh_physical_TOTAL_column']==6 and r['peer_observed_TOTAL_column']==4 for r in metadata);checks['independent_peer_fields']=dict(current_historical=peer['compared_candidate_rows'],distinct_2018=peer['historical_candidate_fields'],candidate_raw_hash_page_differences=0,documented_physical_column_position_differences=metadata,all_historical_physical_TOTAL_ordinals_agree=not metadata)
    native2018=json.loads((OUT/'native-2018-validation.json').read_text());assert native2018['status']=='pass_bounded_original_stage_and_physical_column_scopes' and not native2018['complete2018_native'];assert native2018['counts']==json.loads((OUT/'native-2018-original-readings.json').read_text())['counts'];checks['bounded2018_original_native_and_physical_column_review']=native2018
    assert len(native2018['source_native_TOTAL_disagreements'])==1 and not native2018['all_reviewed_candidate_vectors_close_earlier_county_controls'];exception=native2018['source_native_TOTAL_disagreements'][0];assert exception['source_id']=='sos-2018-county-leflore' and exception['native_minus_printed_TOTAL']['Mike Espy']==-10 and exception['unallocated'];assert len(native2018['rejected_witnesses'])==1 and native2018['rejected_witnesses'][0]['excluded_from_accepted_witness_chain']
    peer2018path=OUT/'native-2018-peer-10views-v1-reconciliation.json';peer2018=json.loads(peer2018path.read_text());assert peer2018['status']=='pass_bounded_post_original_ten_stage_replay' and peer2018['source_stage_views']==10 and peer2018['source_native_observations']==114 and peer2018['source_candidate_positions']==528 and not peer2018['differences'];sp=BASE/peer2018['peer_snapshot']['path'];assert sha(sp.read_bytes())==peer2018['peer_snapshot']['sha256'] and sp.with_name('reconciliation.json').read_bytes()==peer2018path.read_bytes()
    for pin in json.loads(sp.read_text())['pins']:
        z=(BASE/pin['stored_path']).read_bytes();r=gzip.decompress(z);assert len(z)==pin['stored_bytes']<40000000 and sha(z)==pin['stored_sha256'] and len(r)==pin['original_bytes'] and sha(r)==pin['original_sha256']
    for sid,h in peer2018['source_hashes'].items():assert sha(original(sid))==h
    checks['bounded2018_independent_ten_stage_native_replay']=peer2018
    peer2018v2path=OUT/'native-2018-peer-12views-v2-reconciliation.json';peer2018v2=json.loads(peer2018v2path.read_text());assert peer2018v2['status']=='pass_bounded_post_original_twelve_stage_replay' and peer2018v2['source_stage_views']==12 and peer2018v2['source_native_observations']==136 and peer2018v2['source_candidate_positions']==660 and peer2018v2['prior_ten_bodies_reused_byte_exact'] and not peer2018v2['differences'];v2sp=BASE/peer2018v2['peer_snapshot']['path'];assert sha(v2sp.read_bytes())==peer2018v2['peer_snapshot']['sha256'] and v2sp.with_name('reconciliation.json').read_bytes()==peer2018v2path.read_bytes();v2snap=json.loads(v2sp.read_text());assert v2snap['pins'][:10]==json.loads(sp.read_text())['pins'] and len(v2snap['pins'])==12
    for pin in v2snap['pins']:
        z=(BASE/pin['stored_path']).read_bytes();r=gzip.decompress(z);assert len(z)==pin['stored_bytes']<40000000 and sha(z)==pin['stored_sha256'] and len(r)==pin['original_bytes'] and sha(r)==pin['original_sha256']
    for sid,h in peer2018v2['source_hashes'].items():assert sha(original(sid))==h
    checks['bounded2018_independent_twelve_stage_native_replay']=peer2018v2
    reproduction=json.loads((OUT/'source/reproduction-1042020-70stage2018.json').read_text());assert reproduction['exit_code']==0 and reproduction['main_checks']==26
    for pin in [reproduction['log'],reproduction['stored_execution_reproducer'],reproduction['initial_receipt']]+reproduction['original_native_input_witnesses']+reproduction['bounded_peer_witnesses']+list(reproduction['native2020_arithmetic'].values()):
        body=(BASE/pin['path']).read_bytes();assert len(body)==pin['bytes'] and sha(body)==pin['sha256']
    assert reproduction['stored_execution_reproducer']['sha256']==reproduction['reproducer']['sha256'] and reproduction['stored_execution_reproducer']['bytes']==reproduction['reproducer']['bytes']
    checks['bounded_full_offline_reproduction_104and70']=reproduction
    run118path=OUT/'source/reproduction-1042020-118stage2018/completion.json';run118=json.loads(run118path.read_text());assert run118['exit_code']==0 and run118['main_checks']==28 and not run118['complete_native_question']
    for pin in [run118['execution_reproducer'],run118['log']]+run118['native_input_witnesses']:
        body=(BASE/pin['path']).read_bytes();assert len(body)==pin['bytes'] and sha(body)==pin['sha256']
    for record in run118['frozen_run_artifacts']:
        pin=record['stored'];stored=(BASE/pin['path']).read_bytes();assert len(stored)==pin['bytes']<40000000 and sha(stored)==pin['sha256'];body=gzip.decompress(stored);pin=record['original'];assert len(body)==pin['bytes'] and sha(body)==pin['sha256']
    checks['bounded_full_offline_reproduction_104and118']=dict(receipt=dict(path=str(run118path.relative_to(BASE)),bytes=run118path.stat().st_size,sha256=sha(run118path.read_bytes())),exit_code=0,then_main_checks=28,qualification=run118['qualification'])
    manual_units=0;manual_cells=0
    for filename in ['coahoma-updated-readings.json','alcorn-readings.json']:
        m=json.loads((OUT/filename).read_text());assert sha(original(m['source_id']))==m['raw_sha256'];tots={};sums=collections.Counter();unitkeys=[]
        for p in m['pages']:
            w,h=p['render_size'];columns=p['columns']
            for c in columns:
                left,right=c['x_bounds'];assert 0<=left<right<=w;unitkeys.append((p['page'],c['source_column']))
                if c['unit_type'] not in ['summary_TOTAL','unused']:manual_units+=1
            for f in p['fields']:
                assert len(f['values'])==len(columns);assert 0<=f['row_bounds'][1]<f['row_bounds'][3]<=h
                for c,v in zip(columns,f['values']):
                    if c['unit_type']=='unused':assert v is None;continue
                    assert isinstance(v,int) and v>=0;manual_cells+=1
                    if c['unit_type']=='summary_TOTAL':tots[f['field']]=v
                    else:sums[f['field']]+=v
        assert len(unitkeys)==len(set(unitkeys));assert dict(sums)==tots;assert len(tots)==11
        expected={}
        for r in candidates:
            if r['fips']!=m['fips'] or r['contest'] not in ['2024-senate','2024-president']:continue
            name=r['candidate_literal'];name=re.match(r'Presidential Electors for (.*?) for President',name).group(1) if r['contest'].endswith('president') else name;expected[name]=int(r['votes'])
        assert tots==expected
    checks['complete_manual_native_samples']=dict(constituents=manual_units,numeric_cells_including_TOTAL=manual_cells,candidate_fields_per_source=11,qualification='Bounded original visual reviews only; not statewide native completion. Corrections include offsetting AlcornSonski errors invisible to county closure.')
    reviewed=json.loads((OUT/'native-reviewed-validation.json').read_text());assert reviewed['native_constituents']==985 and reviewed['selected_target_rows']==88650;assert reviewed['raw_originals_and_render_hashes_verified'] and not reviewed['statewide_native_complete'];checks['independent_native_replay_and_selected_targets']=reviewed
    finalnative=json.loads((OUT/'native-final-validation.json').read_text());assert finalnative['source_views']==84 and finalnative['counties']==82 and finalnative['candidate_numeric_or_null_positions']==4642;assert finalnative['native_unit_targets']==156240 and finalnative['all82_in_every_state'];assert not finalnative['all_candidate_native_complete'] and not finalnative['historical_native_complete'];checks['complete_named_Senate_native_source_scopes_and_targets']=finalnative
    priority=json.loads((OUT/'native-priority-validation.json').read_text());assert priority['minimum80_count']==887 and priority['preferred_native_count']==1736 and priority['priority_parent_counties']==77 and priority['all4_immutable_original_and_stored_pins_verified'];checks['primary_native_order_and_exact80_immutable_proposal']=priority
    publications=json.loads((OUT/'county-2020-publication-controls.json').read_text());assert publications['controls']['source_publications']==104 and publications['controls']['original_read_candidate_fields']==312;assert publications['controls']['all82_selected_publications_match_each_county_CSV'];checks['actual2020_all_county_publication_TOTALs']=publications['controls']
    native2020=json.loads((OUT/'native-2020-validation.json').read_text());assert native2020['status']=='pass_bounded_original_publication_scopes' and not native2020['complete2020_native'];assert native2020['combined_counts']==json.loads((OUT/'native-2020-coverage.json').read_text())['counts'];checks['bounded2020_original_native_fields_and_immutable_witnesses']=native2020
    historicaltargets=json.loads((OUT/'native-2020-target-validation.json').read_text());assert historicaltargets['status']=='pass_independent_piecewise_and_source_formula_audit' and historicaltargets['state_groups']==134 and historicaltargets['unit_target_rows']==236510 and historicaltargets['all82_counties_in_every_state'];p=BASE/historicaltargets['settings']['path'];assert sha(p.read_bytes())==historicaltargets['settings']['sha256'] and p.stat().st_size==historicaltargets['settings']['bytes'];checks['actual2020_native_partitions_and_bounded_targets']=historicaltargets
    historical2018targets=json.loads((OUT/'native-2018-target-validation.json').read_text());assert historical2018targets['status']=='pass_independent_source_formula_and_piecewise_clipping_audit' and historical2018targets['state_groups']==180 and historical2018targets['unit_rows']==319050 and historical2018targets['unknowns_not_zero'];p=BASE/historical2018targets['settings']['path'];assert sha(p.read_bytes())==historical2018targets['settings']['sha256'] and p.stat().st_size==historical2018targets['settings']['bytes'];checks['actual2018_separate_stage_native_bounded_targets']=historical2018targets
    hp=OUT/'native-2020-peer-reconciliation.json';historicalpeer=json.loads(hp.read_text());assert historicalpeer['status']=='pass_bounded_post_original_seven_publication_replay' and historicalpeer['compared_positions']==297 and historicalpeer['native_constituents']==62 and historicalpeer['source_publications']==7 and not historicalpeer['value_role_differences'] and not historicalpeer['label_differences_after_whitespace_only'];hs=BASE/historicalpeer['peer_snapshot']['path'];assert sha(hs.read_bytes())==historicalpeer['peer_snapshot']['sha256'] and hs.with_name('reconciliation.json').read_bytes()==hp.read_bytes()
    for pin in json.loads(hs.read_text())['pins']:
        z=(BASE/pin['stored_path']).read_bytes();r=gzip.decompress(z);assert len(z)==pin['stored_bytes']<40000000 and sha(z)==pin['stored_sha256'] and len(r)==pin['original_bytes'] and sha(r)==pin['original_sha256']
    for sid,h in historicalpeer['source_raw_hashes'].items():assert sha(original(sid))==h
    for q in historicalpeer['source_page_render_pairs']:
        assert sha((BASE/q['own_raster']).read_bytes())==q['own_raster_sha256'] and sha((BASE/q['peer_raster']).read_bytes())==q['peer_raster_sha256']
    checks['bounded2020_independent_native_peer_replay']=historicalpeer
    peer2020v2=json.loads((OUT/'native-2020-peer-38views-v2-reconciliation.json').read_text());assert peer2020v2['status']=='pass_bounded_post_original_38_publication_replay' and peer2020v2['compared_positions']==2277 and peer2020v2['source_publications']==38 and peer2020v2['native_constituents']==518;assert not peer2020v2['value_role_differences'] and not peer2020v2['label_differences_after_whitespace_only'];checks['bounded2020_independent_38_publication_peer_replay']=peer2020v2
    peer2020v3path=OUT/'native-2020-peer-41views-v3-reconciliation.json';peer2020v3=json.loads(peer2020v3path.read_text());assert peer2020v3['status']=='pass_bounded_post_original_41_publication_replay' and peer2020v3['compared_positions']==2475 and peer2020v3['source_publications']==41 and peer2020v3['native_constituents']==565 and not peer2020v3['value_role_differences'] and not peer2020v3['label_differences_after_whitespace_only'];p=BASE/peer2020v3['peer_snapshot']['path'];assert sha(p.read_bytes())==peer2020v3['peer_snapshot']['sha256'] and p.with_name('reconciliation.json').read_bytes()==peer2020v3path.read_bytes();checks['bounded2020_independent_41_publication_peer_replay']=peer2020v3
    pp=OUT/'native-presidential-peer-batches-reconciliation.json';prespeer=json.loads(pp.read_text());assert prespeer['status']=='pass_bounded_post_original_peer_replay';assert not any(prespeer[k] for k in ['value_differences','label_differences_after_whitespace_only','role_differences','missing_own_positions']);assert sum(prespeer['candidate_positions_by_role'].values())==prespeer['compared_positions'];snap=BASE/prespeer['peer_snapshot']['path'];assert sha(snap.read_bytes())==prespeer['peer_snapshot']['sha256'];assert snap.with_name('reconciliation.json').read_bytes()==pp.read_bytes()
    for pin in json.loads(snap.read_text())['pins']:
        body=(BASE/pin['stored_path']).read_bytes();assert len(body)==pin['stored_bytes']<40000000 and sha(body)==pin['stored_sha256'];raw=gzip.decompress(body);assert len(raw)==pin['original_bytes'] and sha(raw)==pin['original_sha256']
    if prespeer.get('through_batch',0)>=33:
        assert prespeer['complete_preferred82_named_presidential_peer_scope'] and prespeer['bounded_preferred_source_views_including_separate_two']==82 and prespeer['bounded_preferred_native_constituents_including_separate_two']==1736
        omitted=prespeer['own_positions_outside_peer_flat_scope'];assert len(omitted)==prespeer['own_positions_outside_peer_flat_scope_count']==126 and all(r['role']=='unused' and r['value'] is None for r in omitted)
        assert sum(r['key'][0]=='sos-2024-county-perry' for r in omitted)==45 and sum(r['key'][0]=='sos-2024-county-tunica' for r in omitted)==81 and not prespeer['complete_all_blank_position_peer_scope']
        aliases=prespeer['label_representation_aliases_after_whitespace_only'];assert len(aliases)==18 and all(r['key'][0]=='sos-2024-county-holmes' and r['key'][1:3] in [[3,1],[3,4]] for r in aliases) and not prespeer['all_labels_identical_after_whitespace_only']
    checks['bounded_actual_presidential_peer_replay']=prespeer
    p=OUT/'native-2024-all11-complete-peer-reconciliation.json';all11peer=json.loads(p.read_text());assert all11peer['positions']==24926 and all11peer['positions_by_role']==dict(native=19096,TOTAL=902,unused=4807,parallel=121) and not all11peer['value_role_differences'];assert all11peer['new_explicit_peer_unused_positions']==126 and len(all11peer['literal_label_representation_aliases'])==22;sp=BASE/all11peer['input_snapshot']['path'];assert sha(sp.read_bytes())==all11peer['input_snapshot']['sha256'] and sp.with_name('reconciliation.json').read_bytes()==p.read_bytes();checks['complete2024_all11_new_peer_blank_scope']=all11peer
    p=OUT/'native-2018-peer-41views-v3-reconciliation.json';v3=json.loads(p.read_text());assert v3['source_stage_views']==41 and v3['source_native_observations']==578 and v3['source_candidate_positions']==2530 and not v3['differences'];sp=BASE/v3['peer_snapshot']['path'];assert sha(sp.read_bytes())==v3['peer_snapshot']['sha256'] and sp.with_name('reconciliation.json').read_bytes()==p.read_bytes();checks['bounded2018_independent_41_stage_native_replay']=v3
    receipt=json.loads((OUT/'source/current-receipt-readings.json').read_text());assert receipt['status']=='pass_bounded_own_primary_original_reading' and not receipt['live_pool_inferred'] and not receipt['complete_later_legal_audit'];assert sha((BASE/receipt['input_path']).read_bytes())==receipt['input_sha256'];assert sha(original(receipt['court_original']['source_id']))==receipt['court_original']['raw_sha256'];assert sha(original(receipt['SOS_original']['source_id']))==receipt['SOS_original']['raw_sha256'];checks['bounded_current_primary_receipt_and_method_readings']=receipt
    canvass=json.loads((OUT/'canvass-validation.json').read_text());checks['canvass_summary_validation']=canvass
    fs=json.loads((OUT/'printed-field-source-scope.json').read_text());assert fs['status']=='pass_retained_original_packet_and_available_required_field_inventory' and fs['source_documents']==352 and fs['original_PDFpages']==3238 and fs['statistics_panels']==14 and fs['county_summary_panels']==15 and fs['additional_SEMS_E013_views']==3 and fs['vendor_required_numeric_fields']==905 and fs['administrative_split_ballot_style_rows']==58 and not fs['additional_required_panel_pending_in_inventory'];op=BASE/fs['original_layout_overview']['path'];assert sha(op.read_bytes())==fs['original_layout_overview']['sha256'];checks['whole_retained_packet_and_available_printed_field_scope']=dict(source_documents=352,pages=3238,atlas_views=41,summary_panels=15,statistics_panels=14,vendor_profiles=45,split_rows=58,unprinted_values_unknown=True)
    ss=json.loads((OUT/'supplemental-2024-summary-readings.json').read_text());assert len(ss['summaries'])==3
    for r in ss['summaries']:
        assert sha(original(r['source_id']))==r['raw_sha256']
        for v in r['page'].values():
            if isinstance(v,dict):assert sha((BASE/v['path']).read_bytes())==v['sha256']
    split=json.loads((OUT/'union-split-ballot-style-readings.json').read_text());assert len(split['split_rows'])==58 and len(split['parents'])==20 and sum(r['total_voters'] for r in split['split_rows'])==sum(r['printed_TOTAL_voters'] for r in split['parents'])==17058 and split['split_total_minus_profile_registration']==-26;assert all(r['pair_weight'] is None and r['tie_target_status']=='unknown_candidate_allocation' for r in split['split_rows']);assert len({r['source_key'] for r in split['split_rows']})==58;checks['administrative_split_styles_unknown_candidate_targets']=dict(split_rows=58,parent_TOTALs=20,TotalVoters=17058,separate_profile_registration=17084,unallocated_difference=-26)
    cli=json.loads((OUT/'native-2018-selected-cli-scenarios.json').read_text());assert [r['status'] for r in cli['scenarios']]==['impossible','unknown_source_mark','no_positive_pool'];checks['historical2018_selected_cli_edge_states']=3
    finalrunpath=OUT/'source/reproduction-complete-original-v1/completion.json'
    if finalrunpath.exists():
        fr=json.loads(finalrunpath.read_text());assert fr['exit_code']==0 and fr['complete_owned_question']
        for pin in [fr['log'],fr['execution_reproducer']]+fr['input_witnesses']:
            body=(BASE/pin['path']).read_bytes();assert len(body)==pin['bytes']<40000000 and sha(body)==pin['sha256']
        for pin in fr['frozen_run_outputs']:
            z=(BASE/pin['stored_path']).read_bytes();r=gzip.decompress(z);assert len(z)==pin['stored_bytes']<40000000 and sha(z)==pin['stored_sha256'] and len(r)==pin['original_bytes'] and sha(r)==pin['original_sha256']
        checks['complete_original_offline_reproduction']=dict(receipt_path=str(finalrunpath.relative_to(BASE)),receipt_sha256=sha(finalrunpath.read_bytes()),exit_code=0,run_checks=fr['completed_main_checks'],qualification=fr['qualification'])
    v2=json.loads((OUT/'native-priority-v2-independent-validation.json').read_text());assert v2['status']=='pass_independent_source_position_order_and_integer_prefix_audit' and v2['native_units']==1736 and v2['all11_candidate_positions']==24926 and v2['exact_minimum80']==887 and v2['priority_parent_authorities']==77 and not v2['coordinator_accepted'] and not v2['current2026_geography_approved'];sp=BASE/v2['snapshot_path'];assert sp.stat().st_size==v2['snapshot_bytes'] and sha(sp.read_bytes())==v2['snapshot_sha256']
    for folder in ['native-priority-v2','native-priority-v2-field-evidence-v1']:
        snap=json.loads((OUT/'source'/folder/'snapshot.json').read_text())
        for pin in snap['pins']:
            z=(BASE/pin.get('frozen_path',pin.get('stored_path'))).read_bytes();r=gzip.decompress(z);assert sha(z)==pin['stored_sha256'] and len(z)==pin['stored_bytes']<40000000 and sha(r)==pin['original_sha256'] and len(r)==pin['original_bytes'];assert r==(BASE/pin['original_path']).read_bytes()
    checks['complete_named_field_887_v2_immutable_proposal']=v2
    refs=json.loads((OUT/'source/references.json').read_text());assert len({r['id'] for r in refs})==len(refs)
    for r in refs:
        stored=(BASE/r['path']).read_bytes();assert len(stored)<40000000;assert sha(stored)==r['stored_sha256'],r['id'];raw=gzip.decompress(stored) if r['path'].endswith('.gz') else stored;assert sha(raw)==r['raw_sha256'],r['id']
    checks['source_hashes_verified']=len(refs)
    coverage=json.loads((OUT/'native-coverage.json').read_text());checks['native_inventory']=coverage
    if coverage['extracted_pages']<coverage['expected_pages']:gaps.append('Complete-page native extraction still running; exact pending counts in native-coverage.json')
    nativechecks=json.loads((OUT/'native-control-checks.json').read_text());pending=[r for r in nativechecks if r['status']!='numeric_match_pending_identity_review'];checks['native_pending_control_groups']=len(pending)
    if pending:gaps.append('Machine-aid groups retain unaccepted OCR/locator differences; complete original reading ledgers and their explicit source exceptions are authority. No unresolved required panel identified in retained packet inventory.')
    hc=native2020['combined_counts'];gaps.append(f"2020 original native three-candidate review covers {hc['reviewed_source_publications']}/104 separate publications and {hc['reviewed_selected82_publications']}/82 selected county publications; this narrow named-Senate scope is complete. Complete164stage2018 named native vectors and available located vendor/native controls are reviewed; unprinted fields remain unknown.")
    observed=list(csv.DictReader(io.StringIO(gzip.decompress((OUT/'native-raw-cells.csv.gz').read_bytes()).decode())));assert len({r['observation_key'] for r in observed})==len(observed);checks['native_observation_keys_unique']=len(observed)
    gaps.extend(['Final signed November 2026 ballot/withdrawal/result IDs not established by SAMPLE or qualifying list','Generic write-in marks and valid/named write-in candidate scope differ from StateSEMS two-name certification','EAC2024 ballot universe below Senate pair in eight counties; no repair/rescaling','Historical source positions do not establish approved November2026 reporting/geometry identities'])
    links=[]
    for path in [BASE/'county-partisanship.md',OUT/'source/SCHEMA.md']:
        for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
            if target.startswith(('https://','http://','#')):continue
            dest=(path.parent/target.split('#')[0]).resolve();assert dest.exists(),(path,target);links.append(target)
    checks['relative_links_exist']=len(links)
    output=dict(status='pass_owned_research_with_explicit_source_limits',checks=checks,material_gaps=gaps,complete_owned_question=True,complete_native_question=True,completion_definition='All required county and original-source candidate/native scopes plus located required printed controls inventoried/reviewed and arithmetic validated; genuine unavailable fields and source disagreements retained. This does not imply whole historical independent peer replay, final2026 ballot/feed/geography/legal exhaustiveness or887acceptance.',current2026_geography_approved=False,priority887_accepted=False)
    save(OUT/'validation.json',output)
    assets=[]
    for path in sorted([BASE/'county-partisanship.md',BASE/'data/county-baselines.csv']+[p for p in OUT.rglob('*') if p.is_file() and p.name!='asset-manifest.json']):
        data=path.read_bytes();assert len(data)<40000000,str(path);assets.append(dict(path=str(path.relative_to(BASE)),bytes=len(data),sha256=sha(data)))
    save(OUT/'asset-manifest.json',dict(scope='all exclusive owned files; manifest excludes its self hash; external original references pinned separately',asset_count=len(assets),assets=assets,original_references=refs))
    print(json.dumps(dict(status=output['status'],checks=list(checks),native_coverage=coverage,assets=len(assets)),indent=2))
if __name__=='__main__':main()
