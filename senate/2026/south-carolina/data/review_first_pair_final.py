"""Read-only sealed-manifest, report-link and independent remainder arithmetic QA."""
import hashlib
import json
import math
import re
from pathlib import Path
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
STATE = HERE.parent
CACHE = {}


def digest(path):
    path = path.resolve()
    if path not in CACHE:
        raw = path.read_bytes()
        CACHE[path] = len(raw), hashlib.sha256(raw).hexdigest()
    return CACHE[path]


def equal(actual, expected):
    assert math.isclose(actual, expected, abs_tol=1e-7, rel_tol=1e-12), (actual, expected)


def main():
    manifests = []
    for role in ['turnout', 'baselines']:
        folder = HERE / role
        path = folder / 'asset-manifest.json'
        manifest = json.loads(path.read_bytes())
        base = folder if role == 'turnout' else STATE
        owned = manifest['owned_assets'] if role == 'turnout' else manifest['assets']
        declared = set()
        for record in owned:
            asset = (base / record['path']).resolve()
            assert asset not in declared
            declared.add(asset)
            size, sha = digest(asset)
            assert size == record['bytes'] < 40_000_000
            assert sha == record['sha256'], asset
        report = STATE / ('turnout.md' if role == 'turnout' else 'county-partisanship.md')
        table = HERE / ('county-turnout.csv' if role == 'turnout' else 'county-baselines.csv')
        actual = {asset.resolve() for asset in folder.rglob('*') if asset.is_file() and asset != path}
        actual.update([report.resolve(), table.resolve()])
        assert actual == declared, (role, actual-declared, declared-actual)
        assert all('__pycache__' not in asset.parts and asset.suffix != '.pyc' for asset in actual)
        references = manifest.get('read_only_references', [])
        for reference in references:
            asset = folder / reference['path']
            size, sha = digest(asset)
            assert size == reference['bytes']
            assert sha == reference['sha256'], asset
        validation = json.loads((folder / 'validation.json').read_bytes())
        assert validation['status'].startswith('pass')
        manifests.append({'role': role, 'manifest_sha256': digest(path)[1], 'owned_assets': len(owned),
                          'read_only_references': len(references), 'bytes_excluding_manifest': sum(record['bytes'] for record in owned)})

    report_links = 0
    for path in [STATE/'turnout.md', STATE/'county-partisanship.md', HERE/'turnout/source/SCHEMA.md', HERE/'baselines/source/SCHEMA.md']:
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if re.match(r'https?://', target):
                continue
            local = target.split('#', 1)[0].strip('<>')
            assert (path.parent / unquote(local)).exists(), (path, target)
            report_links += 1

    fixtures = json.loads((HERE/'baselines/live-scenarios.json').read_bytes())
    saved = json.loads((HERE/'baselines/live-results.json').read_bytes())
    assert len(fixtures) == len(saved) == 13
    arithmetic = 0
    for fixture, observed in zip(fixtures, saved):
        assert fixture == observed['input']
        counted = fixture['counted']
        remaining = fixture['remaining']
        for result_name, margin in [('result', 0.0), ('Aplus1_result', 0.01)]:
            result = observed[result_name]
            if 'counted_fixed' in result:
                assert result['counted_fixed'] == counted
            if any(value < 0 for value in [counted['A'], counted['B'], *counted.get('others', {}).values()]):
                assert result['status'].startswith('negative')
                continue
            if any(unit['pair_pool'] is not None and unit['pair_pool'] < 0 for unit in remaining):
                assert result['status'].startswith('negative')
                continue
            if any(unit['pair_pool'] is None for unit in remaining):
                assert result['status'] == 'unknown_remaining_pool'
                continue
            pool = sum(unit['pair_pool'] for unit in remaining)
            final_pair = counted['A'] + counted['B'] + pool
            other = dict(counted.get('others', {}))
            for unit in remaining:
                for key, value in unit.get('others', {}).items():
                    other[key] = other.get(key, 0) + value
            final_all = final_pair + sum(other.values())
            equal(result['final_pair_denominator'], final_pair)
            equal(result['final_all_candidate_denominator'], final_all)
            equal(result['target_net'], margin*final_pair)
            if pool:
                threshold = (pool+margin*final_pair-(counted['A']-counted['B']))/(2*pool)
                equal(result['required_uniform_remaining_A_share'], threshold)
            if all(unit['pair_pool'] == 0 or unit.get('A_share') is not None for unit in remaining):
                a = counted['A'] + sum(unit['pair_pool']*min(1,max(0,unit.get('A_share') or 0)) for unit in remaining)
                b = final_pair-a
                equal(result['projected_A'], a)
                equal(result['projected_B'], b)
                if 'all_candidate_vote_sum' in result:
                    equal(result['all_candidate_vote_sum'], final_all)
            assert result.get('probability') is None
            arithmetic += 1
    output = {'status': 'pass_sealed_exact_manifest_membership_and_independent_live_equations',
              'manifests': manifests, 'report_schema_relative_links': report_links,
              'live_fixtures': len(fixtures), 'valid_arithmetic_cases': arithmetic,
              'scope': 'Read-only final first-pair checks; synthetic arithmetic is not observed live reporting or probability calibration.'}
    (HERE/'coordinator-first-pair-final-review.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output,indent=2))


if __name__ == '__main__':
    main()
