"""Mark verified 2024 named-field scope in the working dispatch contract.

This changes no immutable priority witness and makes no method, historical,
current-geography or coordinator-acceptance claim.
"""
import gzip,json
from acquire_sources import BASE,OUT,sha,savejson
from build_2024_all11_contract_dependency import build as attach_all11_dependency
from build_historical_native_dependencies import build as attach_historical_native_dependencies
from attach_complete_peer_v2 import attach as attach_complete_peer_v2

def main():
    recorded={}
    for n in range(2,34):
        path=OUT/f'batch{n}-presidential-original-readings.json'
        batch=json.loads(path.read_text())
        assert batch['source_view_count']==len(batch['sources'])
        for s in batch['sources']:
            assert len(s['candidate_checks'])==9 and all(x['passes'] for x in s['candidate_checks'].values())
            assert not s.get('independent_peer_position_differences',s.get('independent_peer_value_role_label_differences',[]))
            sid=s['source_id'];assert sid not in recorded
            recorded[sid]=dict(path=str(path.relative_to(OUT)),sha256=sha(path.read_bytes()),native_constituents=s['native_constituents'])
    for name in ('hinds-presidential-original-readings.json','small-presidential-original-readings.json'):
        path=OUT/name;body=json.loads(path.read_text());sources=body['sources'] if 'sources' in body else [body]
        for s in sources:
            assert len(s['candidate_checks'])==9 and all(x['passes'] for x in s['candidate_checks'].values())
            assert not s.get('independent_peer_position_differences',s.get('independent_peer_value_role_label_differences',[]))
            sid=s['source_id'];assert sid not in recorded
            recorded[sid]=dict(path=name,sha256=sha(path.read_bytes()),native_constituents=s['native_constituents'])
    for name in ('tunica-presidential-original-readings.json','perry-presidential-original-readings.json','winston-allfield-original-readings.json'):
        path=OUT/name;s=json.loads(path.read_text());assert len(s['candidate_checks'])>=9 and all(x['passes'] for x in s['candidate_checks'].values())
        sid=s['source_id'];assert sid not in recorded
        recorded[sid]=dict(path=name,sha256=sha(path.read_bytes()),native_constituents=s.get('source_native_count',12))
    controls_path=OUT/'native-allfield-controls.json';controls=json.loads(controls_path.read_text())
    assert controls['source_views']==2
    for c in controls['checks']:
        assert c['all11_candidates_reconcile'] and len(c['native_sums'])==11
        assert c['native_sums']==c['printed_TOTAL_values']==c['county_primary_controls']
        sid=c['source_id'];assert sid not in recorded
        recorded[sid]=dict(path=str(controls_path.relative_to(OUT)),sha256=sha(controls_path.read_bytes()),native_constituents=None)
    units=json.loads(gzip.decompress((OUT/'native-constituents-reviewed.json.gz').read_bytes()))
    preferred=[x for x in units if x['role']=='native_reporting_constituent' and x['source_id'] not in ('sos-2024-county-coahoma','sos-2024-county-pike')]
    ids={x['source_id'] for x in preferred}
    assert len(ids)==len(recorded)==82 and ids==set(recorded)
    assert len(preferred)==1736 and len({x['key'] for x in preferred})==1736
    senate=json.loads((OUT/'native-reviewed-peer-reconciliation-84views.json').read_text())
    assert senate['compared_candidate_positions']==4642 and senate['source_views']==84 and not senate['differences'] and not senate['printed_native_id_value_differences']
    two=json.loads((OUT/'native-allfield-peer-reconciliation.json').read_text())
    assert len(two['results'])==2 and all(x['status']=='agree_all_fields_in_reviewed_scope' and not x['differences'] for x in two['results'])
    path=OUT/'priority-set.json';contract=json.loads(path.read_text());coverage=contract['coverage']
    assert contract['status']=='in_progress_not_coordinator_accepted'
    assert contract['current_2026_geographic_approval'] is False
    assert coverage['preferred82_native_constituents']==1736
    coverage['reviewed_all11_candidate_source_views']=82
    coverage['complete_preferred82_original_named_candidate_fields_2024_Senate_and_president']=True
    coverage['native_unit_extraction']='complete_2024_preferred_named_candidates_other_fields_in_progress'
    contract['peer_agreement']=dict(native_fields_complete=False,
        scope='2024 Senate all84 source views agree the independent frozen84 source-bound two-candidate witness; nine presidential fields have complete original preferred82 coverage and bounded post-reading peer comparisons, including separately reviewed Tunica/Perry/Winston and Alcorn/Coahoma. Full generic/method/historical/current-geography agreement remains open.',
        senate_source_views=84,senate_candidate_positions=4642,
        presidential_preferred_source_views=82,presidential_native_constituents=1736,
        senate_reconciliation_path='data/turnout/native-reviewed-peer-reconciliation-84views.json',
        allfield_two_view_reconciliation_path='data/turnout/native-allfield-peer-reconciliation.json')
    complete_peer_snapshot=BASE/'data/baselines/source/2024-all11-complete-peer-v1/snapshot.json'
    complete_peer_reconciliation=BASE/'data/baselines/source/2024-all11-complete-peer-v1/reconciliation.json'
    peer_snapshot_raw=complete_peer_snapshot.read_bytes()
    peer_snapshot=json.loads(peer_snapshot_raw)
    peer_reconciliation=json.loads(complete_peer_reconciliation.read_text())
    assert sha(peer_snapshot_raw)==peer_reconciliation['input_snapshot']['sha256']
    peer_body_pin=peer_snapshot['peer_body']
    stored=(BASE/peer_body_pin['path']).read_bytes()
    raw=gzip.decompress(stored)
    assert len(stored)==peer_body_pin['stored_bytes'] and sha(stored)==peer_body_pin['stored_sha256']
    assert len(raw)==peer_body_pin['original_bytes'] and sha(raw)==peer_body_pin['original_sha256']
    assert peer_reconciliation['status']=='pass_post_original_complete_preferred82_all11_source_position_replay'
    assert peer_reconciliation['source_views']==82 and peer_reconciliation['source_columns']==2266
    assert peer_reconciliation['positions']==24926 and peer_reconciliation['native_units']==1736
    assert not peer_reconciliation['value_role_differences']
    contract['peer_agreement'].update({
        'named_2024_Senate_and_president_source_fields_complete':True,
        'complete_preferred82_all11_source_positions':24926,
        'complete_preferred82_all11_peer_snapshot_path':str(complete_peer_snapshot.relative_to(BASE)),
        'complete_preferred82_all11_peer_snapshot_sha256':sha(peer_snapshot_raw),
        'complete_preferred82_all11_peer_reconciliation_path':str(complete_peer_reconciliation.relative_to(BASE)),
        'complete_preferred82_all11_peer_reconciliation_sha256':sha(complete_peer_reconciliation.read_bytes()),
        'complete_preferred82_all11_peer_body_exact_pin':peer_body_pin,
        'literal_label_representation_aliases':len(peer_reconciliation['literal_label_representation_aliases']),
        'qualification':'All82 preferred source columns/24926 all11 named candidate-or-null positions agree on values and roles after original reading. Holmes wraps and raster/window/optional-ID differences remain explicit. Generic/method/current geography agreement is outside this named-field flag.'})
    contract=attach_all11_dependency(contract)
    styles_path=OUT/'2024-union-ballot-styles-original-reading.json'
    styles=json.loads(styles_path.read_text())
    styles_peer_path=OUT/'2024-union-ballot-styles-peer-reconciliation.json'
    styles_peer=json.loads(styles_peer_path.read_text())
    assert styles_peer['status']=='agree_all_original_source_rows' and not styles_peer['differences']
    assert styles_peer['own_sha256']==sha(styles_path.read_bytes())
    assert len(styles['split_rows'])==58 and len(styles['parent_TOTAL_rows'])==20
    assert styles['printed_Grand_Total_voters']==17058 and styles['candidate_votes_available_on_these_pages'] is False
    contract['source_native_nonadditive_ballot_style_report']={
        'source_id':styles['source_id'],'source_raw_sha256':styles['source_raw_sha256'],
        'original_reading_path':str(styles_path.relative_to(OUT)),
        'original_reading_sha256':sha(styles_path.read_bytes()),
        'independent_peer_comparison_path':str(styles_peer_path.relative_to(OUT)),
        'independent_peer_comparison_sha256':sha(styles_peer_path.read_bytes()),
        'report_number':styles['report_number_literal'],
        'printed_grand_total_voters':17058,
        'separate_vendor_profile_registration':17084,
        'candidate_vote_scope':'all split and parent candidate values unprinted; null, never allocated from county totals',
        'split_rows':[dict(r,senate_candidate_votes=None,presidential_candidate_votes=None,
                           additive_with_preferred_native=False) for r in styles['split_rows']],
        'printed_parent_TOTAL_rows':[dict(r,senate_candidate_votes=None,presidential_candidate_votes=None,
                                          additive_with_splits=False,additive_with_preferred_native=False) for r in styles['parent_TOTAL_rows']],
        'current_2026_geographic_approval':False}
    coverage['nonadditive_source_native_ballot_style_split_rows']=58
    coverage['nonadditive_source_native_ballot_style_parent_TOTAL_rows']=20
    styles_note=' Union BP-009 split/style rows and their printed parent TOTALs form a separate nonadditive administrative source view with no candidate values or crosswalk.'
    if styles_note not in contract['source_native_hierarchy']:
        contract['source_native_hierarchy'] += styles_note
    e013_path=OUT/'2024-extra-e013-original-summary-readings.json'
    e013=json.loads(e013_path.read_text())
    assert e013['source_views']==3 and e013['named_candidate_rows']==33
    assert {s['source_id'] for s in e013['sources']}=={'sos-2024-county-bolivar','sos-2024-county-grenada','sos-2024-county-itawamba'}
    contract['source_native_nonadditive_E013_county_summaries']={
        'original_reading_path':str(e013_path.relative_to(OUT)),
        'original_reading_sha256':sha(e013_path.read_bytes()),
        'county_aggregate_views':e013['sources'],
        'additive_to_preferred_native':False,
        'method_ballot_registration_fields_available':False,
        'current_2026_geographic_approval':False}
    coverage['nonadditive_E013_county_summary_views']=3
    contract=attach_historical_native_dependencies(contract)
    contract=attach_complete_peer_v2(contract)
    savejson(path,contract)
    savejson(OUT/'2024-named-contract-coverage-audit.json',dict(scope='Working priority contract 2024 named-field coverage only; frozen887 v1 unchanged; no current geography, full method or historical native acceptance.',
        preferred_source_views=82,preferred_native_constituents=1736,
        all11_original_source_reading_pins=recorded,
        senate_peer_reconciliation_sha256=sha((OUT/'native-reviewed-peer-reconciliation-84views.json').read_bytes()),
        two_view_allfield_peer_reconciliation_sha256=sha((OUT/'native-allfield-peer-reconciliation.json').read_bytes()),
        preferred_all11_dependency=contract['preferred_2024_all11_source_fields_dependency'],
        priority_contract_sha256=sha(path.read_bytes())))
    print('Working priority contract: 82 preferred original all11 source views; 1736 native; broad method/historical/current acceptance open')

if __name__=='__main__':main()
