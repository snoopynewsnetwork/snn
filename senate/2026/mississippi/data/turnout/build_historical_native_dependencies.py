"""Verify and attach complete frozen historical native objects by exact bytes.

The independent peer's immutable gzip snapshots are read-only canonical
dependencies. This worker's direct-original cell replay remains bounded; the
references do not promote those cells to independent complete coverage.
"""
import csv
import gzip
import io
import json
from collections import Counter

from acquire_sources import BASE, OUT, receipts, savejson, sha

SNAPSHOTS = {
    '2020': ('data/baselines/source/native-2020-104views-v1/snapshot.json',
             '1ff6e98fd18f70ec473ce0b5adac5e082f4f1900a7d03d6090e9181150a71568'),
    '2018': ('data/baselines/source/native-2018-164views-v1/snapshot.json',
             '90e14d7f6f34992c39b3d9370e954cc2d56ad7a58147103eaa0607bc139288d0'),
}


def canonical_json_hash(obj):
    return sha(json.dumps(obj, sort_keys=True, ensure_ascii=False,
                          separators=(',', ':')).encode())


def read_snapshot(year):
    rel, expected = SNAPSHOTS[year]
    path = BASE / rel
    raw = path.read_bytes()
    assert sha(raw) == expected
    snap = json.loads(raw)
    objects = {}
    pins = []
    for pin in snap['pins']:
        stored = (BASE / pin['stored_path']).read_bytes()
        original = gzip.decompress(stored)
        assert len(stored) == pin['stored_bytes'] and sha(stored) == pin['stored_sha256']
        assert len(original) == pin['original_bytes'] and sha(original) == pin['original_sha256']
        current_path = BASE / pin['original_path']
        current_equal = current_path.exists() and current_path.read_bytes() == original
        pins.append(dict(pin, current_mutable_path_equal_to_frozen_bytes=current_equal,
                         canonical_storage='immutable_stored_path_not_mutable_original_path'))
        objects[pin['original_path'].split('/')[-1]] = original
    return {'path': rel, 'sha256': expected, 'bytes': len(raw),
            'pins': pins, 'snapshot': snap, 'objects': objects}


def source_digest(source_obj):
    return {'source_id': source_obj['source_id'],
            'source_raw_sha256': source_obj['raw_sha256'],
            'complete_source_object_sha256': canonical_json_hash(source_obj),
            'pages': [p['page'] for p in source_obj['pages']]}


def check_flat_2020(sources, csv_raw):
    flat = list(csv.DictReader(io.StringIO(csv_raw.decode())))
    assert len(flat) == 8184
    rows = {(r['source_id'], int(r['source_page']), int(r['source_column']), r['candidate']): r
            for r in flat}
    assert len(rows) == len(flat)
    seen = set()
    roles = Counter()
    for source_obj in sources:
        sid = source_obj['source_id']
        for page in source_obj['pages']:
            cols = page['columns']
            for field in page['fields']:
                assert len(field['values']) == len(cols)
                for col, value in zip(cols, field['values']):
                    key = (sid, page['page'], col['source_column'], field['candidate'])
                    row = rows[key]
                    assert key not in seen
                    seen.add(key)
                    assert row['role'] == col['role']
                    assert row['literal_native_label'] == col['label_literal']
                    assert row['literal_printed_id'] == (col.get('literal_printed_id') or '')
                    assert row['votes'] == ('' if value is None else str(value))
                    assert row['source_raw_sha256'] == source_obj['raw_sha256']
                    assert row['county_fips'] == source_obj['county_fips']
                    assert row['party_literal'] == (field.get('party_literal') or '')
                    assert row['full_original_render_path'] == page['full_original_render_path']
                    assert row['render_sha256'] == page['render_sha256']
                    roles[col['role']] += 1
    assert len(seen) == len(flat)
    assert roles == {'source_native_reporting_constituent': 6285,
                     'source_TOTAL': 306, 'unused_template_column': 1590,
                     'source_administrative_reporting_column': 3}
    return len(flat), dict(roles)


