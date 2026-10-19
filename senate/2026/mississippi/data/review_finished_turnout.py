"""Read-only final turnout freeze, full native payload and historical dependency audit."""
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import ast, gzip, hashlib, json, re
from review_finished_baselines import pin, sha, frozen

DATA = Path(__file__).resolve().parent
ROOT = DATA.parent
OUT = DATA / 'turnout'


def main():
    mp = OUT / 'asset-manifest.json'
    assert pin(mp)['sha256'] == '4681e60b69fda456f8ff87d73c5a82a3c1a79e5210059fb9e7bc04f9a6c1d280'
    m = json.loads(mp.read_bytes())
    expected = {str(p.relative_to(ROOT)) for p in OUT.rglob('*') if p.is_file() and p != mp}
    expected.update(['turnout.md', 'data/county-turnout.csv'])
    listed = {a['path'] for a in m['owned_assets']}
    assert listed == expected and len(listed) == len(m['owned_assets']) == 13203
    def asset(a):
        p = ROOT / a['path']
        b = p.read_bytes()
        assert not p.is_symlink() and len(b) == a['bytes'] < 40000000 and sha(b) == a['sha256'], a['path']
        if p.suffix == '.py':
            ast.parse(b, filename=str(p))
        return len(b)
    with ThreadPoolExecutor(max_workers=4) as pool:
        sizes = list(pool.map(asset, m['owned_assets']))
    assert not any(p.name in ('__pycache__', 'node_modules', '.venv', '.pytest_cache') or p.suffix in ('.pyc', '.pyo') for p in OUT.rglob('*'))
    refs = m['read_only_shared_original_references']
    assert len(refs) == len({r['source_id'] for r in refs}) == 152
    for r in refs:
        z = (ROOT / r['path']).read_bytes()
        assert len(z) == r['stored_bytes'] < 40000000 and sha(z) == r['stored_sha256']
        assert sha(gzip.decompress(z) if r['path'].endswith('.gz') else z) == r['raw_sha256']
    vp = OUT / 'validation.json'
    assert pin(vp)['sha256'] == '2e21d3303a06ea531f8e17d2870ea2002cff50e9b47d9fd1a582b9f2fe8da071'
    v = json.loads(vp.read_bytes())
    assert len(v['checks']) == 117 and not v['failed_or_pending_checks'] and all(c['pass_'] for c in v['checks'].values())
    for p, expected_sha in [(ROOT / 'turnout.md', 'a72a5590e6f2bc34c9aa53f5d3bf639673f2cf1d248e37ddff4adaf9e2889628'), (DATA / 'county-turnout.csv', '14c5d0e6071bc7344f5f0784bb2f2c724dc20be529f4c343115d25bb1b216420')]:
        assert pin(p)['sha256'] == expected_sha
    for p in [ROOT / 'turnout.md', OUT / 'source/SCHEMA.md']:
        for target in re.findall(r'\]\(([^)]+)\)', p.read_text()):
            if not target.startswith(('http:', 'https:', '#')):
                assert (p.parent / target.split('#')[0]).resolve().exists(), (p, target)
    cp = OUT / 'priority-set.json'
    assert pin(cp) == dict(path='data/turnout/priority-set.json', bytes=13065430, sha256='782ca7899236ba06e53effee549c4e6845f936c9b4ceea3fecc8828dd9a08c32')
    q = json.loads(cp.read_bytes())
    v2sp = DATA / 'baselines/source/native-priority-v2/snapshot.json'
    assert pin(v2sp)['sha256'] == 'a0432f1e47245c7b934a2328ebda95d3d96566c58cd3f71901406d060efc85ec'
    v2 = json.loads(frozen(json.loads(v2sp.read_bytes())['pins'][0]))
    assert q['ordered_priority_keys'] == v2['ordered_priority_native_keys'] and q['priority_count'] == 887
    assert q['source_native_preferred_ordered_keys'] == v2['ordered_native_keys'] == [r['key'] for r in q['all_unit_order']]
    assert q['remainder']['ordered_keys'] == v2['ordered_nonpriority_native_keys'] and q['remainder']['count'] == 849 and q['remainder']['votes'] == 242744
    assert q['native_priority_by_parent'] == v2['parent_priority_native_keys']
    assert len(q['native_priority_by_parent']) == 82 and sum(bool(a) for a in q['native_priority_by_parent'].values()) == 77
    native = {c['source_position_key']: c for c in v2['all_preferred_source_columns'] if c['role'] == 'native'}
    cumulative = 0
    for i, r in enumerate(q['all_unit_order'], 1):
        c = native[r['key']]
        pair = {n: c['candidate_votes'][n] for n in ('Ty Pinkins', 'Roger F. Wicker')}
        assert r['rank'] == i and r['candidate_votes'] == pair and r['named_candidate_votes'] == sum(pair.values())
        cumulative += sum(pair.values())
        assert r['cumulative_votes'] == cumulative
    assert cumulative == 1215400 and q['top15']['votes'] == 60019
    assert q['minimum80']['preceding_votes'] == 972157 and q['minimum80']['votes'] == 972656
    assert 5 * (972157 + 1) < 4 * 1215401 <= 5 * 972656
    assert not q['current_2026_geographic_approval']
    source_rows = {(r['source_id'], r['source_page'], r['source_column']): r for r in q['source_native_constituents']}
    assert len(source_rows) == len(q['source_native_constituents']) == 2321
    dep = q['preferred_2024_all11_source_fields_dependency']
    dp = ROOT / dep['path']
    z = dp.read_bytes()
    raw = gzip.decompress(z)
    assert len(z) == dep['stored_bytes'] and sha(z) == dep['stored_sha256'] == 'd066e45bebca7ba66163989165a430164f5b84cef61d9e2cda7e4bc4e1d23b6b'
    assert len(raw) == dep['raw_bytes'] and sha(raw) == dep['raw_sha256'] == 'b2a7e234eeb226bd13f35d3a4c32c867f88f7d59a680ec059a7378c036f1fbae'
    all11 = json.loads(raw)
    v2cols = {(c['source_id'], c['PDFpage'], c['physical_source_column']): c for c in v2['all_preferred_source_columns']}
    counts = Counter()
    for c in all11['columns']:
        key = c['source_id'], c['source_page'], c['source_column']
        r = source_rows[key]
        assert r['key'] == c['key'] and r['role'] == c['role'] and r['source_raw_sha256'] == c['source_raw_sha256'] and r['label_literal'] == c['label_literal']
        assert r['candidate_votes'] == c['Senate_candidate_votes']
        assert r['separately_scoped_contests']['2024-president']['candidate_votes'] == c['president_candidate_votes']
        assert {**c['Senate_candidate_votes'], **c['president_candidate_votes']} == v2cols[key]['candidate_votes']
        counts[c['role']] += 11
    assert len(all11['columns']) == 2266 and sum(counts.values()) == 24926
    hp = OUT / 'historical-native-complete-dependencies.json'
    assert pin(hp) == dict(path='data/turnout/historical-native-complete-dependencies.json', bytes=216211, sha256='a4ea86ef031ff6fee3ee1f60520c5f0bf87730673d208fff4563a99d732daa20')
    hd = q['historical_source_native_dependencies']
    assert hd['path'] == hp.name and hd['sha256'] == pin(hp)['sha256'] and hd['bytes'] == pin(hp)['bytes']
    assert hd['full_peer_source_objects_canonical'] and not hd['own_direct_original_native_replay_complete']
    assert hd['own_direct_original_native_replay_scope'] == dict(**{'2020_publications':44, '2018_stage_views':43})
    historical = json.loads(hp.read_bytes())
    findings = {}
    for year, n in [('2020', 104), ('2018', 164)]:
        h = historical[year]
        sp = ROOT / h['canonical_snapshot_path']
        assert len(sp.read_bytes()) == h['canonical_snapshot_bytes'] and sha(sp.read_bytes()) == h['canonical_snapshot_sha256']
        snap = json.loads(sp.read_bytes())
        objects = {}
        assert len(snap['pins']) == len(h['canonical_lossless_component_pins'])
        for a, b in zip(snap['pins'], h['canonical_lossless_component_pins']):
            assert all(b[k] == val for k, val in a.items())
            raw = frozen(a)
            if a['original_path'].endswith('.json'):
                objects[Path(a['original_path']).name] = json.loads(raw)
        ss = objects['native-2020-additional-readings.json']['sources'] + objects['coahoma-2020-amendment-readings.json']['sources'] if year == '2020' else objects['native-2018-original-readings.json']['sources']
        assert len(ss) == len(h['complete_source_objects_in_ledger_order']) == n
        for s, item in zip(ss, h['complete_source_objects_in_ledger_order']):
            encoded = json.dumps(s, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()
            assert item == dict(source_id=s['source_id'], source_raw_sha256=s['raw_sha256'], complete_source_object_sha256=sha(encoded), pages=[p['page'] for p in s['pages']])
        assert {s['source_id'] for s in ss} == set(next(iter(h['ordered_source_partitions'].values())))
        for r in h['original_pdf_receipts']:
            z = (ROOT / r['stored_path']).read_bytes()
            assert len(z) == r['stored_bytes'] < 40000000 and sha(z) == r['stored_sha256'] and sha(gzip.decompress(z)) == r['raw_sha256']
        findings[year] = dict(canonical_snapshot=pin(sp), complete_source_objects_reconstructed=n, candidate_or_null_positions=h['full_flat_candidate_or_null_positions'], source_native_observations=h['native_observations_across_publications_or_stages'], literal_marks=h['literal_source_marks'], source_partitions={k:len(v) for k,v in h['ordered_source_partitions'].items()}, full_source_objects_exact=True, own_direct_scope_still_bounded=True)
    assert findings['2020']['candidate_or_null_positions'] == 8316 and findings['2018']['candidate_or_null_positions'] == 13662 and findings['2018']['literal_marks'] == dict(X=6)
    rp = OUT / 'qa/final-offline-reproduction.json'
    assert pin(rp)['sha256'] == 'd5d13fd229fb7900166dc0886ab3222a6fe1d149e1b00fb6d4daececaa38f3f7'
    receipt = json.loads(rp.read_bytes())
    assert receipt['process_exit_code'] == 0
    for a in list(receipt['output_pins'].values()) + [receipt['completed_log']]:
        assert pin(ROOT / a['path']) == a
    assert (ROOT / receipt['completed_log']['path']).read_text().strip().endswith(receipt['final_line'])
    result = dict(status='pass_finished_turnout_full_frozen_contract_and_exact_historical_dependencies', owned_manifest=pin(mp), validation=pin(vp), final_owned_checks=117, owned_entries=13203, listed_owned_bytes=sum(sizes), maximum_stored_owned_bytes=max(sizes), read_only_shared_original_references=152, every_owned_hash_size_AST_and_membership_verified=True, manifest_excludes_only_itself=True, report=pin(ROOT/'turnout.md'), county_CSV=pin(DATA/'county-turnout.csv'), complete_priority_contract=pin(cp), complete2024_named_dependency=pin(dp), source_columns=2321, preferred2024_columns=2266, preferred2024_candidate_fields=24926, complete_historical_dependency=pin(hp), historical_sources=findings, independent_complete_v2_proposal=pin(v2sp), preferred_native_order=1736, priority_native=887, priority_parents=77, all_parent_counties=82, remainder_native=849, completed_offline_reproduction_receipt=pin(rp), original_worker_build_reexecuted_by_coordinator=False, qualification='Independent readonly final hash/size/AST/membership audit verifies frozen turnout report/CSV/full13MBcontract and every owned asset; archived117check full offline replay receipt and final log verify exit0. Preferred2266columns/24926named-or-null fields match both canonical dependency and independent complete v2proposal; all2321alternative-role columns remain. Full historical104/164source objects are reconstructed by exact frozen component bytes and every object canonical hash/page/raworiginalreceipt matches; all source/admin/X/null/alternative partitions remain without promoting bounded44/104and43/164original replay to whole independent native reading. No mutating worker rebuild, source repair/currentgeo or formal887approval is implied by this audit.', formal_native887_dispatch_accepted=False, current_geography_approved=False)
    p = DATA / 'coordinator-finished-turnout-review.json'
    b = (json.dumps(result, indent=2) + '\n').encode()
    if p.exists():
        assert p.read_bytes() == b
    else:
        p.write_bytes(b)
    assert pin(mp)['sha256'] == '4681e60b69fda456f8ff87d73c5a82a3c1a79e5210059fb9e7bc04f9a6c1d280'
    print(json.dumps(pin(p)))


if __name__ == '__main__':
    main()
