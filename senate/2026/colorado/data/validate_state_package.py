"""Coordinator whole-state seal. --check is strictly read-only."""
from pathlib import Path
import ast
import hashlib
import json
import re
import sys
import urllib.parse

D = Path(__file__).resolve().parent
S = D.parent


def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(S)), bytes=len(b), sha256=hashlib.sha256(b).hexdigest())


def load(p):
    return json.loads(p.read_bytes())


def main(check=False):
    manifest_path = D / 'coordinator-asset-manifest.json'
    validation_path = D / 'coordinator-validation.json'
    manifests = []
    checked = 0
    for role, relative, key, expected, refs_key, extra in [
        ('turnout', 'data/turnout/asset-manifest.json', 'assets', 129, None, ['turnout.md', 'data/county-turnout.csv']),
        ('baselines', 'data/baselines/asset-manifest.json', 'assets', 107, 'referenced_originals', ['county-partisanship.md', 'data/county-baselines.csv']),
        ('official', 'data/results-sources/asset-manifest.json', 'assets', 714, 'immutable_external_files', ['official-results.md', 'data/official-results-sources.csv']),
        ('maps', 'maps/asset-manifest.json', 'owned_files', 749, 'read_only_dependencies', ['precinct-maps.md']),
    ]:
        p = S / relative
        m = load(p)
        owned = m[key]
        assert len(owned) == expected
        refs = m[refs_key] if refs_key else []
        for e in owned + refs:
            assert pin(S / e['path']) == {k: e[k] for k in ['path', 'bytes', 'sha256']}
            assert e['bytes'] < 40_000_000
            checked += 1
        actual = {str(f.relative_to(S)) for f in p.parent.rglob('*') if f.is_file() and f != p} | set(extra)
        assert actual == {e['path'] for e in owned}
        manifests.append(dict(role=role, manifest=pin(p), exact_owned=expected, complete_immutable_external=len(refs)))
    acceptance = load(D / 'coordinator-priority-acceptance.json')
    p = D / 'turnout/priority-set.json'
    assert pin(p) == acceptance['frozen_contract']
    c = load(p)
    assert len(c['full_order']) == 3199 and len(c['county_parents']) == len(c['county_native_hierarchy']) == 64
    assert len(c['ordered_priority_keys']) == 1992 and len(c['ordered_remainder_keys']) == 1207
    assert (c['total'], c['top15_votes'], c['priority_votes'], c['preceding_votes'], c['crossing_votes'], c['remainder_votes']) == (3192745, 39005, 2554233, 2553363, 870, 638512)
    assert c['current_geography_approved'] is False and c['formal_coordinator_acceptance'] is False
    reviews = [
        'coordinator-first-pair-source-review.json', 'coordinator-first-pair-target-review.json',
        'coordinator-annotated-turnout-review.json', 'coordinator-current-roster-original-review.json',
        'coordinator-finished-packages-review.json', 'coordinator-finished-visual-review.json',
        'coordinator-final-command-review.json', 'coordinator-cache-cleanup-review.json',
        'coordinator-frozen-whitespace-review.json',
    ]
    for name in reviews:
        assert load(D / name)['status'].lower().startswith('pass')
    syntax = links = 0
    for p in S.rglob('*'):
        if p.is_file():
            assert p.stat().st_size < 40_000_000
            assert not any(x in p.parts for x in ['__pycache__', '.venv', 'node_modules', '.pytest_cache'])
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
            assert dest.exists() or (not check and dest in {manifest_path.resolve(), validation_path.resolve()}), (str(p), target)
            links += 1
    output = dict(status='pass_complete_four_question_historical_research_with_explicit_source_limits',
                  question_manifests=manifests, exact_question_owned_and_external_hash_checks=checked,
                  actual_question_workers_finished=4, independent_reviews=[pin(D / name) for name in reviews],
                  external_historical_authority=pin(D / 'coordinator-priority-acceptance.json'), frozen_contract=pin(D / 'turnout/priority-set.json'),
                  historical_native=3199, priority=1992, remainder=1207, parents=64, priority_parents=45,
                  reported_candidate_votes=3192745, top15_votes=39005, priority_votes=2554233, preceding1991=2553363,
                  original_historical_contexts=9831, all_candidate_positions=101529, native_candidate_positions=99514,
                  original_numeric_positions=121191, original_statistic_XML_cells=22281, cached_error_tail=1043548,
                  source_review_checks=261529, independent_arithmetic_checks=1178902, state_scenarios=36, county_targets=1152, native_targets=57816,
                  final_official_checks=1346861, final_maps_checks=2701008, raw_official_observations=866, raw_map_receipts=186,
                  original_map_services=4, complete_service_features=527, Adams_true_curves_retained=49,
                  Census_features=3108, Census_XY=1283644, Fremont_SHP_features=20, Fremont_SHP_XY=27642,
                  acquired_PDFs=22, automatically_rendered_pages=114, qualified_county_reference_priority_entries=1432, Census_only_priority_entries=560,
                  current_geographic_or_November_return_approval=False, local_Markdown_links=links, Python_AST_files=syntax,
                  all_stored_artifacts_strictly_below40MB=True, cache_dependency_trees_absent=True,
                  whole_manifest_excludes_only='data/coordinator-asset-manifest.json', validation_has_no_reverse_manifest_pin=True,
                  qualification='Historical candidate/scenario/source/map-reference research only. Pseudo-ballots, source-null fields, Montezuma annotated/raw lanes and16statistics-unavailable contexts remain explicit. Current roster/setup is bounded; zero Denver setup and November vendor403s are not changing returns. All map references are shared-parent, no current/legal leaf join;49curves excluded only from linear derivatives, positive intersections diagnostic. ElectronicUOCAVA submitted/received disagreement and later signed-ballot/court effects remain external. No exact outstanding pool, measured cadence, collector or calibrated probability approved.')
    value = (json.dumps(output, indent=2) + '\n').encode()
    if check:
        assert validation_path.read_bytes() == value
    else:
        validation_path.write_bytes(value)
    entries = [pin(p) for p in sorted(S.rglob('*')) if p.is_file() and p != manifest_path]
    output = dict(schema='CO-coordinator-whole-state-assets-v1', assets=entries,
                  excludes_only='data/coordinator-asset-manifest.json', total_files=len(entries),
                  total_bytes=sum(e['bytes'] for e in entries), maximum_stored_bytes=max(e['bytes'] for e in entries),
                  worker_assets_unchanged=True, validation_no_reverse_manifest_pin=True)
    value = (json.dumps(output, indent=2) + '\n').encode()
    if check:
        assert manifest_path.read_bytes() == value
    else:
        manifest_path.write_bytes(value)
    print(json.dumps(dict(validation=pin(validation_path), manifest=pin(manifest_path), files=len(entries), total_bytes=output['total_bytes'], maximum=output['maximum_stored_bytes'])))


if __name__ == '__main__':
    main('--check' in sys.argv)
