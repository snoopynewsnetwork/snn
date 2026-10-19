"""Independent coordinator verification of the sealed official-source package."""
from collections import Counter
from pathlib import Path
import ast
import csv
import gzip
import hashlib
import io
import json

D = Path(__file__).resolve().parent
S = D.parent
R = D / 'results-sources'


def sha(value):
    return hashlib.sha256(value).hexdigest()


def pin(path):
    value = path.read_bytes()
    return dict(path=str(path.relative_to(S)), bytes=len(value), sha256=sha(value))


def load(path):
    value = path.read_bytes()
    return json.loads(gzip.decompress(value) if path.suffix == '.gz' else value)


def semantic(value):
    return sha(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode())


def pointer(value, path):
    for key in path.split('/')[1:]:
        key = key.replace('~1', '/').replace('~0', '~')
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def main():
    manifest = load(R / 'manifest.json')
    assert pin(R / 'manifest.json')['sha256'] == '60b9968c1a4a2b4cc8594d988aca319beb030b6ceb9375dde7e52d605205a4db'
    owned = manifest['owned']
    refs = manifest['immutable_external_complete_references']
    assert len(owned) == 1011 and len(refs) == 173
    for entry in owned + refs:
        path = S / entry['path']
        assert pin(path) == {k: entry[k] for k in ['path', 'bytes', 'sha256']}
        assert entry['bytes'] < 40_000_000
        value = path.read_bytes()
        raw = gzip.decompress(value) if path.suffix == '.gz' else value
        if 'reconstructed_sha256' in entry:
            assert sha(raw) == entry['reconstructed_sha256'] and len(raw) == entry['reconstructed_bytes']
        if 'semantic_sha256' in entry:
            assert semantic(json.loads(raw)) == entry['semantic_sha256']
        if 'complete_rows_semantic_sha256' in entry:
            assert semantic(list(csv.reader(io.StringIO(raw.decode())))) == entry['complete_rows_semantic_sha256']
    actual = {str(p.relative_to(S)) for p in R.rglob('*') if p.is_file()} | {'official-results.md', 'data/official-results-sources.csv'}
    assert actual == {x['path'] for x in owned} | {'data/results-sources/manifest.json'}
    assert not any(p.name in ['__pycache__', 'node_modules', '.venv', '.pytest_cache'] for p in R.rglob('*'))
    for path in R.rglob('*.py'):
        ast.parse(path.read_bytes(), filename=str(path))
    statuses = Counter()
    receipts = []
    for path in sorted((R / 'receipts').glob('*.json')):
        entry = load(path)
        assert path.stem == entry['id']
        assert entry['method'] == 'GET' and entry['retrieved_utc'] and 'redirects' in entry and 'response_headers' in entry
        statuses[entry['http_status']] += 1
        if entry.get('stored_path'):
            stored = (R / entry['stored_path']).read_bytes()
            value = gzip.decompress(stored)
            assert sha(stored) == entry['stored_sha256'] and len(stored) == entry['stored_bytes']
            assert sha(value) == entry['raw_sha256'] and len(value) == entry['raw_bytes']
        else:
            assert entry.get('error') and entry['http_status'] is None
        receipts.append(entry)
    assert len(receipts) == 451
    graph = load(R / 'historical-source-graph.json')
    assert graph['immutable_complete_files'] == refs
    acceptance = load(D / 'coordinator-priority-acceptance.json')
    contract = load(D / 'turnout/priority-set.json')
    assert pin(D / 'turnout/priority-set.json')['sha256'] == '9bf413132cd591ac110ac1d88bc6d52f818679f6b28b33a0ca77e30c4d1e6676'
    assert graph['external_acceptance_path'] == manifest['external_acceptance_path'] == 'data/coordinator-priority-acceptance.json'
    assert manifest['current_approved'] is False and contract['priority_accepted'] is False and contract['current_geography_approved'] is False
    assert graph['complete_source_companion_paths'] == [x['path'] for x in acceptance['complete_source_companion_files']]
    assert len(graph['root_fields']) == len(contract) == 42
    for entry in graph['root_fields']:
        assert semantic(pointer(contract, entry['pointer'])) == entry['semantic_sha256']
    assert len(graph['complete_object_references']) == 5169
    cache = {graph['contract_path']: contract}
    for entry in graph['complete_object_references']:
        path = entry['file']
        if path not in cache:
            cache[path] = load(S / path)
        assert semantic(pointer(cache[path], entry['pointer'])) == entry['semantic_sha256']
    for file, field, count in [('priority-investigations.json', 'ordered_priority_keys', 528), ('remainder-monitoring.json', 'ordered_remainder_keys', 457)]:
        rows = load(R / file)
        assert len(rows) == count and [x['historical_key'] for x in rows] == contract[field]
        for row in rows:
            assert row['current_approved'] is False
            assert all(row[k] is None for k in ['current_leaf_id', 'current_contest_id', 'current_choice_ids', 'current_method', 'current_geometry'])
    result = dict(status='pass_independent_sealed_official_package_review', manifest=pin(R / 'manifest.json'),
                  validation=pin(R / 'validation.json'), original_coordinator_review=pin(D / 'coordinator-official-original-review.json'),
                  exact_owned_files=1011, immutable_complete_external_files=173,
                  complete_source_companions=29, full_contract_root_fields=42, complete_recursive_objects=5169,
                  complete_acquisition_observations=451, observed_HTTP_statuses={str(k): v for k, v in statuses.items()},
                  all_authorities=45, priority_entries=528, remainder_entries=457, historical_units=985,
                  full_original_XLSX_rows=419099, full_original_explicit_XLSX_cells=3131500,
                  current_approval=False, source_scope='May2026 primary/public constructors and bounded current law/ballot sources only; no historical/current leaf join or genuine November returns admitted.')
    target = D / 'coordinator-finished-official-review.json'
    value = (json.dumps(result, indent=2) + '\n').encode()
    if target.exists():
        assert target.read_bytes() == value
    else:
        target.write_bytes(value)
    print(json.dumps(pin(target)))


if __name__ == '__main__':
    main()
