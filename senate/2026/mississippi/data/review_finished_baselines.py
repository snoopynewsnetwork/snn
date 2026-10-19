"""Read-only final owned-manifest and complete named-field v2 proposal review."""
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import ast, csv, gzip, hashlib, io, json, re

DATA = Path(__file__).resolve().parent
ROOT = DATA.parent
OUT = DATA / 'baselines'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(ROOT)), bytes=len(b), sha256=sha(b))


def checkpin(a):
    assert pin(ROOT / a['path']) == a


def frozen(a):
    p = ROOT / a.get('frozen_path', a.get('stored_path'))
    z = p.read_bytes()
    b = gzip.decompress(z)
    assert len(z) == a['stored_bytes'] < 40000000 and sha(z) == a['stored_sha256']
    assert len(b) == a['original_bytes'] and sha(b) == a['original_sha256']
    return b


def main():
    mp = OUT / 'asset-manifest.json'
    assert pin(mp) == dict(path='data/baselines/asset-manifest.json', bytes=3387560, sha256='f5efa2370206c204af2bb557ced7732fc7b79e4540edbb454cf2350f142aecb2')
    manifest = json.loads(mp.read_bytes())
    expected = {str(p.relative_to(ROOT)) for p in OUT.rglob('*') if p.is_file() and p != mp}
    expected.update(['county-partisanship.md', 'data/county-baselines.csv'])
    listed = {a['path'] for a in manifest['assets']}
    assert len(listed) == len(manifest['assets']) == manifest['asset_count'] == 12404 and listed == expected
    def verify_asset(a):
        p = ROOT / a['path']
        assert p.is_file() and not p.is_symlink()
        b = p.read_bytes()
        assert len(b) == a['bytes'] < 40000000 and sha(b) == a['sha256'], a['path']
        if p.suffix == '.py':
            ast.parse(b, filename=str(p))
        return len(b)
    with ThreadPoolExecutor(max_workers=4) as pool:
        sizes = list(pool.map(verify_asset, manifest['assets']))
    assert not any(p.name in ('__pycache__', 'node_modules', '.venv', '.pytest_cache') or p.suffix in ('.pyc', '.pyo') for p in OUT.rglob('*'))
    refs = manifest['original_references']
    assert len({r['id'] for r in refs}) == len(refs) == 419
    for r in refs:
        p = ROOT / r['path']
        z = p.read_bytes()
        b = gzip.decompress(z) if p.suffix == '.gz' else z
        assert len(z) < 40000000 and sha(z) == r['stored_sha256'] and sha(b) == r['raw_sha256']
    vp = OUT / 'validation.json'
    assert pin(vp) == dict(path='data/baselines/validation.json', bytes=368329, sha256='6d06794d0e067c6d03916210f51763bf167f2e99a78c4921b49fc680895d7b7f')
    validation = json.loads(vp.read_bytes())
    assert len(validation['checks']) == 37 and validation['complete_owned_question']
    assert not validation['priority887_accepted'] and not validation['current2026_geography_approved']
    reportp = ROOT / 'county-partisanship.md'
    assert pin(reportp) == dict(path='county-partisanship.md', bytes=70445, sha256='8387e7ace452a41ec1ed2a8fb9a41bd9ae1d972fc54bc6bb2811d8b7d783241d')
    for p in (reportp, OUT / 'source/SCHEMA.md'):
        for target in re.findall(r'\]\(([^)]+)\)', p.read_text()):
            if target.startswith(('https://', 'http://', '#')):
                continue
            assert (p.parent / target.split('#')[0]).resolve().exists(), (p, target)

    sp = OUT / 'source/native-priority-v2/snapshot.json'
    assert pin(sp) == dict(path='data/baselines/source/native-priority-v2/snapshot.json', bytes=3275, sha256='a0432f1e47245c7b934a2328ebda95d3d96566c58cd3f71901406d060efc85ec')
    snapshot = json.loads(sp.read_bytes())
    bodies = {a['original_path']: frozen(a) for a in snapshot['pins']}
    contract = json.loads(bodies['data/baselines/native-priority-contract-v2.json'])
    rows = list(csv.DictReader(io.StringIO(bodies['data/baselines/native-priority-source-fields-v2.csv'].decode())))
    assert contract['coordinator_accepted'] is False and contract['current2026_geography_approved'] is False
    oldsp = ROOT / snapshot['previous_v1']['path']
    checkpin(snapshot['previous_v1'])
    old = json.loads(oldsp.read_bytes())
    oldcontract = json.loads(frozen(old['pins'][0]))
    unchanged = ['ordered_native_keys', 'ordered_priority_native_keys', 'ordered_nonpriority_native_keys', 'parent_all_native_keys', 'parent_priority_native_keys', 'primary_native_source_scope', 'county_parent_sensitivity', 'unknown_Tunica1_upper_bound_proof']
    for name in unchanged:
        assert contract[name] == oldcontract[name], name
    dep = DATA / 'turnout/source/2024-preferred-all11-source-fields-v1.json.gz'
    assert pin(dep)['sha256'] == 'd066e45bebca7ba66163989165a430164f5b84cef61d9e2cda7e4bc4e1d23b6b'
    raw = gzip.decompress(dep.read_bytes())
    assert sha(raw) == 'b2a7e234eeb226bd13f35d3a4c32c867f88f7d59a680ec059a7378c036f1fbae'
    priorproof = DATA / 'coordinator-integrated-preferred82-all11-payload-review.json'
    assert pin(priorproof)['sha256'] == '1d2be9c2467a3093deee4fc0bd15d6ac7c246e35ce7263051367f4aca72b50f0'
    depcols = {(c['source_id'], c['source_page'], c['source_column']): c for c in json.loads(raw)['columns']}
    rolemap = dict(native_reporting_constituent='native', source_TOTAL='TOTAL', unused_template_column='unused', parallel_native_observation='parallel')
    fields = Counter()
    native = {}
    seen = set()
    labels = []
    for c in contract['all_preferred_source_columns']:
        key = c['source_id'], c['PDFpage'], c['physical_source_column']
        assert key not in seen
        seen.add(key)
        p = depcols[key]
        assert c['source_raw_sha256'] == p['source_raw_sha256'] and c['role'] == rolemap[p['role']]
        assert c['county_fips'] == p['parent_county_fips'] and c['source_position_key'] == p['key']
        assert c['candidate_votes'] == {**p['president_candidate_votes'], **p['Senate_candidate_votes']}
        if c['label_literal'] != p['label_literal']:
            assert ''.join(c['label_literal'].split()) == ''.join(p['label_literal'].split())
            labels.append(dict(source_position=list(key), v2=c['label_literal'], turnout=p['label_literal']))
        fields[c['role']] += len(c['candidate_votes'])
        if c['role'] == 'native':
            native[c['source_position_key']] = c
    assert seen == set(depcols) and len(native) == 1736
    assert sum(fields.values()) == 24926 and fields == dict(native=19096, TOTAL=902, unused=4807, parallel=121)
    def pair(c):
        return c['candidate_votes']['Ty Pinkins'] + c['candidate_votes']['Roger F. Wicker']
    ordered = sorted(native, key=lambda k: (-pair(native[k]), k))
    assert ordered == contract['ordered_native_keys'] and ordered[:887] == contract['ordered_priority_native_keys'] and ordered[887:] == contract['ordered_nonpriority_native_keys']
    cumulative = 0
    prefix = []
    for i, (key, r) in enumerate(zip(ordered, rows), 1):
        c = native[key]
        cumulative += pair(c)
        prefix.append(cumulative)
        assert r['key'] == key and int(r['rank']) == i and int(r['named_Senate_pair_votes']) == pair(c) and int(r['cumulative_named_Senate_votes']) == cumulative
        assert json.loads(r['candidate_votes']) == c['candidate_votes'] and r['primary_priority'] == str(i <= 887)
    assert len(rows) == 1736 and cumulative == 1215400 and prefix[14] == 60019 and prefix[885:887] == [972157, 972656]
    assert all(5 * prefix[885] < 4 * denominator <= 5 * prefix[886] for denominator in [1215400, 1215401])
    assert 5 * (prefix[885] + 1) < 4 * 1215401
    for h in contract['historical_original_witnesses']:
        checkpin(h)
        for a in json.loads((ROOT / h['path']).read_bytes())['pins']:
            frozen(a)
    cp = OUT / 'source/native-priority-v2-field-evidence-v1/snapshot.json'
    assert pin(cp)['sha256'] == '9bfe1e6f08f9e9b12e494302c58176e38a2a610adeb0497d1785379227e5c02a'
    companion = json.loads(cp.read_bytes())
    assert len(companion['pins']) == 17
    for a in companion['pins']:
        assert frozen(a) == (ROOT / a['original_path']).read_bytes()
    rp = OUT / 'source/reproduction-complete-original-v1/completion.json'
    assert pin(rp)['sha256'] == '5c47dc35bc942c11b8a31d89aacee3f99c36d9e817650c220610b11da3cc5755'
    receipt = json.loads(rp.read_bytes())
    assert receipt['exit_code'] == 0 and receipt['completed_main_checks'] == 35
    for a in [receipt['execution_reproducer'], receipt['log']] + receipt['input_witnesses']:
        checkpin(a)
    for a in receipt['frozen_run_outputs']:
        frozen(a)
    log = (ROOT / receipt['log']['path']).read_text()
    assert 'pass_owned_research_with_explicit_source_limits' in log
    result = dict(status='pass_finished_owned_partisanship_manifest_and_complete_v2_proposal', owned_manifest=pin(mp), report=pin(reportp), county_CSV=pin(DATA / 'county-baselines.csv'), validation=pin(vp), final_owned_checks=37, owned_entries=12404, manifest_excludes_only_itself=True, listed_owned_bytes=sum(sizes), maximum_stored_owned_bytes=max(sizes), every_owned_asset_hash_size_and_python_AST_verified=True, original_reference_count=419, completed_original_reproduction_receipt=pin(rp), reproduction_then_current_checks=35, stable_source_calculator_rebuild_reexecuted_by_coordinator=False, complete_v2_proposal_snapshot=pin(sp), v2_body_pins=snapshot['pins'], unchanged_v1_fields=unchanged, all_preferred_columns=2266, candidate_positions=24926, role_field_counts=dict(fields), ordered_native=1736, priority_native=887, priority_parent_authorities=77, preceding886=972157, priority887=972656, source_pair_denominator=1215400, certified_pair_denominator=1215401, source_literal_wrap_representations=labels, full17_body_field_companion=pin(cp), historical_full_source_dependencies=contract['historical_original_witnesses'], qualification='All frozen owned paths and419read-only original references rehashed independently, no owned writes or mutating producer validator. Full original reproduction receipt/log/script/input/output pins verify exit0 at35then-current checks; two later packaging checks are included in final37. V2 preserves exact old order/parent maps and all24926named values/nulls, plus17complete located-control/peer bodies and full104/164historical witness dependencies. Source differences and incomplete independent historical replay remain explicit. Finished package readiness is distinct from formal dispatch/current2026 geography approval, which remain false.', formal_native887_dispatch_accepted=False, current_geography_approved=False)
    p = DATA / 'coordinator-finished-baseline-review.json'
    b = (json.dumps(result, indent=2) + '\n').encode()
    if p.exists():
        assert p.read_bytes() == b
    else:
        p.write_bytes(b)
    assert pin(mp)['sha256'] == 'f5efa2370206c204af2bb557ced7732fc7b79e4540edbb454cf2350f142aecb2'
    print(json.dumps(pin(p)))


if __name__ == '__main__':
    main()
