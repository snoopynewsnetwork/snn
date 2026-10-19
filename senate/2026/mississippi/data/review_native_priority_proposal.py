"""Review the immutable worker887 proposal; this creates no acceptance record."""
from pathlib import Path
from collections import defaultdict
import csv
import gzip
import hashlib
import io
import json

DATA = Path(__file__).resolve().parent
ROOT = DATA.parent
PROPOSAL = DATA / 'baselines/source/native-priority-v1/snapshot.json'
NAMES = ['Ty Pinkins','Roger F. Wicker']


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(path):
    b = path.read_bytes()
    return {'path':str(path.relative_to(ROOT)),'bytes':len(b),'sha256':sha(b)}


def main():
    manifest = json.loads(PROPOSAL.read_bytes())
    assert manifest['coordinator_accepted'] is False
    assert manifest['full_original_field_method_native_history_gate'] is False
    assert manifest['current2026_geography_approved'] is False
    files = {}
    for p in manifest['pins']:
        stored = (ROOT / p['frozen_path']).read_bytes()
        raw = gzip.decompress(stored)
        assert (len(stored),sha(stored)) == (p['stored_bytes'],p['stored_sha256'])
        assert (len(raw),sha(raw)) == (p['original_bytes'],p['original_sha256'])
        assert len(stored) < 40000000
        files[Path(p['original_path']).name] = raw
    contract = json.loads(files['native-priority-contract.json'])
    orders = json.loads(files['native-source-orders.json'])
    proof = json.loads(files['native-order-peer-reconciliation.json'])
    replay_path = DATA / 'coordinator-qa/native-replay-84views/native-2024-senate-reviewed-84views.json.gz'
    replay_raw = gzip.decompress(replay_path.read_bytes())
    assert sha(replay_raw) == manifest['input_native_ledger_sha256'] == contract['input_ledger_sha256'] == orders['input_ledger_sha256']
    replay = json.loads(replay_raw)
    source_units = {}
    for s in replay['sources']:
        units = []
        for p in s['pages']:
            for c in p['columns']:
                if c['role'] != 'source_native_reporting_constituent':
                    continue
                units.append({'key':f'{s["county_fips"]}:{s["source_id"]}:p{p["page"]}:c{c["source_column"]}',
                    'parent_county_fips':s['county_fips'],'parent_county':s['county'],
                    'source_id':s['source_id'],'source_raw_sha256':s['raw_sha256'],
                    'source_page':p['page'],'source_column':c['source_column'],
                    'label_literal':c['label_literal'],'printed_native_id':c['printed_native_id'],
                    'header_bounds':c['header_bounds'],'candidate_bounds':{n:c['fields'][n]['source_box'] for n in NAMES},
                    'candidate_votes':{n:c['fields'][n]['value'] for n in NAMES}})
        source_units[s['source_id']] = units
    assert set(source_units) == set(orders['source_views']) and len(source_units) == 84
    compared = 0

    def check(units,view):
        nonlocal compared
        ordered = sorted(units,key=lambda u:(-sum(u['candidate_votes'].values()),u['key']))
        assert len(ordered) == len(view['full_descending_order']) == view['count']
        total = sum(sum(u['candidate_votes'].values()) for u in units)
        assert total == view['named_candidate_total']
        cumulative = 0
        for rank,(u,row) in enumerate(zip(ordered,view['full_descending_order']),1):
            assert all(row[k] == v for k,v in u.items())
            votes = sum(u['candidate_votes'].values())
            cumulative += votes
            assert row['named_candidate_votes'] == votes and row['rank'] == rank and row['cumulative_votes'] == cumulative
            assert abs(row['state_source_pair_weight']-votes/total) < 1e-15
            assert abs(row['share_of_explicit_denominator']-votes/view['explicit_80_denominator']) < 1e-15
            compared += 1
        return ordered

    for sid,units in source_units.items():
        check(units,orders['source_views'][sid])
    preferred = [u for sid,units in source_units.items() if sid not in ['sos-2024-county-coahoma','sos-2024-county-pike'] for u in units]
    ordered = check(preferred,orders['preferred82_view'])
    keys = [u['key'] for u in ordered]
    assert len(keys) == 1736 and compared == 3515
    assert contract['ordered_native_keys'] == keys
    assert contract['ordered_priority_native_keys'] == keys[:887]
    assert contract['ordered_nonpriority_native_keys'] == keys[887:]
    prior = json.loads((DATA / 'coordinator-native-order-review.json').read_bytes())
    assert prior['full1736_keys'] == keys and prior['ordered887_keys'] == keys[:887]
    primary = contract['primary_native_source_scope']
    assert primary['minimum80'] == prior['minimum80']
    assert primary['top15']['votes'] == 60019 and primary['remainder_votes'] == 242744
    assert primary['named_pair_votes'] == manifest['source_native_named_denominator'] == 1215400
    assert contract['separate_certified_county_denominator'] == manifest['certified_county_named_denominator'] == 1215401
    assert contract['unallocated_primary_disagreement']['allocation'] is None
    assert all(contract[k] is False for k in ['coordinator_accepted','full_all_candidate_method_historical_native_gate','current2026_geography_approved'])
    parents = {u['parent_county_fips'] for u in ordered}
    assert len(parents) == 82 and set(contract['parent_all_native_keys']) == set(contract['parent_priority_native_keys']) == parents
    for parent in parents:
        assert contract['parent_all_native_keys'][parent] == [u['key'] for u in ordered if u['parent_county_fips'] == parent]
        assert contract['parent_priority_native_keys'][parent] == [u['key'] for u in ordered[:887] if u['parent_county_fips'] == parent]
    assert sum(map(len,contract['parent_priority_native_keys'].values())) == 887
    rows = list(csv.DictReader(io.StringIO(files['native-full-order.csv'].decode(),newline='')))
    assert len(rows) == 1736
    for rank,(u,r) in enumerate(zip(ordered,rows),1):
        assert r['key'] == u['key'] and int(r['rank']) == rank
        assert int(r['Pinkins']) == u['candidate_votes']['Ty Pinkins']
        assert int(r['Wicker']) == u['candidate_votes']['Roger F. Wicker']
        assert r['primary_priority'] == str(rank<=887)
        assert r['label_literal'] == u['label_literal']
        assert json.loads(r['candidate_bounds']) == u['candidate_bounds']
    assert proof['own_sha256'] == sha(files['native-source-orders.json'])
    assert proof['compared_ordered_unit_positions'] == 3515 and proof['compared_candidate_fields'] == 7030
    assert proof['exact_order_key_candidate_parent_rank_cumulative_disagreements'] == 0
    assert proof['working_peer_ID_addition_unique_source_positions'] == 43
    assert proof['all849nonpriority_native_units_retained'] is True
    assert proof['coordinator_accepted'] is False and proof['current2026_geography_approved'] is False
    outcome = {
        'status':'pass_bounded_immutable_v1_887_native_proposal_no_dispatch_acceptance',
        'proposal_snapshot_manifest':pin(PROPOSAL),'worker_frozen_file_pins':manifest['pins'],
        'independent_replay_input':pin(replay_path),'source_views':84,'preferred_native_units':1736,
        'ordered_unit_positions':3515,'candidate_positions':7030,'primary_ordered_keys':887,
        'nonpriority_keys':849,'all_parent_maps':82,
        'parents_with_priority_children':sum(bool(v) for v in contract['parent_priority_native_keys'].values()),
        'parent_county_sensitivity_not_dispatch':contract['county_parent_sensitivity'],
        'source_denominator':1215400,'separate_certified_denominator':1215401,
        'unallocated_difference':contract['unallocated_primary_disagreement'],
        'upper_bound_proof':contract['unknown_Tunica1_upper_bound_proof'],
        'optional_ID_metadata_scope':contract['optional_printed_ID_metadata_scope'],
        'coordinator_dispatch_acceptance':False,'scope':'The coherent immutable v1 four-file proposal matches independent frozen source readings and coordinator full order, including exact887 arrays,849 remainder, all82 parent/all-child/priority-child maps and3515 order positions.77 parent authorities contain at least one priority child; this does not make the county41 sensitivity the dispatch. This bounded review creates no acceptance authority or second-wave authorization. Remaining original all-candidate/method/historical native gates and current geographic/reporting approval remain separate.'}
    (DATA / 'coordinator-native-priority-v1-review.json').write_text(json.dumps(outcome,indent=2)+'\n')
    print(json.dumps({k:outcome[k] for k in ['status','source_views','preferred_native_units','ordered_unit_positions','candidate_positions','primary_ordered_keys','parents_with_priority_children']}))


if __name__ == '__main__':
    main()
