"""Independent full dispatch graph replay; no producer code or mutations."""
from pathlib import Path
from collections import Counter
import csv
import gzip
import hashlib
import io
import json

S = Path(__file__).resolve().parents[1]
D = S/'data'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def canonical(v):
    return json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()


def exact(r):
    b = (S/r['path']).read_bytes()
    assert len(b) == r['bytes'] < 40000000 and sha(b) == r['sha256']
    return b


def read(name):
    p = S/name
    b = p.read_bytes()
    b = gzip.decompress(b) if p.suffix == '.gz' else b
    if '.csv' in p.name:
        return list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))
    if '.jsonl' in p.name:
        return [json.loads(line) for line in b.splitlines() if line]
    return json.loads(b)


def pointer(value, p):
    for k in p.split('/')[1:]:
        k = k.replace('~1', '/').replace('~0', '~')
        value = value[int(k)] if isinstance(value, list) else value[k]
    return value


def main():
    a = read('data/coordinator-priority-acceptance.json')
    c = json.loads(exact(a['frozen_contract']))
    assert len(c) == len(a['complete_root_field_semantics']) == 24
    for r in a['complete_root_field_semantics']:
        assert sha(canonical(pointer(c, r['pointer']))) == r['full_recursive_semantic_sha256']
    for group in ('frozen_first_pair_assets', 'independent_coordinator_reviews'):
        for r in a[group]:
            exact(r)
    assets = 0
    for r in a['producer_seals']:
        mf = json.loads(exact(r))
        listed = mf[r['owned_field']]
        assert len(listed) == r['owned_entries_excluding_manifest']
        assets += len(listed)
        for record in listed:
            exact(record)
    refs = read('data/baselines/source/original-references.json')
    for r in refs:
        if 'inherited_receipt_path' in r:
            assert sha((D/'baselines/source'/r['inherited_receipt_path']).read_bytes()) == r['inherited_receipt_sha256']
        if r.get('body_reference'):
            p = D/'baselines/source'/r['body_reference']
            z = p.read_bytes()
            raw = gzip.decompress(z) if p.suffix == '.gz' else z
            assert len(z) == r['stored_bytes'] < 40000000 and sha(z) == r['stored_sha256']
            assert len(raw) == r['raw_bytes'] and sha(raw) == r['raw_sha256']
    for record in read('data/turnout/pre-peer-witness.json')['original_pins']:
        exact(record)
    for r in a['complete_source_companion_files']:
        b = exact(r)
        if r['path'].endswith('.gz'):
            b = gzip.decompress(b)
            assert len(b) == r['complete_reconstructed_bytes'] and sha(b) == r['complete_reconstructed_sha256']
        value = read(r['path'])
        assert sha(canonical(value)) == r['full_semantic_sha256'] and len(value) == r['complete_length']
    total = 0
    global_counts = Counter()
    for r in a['complete_source_object_reference_bodies']:
        exact(r)
        digest = hashlib.sha256()
        size = count = 0
        by_file = Counter()
        filename = value = None
        with gzip.open(S/r['path'], 'rb') as f:
            for line in f:
                digest.update(line)
                size += len(line)
                row = json.loads(line)
                if row['file'] != filename:
                    filename = row['file']
                    value = read(filename)
                obj = pointer(value, row['pointer']) if 'pointer' in row else value[row['CSV_row_1based_including_header']-1]
                assert sha(canonical(obj)) == row['full_recursive_semantic_sha256'], row
                count += 1
                by_file[filename] += 1
        assert size == r['complete_reconstructed_bytes'] and digest.hexdigest() == r['complete_reconstructed_sha256']
        assert count == r['complete_object_count'] and dict(by_file) == r['source_objects_by_file']
        total += count
        global_counts.update(by_file)
    assert total == a['complete_source_object_count'] == 724943
    assert dict(global_counts) == a['source_objects_by_file']
    keys = a['ordered_full_keys']
    priority = a['ordered_priority_keys']
    remainder = a['ordered_remainder_keys']
    assert keys == priority + remainder and (len(keys), len(priority), len(remainder)) == (575, 233, 342)
    assert keys == c['complete_ordered_keys'] and priority == c['ordered_priority_keys'] and remainder == c['remainder']['ordered_keys']
    assert len(a['derived_ordered_child_arrays_by_parent']) == len(a['ordered_priority_parent_FIPS']) == 21
    units = {u['key']: u for u in c['all_units']}
    for fips, parent in a['derived_ordered_child_arrays_by_parent'].items():
        ranked = [k for k in keys if units[k]['county_fips'] == fips]
        assert ranked == parent['canonical_rank_ordered_children']
        assert set(ranked) == set(parent['original_source_ordered_children'])
        assert [k for k in ranked if k in set(priority)] == parent['ordered_priority_children']
        assert [k for k in ranked if k in set(remainder)] == parent['ordered_remainder_children']
    for field in ('current_geography_approved', 'current_November_returns_admitted', 'current_choice_or_reporting_IDs_approved',
                  'legal_native_80_robustness_approved', 'live_cadence_or_exact_remainder_approved', 'collector_or_probability_approval'):
        assert a[field] is False
    p = D/'coordinator-acceptance-validation.json'
    out = dict(status='pass_independent_complete_dispatch_reconstruction', complete_root_fields=len(c),
               complete_companions=len(a['complete_source_companion_files']), complete_recursive_objects=total,
               complete_ledger_partitions=len(a['complete_source_object_reference_bodies']), source_files=len(global_counts),
               producer_owned_assets_rehashed=assets, original_reference_entries=len(refs),
               all_primary575_priority233_remainder342_parent21_arrays_exact=True,
               current_or_legal_native_approval=False, acceptance_bytes=(D/'coordinator-priority-acceptance.json').stat().st_size,
               acceptance_sha256=sha((D/'coordinator-priority-acceptance.json').read_bytes()), no_producer_import_or_mutation=True)
    p.write_text(json.dumps(out, indent=2)+'\n')
    print(out)


if __name__ == '__main__':
    main()
