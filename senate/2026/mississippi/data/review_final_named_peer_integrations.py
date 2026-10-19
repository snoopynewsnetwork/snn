"""Recompute the new immutable named-field reciprocal proofs within prior scopes."""
from pathlib import Path
from collections import Counter
import csv, gzip, hashlib, io, json

from review_allfield_milestone import NAMES, load, sources

DATA = Path(__file__).resolve().parent
ROOT = DATA.parent
QA = DATA / 'coordinator-qa/final-named-peer-integration-v1'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(ROOT)), bytes=len(b), sha256=sha(b))


def freeze(p, expected):
    q = QA / (p.name + '.gz')
    b = gzip.decompress(q.read_bytes()) if q.exists() else p.read_bytes()
    assert sha(b) == expected
    if not q.exists():
        q.write_bytes(gzip.compress(b, mtime=0))
    return json.loads(b), dict(original=dict(path=str(p.relative_to(ROOT)), bytes=len(b), sha256=sha(b)), lossless_copy=pin(q))


def body(a):
    z = (ROOT / a['stored_path']).read_bytes()
    b = gzip.decompress(z)
    assert len(z) == a['stored_bytes'] and sha(z) == a['stored_sha256']
    assert len(b) == a['original_bytes'] and sha(b) == a['original_sha256']
    return b


