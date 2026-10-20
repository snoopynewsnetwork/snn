#!/usr/bin/env python3
"""Read-only independent final turnout review; writes only coordinator proof."""
from pathlib import Path
import collections
import copy
import csv
import gzip
import hashlib
import json

STATE = Path(__file__).resolve().parent.parent
D = STATE / 'data/turnout'
checks = 0


def check(value, message):
    global checks
    checks += 1
    if not value:
        raise AssertionError(message)


def load(p):
    return json.loads(p.read_bytes())


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(p):
    b = p.read_bytes()
    return {'path': str(p.relative_to(STATE)), 'bytes': len(b), 'sha256': sha(b)}


def exact(p, record):
    b = p.read_bytes()
    check(len(b) == record['bytes'], str(p) + ' bytes')
    check(sha(b) == record['sha256'], str(p) + ' sha')
    check(len(b) < 40000000, str(p) + ' strict size')
    return b


mf = load(D / 'asset-manifest.json')
listed = [r['path'] for r in mf['assets']]
check(len(listed) == len(set(listed)) == 2336, 'unique complete final seal')
actual = {str(p.relative_to(STATE)) for p in D.rglob('*') if p.is_file()}
actual.update({'turnout.md', 'data/county-turnout.csv'})
check(set(listed) == actual - {'data/turnout/asset-manifest.json'}, 'self only exclusion')
for r in mf['assets']:
    exact(STATE / r['path'], r)
check(not any(p.name in ('__pycache__', 'node_modules', '.venv', 'venv') for p in D.rglob('*')), 'no dependency/cache trees')

captures = {}
for name in ('pre-reciprocal-capture.json', 'peer-capture.json', 'peer-return-capture.json'):
    cap = load(D / 'reciprocal-review' / name)
    for r in cap['records']:
        if r.get('capture_path'):
            z = (STATE / r['capture_path']).read_bytes()
            check(len(z) == r['stored_bytes'] and sha(z) == r['stored_sha256'], 'complete captured stored body')
            raw = gzip.decompress(z)
            check(len(raw) == r['bytes'] and sha(raw) == r['sha256'], 'complete captured original body')
            captures[(name, r.get('path', r.get('peer_path')))] = raw

prior = load(D / 'reciprocal-review/pre-reciprocal-capture.json')
check(len(prior['records']) == 1523, 'complete pre-mutation inventory')
allowed = {'turnout.md', 'data/turnout/source/SCHEMA.md', 'data/turnout/build_package.py',
           'data/turnout/validate_turnout.py', 'data/turnout/reproducibility.json',
           'data/turnout/asset-manifest.json', 'data/turnout/priority-set.json',
           'data/turnout/validation.json'}
invariant_count = 0
for r in prior['records']:
    if r['path'] not in allowed:
        exact(STATE / r['path'], r)
        invariant_count += 1
check(invariant_count == 1515, 'all original invariant bodies')

witness = load(D / 'pre-peer-witness.json')
check(sha((D / 'pre-peer-witness.json').read_bytes()) == '7e26b6b14d5f881af05800aec84beaa4f38abbeb40b034dad1b49e2a061454f1', 'original witness unchanged')
check(witness['peer_derivatives_read'] is False, 'original-first witness scope')
for r in witness['frozen_bodies']:
    z = (STATE / r['frozen_path']).read_bytes()
    check(len(z) == r['stored_bytes'] and sha(z) == r['stored_sha256'], 'pre-peer stored body')
    raw = gzip.decompress(z)
    check(len(raw) == r['original_bytes'] and sha(raw) == r['original_sha256'], 'pre-peer full original body')
for r in witness['original_pins']:
    exact(STATE / r['path'], r)

c = load(D / 'priority-set.json')
old = json.loads(captures[('pre-reciprocal-capture.json', 'data/turnout/priority-set.json')])
new = copy.deepcopy(c)
for key in ('status', 'independent_peer'):
    old.pop(key)
    new.pop(key)
check(old['unresolved'][:3] == new['unresolved'][:3], 'original source qualifications unchanged')
check(len(old['unresolved']) == len(new['unresolved']) == 4, 'only fourth peer status qualification replaced')
old['unresolved'] = old['unresolved'][:3]
new['unresolved'] = new['unresolved'][:3]
check(old == new, 'every non-review contract object unchanged')
check(c['coordinator_acceptance']['accepted'] is False, 'producer does not self-accept')
check(c['independent_peer']['full_future_final_equality_claimed'] is False, 'future peer outputs outside claim')

