#!/usr/bin/env python3
"""Executed offline checks and complete owned asset inventory. No self-hash cycle."""
import csv,gzip,json,math,re,sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote,urlparse
sys.dont_write_bytecode=True
from acquire import HERE,STATE,sha,pin,dump
from build import loadgz,CONTESTS,PRES,S22,S20,COUNTIES,native
from calculator import uniform,selected,remainder

def run():
    checks={};gaps=[]
    refs=pin();checks['shared_original_hashes_verified']=len(refs)
    inv=json.loads((HERE/'source/extraction-inventory.json').read_text());cs=json.loads((HERE/'source/controls.json').read_text());rec=json.loads((HERE/'reconciliation.json').read_text())
    invd={r['source_id']:r for r in inv};peerinv={r['source_id']:r for r in json.loads((STATE/'data/turnout/extracts/index.json').read_text())}
    count=0;candidatechecks=0
    for r in rec:
        sid=r['source_id'];ns=native(sid);assert len(ns)==320
        assert {x['county'] for x in ns}==set(COUNTIES)
        assert len({(x['county'],x['native_label'],json.dumps(x['source_locator'],sort_keys=True)) for x in ns})==320
        assert invd[sid]['original_decoded_sha256']==peerinv[sid]['original_sha256'],sid
        count+=1
        if sid in CONTESTS or 'senator' in sid or 'president' in sid or sid==S20:
            assert not r['county_control_disagreements'],sid
            for f,v in r['numeric_native_sums'].items():
                if r['state_control'][f] is not None:assert v==r['state_control'][f],(sid,f)
            candidatechecks+=1
    assert count==23;checks.update(source_rosters_320_each=count,source_scoped_native_records=count*320,decoded_source_hashes_compared_to_peer=count,all_candidate_source_county_state_balances=candidatechecks)
    expected={PRES:dict(harris_walz=418488,trump_vance=395523,oliver_ter_maat=4425,stein_ware=3680,undervotes=4482,overvotes=362,generic_write_ins=4073),S22:dict(hassan=332490,bolduc=275631,kauffman=12390,scatter=464),S20:dict(shaheen=450778,messner=326229,odonnell=18421,scatter=486)}
    for sid,f in expected.items():assert next(x for x in rec if x['source_id']==sid)['numeric_native_sums']==f
    with (STATE/'data/county-baselines.csv').open() as f:bs=list(csv.DictReader(f))
    assert len(bs)==960 and len({(r['source_id'],r['geography_key']) for r in bs})==960
    for sid,m in CONTESTS.items():
        rows=[r for r in bs if r['source_id']==sid];assert len(rows)==320
        for key in m['candidates']:assert sum(int(r[key]) for r in rows if r[key]!='')==expected[sid][key]
        for r in rows:
            if r['A_votes'] and r['B_votes']:
                t=int(r['A_votes'])+int(r['B_votes']);assert t==int(r['pair_votes'])
                if t:assert abs(float(r['A_pair_share'])-int(r['A_votes'])/t)<1e-14
    checks['baseline_csv_rows']=len(bs)
    # State/county hierarchy partitions exactly once; parents are display only.
    h=json.loads((HERE/'hierarchy.json').read_text())
    for sid in CONTESTS:
        leaves=[g for c in h if c['source_id']==sid for p in c['parents'] for g in p['children']]
        assert len(leaves)==320 and len({x['geography_key'] for x in leaves})==320
        assert all(c['county_is_control_not_leaf'] for c in h if c['source_id']==sid)
    checks['disjoint_hierarchy_contests']=3
    p=json.loads((HERE/'priority-set.json').read_text());ls=p['all_units'];assert len(ls)==320
    assert ls==sorted(ls,key=lambda r:(-r['reported_candidate_write_in_votes'],r['county_fips'],r['native_label'].strip()))
    total=sum(r['reported_candidate_write_in_votes'] for r in ls);assert total==826189
    n=p['minimum80_count'];cum=sum(r['reported_candidate_write_in_votes'] for r in ls[:n]);prev=sum(r['reported_candidate_write_in_votes'] for r in ls[:n-1]);assert (n,cum,prev)==(143,662624,660378)
    assert 5*prev<4*total<=5*cum and ls[n-1]['native_label']=='Tilton'
    assert sum(r['reported_candidate_write_in_votes'] for r in ls[:15])==185659
    assert sum(r['reported_candidate_write_in_votes'] for r in ls[n:])==163565
    accepted=json.loads((STATE/'data/coordinator-priority-acceptance.json').read_text());frozen=STATE/'data/turnout/priority-set.json';assert accepted['accepted'] is True
    assert sha(frozen.read_bytes())==accepted['contract_sha256']=='11c042966c67a50e496ad6f839afd8e3c8b28afe6e2761c6cda1aa51f7ce90fc'
    assert len(frozen.read_bytes())==3653481
    assert accepted['full_ordered_keys']==p['full_ordered_keys'] and accepted['ordered_priority_keys']==p['ordered_priority_keys']
    checks['priority']=dict(all_native=320,denominator=total,top15_votes=185659,minimum80_count=n,minimum80_votes=cum,preceding_votes=prev,crossing='Tilton',remainder_votes=163565,formal_acceptance_reference='data/coordinator-priority-acceptance.json',current_geography_approval=False)
    peer=json.loads((HERE/'peer-reconciliation.json').read_text())
    for k in ['priority_field_disagreements','source_native_disagreements','raw_value_disagreements','BIFF_type_disagreements']:assert peer[k]==[],k
    assert all(r['full_candidate_method_fields_equal'] for r in peer['source_native_checks'])
    checks['peer']=dict(rosters=len(peer['source_native_checks']),parsed_fields=peer['parsed_fields_compared'],raw_values=peer['raw_values_compared'],BIFF_types=peer['BIFF_types_compared'],disagreements=0)
    # Retained source defects are assertions about evidence, not fixes.
    r=next(x for x in rec if x['source_id']=='2024-ge-ballots-cast-14-xls');assert r['state_control']['regular']+r['state_control']['absentee']-r['state_control']['ballots_cast']==1
    assert r['numeric_native_sums']['ballots_cast']==831468 and r['state_control']['ballots_cast']==831467
    assert len(r['county_control_disagreements'])==2 and len(r['native_identity_disagreements'])==1
    r=next(x for x in rec if x['source_id']=='2024-ge-names-on-checklist-7-xlsx');assert len(r['native_identity_disagreements'])==1 and r['native_identity_disagreements'][0]['component_sum']==296 and r['native_identity_disagreements'][0]['reported']==3
    checks['preserved_source_defects']=dict(ballots2024_native_minus_state=1,ballots2024_state_component_minus_total=1,Coos_absentee_and_total_residual=1,Somersworth_Ward3_component_minus_total=1,Hopkinton_new_reg_component_minus_total=293,Senate2022_Clerk_vs_selected_Hassan=-297,Senate2022_Clerk_vs_selected_Bolduc=297)
    def readcsv(f):return list(csv.DictReader((HERE/f).open()))
    ss=readcsv('state-scenarios.csv');nt=readcsv('native-targets.csv');ct=readcsv('county-targets.csv');assert (len(ss),len(nt),len(ct))==(16,5120,160)
    worst=0.
    for s in ss:
        subset=[r for r in nt if r['scenario']==s['scenario'] and r['target']==s['target']];assert len(subset)==320 and len({r['geography_key'] for r in subset})==320
        T=float(s['total_pair_votes']);goal=float(s['target_net_votes']);net=sum(float(r['target_net_votes']) for r in subset);err=abs(net-goal);worst=max(worst,err);assert err<1e-7
        assert abs(sum(float(r['pair_weight']) for r in subset)-1)<1e-12
        assert abs(sum(float(r['pair_volume']) for r in subset)-T)<1e-7
        C=float(s['all_reported_candidate_generic_volume']);assert abs(sum(float(r['all_reported_volume']) for r in subset)-C)<1e-7
        assert abs(100*goal/C-float(s['target_all_reported_margin_pp']))<1e-12
        for r in subset:
            t=float(r['pair_volume']);q=r['target_A_pair_share']
            if q!='':assert 0<=float(q)<=1
            else:assert t==0
            assert abs(float(r['net_votes_per_1pp_A_share'])-.02*t)<1e-9
            if r['selected_only_required_share_unbounded']:
                req=float(r['selected_only_required_share_unbounded']);fixed=float(r['other_fixed_net_votes'])
                assert abs(fixed+t*(2*req-1)-goal)<1e-7
        county=[r for r in ct if r['scenario']==s['scenario'] and r['target']==s['target']];assert len(county)==10
        for c in county:
            ns=[r for r in subset if r['county']==c['county']];assert abs(sum(float(r['target_net_votes']) for r in ns)-float(c['target_net_votes']))<1e-7
        tie=next(r for r in ss if r['scenario']==s['scenario'] and r['target']=='tie')
        if s['target']!='tie':assert abs(float(s['unbounded_shift_share_pp'])-float(tie['unbounded_shift_share_pp'])-.5)<1e-12
    checks['scenario_arithmetic']=dict(state_rows=16,native_rows=5120,county_rows=160,all_state_native_leaves=320,tolerance_net_votes=1e-7,max_target_residual_votes=worst,weights_sum_tolerance=1e-12,unbounded_A_plus1_minus_tie_share_pp=.5)
    clipped=uniform([1,99],[0,1],0);assert clipped['unbounded_would_clip'] and abs(clipped['achieved_net_votes'])<1e-10
    assert uniform([],[])['status']=='no_positive_pool'
    assert uniform([1],[.5],1.1)['status']=='impossible_bounded_target'
    assert uniform([1],[None])['status']=='unknown_preference_for_positive_pool'
    win=uniform([100],[.6]);assert win['baseline_meets_target'] and win['unbounded_shift_share_pp']<0
    assert selected([0],[None],0)['status']=='no_positive_pool'
    assert remainder(dict(counted=dict(A=1,B=1,others={}),remaining=[dict(key='same',total_candidate_votes=0,pair_fraction=1,A_pair_share=.5)]*2))['status']=='invalid_duplicate_remaining_unit_key'
    checks['bounded_solver_edge_cases']=6
    checks['duplicate_remaining_unit_rejected']=True
    inputs=json.loads((HERE/'synthetic-inputs.json').read_text());saved=json.loads((HERE/'synthetic-results.json').read_text());actual=[remainder(x) for x in inputs];assert saved==actual and len(saved)==20
    by={r['label']:r for r in saved}
    for i,r in zip(inputs,saved):assert r['counted_fixed']==i['counted']
    assert by['unknown_pool']['status']=='unknown_remaining_pool'
    assert by['negative_pool_rejected']['status']=='invalid_negative_or_nonfinite_pool'
    assert by['negative_count_rejected']['status']=='invalid_counted_votes'
    assert by['impossible_remainder']['requirement_status']=='impossible_at_all_A'
    assert by['secured_against_B']['requirement_status']=='already_secured_at_all_B'
    for k in ['clip_A_share_high','clip_A_share_negative']:assert by[k]['remaining_forecast'][0]['share_was_clipped']
    x=by['final_pair_denominator_A_plus_1'];assert x['final_pair_denominator']==300 and x['final_candidate_denominator']==330 and abs(x['required_remaining_A_pair_share_unbounded']-.64375)<1e-14
    assert abs(by['final_all_candidate_denominator_A_plus_1']['required_remaining_A_pair_share_unbounded']-.645625)<1e-14
    assert by['pair_win_but_other_wins']['conditional_plurality_status']=='A_tied_or_behind_a_named_opponent'
    assert not by['pair_win_but_other_wins']['strict_plurality_possible_under_pool']
    assert by['unallocated_others_legal_status_unknown']['conditional_plurality_status']=='unresolved_named_other_allocation'
    assert by['selected_only_impossible_others_fixed']['selected_requirement']['status']=='impossible_at_all_A'
    assert by['selected_only_secured_others_fixed']['selected_requirement']['status']=='already_secured_at_all_B'
    checks['synthetic_scenarios']=dict(executed=20,counted_votes_fixed=True,final_denominators_verified=True,plurality_distinct_from_pair=True,calibrated_probabilities=False)
    # Every owned raw derivative is structurally readable and source-scoped.
    rawcount=0
    for f in (HERE/'raw').glob('*.jsonl.gz'):
        rows=loadgz(f);assert len(rows)==invd[f.name.removesuffix('.jsonl.gz')]['raw_rows'];rawcount+=len(rows)
    checks['raw_source_rows_verified']=rawcount
    for f in (HERE/'source').glob('*.json'):
        m=json.loads(f.read_text())
        if not isinstance(m,dict) or 'body_path' not in m:continue
        body=(f.parent/m['body_path']).read_bytes();assert sha(body)==m['stored_sha256']
        decoded=gzip.decompress(body);assert sha(decoded)==m['original_sha256'] and len(decoded)==m['original_bytes']
        headers=(f.parent/m['headers_path']).read_bytes();assert sha(headers)==m['headers_sha256']
    generated={HERE/'validation.json',HERE/'asset-manifest.json'};missing=[];linkcount=0
    for md in [STATE/'county-partisanship.md',HERE/'source/SCHEMA.md']:
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',md.read_text()):
            if urlparse(target).scheme or target.startswith('#'):continue
            path=(md.parent/unquote(target.split('#')[0])).resolve();linkcount+=1
            if not path.exists() and path not in generated:missing.append(str(path))
    assert not missing,missing;checks['relative_links_checked']=linkcount
    paths=[STATE/'county-partisanship.md',STATE/'data/county-baselines.csv']+sorted(x for x in HERE.rglob('*') if x.is_file() and x.name!='asset-manifest.json')
    assert not any(x.name in ['__pycache__','node_modules','.cache'] for x in HERE.rglob('*'))
    assert all(x.stat().st_size<40000000 for x in paths)
    checks['asset_bounds']='Every owned asset strictly below40000000 bytes; no cache/dependency directories; complete original-byte references hash-verified.'
    gaps=['Final valid/named historical write-in allocation and generic-vote validity scope unavailable; generic fields retained separately.', 'Historical legal certification/amendment issuance sequence not independently resolved for every vintage; Clerk2022 vs SOS2022 297-vote shift preserved.', 'Current Farmington official general sample ballot verified; statewide current result-feed candidate IDs/ballot-style mapping and subsequent amendments unverified.', 'Historical native labels/identifiers do not approve2026 boundaries or establish cross-year ward equivalence/clerk authority.', '2024ballots and checklist source discrepancies preserved; exact administrative registration as-of instant and active/inactive scope unknown.', 'No2026 turnout projection, remaining-vote estimate, candidate/method/lower-preference inference, live collector, measured cadence or calibrated probability.']
    validation=dict(schema_version='nh-baselines-validation-1.0',status='pass_with_explicit_primary_source_disagreements_and_operational_gaps',checks=checks,gaps=gaps,asset_manifest_protocol='Written after this file; includes this file hash; no reverse hash or manifest self-hash.',provenance='Executed offline against retained original bytes and independently regenerated calculations.')
    dump(HERE/'validation.json',validation)
    paths=[STATE/'county-partisanship.md',STATE/'data/county-baselines.csv']+sorted(x for x in HERE.rglob('*') if x.is_file() and x.name!='asset-manifest.json')
    assets=[dict(path=str(p.relative_to(STATE)),bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in paths]
    manifest=dict(schema_version='nh-baselines-assets-1.0',scope='Only assigned partisanship paths; state-relative paths.',self_hash_excluded='data/baselines/asset-manifest.json; self-hash would be recursive. All other owned files including validation hashed.',assets=assets,shared_original_references=[{k:r[k] for k in ['id','path','stored_sha256','original_sha256','original_bytes']} for r in refs],coordinator_acceptance_authority='data/coordinator-priority-acceptance.json',worker_acceptance_authority=False)
    dump(HERE/'asset-manifest.json',manifest)
    for r in assets:
        b=(STATE/r['path']).read_bytes();assert len(b)==r['bytes'] and sha(b)==r['sha256'] and len(b)<40000000
    assert (HERE/'asset-manifest.json').stat().st_size<40000000
    print(json.dumps(dict(status=validation['status'],owned_assets=len(assets),shared_originals=len(refs),baseline_rows=960,native_target_rows=5120,synthetic_cases=20,priority_units=143,all_native=320,all_asset_hashes_verified=True)))
if __name__=='__main__':run()