def main():
    QA.mkdir(parents=True, exist_ok=True)
    new24, new24pin = freeze(DATA / 'baselines/native-2024-all11-complete-peer-reconciliation.json', 'fc1e48f2e86922b9740d9878ab146245b1d9e023b7b157e5d2a92eed088b1a55')
    s24p = DATA / 'baselines/source/2024-all11-complete-peer-v1/snapshot.json'
    assert pin(s24p) == new24['input_snapshot']
    s24 = json.loads(s24p.read_bytes())
    assert pin(ROOT / s24['own_snapshot']['path']) == s24['own_snapshot']
    a = s24['peer_body']
    z = (ROOT / a['path']).read_bytes()
    raw = gzip.decompress(z)
    assert len(z) == a['stored_bytes'] == 96203 and sha(z) == a['stored_sha256'] == 'd066e45bebca7ba66163989165a430164f5b84cef61d9e2cda7e4bc4e1d23b6b'
    assert len(raw) == a['original_bytes'] == 2048366 and sha(raw) == a['original_sha256'] == 'b2a7e234eeb226bd13f35d3a4c32c867f88f7d59a680ec059a7378c036f1fbae'
    dep = json.loads(raw)
    _, items, original82 = load('82views', '94576fcfa4b7b245e2d5baa9e8366e4489594804f41694ea04a9f6315e46b336')
    expected = {}
    roles = Counter()
    alias_keys = set()
    for sid, s in sources(items).items():
        for p in s['pages']:
            rr = p.get('roles')
            if rr is None:
                rr = [{'summary_TOTAL': 'source_TOTAL', 'unused': 'unused_template_column'}.get(c['unit_type'], 'source_native_reporting_constituent') for c in p['columns']]
            for i, role in enumerate(rr):
                label = p['headers'][i]['label_literal'] if 'headers' in p else p['columns'][i]['native_label_literal'] if 'columns' in p else p['labels_literal'][i] if i < len(p['labels_literal']) else ''
                fields = {f.get('candidate', f.get('field')): f['values'][i] for f in p['fields']}
                assert set(fields) == set(NAMES)
                expected[sid, p['page'], i + 1] = (s['raw_sha256'], role, label, fields)
    rolemap = {'source_native_reporting_constituent': 'native', 'source_TOTAL': 'TOTAL', 'unused_template_column': 'unused', 'parallel_native_observation': 'parallel'}
    dep_rolemap = {'native_reporting_constituent': 'native', 'source_TOTAL': 'TOTAL', 'unused_template_column': 'unused', 'parallel_native_observation': 'parallel'}
    seen = set()
    for c in dep['columns']:
        key = c['source_id'], c['source_page'], c['source_column']
        assert key not in seen
        seen.add(key)
        rawsha, role, label, fields = expected[key]
        assert c['source_raw_sha256'] == rawsha and dep_rolemap[c['role']] == rolemap[role]
        values = {**c['Senate_candidate_votes'], **c['president_candidate_votes']}
        assert values == fields
        roles[rolemap[role]] += len(values)
        if ' '.join(label.split()) != ' '.join(c['label_literal'].split()):
            assert key[0] == 'sos-2024-county-holmes'
            assert ''.join(label.split()) == ''.join(c['label_literal'].split())
            alias_keys.update((*key, candidate) for candidate in values)
    assert seen == set(expected) and len(seen) == 2266
    assert dict(roles) == new24['positions_by_role'] == dict(native=19096, TOTAL=902, unused=4807, parallel=121)
    assert sum(roles.values()) == new24['positions'] == 24926
    assert alias_keys == {tuple(r['key']) for r in new24['literal_label_representation_aliases']} and len(alias_keys) == 22
    assert not new24['value_role_differences'] and new24['new_explicit_peer_unused_positions'] == 126
    assert pin(ROOT / new24['older_v4_body_unchanged']['path']) == new24['older_v4_body_unchanged']

    new18, new18pin = freeze(DATA / 'baselines/native-2018-peer-41views-v3-reconciliation.json', '8bdff466b3c624ab9e6fbfdf9d2384d500e7c0efb8c81de655ea005a06377420')
    s18p = DATA / 'baselines/source/native-2018-peer-41views-v3/snapshot.json'
    assert pin(s18p) == new18['peer_snapshot']
    s18 = json.loads(s18p.read_bytes())
    assert pin(ROOT / s18['own_witness']['path']) == s18['own_witness'] == new18['own_original_witness']
    assert s18['own_witness']['sha256'] == '90e14d7f6f34992c39b3d9370e954cc2d56ad7a58147103eaa0607bc139288d0'
    own = {}
    for r in csv.DictReader(io.StringIO(body(s18['own_flat']).decode())):
        key = r['source_id'], int(r['source_page']), int(r['source_column']), r['candidate']
        assert key not in own
        own[key] = r
    oldp = DATA / 'coordinator-independent-2018-through43-review.json'
    assert pin(oldp)['sha256'] == '61749b4a661d6fec94570713fa25c11750768d530d8e53c8114f0eab0bbf7b83'
    old = json.loads(oldp.read_bytes())
    captured = {x['original']['path']: x for x in old['complete_frozen_worker_derivative_bodies']}
    rows = []
    compared_bodies = []
    for a in s18['pins']:
        b = body(a)
        previous = captured[a['original_path']]
        assert previous['original']['sha256'] == sha(b) and previous['original']['bytes'] == len(b)
        assert gzip.decompress((ROOT / previous['lossless_copy']['path']).read_bytes()) == b
        compared_bodies.append(dict(path=a['original_path'], bytes=len(b), sha256=sha(b)))
        if a['original_path'].endswith('.csv'):
            rows.extend(csv.DictReader(io.StringIO(b.decode())))
    assert len(compared_bodies) == 42
    positions = set()
    rolecounts = Counter()
    units = set()
    sourcehashes = {}
    rmap = {'source_native_reporting_constituent': 'native', 'source_TOTAL': 'TOTAL', 'unused_template_column': 'unused'}
    for r in rows:
        key = r['source_id'], int(r['source_pdf_page']), int(r['physical_source_column']), r['candidate']
        assert key not in positions
        positions.add(key)
        o = own[key]
        assert rmap[r['role']] == o['role']
        assert r['votes'] == o['votes']
        assert r['source_raw_sha256'] == o['source_raw_sha256'] and r['county_fips'] == o['county_fips']
        assert ' '.join(r['literal_source_header'].split()) == ' '.join(o['literal_native_label'].split())
        rolecounts[o['role']] += 1
        sourcehashes[r['source_id']] = r['source_raw_sha256']
        if o['role'] == 'native':
            units.add(key[:3])
    omitted_sources = set(r['source_id'] for r in old['source_findings']) - set(sourcehashes)
    assert omitted_sources == {'sos-2018-county-quitman', 'sos-2018-runoff-county-quitman'}
    assert len(positions) == new18['source_candidate_positions'] == 2530 and len(units) == new18['source_native_observations'] == 578
    assert len(sourcehashes) == new18['source_stage_views'] == 41 and sourcehashes == new18['source_hashes']
    assert dict(rolecounts) == new18['candidate_positions_by_role'] == dict(native=1752, TOTAL=124, unused=654)
    assert sum(v for k, v in rolecounts.items() if k != 'unused') == new18['numeric_positions'] == 1876 and not new18['differences']
    for pair in new18['source_page_render_pairs']:
        for side in ('own', 'peer'):
            assert pin(ROOT / pair[side + '_raster'])['sha256'] == pair[side + '_raster_sha256']
    out = dict(
        status='pass_bounded_final_named_reciprocal_integrations',
        complete_preferred2024=dict(worker_proof=new24pin, input_snapshot=pin(s24p), independent_original82=original82, exact_peer_dependency=pin(ROOT / s24['peer_body']['path']), source_columns=2266, candidate_positions=24926, candidate_positions_by_role=dict(roles), explicit_prior_template_omissions_now_null=126, Holmes_wrap_representation_positions=22, prior_V4_unchanged=new24['older_v4_body_unchanged']),
        reciprocal2018=dict(worker_proof=new18pin, input_snapshot=pin(s18p), original164=s18['own_witness'], earlier_coordinator43=pin(oldp), exact_bodies_reused_from_coordinator43=compared_bodies, source_stages=41, source_native_observations=578, candidate_positions=2530, candidate_positions_by_role=dict(rolecounts), subset_excludes_only=sorted(omitted_sources), independent_original_scope_expanded=False),
        qualification='New reciprocal proofs recompute against complete immutable original source witnesses. All2024 named values/nulls/roles agree with exact source dependency and82original ledgers;22Holmes hyphen-wrap representations remain explicit, and126old omitted template fields are null rather than zero. New2018proof is an exact42-body subset of the earlier43-stage coordinator review, excluding only twoQuitman stages; it adds no independent original cells. Both source raster hashes remain separately verified without raster/numeric-window/ID/current-geography equivalence. Source Tunica one-vote and Leflore ten-vote residuals remain unallocated. Prior proofs and source bodies stay unchanged.',
        formal_native887_dispatch_accepted=False,
        current_geography_approved=False,
    )
    p = DATA / 'coordinator-final-named-peer-integration-review.json'
    b = (json.dumps(out, indent=2) + '\n').encode()
    if p.exists():
        assert p.read_bytes() == b
    else:
        p.write_bytes(b)
    print(json.dumps(pin(p)))


if __name__ == '__main__':
    main()
