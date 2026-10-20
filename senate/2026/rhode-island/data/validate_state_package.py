"""Coordinator whole-state historical research seal; --check performs no writes."""
from pathlib import Path
import ast, hashlib, json, re, sys, urllib.parse

S = Path(__file__).resolve().parents[1]
D = S / 'data'
CACHE = {}

def load(p):
    return json.loads(p.read_bytes())

def pin(p):
    p = p.resolve()
    if p not in CACHE:
        b = p.read_bytes()
        CACHE[p] = dict(path=str(p.relative_to(S)), bytes=len(b), sha256=hashlib.sha256(b).hexdigest())
    return CACHE[p]

def main(check=False):
    mf = D / 'coordinator-asset-manifest.json'
    validation = D / 'coordinator-validation.json'
    specs = [
        ('turnout', 'data/turnout/asset-manifest.json', 'owned_assets', 378, ['turnout.md', 'data/county-turnout.csv']),
        ('baselines', 'data/baselines/asset-manifest.json', 'owned_assets', 234, ['county-partisanship.md', 'data/county-baselines.csv']),
        ('official', 'data/results-sources/asset-manifest.json', 'owned_assets', 1236, ['official-results.md', 'data/official-results-sources.csv']),
        ('maps', 'maps/manifest.json', 'owned_files', 710, ['precinct-maps.md'])
    ]
    seals = []
    n = 0
    for role, path, key, count, extra in specs:
        p = S / path
        m = load(p)
        rows = m[key]
        actual = {str(f.relative_to(S)) for f in p.parent.rglob('*') if f.is_file() and f != p} | set(extra)
        assert len(rows) == len({r['path'] for r in rows}) == count
        assert {r['path'] for r in rows} == actual, role
        for r in rows:
            assert pin(S / r['path']) == {k:r[k] for k in ['path', 'bytes', 'sha256']} and r['bytes'] < 40000000, r['path']
            n += 1
        seals.append(dict(role=role, manifest=pin(p), owned_entries_excluding_manifest=count))
    a = load(D / 'coordinator-priority-acceptance.json')
    c = load(D / 'turnout/priority-set.json')
    assert pin(D / 'turnout/priority-set.json') == a['frozen_contract']
    assert len(c) == len(a['complete_root_field_semantics']) == 23
    assert len(a['complete_source_companion_files']) == 384 and a['complete_source_object_count'] == 1699508
    assert len(a['complete_source_object_reference_bodies']) == 12
    assert len(a['frozen_file_pins']) == 632 and len(a['historical_full_body_resolvers']) == 877
    full = c['complete_descending_order']
    assert len(full) == 458 and len(c['all_source_native_constituents']) == 497
    assert len(c['municipal_and_administrative_parent_sensitivity']['full_inventory']) == 43
    assert a['ordered_full_keys'] == [r['key'] for r in full]
    assert a['ordered_priority_keys'] == [r['key'] for r in full[:242]]
    assert a['ordered_remainder_keys'] == [r['key'] for r in full[242:]]
    assert sum(r['votes'] for r in full) == 491948
    assert sum(r['votes'] for r in full[:241]) == 393066
    assert sum(r['votes'] for r in full[:242]) == 394072
    assert len(a['ordered_priority_parent_keys']) == 37
    for k in ['current_geography_approved', 'current_November_returns_admitted', 'current_choice_or_reporting_IDs_approved', 'legal_native80_robustness_approved', 'live_cadence_or_exact_remainder_approved', 'collector_or_probability_approval']:
        assert a[k] is False
    reviews = ['coordinator-turnout-original-review.json', 'coordinator-turnout-repair-final-review.json', 'coordinator-baseline-final-review.json', 'coordinator-baseline-cli-review.json', 'coordinator-priority-validation.json', 'coordinator-official-final-review.json', 'coordinator-official-visual-review.json', 'coordinator-maps-final-review.json']
    for name in reviews:
        r = load(D / name)
        assert r['status'].startswith('pass'), name
    syntax = links = 0
    for p in S.rglob('*'):
        assert not {'__pycache__', 'node_modules', '.venv', 'venv', '.pytest_cache'} & set(p.relative_to(S).parts), p
        if not p.is_file():
            continue
        assert p.stat().st_size < 40000000, p
        if p.suffix == '.py':
            ast.parse(p.read_bytes(), filename=str(p)); syntax += 1
        if p.suffix != '.md':
            continue
        for target in re.findall(r'\[[^\]\n]*\]\(([^\n)]+)\)', p.read_text()):
            target = target.split(' "')[0].strip('<>')
            u = urllib.parse.urlsplit(target)
            if u.scheme or u.netloc or not u.path:
                continue
            dest = (p.parent / urllib.parse.unquote(u.path)).resolve()
            assert dest.exists() or (not check and dest in [mf.resolve(), validation.resolve()]), (p, target)
            links += 1
    result = dict(status='pass_complete_four_question_bounded_historical_research', actual_question_workers_finished=4, producer_seals=seals, exact_question_owned_hash_checks=n, independent_reviews=[pin(D / name) for name in reviews], external_historical_source_authority=pin(D / 'coordinator-priority-acceptance.json'), frozen_contract=pin(D / 'turnout/priority-set.json'), complete_roots=23, whole_companions=384, recursive_full_objects=1699508, ordered_ledgers=12, immutable_pins=632, historical_body_resolvers=877, full_ranked_Senate_contexts=458, priority_contexts=242, remainder_contexts=216, full_inventory_contexts=497, unavailable_Senate_contexts=39, municipal_parents=39, separate_federal_admin_contexts=4, priority_municipal_chains=37, reported_candidate_generic_votes=491948, top15_votes=34697, minimum80_votes=394072, preceding_241_votes=393066, independent_maps_checks=316080, complete_native_services=2, native_features_each=416, native_ID_pages_max50=18, map_PDFs=21, automatically_rendered_PDF_pages=36, static_HTML_atlas_pages=48, coordinator_manually_viewed_map_PDF_pages=2, coordinator_manually_viewed_native_previews=1, Python_AST_files=syntax, local_Markdown_links=links, all_producer_bytes_unchanged=True, inferred_result_polygon_joins=0, spatial_allocation=False, current_November_returns_IDs_geometry_eligible_pool_cadence_probability_approved=False, whole_manifest_excludes_only='data/coordinator-asset-manifest.json', validation_has_no_reverse_manifest_pin=True, qualifications='Corrected full literal write-in detail1227/eight versus historicalrow6-only1226/nine; generic1244 unchanged/unallocated. Four federal administrative contexts remain outside municipal totals. Root/nested/setup and state/local/shared-primary export scopes overlap. Directory/redirect/request metadata limits, legal declaration-versus-calendar recount dates, map vintage differences/invalid original and distinct416-feature coordinate/ring structures remain explicit. Later signed/amended roster/eligible write-ins, physical/current/legal/reporting joins, genuine November production returns, measured cadence, exact outstanding pool, collector and calibrated probabilities remain false/unknown external qualifications.')
    b = (json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode()
    if check:
        assert validation.read_bytes() == b
    else:
        validation.write_bytes(b)
    CACHE.pop(validation.resolve(), None)
    rows = [pin(p) for p in sorted(S.rglob('*')) if p.is_file() and p != mf]
    whole = dict(schema='RI-coordinator-complete-state-assets-v1', assets=rows, excludes_only='data/coordinator-asset-manifest.json', total_files=len(rows), total_bytes=sum(r['bytes'] for r in rows), maximum_stored_bytes=max(r['bytes'] for r in rows), all_producer_bytes_unchanged=True, validation_has_no_reverse_manifest_pin=True)
    b = (json.dumps(whole, ensure_ascii=False, indent=2) + '\n').encode()
    if check:
        assert mf.read_bytes() == b
    else:
        mf.write_bytes(b)
    print(json.dumps(dict(status=result['status'], validation=pin(validation), files_excluding_manifest=len(rows), total_bytes=whole['total_bytes'], largest=whole['maximum_stored_bytes'])))

if __name__ == '__main__':
    main('--check' in sys.argv)
