"""Complete coordinator state seal; --check is read-only, no producer imports."""
from pathlib import Path
import ast
import hashlib
import json
import re
import sys
import urllib.parse

S = Path(__file__).resolve().parents[1]
D = S / 'data'
CACHE = {}


def pin(p):
    p = p.resolve()
    if p not in CACHE:
        b = p.read_bytes()
        CACHE[p] = dict(path=str(p.relative_to(S)), bytes=len(b), sha256=hashlib.sha256(b).hexdigest())
    return CACHE[p]


def read(p):
    return json.loads(p.read_bytes())


def main(check=False):
    manifest = D / 'coordinator-asset-manifest.json'
    validation = D / 'coordinator-validation.json'
    official = read(D / 'coordinator-official-final-review.json')
    maps = read(D / 'coordinator-maps-final-review.json')
    math = read(D / 'coordinator-first-pair-math-review.json')
    specs = [
        ('turnout', 'data/turnout/asset-manifest.json', 'owned_assets', 524, ['turnout.md', 'data/county-turnout.csv']),
        ('baselines', 'data/baselines/asset-manifest.json', 'owned_assets', 257, ['county-partisanship.md', 'data/county-baselines.csv']),
        ('official', 'data/results-sources/asset-manifest.json', 'owned', official['owned_entries'], ['official-results.md', 'data/official-results-sources.csv']),
        ('maps', 'maps/asset-manifest.json', 'owned_assets', 10155, ['precinct-maps.md']),
    ]
    seals = []
    checks = 0
    for role, name, key, count, extra in specs:
        p = S / name
        m = read(p)
        rows = m[key]
        assert len(rows) == count
        actual = {str(q.relative_to(S)) for q in p.parent.rglob('*') if q.is_file() and q != p} | set(extra)
        assert actual == {r['path'] for r in rows} and len(actual) == count, role
        for r in rows:
            assert pin(S / r['path']) == r, r['path']
            checks += 1
        seals.append(dict(role=role, manifest=pin(p), owned_listed_files=count))
    a = read(D / 'coordinator-priority-acceptance.json')
    c = read(D / 'turnout/priority-set.json')
    assert pin(D / 'turnout/priority-set.json') == a['frozen_contract']
    assert len(c) == 25 and a['complete_source_object_count'] == 397917
    assert len(a['complete_source_companion_files']) == 174 and len(a['complete_source_object_reference_bodies']) == 3
    assert a['source_candidate_denominator'] == 3407108 and a['top15_votes'] == 58012
    assert (len(a['ordered_full_keys']), len(a['ordered_priority_keys']), len(a['ordered_remainder_keys'])) == (2394,1470,924)
    assert a['ordered_full_keys'] == a['ordered_priority_keys'] + a['ordered_remainder_keys']
    assert len(a['ordered_priority_parent_literals']) == 287
    for k in ['current_geography_approved', 'current_November_returns_admitted', 'current_choice_or_reporting_IDs_approved', 'legal_native_80_robustness_approved', 'live_cadence_or_exact_remainder_approved', 'collector_or_probability_approval']:
        assert a[k] is False
    reviews = ['coordinator-turnout-final-review.json', 'coordinator-baseline-final-review.json',
               'coordinator-first-pair-math-review.json', 'coordinator-live-input-review/review.json',
               'coordinator-acceptance-validation.json', 'coordinator-native-map-snapshot-review.json',
               'coordinator-maps-final-review.json', 'coordinator-maps-visual-review.json',
               'coordinator-official-final-review.json', 'coordinator-current-order-review/review.json']
    for name in reviews:
        status = read(D / name)['status']
        assert status.startswith('pass') or status.startswith('actual_coordinator'), (name,status)
    assert official['priority'] == maps['priority'] == 1470
    assert official['remainder'] == maps['remainder'] == 924
    assert math['state_scenarios'] == 36 and math['every_unit_target_rows'] == 36702
    syntax = links = 0
    for p in S.rglob('*'):
        if not p.is_file():
            continue
        assert p.stat().st_size < 40000000, p
        assert not any(v in p.parts for v in ['__pycache__', 'node_modules', '.venv', 'venv', '.pytest_cache']), p
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
            assert dest.exists() or (not check and dest in [manifest.resolve(), validation.resolve()]), (p,target)
            links += 1
    result = dict(status='pass_complete_four_question_historical_research_with_explicit_source_limits',
                  actual_question_workers_finished=4, question_seals=seals,
                  exact_question_owned_hash_checks=checks,
                  independent_reviews=[pin(D / name) for name in reviews],
                  historical_acceptance=pin(D / 'coordinator-priority-acceptance.json'),
                  frozen_contract=pin(D / 'turnout/priority-set.json'),
                  full_contract_root_fields=25, complete_companions=174, complete_recursive_objects=397917,
                  full_native_source_observations=2394, ordered_priority=1470, ordered_remainder=924,
                  all_municipal_parents=351, priority_municipal_parents=287,
                  named_pair_denominator=3407108, top15=58012, preceding1469=2725231,
                  priority_votes=2726450, crossing_literal=['Northampton','3','B'], crossing_votes=1219,
                  remainder_votes=680658, separate_AllOthers=6221, separate_Blanks=99601, separate_TBC=3512930,
                  native_GIS_features=[2256,147], map_original_PDFs=508, automatically_rendered_map_pages=3526,
                  worker_manual_map_PDF_first_pages=6, worker_manual_native_previews=4,
                  coordinator_additional_map_PDF_first_pages=2, coordinator_additional_native_previews=1,
                  no_original_SHP_archive_claim=True, current_source_leaf_matches=0,
                  independent_official_checks=official['checks'], independent_map_checks=maps['checks'],
                  independently_checked_state_scenarios=36, every_unit_target_rows=36702,
                  Python_AST_files=syntax, local_markdown_links=links,
                  all_producer_bytes_unchanged=True, cache_dependency_directories_absent=True,
                  strict_per_stored_object_limit=40000000,
                  current_geometry_returns_liveIDs_cadence_exact_remainder_probability_approved=False,
                  whole_manifest_excludes_only='data/coordinator-asset-manifest.json',
                  validation_has_no_reverse_manifest_pin=True,
                  qualification='Historical source dispatch and conditional arithmetic only. Unknown eligible/named AllOthers, method/admin/registration/nonvote scopes and 2022HTML/2020turnout33/2024method64 disagreements retained. Acquired maps are shared native/historical context with zero approved result-leaf matches. Secretary certification-only publication, incomplete directory/raw access, local-chain gaps, bounded current roster/law/docket findings, genuine November identities/votes/cadence/outstanding pools and calibration remain precise external qualifications.')
    b = (json.dumps(result, indent=2, ensure_ascii=False)+'\n').encode()
    if check:
        assert validation.read_bytes() == b
    else:
        validation.write_bytes(b)
    CACHE.pop(validation.resolve(), None)
    rows = [pin(p) for p in sorted(S.rglob('*')) if p.is_file() and p != manifest]
    whole = dict(schema='MA-coordinator-whole-state-assets-v1', assets=rows,
                 excludes_only='data/coordinator-asset-manifest.json', total_files=len(rows),
                 total_bytes=sum(r['bytes'] for r in rows), maximum_stored_bytes=max(r['bytes'] for r in rows),
                 all_producer_bytes_unchanged=True, validation_has_no_reverse_manifest_pin=True)
    b = (json.dumps(whole, indent=2, ensure_ascii=False)+'\n').encode()
    if check:
        assert manifest.read_bytes() == b
    else:
        manifest.write_bytes(b)
    print(json.dumps(dict(validation=pin(validation), files=len(rows), total_bytes=whole['total_bytes'], maximum=whole['maximum_stored_bytes'])))


if __name__ == '__main__':
    main('--check' in sys.argv)
