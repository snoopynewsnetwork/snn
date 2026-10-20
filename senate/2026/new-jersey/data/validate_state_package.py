"""Coordinator whole-state seal; run after all four actual finish handoffs.

--check is read-only. No producer code is imported or executed.
"""
from pathlib import Path
import ast
import hashlib
import json
import re
import sys
import urllib.parse

S = Path(__file__).resolve().parents[1]
D = S / 'data'


def read(p):
    return json.loads(p.read_bytes())


def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(S)), bytes=len(b), sha256=hashlib.sha256(b).hexdigest())


def main(check=False):
    manifest = D / 'coordinator-asset-manifest.json'
    validation = D / 'coordinator-validation.json'
    official = read(D / 'coordinator-official-final-review.json')
    maps = read(D / 'coordinator-maps-final-review.json')
    math = read(D / 'coordinator-first-pair-math-review.json')
    specs = [
        ('turnout', 'data/turnout/asset-manifest.json', 'assets', 2336, ['turnout.md', 'data/county-turnout.csv']),
        ('baselines', 'data/baselines/asset-manifest.json', 'files', 318, ['county-partisanship.md', 'data/county-baselines.csv']),
        ('official', 'data/results-sources/asset-manifest.json', 'files', 1443, ['official-results.md', 'data/official-results-sources.csv']),
        ('maps', maps['producer_manifest']['path'], maps['producer_manifest_list_key'], maps['owned_entries'], ['precinct-maps.md']),
    ]
    seals = []
    checks = 0
    for role, name, key, count, extra in specs:
        p = S / name
        m = read(p)
        rows = m[key]
        assert len(rows) == count, role
        actual = {str(q.relative_to(S)) for q in p.parent.rglob('*') if q.is_file() and q != p} | set(extra)
        assert actual == {r['path'] for r in rows}, role
        for r in rows:
            assert pin(S / r['path']) == {k: r[k] for k in ['path', 'bytes', 'sha256']}, r['path']
            assert r['bytes'] < 40000000
            checks += 1
        seals.append(dict(role=role, manifest=pin(p), owned_entries_excluding_manifest=count))
    a = read(D / 'coordinator-priority-acceptance.json')
    c = read(D / 'turnout/priority-set.json')
    assert pin(D / 'turnout/priority-set.json') == a['frozen_contract']
    assert len(c) == 24 and a['complete_source_object_count'] == 724943
    assert len(a['complete_source_companion_files']) == 504
    assert len(a['complete_source_object_reference_bodies']) == 5
    assert (a['source_candidate_denominator'], a['top15_votes']) == (4031795, 631518)
    assert (len(a['ordered_full_keys']), len(a['ordered_priority_keys']), len(a['ordered_remainder_keys'])) == (575, 233, 342)
    assert a['ordered_full_keys'] == a['ordered_priority_keys'] + a['ordered_remainder_keys']
    assert len(a['ordered_priority_parent_FIPS']) == 21
    for k in ['current_geography_approved', 'current_November_returns_admitted', 'current_choice_or_reporting_IDs_approved', 'legal_native_80_robustness_approved', 'live_cadence_or_exact_remainder_approved', 'collector_or_probability_approval']:
        assert a[k] is False
    reviews = [
        'coordinator-native-original-review.json', 'coordinator-turnout-final-review.json',
        'coordinator-baseline-core-review.json', 'coordinator-baseline-final-review.json',
        'coordinator-first-pair-math-review.json', 'coordinator-live-input-review/review.json',
        'coordinator-acceptance-validation.json', 'coordinator-monmouth-original-review/review.json',
        'coordinator-somerset-caption-review/review.json',
        'coordinator-current-roster-order-review/review.json', 'coordinator-official-final-review.json',
        'coordinator-maps-final-review.json', 'coordinator-maps-visual-review.json',
        'coordinator-native-map-snapshot-review.json', 'coordinator-census-map-original-review.json',
    ]
    for name in reviews:
        status = read(D / name)['status']
        assert status.startswith('pass') or status.startswith('actual_coordinator'), (name, status)
    assert official['priority'] == maps['priority'] == 233
    assert official['remainder'] == maps['remainder'] == 342
    assert (math['state_scenarios'], math['every_unit_rows']) == (40, 8588)
    syntax = links = 0
    for p in S.rglob('*'):
        if not p.is_file():
            continue
        assert p.stat().st_size < 40000000, p
        assert not {'__pycache__', 'node_modules', '.venv', 'venv', '.pytest_cache'}.intersection(p.parts), p
        if p.suffix == '.py':
            ast.parse(p.read_bytes(), filename=str(p))
            syntax += 1
    for p in S.rglob('*.md'):
        for target in re.findall(r'\[[^\]\n]*\]\(([^\n)]+)\)', p.read_text()):
            target = target.split(' "')[0].strip('<>')
            u = urllib.parse.urlsplit(target)
            if u.scheme or u.netloc or not u.path:
                continue
            dest = (p.parent / urllib.parse.unquote(u.path)).resolve()
            assert dest.exists() or (not check and dest in [manifest.resolve(), validation.resolve()]), (p, target)
            links += 1
    result = dict(
        status='pass_complete_four_question_historical_research_with_explicit_source_limits',
        actual_question_workers_finished=4, question_seals=seals,
        exact_question_owned_hash_checks=checks,
        independent_reviews=[pin(D / name) for name in reviews],
        historical_acceptance=pin(D / 'coordinator-priority-acceptance.json'),
        frozen_contract=pin(D / 'turnout/priority-set.json'),
        complete_root_fields=24, complete_companions=504, complete_recursive_objects=724943,
        complete_reference_partitions=5, producer_first_pair_listed_bodies=2654,
        original_dependency_entries_including_failures=417,
        native_publication_observations=575, municipal_labels=564, administrative_observations=11,
        ordered_priority=233, ordered_remainder=342, all_county_parents=21,
        published_six_candidate_denominator=4031795, top15=631518,
        preceding232=3224325, priority_votes=3229453, crossing_votes=5128,
        crossing_source_key='2024-official-general-results-us-senate-monmouth:p0001:l0016',
        remainder_votes=802342, historical_native_rows_across_four_contests=2296,
        county_baseline_rows=84, primary_county_candidate_controls=588,
        conditional_settings=13, state_scenarios=40, every_unit_targets=8588,
        independent_official_checks=official['checks'], independent_map_checks=maps['checks'],
        complete_current_authority_inventory_rows=86, request_observations=485,
        response_hops=523, complete_distinct_official_entities=415,
        primary_Clarity_sets=11, general_Clarity_zero_template_sets=1,
        Senate_current_or_geographic_leaf_matches_approved=0,
        Python_AST_files=syntax, local_markdown_links=links,
        all_producer_bytes_unchanged=True, cache_dependency_directories_absent=True,
        strict_per_stored_object_limit=40000000,
        current_geometry_returns_liveIDs_cadence_exact_remainder_probability_approved=False,
        whole_manifest_excludes_only='data/coordinator-asset-manifest.json',
        validation_has_no_reverse_manifest_pin=True,
        qualification='Historical municipal/admin publication source scope and conditional arithmetic. Native finer tables/methods remain nonadditive; protected/null fields and Neptune/Somerset420/Clerk100/Kenndy source differences remain. Current general zero templates are setup only. Acquired native maps and Census fallbacks have no approved result-leaf/current/legal crosswalk. Full later ballot/write-in eligibility, law/docket exhaustion, genuine November identities/votes/cadence/outstanding pools and calibration remain external qualifications.'
    )
    b = (json.dumps(result, indent=2, ensure_ascii=False) + '\n').encode()
    if check:
        assert validation.read_bytes() == b
    else:
        validation.write_bytes(b)
    rows = [pin(p) for p in sorted(S.rglob('*')) if p.is_file() and p != manifest]
    whole = dict(schema='NJ-coordinator-whole-state-assets-v1', assets=rows,
                 excludes_only='data/coordinator-asset-manifest.json', total_files=len(rows),
                 total_bytes=sum(r['bytes'] for r in rows), maximum_stored_bytes=max(r['bytes'] for r in rows),
                 all_producer_bytes_unchanged=True, validation_has_no_reverse_manifest_pin=True)
    b = (json.dumps(whole, indent=2, ensure_ascii=False) + '\n').encode()
    if check:
        assert manifest.read_bytes() == b
    else:
        manifest.write_bytes(b)
    print(json.dumps(dict(validation=pin(validation), manifest=pin(manifest), files=len(rows), total_bytes=whole['total_bytes'], maximum=whole['maximum_stored_bytes'])))


if __name__ == '__main__':
    main('--check' in sys.argv)
