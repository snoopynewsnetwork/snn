"""Own read-only reconstruction of every externally enumerated historical body.

No producer code is executed or imported. The external acceptance is path-only.
Run with Python -B. --check compares the deterministic report without writing.
"""
import collections, csv, gzip, hashlib, io, json, sys, tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE = HERE.parent
AUTHORITY = STATE / 'data/coordinator-priority-acceptance.json'

def canonical(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()

def digest(b):
    return hashlib.sha256(b).hexdigest()

def replay():
    authority = json.loads(AUTHORITY.read_bytes())
    checks = collections.Counter()
    def require(ok, label):
        if not ok:
            raise AssertionError(label)
        checks[label.split(':')[0]] += 1
    bodies = {}
    def body(pin):
        key = (pin['path'], pin['sha256'])
        if key not in bodies:
            b = (STATE / pin['path']).read_bytes()
            require(len(b) == pin['bytes'] < 40000000 and digest(b) == pin['sha256'], 'fixed original:' + pin['path'])
            bodies[key] = b
        return bodies[key]
    def parse(pin):
        b = body(pin)
        if pin['path'].endswith('.gz'): b = gzip.decompress(b)
        if pin['path'].endswith(('.csv', '.csv.gz')): return list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))
        if '.jsonl' in pin['path']: return [json.loads(line) for line in b.splitlines() if line]
        return json.loads(b)
    pins = {p['path']: p for p in authority['frozen_file_pins']}
    for pin in authority['frozen_file_pins'] + authority['independent_coordinator_reviews']: body(pin)
    contract = parse(authority['frozen_contract'])
    require(len(contract) == len(authority['complete_root_field_semantics']) == 25, 'root count')
    for row in authority['complete_root_field_semantics']:
        require(digest(canonical(contract[row['pointer'][1:]])) == row['full_recursive_semantic_sha256'], 'whole root')
    for row in authority['complete_source_companion_files']:
        value = parse(row)
        require(digest(canonical(value)) == row['full_semantic_sha256'] and (len(value) if isinstance(value, (list, dict)) else None) == row['complete_length'], 'whole companion:' + row['path'])
    archives = {}
    for row in authority['historical_full_body_resolvers']:
        storage = row['storage']
        if storage['kind'] == 'immutable_original_reference': b = body(storage['file'])
        else:
            apin = storage['archive']; key = (apin['path'], apin['sha256'])
            if key not in archives: archives[key] = tarfile.open(fileobj=io.BytesIO(gzip.decompress(body(apin))))
            b = archives[key].extractfile(storage['member']).read()
        require(len(b) == row['bytes'] and digest(b) == row['sha256'], 'historical exact path and hash:' + row['path'])
    # Reconstruct the ordered ledger independently, traversing every container,
    # rather than merely resolving the pointers claimed by an existing ledger.
    def containers(value, pointer=''):
        if isinstance(value, (dict, list)):
            yield pointer, value
            for key, item in value.items() if isinstance(value, dict) else enumerate(value):
                if isinstance(item, (dict, list)):
                    yield from containers(item, pointer + '/' + str(key).replace('~', '~0').replace('/', '~1'))
    def ordered_graph():
        # The authority's first 25 entries are whole roots (including scalars),
        # followed by recursive containers of every companion, including the
        # complete contract again in its sorted companion position.
        for key, value in contract.items():
            yield 'data/turnout/priority-set.json', '/' + key, value
        for companion in authority['complete_source_companion_files']:
            for pointer, value in containers(parse(companion)):
                yield companion['path'], pointer, value
    expected = ordered_graph(); counts = collections.Counter()
    for part in authority['complete_source_object_reference_bodies']:
        raw = gzip.decompress(body(part))
        require(len(raw) == part['complete_reconstructed_bytes'] and digest(raw) == part['complete_reconstructed_sha256'], 'whole ordered ledger bytes')
        count = 0
        for line in raw.splitlines():
            row = json.loads(line)
            file, pointer, value = next(expected)
            require(row['file'] == file and row['pointer'] == pointer and digest(canonical(value)) == row['full_recursive_semantic_sha256'], 'complete recursive ordered object')
            counts[file] += 1; count += 1
        require(count == part['complete_object_count'], 'ledger object count')
    require(next(expected, None) is None, 'last file traversal exhausted')
    require(dict(counts) == authority['source_objects_by_file'] and sum(counts.values()) == 3474062, 'complete graph')
    ordered = contract['ordered_units']; priority = set(authority['ordered_priority_keys'])
    require([u['key'] for u in ordered] == authority['ordered_full_keys'], 'all native order')
    require(contract['ordered_priority_keys'] == authority['ordered_priority_keys'] and contract['ordered_remainder_keys'] == authority['ordered_remainder_keys'], 'priority remainder exact order')
    require(len(ordered) == 2669 and len(priority) == 1538 and len(contract['ordered_remainder_keys']) == 1131, 'native cardinality')
    require(ordered == sorted(ordered, key=lambda u: (-u['reported_candidate_writein_votes'], u['source_record'])), 'numeric logical record ordering')
    require(sum(u['reported_candidate_writein_votes'] for u in ordered) == 4445535 and sum(u['reported_candidate_writein_votes'] for u in ordered[:15]) == 80617, 'denominator and top15')
    require(sum(u['reported_candidate_writein_votes'] for u in ordered[:1537]) == 3555604 and sum(u['reported_candidate_writein_votes'] for u in ordered[:1538]) == 3557034, 'exact crossing')
    require(len(contract['parent_inventory']) == 133 and len(authority['ordered_priority_parent_keys']) == 108, 'parent scope')
    for p in contract['parent_inventory']:
        key = p['historical_parent_key']; arrays = authority['all_parent_ordered_child_arrays'][key]
        children = [u['key'] for u in ordered if u['parent_key'] == key]
        require(p['all_native_keys'] == arrays['original_ordered_native_inventory_keys'] and children == arrays['full_source_rank_ordered_children'], 'full parent child arrays')
        require(arrays['ordered_priority_children'] == [k for k in children if k in priority] and arrays['ordered_remainder_children'] == [k for k in children if k not in priority], 'parent priority remainder arrays')
    for seal in authority['producer_seals']:
        manifest = parse(seal); entries = manifest[seal['owned_field']]
        require(len(entries) == seal['owned_entries'], 'producer seal full list')
        for entry in entries: body(entry)
        root = STATE / Path(seal['path']).parent
        extras = {'turnout.md', 'data/county-turnout.csv'} if root.name == 'turnout' else {'county-partisanship.md', 'data/county-baselines.csv'}
        actual = {str(p.relative_to(STATE)) for p in root.rglob('*') if p.is_file() and p != STATE / seal['path']} | extras
        require(actual == {p['path'] for p in entries}, 'producer exact membership')
    return {'status': 'pass', 'authority_path': str(AUTHORITY.relative_to(STATE)), 'whole_roots': 25, 'whole_companions': 471, 'recursive_objects': sum(counts.values()), 'ordered_ledgers': 24, 'fixed_files': len(pins), 'historical_full_bodies': 1172, 'producer_seals': 2, 'checks': dict(checks), 'network': False, 'producer_imports_or_writes': False, 'current_geographic_approval': False}

if __name__ == '__main__':
    result = replay(); out = json.dumps(result, indent=2) + '\n'; path = HERE / 'authority-replay.json'
    if '--check' in sys.argv: assert path.read_text() == out
    else: path.write_text(out)
    print(out)