source = load(D / 'extract/native-rows.json')['2024-senate']
ranked = sorted(source, key=lambda r: (-sum(v for v in r['values'] if v is not None), r['key']))
keys = [r['key'] for r in ranked]
total = sum(sum(v for v in r['values'] if v is not None) for r in ranked)
check(total == 4031795 and len(keys) == len(set(keys)) == 575, 'complete source universe')
check(collections.Counter(r['unit_type'] for r in ranked) == {'municipality': 564, 'administrative': 11}, 'source roles distinct')
check(keys == c['complete_ordered_keys'], 'entire canonical order')
check(keys[:233] == c['ordered_priority_keys'] and keys[233:] == c['remainder']['ordered_keys'], 'entire priority and remainder arrays')
check(len(c['all_units']) == 575, 'complete source objects')
cum = 0
for i, (r, u) in enumerate(zip(ranked, c['all_units']), 1):
    for key, value in r.items():
        check(u[key] == value, 'complete original source unit field ' + key)
    volume = sum(v for v in r['values'] if v is not None)
    check(u['rank'] == i and u['volume'] == volume and u['previous_votes'] == cum, 'rank and volume')
    cum += volume
    check(u['cumulative_votes'] == cum and u['share_denominator'] == total, 'cumulative and denominator')
    check(u['in_minimum80'] == (i <= 233) and u['in_top15'] == (i <= 15), 'complete membership flags')
before = sum(sum(v for v in r['values'] if v is not None) for r in ranked[:232])
cross = before + sum(v for v in ranked[232]['values'] if v is not None)
check((before, cross) == (3224325, 3229453) and 5 * before < 4 * total <= 5 * cross, 'exact integer threshold')
check(ranked[232]['key'] == '2024-official-general-results-us-senate-monmouth:p0001:l0016', 'exact source crossing')
check(sum(sum(v for v in r['values'] if v is not None) for r in ranked[:15]) == 631518, 'top fifteen')
check(total - cross == 802342 and len(keys[233:]) == 342, 'full remainder')
check(len(c['county_coverage']) == 21, 'all parent objects')
for parent in c['county_coverage']:
    child = [r['key'] for r in ranked if r['county_fips'] == parent['county_fips']]
    check(child == parent['ranked_source_unit_keys'], 'complete ordered children')
    check(parent['approved_2026_native_or_geometry_crosswalk'] is False, 'no current parent identity approval')
csv_rows = list(csv.DictReader((STATE / 'data/county-turnout.csv').open()))
check([r['key'] for r in csv_rows] == keys, 'entire compatibility CSV order')
check(sha((STATE / 'data/county-turnout.csv').read_bytes()) == '334dbe564c1123b4d64e4d5e08830534d99153fc3a2deec72adac8c2ee117b3f', 'original CSV unchanged')

comparison = load(D / 'reciprocal-review/comparison.json')
check(comparison['checks'] == 82206 and not comparison['differences'], 'bounded own captured comparison')
reverse = comparison['reverse_peer_fixed_core_result']
check(reverse['checks'] == reverse['passed'] == 40921 and reverse['failed'] == 0 and not reverse['differences'], 'bounded completed reverse comparison')
check(not any(comparison['acceptance'].values()), 'peer comparison not admission')
seal = load(D / 'final-seal.json')
for r in seal['pins']:
    exact(STATE / r['path'], r)
check(not any(seal['acceptance'].values()), 'final seal false approvals')
check('manifest_sha256' not in seal and 'validation_sha256' not in seal, 'no reverse seal cycle')
validation = load(D / 'validation.json')
check(len(validation['checks']) == 41 and all(validation['checks'].values()) and not validation['failures'], 'recorded complete final QA')

original_proof = STATE / 'data/coordinator-native-original-review.json'
original = load(original_proof)
check(original['checks'] == 17033 and original['complete_original_PDFs'] == 84 and original['complete_original_native_rows'] == 2296, 'independent whole original replay')
check(original['complete_county_candidate_fields'] == 588 and original['no_producer_import_or_write'], 'independent original control scope')
result = {
    'status': 'pass_independent_final_turnout_source_and_bounded_reciprocal_seal',
    'checks': checks,
    'owned_manifest_entries': len(listed),
    'pre_mutation_complete_pins': len(prior['records']),
    'unchanged_prior_bodies': invariant_count,
    'original_witness_bodies': len(witness['frozen_bodies']),
    'complete_native_rows': 575,
    'complete_parent_hierarchies': 21,
    'priority': 233,
    'remainder': 342,
    'independent_original_replay': pin(original_proof),
    'pins': [pin(p) for p in (D / 'asset-manifest.json', D / 'priority-set.json', D / 'final-seal.json', D / 'reciprocal-review/comparison.json', D / 'validation.json')],
    'qualification': 'Fixed completed original-first peer core only; later baseline report/finer/scenario/final outputs excluded. Source-native575 municipal/admin publication scope is not finest precinct or current legal geography, eligible writein exhaustiveness or live admission.',
    'producer_writes_or_imports': False,
    'formal_coordinator_priority_acceptance': False,
}
out = STATE / 'data/coordinator-turnout-final-review.json'
out.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'checks': checks, 'proof': pin(out)}))