def check_flat_2018(sources, csv_raw):
    flat = list(csv.DictReader(io.StringIO(csv_raw.decode())))
    assert len(flat) == 13662
    rows = {(r['source_id'], int(r['source_page']), int(r['source_column']), r['candidate']): r
            for r in flat}
    assert len(rows) == len(flat)
    seen = set()
    roles = Counter()
    marks = Counter()
    for source_obj in sources:
        sid = source_obj['source_id']
        for page in source_obj['pages']:
            cols = page['columns']
            for field in page['fields']:
                assert len(field['values']) == len(cols)
                for col, value in zip(cols, field['values']):
                    key = (sid, page['page'], col['source_column'], field['candidate'])
                    row = rows[key]
                    assert key not in seen
                    seen.add(key)
                    assert row['role'] == col['role']
                    assert row['literal_native_label'] == col['label_literal']
                    assert row['literal_printed_id'] == (col.get('literal_printed_id') or '')
                    assert row['votes'] == ('' if value is None else str(value))
                    assert row['raw_source_mark'] == field.get('source_marks', {}).get(str(col['source_column']), '')
                    assert row['source_raw_sha256'] == source_obj['raw_sha256']
                    if 'county_fips' in source_obj:
                        assert row['county_fips'] == source_obj['county_fips']
                    else:
                        assert sid in ('sos-2018-county-issaquena','sos-2018-runoff-county-issaquena')
                        assert row['county_fips'] == '28055'
                    assert row['stage'] == source_obj['stage']
                    assert row['party_literal'] == (field.get('party_literal') or '')
                    assert row['full_original_render_path'] == page['full_original_render_path']
                    assert row['render_sha256'] == page['render_sha256']
                    roles[col['role']] += 1
                    if row['raw_source_mark']:
                        marks[row['raw_source_mark']] += 1
    assert len(seen) == len(flat)
    assert roles == {'native': 10632, 'TOTAL': 492, 'unused': 2530, 'administrative': 8}
    assert marks == {'X': 6}
    return len(flat), dict(roles), dict(marks)


