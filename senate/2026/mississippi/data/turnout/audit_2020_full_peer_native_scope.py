"""Read-only full-source audit of the peer's 104 2020 Senate publications.

The 102-publication flat original witness and separate two-Coahoma original
ledger are combined only as alternative publication scopes. Selected82 are
read from our independent all-county control, never chosen by native labels.
"""
import csv
import gzip
import io
import json
from collections import Counter, defaultdict

from acquire_sources import BASE, OUT, receipts, savejson, sha

SNAP = BASE / 'data/baselines/source/native-2020-104views-v1/snapshot.json'
SNAP_SHA = '1ff6e98fd18f70ec473ce0b5adac5e082f4f1900a7d03d6090e9181150a71568'
CANDIDATES = ('Mike Espy', 'Cindy Hyde-Smith', 'Jimmy L. Edwards')


def pinned(snapshot, suffix):
    pin = next(p for p in snapshot['pins'] if p['original_path'].endswith(suffix))
    stored = (BASE / pin['stored_path']).read_bytes()
    raw = gzip.decompress(stored)
    assert len(stored) == pin['stored_bytes'] and sha(stored) == pin['stored_sha256']
    assert len(raw) == pin['original_bytes'] and sha(raw) == pin['original_sha256']
    return raw, pin


def main():
    snap_raw = SNAP.read_bytes()
    assert sha(snap_raw) == SNAP_SHA
    snap = json.loads(snap_raw)
    flat_raw, flat_pin = pinned(snap, 'native-2020-additional-candidate-votes.csv')
    coah_raw, coah_pin = pinned(snap, 'coahoma-2020-amendment-readings.json')
    flat = list(csv.DictReader(io.StringIO(flat_raw.decode())))
    coahoma = json.loads(coah_raw)
    own = json.loads((OUT / '2020-publication-original-total-readings.json').read_text())
    own_totals = {s['source_id']: s for s in own['sources']}
    by_county_route = defaultdict(set)
    for sid in own_totals:
        route = sid.removeprefix('sos-2020-county-').removesuffix('-amended')
        by_county_route[route].add(sid)
    assert len(by_county_route) == 82
    selected = {next((sid for sid in ids if sid.endswith('-amended')), next(iter(ids)))
                for ids in by_county_route.values()}
    assert sum(sid.endswith('-amended') for sid in selected) == 22
    receipt = {r['id']: r for r in receipts}
    assert len(flat) == 8184 and len(own_totals) == 104 and len(selected) == 82

    grouped = defaultdict(list)
    roles = Counter()
    columns = {}
    renders = {}
    for row in flat:
        sid = row['source_id']
        assert sid in own_totals and sid in receipt
        assert row['source_raw_sha256'] == receipt[sid]['raw_sha256'] == own_totals[sid]['source_raw_sha256']
        assert row['candidate'] in CANDIDATES
        assert row['role'] in ('source_native_reporting_constituent', 'source_TOTAL',
                               'unused_template_column', 'source_administrative_reporting_column')
        if row['role'] == 'unused_template_column':
            assert row['votes'] == '' and row['literal_native_label'] == ''
        else:
            assert row['votes'].isdigit() and int(row['votes']) >= 0
        roles[row['role']] += 1
        key = (sid, row['source_page'], row['source_column'])
        descriptor = (row['role'], row['source_key'], row['literal_native_label'],
                      row['literal_printed_id'], row['county_fips'])
        if key in columns:
            assert columns[key] == descriptor
        else:
            columns[key] = descriptor
        render_key = (sid, row['source_page'])
        render = (row['full_original_render_path'], row['render_sha256'])
        if render_key in renders:
            assert renders[render_key] == render
        else:
            renders[render_key] = render
        grouped[(sid, row['candidate'])].append(row)

    source_checks = []
    source_native_counts = Counter()
    for (sid, candidate), rows in sorted(grouped.items()):
        totals = [r for r in rows if r['role'] == 'source_TOTAL']
        assert len(totals) == 1
        printed = int(totals[0]['votes'])
        native = sum(int(r['votes']) for r in rows if r['role'] == 'source_native_reporting_constituent')
        assert printed == native == own_totals[sid]['candidate_values'][candidate]
        if candidate == CANDIDATES[0]:
            source_native_counts[sid] = sum(r['role'] == 'source_native_reporting_constituent' for r in rows)
        source_checks.append({'source_id': sid, 'candidate': candidate,
                              'source_raw_sha256': receipt[sid]['raw_sha256'],
                              'own_original_county_TOTAL': own_totals[sid]['candidate_values'][candidate],
                              'peer_printed_TOTAL': printed, 'peer_native_sum': native,
                              'peer_TOTAL_page': int(totals[0]['source_page']),
                              'peer_TOTAL_physical_column': int(totals[0]['source_column']),
                              'selected_amended_where_linked': sid in selected})

    assert len(grouped) == 306 and len(source_native_counts) == 102
    assert roles == {'source_native_reporting_constituent': 6285,
                     'source_TOTAL': 306, 'unused_template_column': 1590,
                     'source_administrative_reporting_column': 3}
    assert len(columns) == 2728

    coahoma_checks = []
    coahoma_column_roles = Counter()
    for publication in coahoma['sources']:
        sid = publication['source_id']
        assert sid in own_totals and sid in receipt and sid not in source_native_counts
        assert publication['raw_sha256'] == receipt[sid]['raw_sha256'] == own_totals[sid]['source_raw_sha256']
        assert publication['native_constituents'] == 18
        source_native_counts[sid] = 18
        for page in publication['pages']:
            evidence = BASE / 'data/baselines' / page['evidence_path']
            assert evidence.exists()
            assert sha(evidence.read_bytes()) == page['evidence_sha256']
            coahoma_column_roles.update(col['role'] for col in page['columns'])
        assert len(publication['checks']) == 3
        for item in publication['checks']:
            candidate = item['candidate']
            assert candidate in CANDIDATES
            assert item['component_sum'] == item['printed_TOTAL'] == own_totals[sid]['candidate_values'][candidate]
            coahoma_checks.append({'source_id': sid, 'candidate': candidate,
                                   'source_raw_sha256': receipt[sid]['raw_sha256'],
                                   'own_original_county_TOTAL': own_totals[sid]['candidate_values'][candidate],
                                   'peer_printed_TOTAL': item['printed_TOTAL'],
                                   'peer_native_sum': item['component_sum'],
                                   'selected_amended_where_linked': sid in selected})
    assert len(coahoma_checks) == 6
    assert coahoma_column_roles == {'source_native_reporting_constituent': 36,
                                    'source_TOTAL': 2, 'unused_template_column': 6}
    assert len(source_native_counts) == 104 and sum(source_native_counts.values()) == 2131

    render_checks = []
    for (sid, page), (path, digest) in sorted(renders.items()):
        raw = (BASE / path).read_bytes()
        assert sha(raw) == digest
        render_checks.append({'source_id': sid, 'source_pdf_page': int(page),
                              'path': path, 'sha256': digest, 'bytes': len(raw)})
    combined = source_checks + coahoma_checks
    assert len(combined) == 312 and len({r['source_id'] for r in combined}) == 104
    preferred = [r for r in combined if r['selected_amended_where_linked']]
    assert len(preferred) == 246 and len({r['source_id'] for r in preferred}) == 82
    state = {candidate: sum(r['peer_native_sum'] for r in preferred if r['candidate'] == candidate)
             for candidate in CANDIDATES}
    assert state == {'Mike Espy': 578691, 'Cindy Hyde-Smith': 709511, 'Jimmy L. Edwards': 23152}
    output = {
        'scope': 'Read-only audit of peer complete 2020 original-native publication witness versus own independently read 104 county publication TOTAL controls. The separate Coahoma pair is nonadditive and retained in its own pinned original ledger. No new own original-native cells, release chronology or cross-year/current precinct identity inferred.',
        'peer_snapshot_path': str(SNAP.relative_to(BASE)),
        'peer_snapshot_sha256': SNAP_SHA,
        'peer_flat102_pin': flat_pin,
        'peer_coahoma_two_publication_pin': coah_pin,
        'own_original_publication_control_path': 'data/turnout/2020-publication-original-total-readings.json',
        'own_original_publication_control_sha256': sha((OUT / '2020-publication-original-total-readings.json').read_bytes()),
        'publication_views': 104,
        'selected_amended_where_linked_views': 82,
        'candidate_source_controls': len(combined),
        'native_observations_across_distinct_publications': sum(source_native_counts.values()),
        'flat102_candidate_or_null_positions': len(flat),
        'combined104_candidate_or_null_positions': len(flat) + 132,
        'flat102_roles_by_candidate_position': dict(roles),
        'separate_coahoma_two_publication_column_roles': dict(coahoma_column_roles),
        'selected82_native_candidate_state_controls': state,
        'source_native_counts': dict(sorted(source_native_counts.items())),
        'flat102_source_checks': source_checks,
        'separate_coahoma_source_checks': coahoma_checks,
        'flat102_original_render_sha256_by_page': render_checks,
        'accepted_new_own_original_native_cells_from_this_audit': 0,
    }
    savejson(OUT / '2020-full-peer-native-scope-audit.json', output)
    print('full peer 2020 source audit', len(combined), 'candidate controls;',
          len(source_native_counts), 'publication views; selected native sums', state)


if __name__ == '__main__':
    main()
