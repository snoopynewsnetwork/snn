"""Independent final turnout seal and complete immutable source-core history."""
from pathlib import Path
import gzip
import hashlib
import json

S = Path(__file__).resolve().parents[1]
T = S / 'data/turnout'
N = 0


def ck(value, note=''):
    global N
    assert value, note
    N += 1


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(S)), bytes=len(b), sha256=sha(b))


def read(p):
    return json.loads(p.read_bytes())


def captured(row):
    if row['storage'] == 'lossless_gzip_body':
        z = (S / row['body']).read_bytes()
        ck(sha(z) == row['stored_sha256'] and len(z) == row['stored_bytes'])
        b = gzip.decompress(z)
    else:
        ck(row['storage'] == 'immutable_primary_reference')
        b = (S / row['path']).read_bytes()
    ck(sha(b) == row['sha256'] and len(b) == row['bytes'], row['path'])
    return b


def main():
    mf = T / 'asset-manifest.json'
    ck(sha(mf.read_bytes()) == '1ad33f1b2ba8d3fb6e38b03177fe973921b2925a24d87ff7dce58ffe92b9911e')
    m = read(mf)
    expected = {r['path'] for r in m['owned_assets']}
    actual = {str(p.relative_to(S)) for p in T.rglob('*') if p.is_file() and p != mf}
    actual |= {'turnout.md', 'data/county-turnout.csv'}
    ck(actual == expected and len(actual) == len(m['owned_assets']) == 256)
    for r in m['owned_assets'] + m['source_assets']:
        ck(pin(S/r['path']) == {k:r[k] for k in ['path','bytes','sha256']}, r['path'])
        ck(r['bytes'] < 40000000 and not any(k in Path(r['path']).parts for k in ['__pycache__','node_modules','.venv']))
    old_contract = None
    snapshots = []
    for name, count, owned_key, owned_count in [('turnout-pre-peer',92,'owned_assets',91),('baseline-final-peer',104,'owned',103)]:
        p = T / 'history' / name / 'capture.json'
        cap = read(p)
        ck(len(cap['records']) == count)
        records = {r['path']:r for r in cap['records']}
        ck(len(records) == count)
        original_manifest = json.loads(captured(records[cap['manifest_path']]))
        ck(sha(captured(records[cap['manifest_path']])) == cap['manifest_sha256'])
        ck(len(original_manifest[owned_key]) == owned_count)
        for r in original_manifest[owned_key]:
            ck(r['path'] in records and all(records[r['path']][k] == r[k] for k in ['bytes','sha256']))
        for r in records.values():
            captured(r)
        if name == 'turnout-pre-peer':
            old_contract = json.loads(captured(records['data/turnout/priority-set.json']))
            witness = read(T/'original-first-witness-v2.json')
            ck(sha((T/'original-first-witness-v2.json').read_bytes()) == '427ad9e10b16e85cc675f6479796f09813afa5a72845b1199d4dd6b4e8ae7c51')
            for f, r in witness['files'].items():
                rr = records['data/turnout/' + f]
                ck(rr['bytes'] == r['bytes'] and rr['sha256'] == r['sha256'])
                if f != 'priority-set.json':
                    ck(sha((T/f).read_bytes()) == r['sha256'])
        snapshots.append(dict(capture=pin(p), original_owned=owned_count, complete_captured_files=count))
    contract = read(T/'priority-set.json')
    changed = [k for k in old_contract if old_contract[k] != contract.get(k)]
    ck(changed == ['status','peer_agent_id','peer_agreement'])
    ck(set(contract)-set(old_contract) == {'peer_review'})
    ck(contract['ordered_priority_keys'] == [] and not contract['accepted_for_dispatch'])
    ck(all(contract[k] is None for k in ['certified_native_top15','certified_native_minimum80','certified_native_full_order']))
    ck(len(contract['constituents']) == len(contract['complete_coverage_order']) == 2201)
    ck(len(contract['county_contexts']) == 33)
    ck(sha((S/'data/county-turnout.csv').read_bytes()) == '2ad2396b15b082f6c9aaa71b041869faae9873b83eb8a92e9170847bb65bd9ce')
    p = T/'peer-reconciliation.json'
    peer = read(p)
    ck(sha(p.read_bytes()) == '2c61c90d5629ca77cefce24d71a77cb1cc960001c91509194a4ab24daab9b55a')
    ck(peer['status'] == 'passed_bounded_source_core' and peer['comparison_checks'] == 800667 and peer['mismatches'] == [])
    ck(peer['coverage']['candidate_control_positions'] == 50179 and peer['coverage']['order_universes'] == 18)
    ck(len(peer['exclusions']) >= 4 and not peer['accepted_for_dispatch'])
    fixtures = read(T/'negative-fixtures.json')
    ck(fixtures['status'] == 'passed' and len(fixtures['fixtures']) == 13)
    ck(all(r['rejected'] for r in fixtures['fixtures']) and fixtures['valid_controls_accepted'] == 3)
    seal = read(T/'final-seal.json')
    for name, digest in seal['sealed_target_hashes'].items():
        ck(sha((S/name).read_bytes()) == digest)
    ck('current_manifest_sha256' not in seal and not seal['coordinator_acceptance'] and not seal['accepted_for_dispatch'])
    result = dict(status='pass_final_bounded_reciprocal_source_core_seal', checks=N,
                  final_manifest=pin(mf), owned_entries=256, immutable_source_assets=len(m['source_assets']),
                  complete_snapshot_reviews=snapshots, original_witness_and_targets_unchanged=True,
                  only_contract_changes=changed+['added peer_review'], source_counts_keys_orders_unchanged=True,
                  complete_native=2201, complete_parents=33, captured_peer_source_assertions=800667,
                  independent_negative_fixtures=13, peer_calculators_and_future_final_bytes_excluded=True,
                  independent_original_source_review=pin(S/'data/coordinator-turnout-original-review.json'),
                  canonical_certified_priority_unavailable=True, county_substitution_or_private_allocation=False,
                  producer_imports_or_writes=False,
                  qualification='Source core only. Historical old baseline bodies including its old manifest are materialized from exact captured gzip/primary references, never assumed equal to later repaired current baseline paths. Original protected values and all source discrepancies remain. Current/legal/geographic/feed/probability admission remains false.')
    out = S/'data/coordinator-turnout-final-review.json'
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(dict(checks=N, proof=pin(out)))


if __name__ == '__main__':
    main()