def build(contract):
    receipt = {r['id']: r for r in receipts}
    twenty = read_snapshot('2020')
    eighteen = read_snapshot('2018')
    x20 = twenty['objects']
    add20 = json.loads(x20['native-2020-additional-readings.json'])
    coah20 = json.loads(x20['coahoma-2020-amendment-readings.json'])
    cov20 = json.loads(x20['native-2020-coverage.json'])
    assert len(add20['sources']) == 102 and len(coah20['sources']) == 2
    flat20_count, roles20 = check_flat_2020(add20['sources'], x20['native-2020-additional-candidate-votes.csv'])
    sources20 = add20['sources'] + coah20['sources']
    assert len(sources20) == len({s['source_id'] for s in sources20}) == 104
    assert len(cov20['reviewed_sources']) == 104
    all20 = cov20['all104_publication_status']
    assert len(all20) == 104 and {s['source_id'] for s in all20} == {s['source_id'] for s in sources20}
    selected20 = [s['source_id'] for s in all20 if s['selected_for_82_county_amended_where_explicit_control']]
    alternative20 = [s['source_id'] for s in all20 if not s['selected_for_82_county_amended_where_explicit_control']]
    assert len(selected20) == 82 and len(alternative20) == 22
    assert sum(s['native_constituents'] for s in cov20['reviewed_sources']) == 2131
    assert sum(s['native_constituents'] for s in cov20['reviewed_sources'] if s['source_id'] in selected20) == 1765
    assert cov20['selected82_native_candidate_sums'] == {'Mike Espy': 578691, 'Cindy Hyde-Smith': 709511, 'Jimmy L. Edwards': 23152}
    for source_obj in sources20:
        assert receipt[source_obj['source_id']]['raw_sha256'] == source_obj['raw_sha256']
    audit20_path = OUT / '2020-full-peer-native-scope-audit.json'
    audit20 = json.loads(audit20_path.read_text())
    assert audit20['publication_views'] == 104 and audit20['combined104_candidate_or_null_positions'] == 8316
    assert audit20['selected82_native_candidate_state_controls'] == cov20['selected82_native_candidate_sums']
    assert audit20['accepted_new_own_original_native_cells_from_this_audit'] == 0

    x18 = eighteen['objects']
    ledger18 = json.loads(x18['native-2018-original-readings.json'])
    assert len(ledger18['sources']) == 164
    flat18_count, roles18, marks18 = check_flat_2018(ledger18['sources'], x18['native-2018-original-candidate-votes.csv'])
    special18 = [s['source_id'] for s in ledger18['sources'] if s['stage'] == 'special']
    runoff18 = [s['source_id'] for s in ledger18['sources'] if s['stage'] == 'runoff']
    assert len(special18) == len(runoff18) == 82
    def source_fips(s):
        if 'county_fips' in s:
            return s['county_fips']
        assert s['source_id'] in ('sos-2018-county-issaquena','sos-2018-runoff-county-issaquena')
        return '28055'
    assert len({source_fips(s) for s in ledger18['sources'] if s['stage']=='special'}) == 82
    assert len({source_fips(s) for s in ledger18['sources'] if s['stage']=='runoff'}) == 82
    for source_obj in ledger18['sources']:
        assert receipt[source_obj['source_id']]['raw_sha256'] == source_obj['raw_sha256']
    audit18_path = OUT / '2018-full-peer-native-scope-audit.json'
    audit18 = json.loads(audit18_path.read_text())
    assert audit18['source_views'] == 164 and audit18['candidate_or_null_positions'] == flat18_count
    assert audit18['native_observations_across_distinct_stages'] == 3545
    assert audit18['exceptions'] and audit18['accepted_new_own_original_native_cells_from_this_audit'] == 0
    assert audit18['literal_source_marks'] == marks18

    def public_year(year, frozen, sources, partitions, audit_path, field_positions, native_count, roles, marks=None):
        return {'source_scope': year,
                'canonical_snapshot_path': frozen['path'],
                'canonical_snapshot_sha256': frozen['sha256'],
                'canonical_snapshot_bytes': frozen['bytes'],
                'canonical_lossless_component_pins': frozen['pins'],
                'ordered_source_partitions': partitions,
                'complete_source_objects_in_ledger_order': [source_digest(s) for s in sources],
                'original_pdf_receipts': [
                    {'source_id': s['source_id'], 'raw_sha256': s['raw_sha256'],
                     'stored_path': receipt[s['source_id']]['path'],
                     'stored_sha256': receipt[s['source_id']]['stored_sha256'],
                     'stored_bytes': receipt[s['source_id']]['stored_bytes']}
                    for s in sources],
                'full_flat_candidate_or_null_positions': field_positions,
                'flat_candidate_position_roles': roles,
                'literal_source_marks': marks or {},
                'independent_worker_read_only_full_scope_audit_path': str(audit_path.relative_to(BASE)),
                'independent_worker_read_only_full_scope_audit_sha256': sha(audit_path.read_bytes()),
                'native_observations_across_publications_or_stages': native_count,
                'own_direct_original_native_replay_scope': 'bounded_subset_only',
                'current_2026_geographic_approval': False}

    year20 = public_year('2020_regular_same_Class_II', twenty, sources20,
                         {'all104_in_coverage_index_order': [s['source_id'] for s in all20],
                          'selected82_amended_where_explicit_in_index_order': selected20,
                          'nonadditive_alternative22_in_index_order': alternative20},
                         audit20_path, flat20_count + 132, 2131, dict(roles20))
    year20['selected82_native_candidate_state_controls'] = cov20['selected82_native_candidate_sums']
    year20['flat102_positions'] = flat20_count
    year20['separate_Coahoma_original_and_amended_positions'] = 132
    year20['qualification'] = 'Full104 peer original Senate3 native publication objects are canonical frozen dependencies; this worker independently reviewed all104 county candidate TOTALs and only a bounded subset of native glyphs. Twenty-two publication alternatives remain nonadditive. Snapshot legacy complete2020_native=false refers to broader fields, while its named-Senate3 coverage fields are true.'
    year18 = public_year('2018_special_Nov6_and_runoff_Nov27', eighteen, ledger18['sources'],
                         {'all164_in_original_ledger_order': [s['source_id'] for s in ledger18['sources']],
                          'Nov6_special82_in_ledger_order': special18,
                          'Nov27_runoff82_in_ledger_order': runoff18},
                         audit18_path, flat18_count, 3545, dict(roles18), marks18)
    year18['qualification'] = 'Full164 peer original Senate special/runoff native objects, nulls, X marks, three administrative columns and Leflore Nov6 Espy minus10 remain canonical frozen dependencies. This worker independently reviewed all164 county-stage TOTAL controls and only a bounded subset of native glyphs; no party union or cross-stage identity join.'
    body = {'schema': 'historical_native_complete_frozen_dependency_v1',
            '2020': year20, '2018': year18,
            'scope': 'Exact lossless immutable peer source-native dependencies independently audited against original source hashes and this worker’s independent whole-state county controls. No direct-original full-native assertion by this worker or approved current geography.'}
    path = OUT / 'historical-native-complete-dependencies.json'
    savejson(path, body)
    contract['historical_source_native_dependencies'] = {
        'path': str(path.relative_to(OUT)), 'sha256': sha(path.read_bytes()),
        'bytes': path.stat().st_size,
        '2020': {'source_publications': 104, 'selected_publications': 82,
                 'nonadditive_alternative_publications': 22, 'native_observations': 2131,
                 'candidate_or_null_positions': 8316,
                 'candidate_universe': ['Mike Espy', 'Cindy Hyde-Smith', 'Jimmy L. Edwards']},
        '2018': {'source_stage_views': 164, 'Nov6_special': 82, 'Nov27_runoff': 82,
                 'native_observations_across_stages': 3545,
                 'candidate_or_null_positions': 13662,
                 'literal_X_positions': 6,
                 'Nov6_candidate_universe': ['Tobey Bernard Bartee', 'Mike Espy', 'Cindy Hyde-Smith', 'Chris McDaniel'],
                 'Nov27_candidate_universe': ['Mike Espy', 'Cindy Hyde-Smith']},
        'own_direct_original_native_replay_scope': {'2020_publications': 44, '2018_stage_views': 43},
        'full_peer_source_objects_canonical': True,
        'own_direct_original_native_replay_complete': False,
        'current_2026_geographic_approval': False}
    return contract


if __name__ == '__main__':
    path = OUT / 'priority-set.json'
    contract = build(json.loads(path.read_text()))
    savejson(path, contract)
    print('Historical native frozen dependency: 2020 all104/8316 fields; 2018 all164/13662 fields')
