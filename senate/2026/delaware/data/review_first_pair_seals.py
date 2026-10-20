"""Independent coordinator full selected HTML field, seal and live-CLI audit."""
from pathlib import Path
from collections import Counter
import ast
import gzip
import hashlib
import json
import math
import os
import subprocess
import tempfile
from review_native_originals import Tables

D = Path(__file__).resolve().parent
S = D.parent
B = D / 'baselines'
T = D / 'turnout'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(S)), bytes=len(b), sha256=sha(b))


def main():
    sealed = []
    for root, expected, report, table in [(B, 139, 'county-partisanship.md', 'county-baselines.csv'),
                                           (T, 202, 'turnout.md', 'county-turnout.csv')]:
        mf = json.loads((root / 'asset-manifest.json').read_bytes())
        if root == B:
            owned = [e for e in mf['assets'] if e['ownership'] == 'assigned report/data']
            refs = [e for e in mf['assets'] if e['ownership'] == 'read-only shared original']
            def path(e):
                return (root / e['path']).resolve()
        else:
            owned, refs = mf['owned'], mf['shared_originals']
            def path(e):
                return S / e['path']
        assert len(owned) == expected and len(refs) == 12
        for e in owned + refs:
            p = path(e)
            b = p.read_bytes()
            assert sha(b) == e['sha256'] and len(b) == e['bytes'] < 40_000_000
        actual = {p.resolve() for p in root.rglob('*') if p.is_file() and p.name != 'asset-manifest.json'} | {(S / report).resolve(), (D / table).resolve()}
        assert actual == {path(e).resolve() for e in owned}
        assert not any(p.name in ['__pycache__', 'node_modules', '.venv', '.pytest_cache'] for p in root.rglob('*'))
        for p in root.rglob('*.py'):
            ast.parse(p.read_bytes(), filename=str(p))
        sealed.append(dict(manifest=pin(root / 'asset-manifest.json'), owned=len(owned), immutable_original_refs=len(refs)))
    sourcepins = json.loads((D / 'coordinator-original-report-pins.json').read_bytes())
    parsed = {}
    for name in ['sos-2024-general-report', 'sos-observed-2020-general-report', 'official-2022-report']:
        e = sourcepins[name]
        raw = gzip.decompress((D / 'news' / e['asset']).read_bytes())
        assert sha(raw) == e['raw_sha256']
        parsed[name] = {t['start']: t for t in Tables(raw.decode('utf-8-sig')).tables}
    tables = json.loads((B / 'extracted/contest-tables.json').read_bytes())
    count = fields = 0
    for table in tables:
        raw = parsed[table['source_id']][table['source_char_start']]
        assert raw['end'] == table['source_char_end']
        assert [c['text'] for c in raw['rows'][0]['cells']] == table['headers']
        assert len(raw['rows']) - 1 == len(table['rows'])
        for own, producer in zip(raw['rows'][1:], table['rows']):
            assert (own['start'], own['end']) == (producer['source_char_start'], producer['source_char_end'])
            assert [c['text'] for c in own['cells']] == producer['cells']
            labels = [c['attrs'].get('data-label') for c in own['cells']]
            assert labels == producer['data_labels']
            assert len(producer['fields']) == len(producer['cells'])
            count += 1
            fields += len(producer['cells'])
    assert len(tables) == 2674 and count == 10699
    c = json.loads((T / 'priority-set.json').read_bytes())
    assert pin(T / 'priority-set.json')['sha256'] == '486c051146782d315d3866e65dda2db86a6ee1a6767b98d94486aa5bd7e195a6'
    original = json.loads((D / 'coordinator-native-original-review.json').read_bytes())['contexts']['2024_SEN']
    assert c['total'] == 500606 and c['priority_votes'] == 400539 and c['preceding_votes'] == 399708
    assert c['ordered_priority_keys'] == original['full_source_order'][:311]
    assert c['ordered_remainder_keys'] == original['full_source_order'][311:]
    assert len(c['full_order']) == 530 and len(c['all_available_source_constituents']) == 1495
    assert c['formal_coordinator_acceptance'] is False and c['current_geography_approved'] is False
    inputs = json.loads((B / 'synthetic-inputs.json').read_bytes())
    saved = json.loads((B / 'synthetic-results.json').read_bytes())
    assert len(inputs) == len(saved) == 21
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / 'cases.json'
        p.write_text(json.dumps(inputs))
        command = ['python3', '-B', str(B / 'calculators.py'), str(p)]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
                                env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        output = json.loads(result.stdout)
        assert output == [dict(name=e['name'], result=e['result']) for e in saved]
        own_negative = []
        for value in [float('nan'), float('inf'), -float('inf'), None, 'wrong', 2]:
            example = dict(counted={'A': 40, 'B': 60, 'other': {}}, remaining=[dict(unit='one', remaining_total=100, remaining_other={}, pair_share=.5)], target_pair_margin=value)
            p.write_text(json.dumps(example))
            completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
            observed = json.loads(completed.stdout)
            assert observed['status'].startswith('invalid') and 'target' in observed['status']
            own_negative.append(dict(target_repr=repr(value), result=observed))
    arithmetic = 0
    for example, observed in zip(inputs, saved):
        r = observed['result']
        if 'remaining_pair_pool' not in r:
            continue
        counted = example['counted']
        units = example['remaining']
        U = sum(u['remaining_total'] - sum(u['remaining_other'].values()) for u in units)
        pair = counted['A'] + counted['B'] + U
        allvotes = counted['A'] + counted['B'] + sum(counted.get('other', {}).values()) + sum(u['remaining_total'] for u in units)
        assert (r['remaining_pair_pool'], r['final_pair_denominator'], r['final_all_candidate_denominator']) == (U, pair, allvotes)
        assert r['counted_fixed'] == counted
        arithmetic += 4
        if U > 0:
            q = (U + example.get('target_pair_margin', 0) * pair - counted['A'] + counted['B']) / (2 * U)
            assert abs(q - r['required_remaining_A_share_unbounded']) < 1e-12
            arithmetic += 1
            if all(u.get('pair_share') is not None for u in units):
                A = counted['A'] + sum((u['remaining_total'] - sum(u['remaining_other'].values())) * min(1, max(0, u['pair_share'])) for u in units)
                Bvotes = pair - A
                assert abs(A - r['final_A']) < 1e-12 and abs(Bvotes - r['final_B']) < 1e-12
                arithmetic += 2
    out = dict(status='pass_independent_complete_original_field_seal_and_live_CLI_review', question_seals=sealed,
               original_selected_HTML_tables=len(tables), original_candidate_rows=count, original_literal_cells=fields,
               source_positions_headers_labels_parties_and_null_methods_preserved=True,
               contract=pin(T / 'priority-set.json'), full_native=530, ordered_priority=311, remainder=219, all_year_native_union=1495,
               live_CLI_scenarios=21, independent_live_formula_checks=arithmetic, own_nonfinite_and_invalid_target_CLI_tests=own_negative,
               current_geography_or_choice_ID_or_return_approval=False,
               qualifications='Historical named source universe and explicit unknown supplementary/geographic/participation scopes only. All originals and producer bytes unchanged; no current legal/signed ballot exhaustiveness, native write-in allocation, collector/cadence/pool/probability approval.')
    target = D / 'coordinator-first-pair-seal-review.json'
    value = (json.dumps(out, indent=2) + '\n').encode()
    if target.exists():
        assert target.read_bytes() == value
    else:
        target.write_bytes(value)
    print(json.dumps(dict(**pin(target), original_rows=count, live_checks=arithmetic)))


if __name__ == '__main__':
    main()
