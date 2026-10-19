"""Whole-state integration seal; --check verifies bytes without writing."""
from pathlib import Path
import ast
import gzip
import hashlib
import json
import re
import sys
import urllib.parse

D = Path(__file__).resolve().parent
S = D.parent


def pin(path):
    value = path.read_bytes()
    return dict(path=str(path.relative_to(S)), bytes=len(value), sha256=hashlib.sha256(value).hexdigest())


def load(path):
    return json.loads(path.read_bytes())


def main(check=False):
    mfpath = D / 'coordinator-asset-manifest.json'
    validation = D / 'coordinator-validation.json'
    manifests = []
    total_pins = 0
    for role, relative, key, expected in [
        ('turnout', 'data/turnout/asset-manifest.json', 'owned_assets', 86),
        ('baselines', 'data/baselines/asset-manifest.json', 'owned', 70),
        ('official', 'data/results-sources/manifest.json', 'owned', 1011),
        ('maps', 'maps/manifest.json', 'owned', 1632),
    ]:
        path = S / relative
        manifest = load(path)
        owned = manifest[key]
        assert len(owned) == expected
        for entry in owned:
            assert pin(S / entry['path']) == {k: entry[k] for k in ['path', 'bytes', 'sha256']}
            assert entry['bytes'] < 40_000_000
            total_pins += 1
        folder = path.parent
        extra = {'turnout': {'turnout.md', 'data/county-turnout.csv'},
                 'baselines': {'county-partisanship.md', 'data/county-baselines.csv'},
                 'official': {'official-results.md', 'data/official-results-sources.csv'},
                 'maps': {'precinct-maps.md'}}[role]
        actual = {str(p.relative_to(S)) for p in folder.rglob('*') if p.is_file() and p != path} | extra
        assert actual == {x['path'] for x in owned}
        if role == 'official':
            references = manifest['immutable_external_complete_references']
        elif role == 'maps':
            references = load(S / 'maps/frozen-references.json')['references']
        else:
            references = []
        for entry in references:
            assert pin(S / entry['path']) == {k: entry[k] for k in ['path', 'bytes', 'sha256']}
            assert entry['bytes'] < 40_000_000
            total_pins += 1
        manifests.append(dict(role=role, manifest=pin(path), exact_owned=expected, complete_immutable_references=len(references)))
    a = load(D / 'coordinator-priority-acceptance.json')
    cpath = D / 'turnout/priority-set.json'
    assert pin(cpath) == a['frozen_contract']
    c = load(cpath)
    assert len(c['complete_order']) == 985 and len(c['all_county_constituents']) == 44
    assert len(c['ordered_priority_keys']) == 528 and len(c['ordered_remainder_keys']) == 457
    assert c['primary_priority']['denominator'] == 905057
    assert c['primary_priority']['minimum80_votes'] == 724515 and c['primary_priority']['preceding_votes'] == 723753
    assert c['primary_priority']['remainder_votes'] == 180542 and c['primary_priority']['top15_votes'] == 65391
    assert not c['priority_accepted'] and not c['current_geography_approved']
    reviews = [
        'coordinator-first-pair-original-review.json', 'coordinator-first-pair-target-review.json',
        'coordinator-turnout-final-seal-review.json', 'coordinator-first-pair-original-visual-review.json',
        'coordinator-official-original-review.json', 'coordinator-finished-official-review.json',
        'coordinator-official-command-review.json', 'coordinator-map-native-preparation-review.json',
        'coordinator-map-original-topology-review.json', 'coordinator-finished-maps-review.json',
        'coordinator-finished-maps-visual-review.json',
    ]
    for name in reviews:
        assert load(D / name)['status'].startswith('pass')
    syntax = links = 0
    for path in S.rglob('*'):
        if path.is_file():
            assert path.stat().st_size < 40_000_000
            assert not any(x in path.parts for x in ['__pycache__', '.venv', 'node_modules', '.cache'])
            if path.suffix == '.py':
                ast.parse(path.read_bytes(), filename=str(path))
                syntax += 1
    for path in S.rglob('*.md'):
        for target in re.findall(r'\[[^\]\n]*\]\(([^\n)]+)\)', path.read_text()):
            target = target.split(' "')[0].strip('<>')
            url = urllib.parse.urlsplit(target)
            if url.scheme or url.netloc or not url.path:
                continue
            resolved = (path.parent / urllib.parse.unquote(url.path)).resolve()
            assert resolved.exists() or (not check and resolved in {validation.resolve(), mfpath.resolve()}), (str(path), target)
            links += 1
    out = dict(status='pass_complete_four_question_historical_research_with_explicit_source_limits',
               question_manifests=manifests, exact_question_owned_and_external_pin_checks=total_pins,
               question_workers_actually_finished=4, independent_reviews=[pin(D / name) for name in reviews],
               external_historical_authority=pin(D / 'coordinator-priority-acceptance.json'), frozen_contract=pin(cpath),
               primary_source_native=985, priority=528, remainder=457, all_county_parents=44, priority_parents=32,
               named_source_denominator=905057, top15_votes=65391, priority_votes=724515, preceding527=723753,
               original_candidate_controls=36565, original_statistic_positions=2099,
               first_pair_source_checks=380448, independent_target_checks=951622,
               original_current_primary_export_rows=419099, original_current_primary_export_cells=3131500,
               full_state_map_features=976, exact_state_native_positions=749523, Cassia_records=24, Cassia_XY=17319,
               current_geographic_or_November_return_approval=False, Python_AST_files=syntax,
               local_Markdown_links=links, all_stored_artifacts_strictly_below40MB=True, no_cache_dependency_trees=True,
               whole_manifest_excludes_only='data/coordinator-asset-manifest.json',
               qualification='Historical source/scenario/map-reference research only. Boundary source conflicts/net3, sparse original nulls, LisaMarie46/67 unknown-stage difference, incompatible map/reporting universes and dated/incidental publications remain explicit. Invalid Roseberry and241state/34Cassia intersections are unrepaired diagnostics. Bounded current sample/operative-text evidence does not exhaust later signed ballot/court/write-in scope. No current IDs/geometry, genuine changing November returns, measured cadence, exact remaining pool, collector or calibrated probability is approved. Validation has no reverse whole-manifest hash.')
    value = (json.dumps(out, indent=2) + '\n').encode()
    if check:
        assert validation.read_bytes() == value
    else:
        validation.write_bytes(value)
    entries = [pin(p) for p in sorted(S.rglob('*')) if p.is_file() and p != mfpath]
    out = dict(schema='ID-coordinator-whole-state-assets-v1', assets=entries,
               excludes_only='data/coordinator-asset-manifest.json', total_files=len(entries),
               total_bytes=sum(x['bytes'] for x in entries), maximum_stored_bytes=max(x['bytes'] for x in entries),
               worker_assets_unchanged=True, validation_no_reverse_manifest_pin=True)
    value = (json.dumps(out, indent=2) + '\n').encode()
    if check:
        assert mfpath.read_bytes() == value
    else:
        mfpath.write_bytes(value)
    print(json.dumps(dict(validation=pin(validation), whole_manifest=pin(mfpath), files=len(entries), total_bytes=out['total_bytes'], maximum=out['maximum_stored_bytes'])))


if __name__ == '__main__':
    main('--check' in sys.argv)
