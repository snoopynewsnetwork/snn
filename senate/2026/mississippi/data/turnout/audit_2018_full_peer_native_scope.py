"""Bounded read-only audit of the peer's complete 2018 native publication set.

This compares its immutable native derivative to independently read county
TOTAL controls. It never relabels a peer cell as our own original transcription.
"""
import csv
import gzip
import io
import json
from collections import Counter, defaultdict

from acquire_sources import BASE, OUT, receipts, savejson, sha

SNAPSHOT = BASE / 'data/baselines/source/native-2018-164views-v1/snapshot.json'
SNAPSHOT_SHA = '90e14d7f6f34992c39b3d9370e954cc2d56ad7a58147103eaa0607bc139288d0'


def pinned(snapshot, suffix):
    pin = next(p for p in snapshot['pins'] if p['original_path'].endswith(suffix))
    stored = (BASE / pin['stored_path']).read_bytes()
    original = gzip.decompress(stored)
    assert len(stored) == pin['stored_bytes'] and sha(stored) == pin['stored_sha256']
    assert len(original) == pin['original_bytes'] and sha(original) == pin['original_sha256']
    return original, pin


def main():
    snapshot_raw = SNAPSHOT.read_bytes()
    assert sha(snapshot_raw) == SNAPSHOT_SHA
    snapshot = json.loads(snapshot_raw)
    csv_raw, flat_pin = pinned(snapshot, 'native-2018-original-candidate-votes.csv')
    json_raw, ledger_pin = pinned(snapshot, 'native-2018-original-readings.json')
    peer_ledger = json.loads(json_raw)
    rows = list(csv.DictReader(io.StringIO(csv_raw.decode())))
    own_controls = list(csv.DictReader((OUT / 'historical-county-candidate-votes.csv').open()))
    own_controls = [r for r in own_controls if r['election_date'] in ('2018-11-06', '2018-11-27')]
    control = {(r['source_id'], r['candidate']): r for r in own_controls}
    original_receipts = {r['id']: r for r in receipts}
    assert len(control) == 492 and len(rows) == 13662 and len(peer_ledger['sources']) == 164
    assert len({r['source_id'] for r in rows}) == 164
    assert len({(r['source_id'], r['source_page'], r['source_column'], r['candidate']) for r in rows}) == len(rows)

    by_source_candidate = defaultdict(list)
    columns = {}
    page_renders = {}
    roles = Counter()
    marks = Counter()
    for r in rows:
        sid = r['source_id']
        assert sid in original_receipts
        assert original_receipts[sid]['raw_sha256'] == r['source_raw_sha256']
        ctl = control[(sid, r['candidate'])]
        assert ctl['raw_sha256'] == r['source_raw_sha256'] and ctl['fips'] == r['county_fips']
        assert (r['stage'] == 'special') == (ctl['election_date'] == '2018-11-06')
        if r['role'] == 'unused':
            assert r['votes'] == '' and r['raw_source_mark'] == '' and r['literal_native_label'] == ''
        elif r['raw_source_mark']:
            assert r['role'] == 'native' and r['raw_source_mark'] == 'X' and r['votes'] == ''
        else:
            assert r['votes'].isdigit() and int(r['votes']) >= 0
        roles[r['role']] += 1
        if r['raw_source_mark']:
            marks[r['raw_source_mark']] += 1
        key = (sid, r['source_page'], r['source_column'])
        descriptor = (r['role'], r['source_key'], r['literal_native_label'], r['literal_printed_id'], r['county_fips'])
        if key in columns:
            assert columns[key] == descriptor
        else:
            columns[key] = descriptor
        render = (r['full_original_render_path'], r['render_sha256'])
        page_key = (sid, r['source_page'])
        if page_key in page_renders:
            assert page_renders[page_key] == render
        else:
            page_renders[page_key] = render
        by_source_candidate[(sid, r['candidate'])].append(r)

    source_checks = []
    exceptional = []
    state_native = Counter()
    state_controls = Counter()
    for (sid, candidate), cells in sorted(by_source_candidate.items()):
        ctl = control[(sid, candidate)]
        totals = [r for r in cells if r['role'] == 'TOTAL']
        assert len(totals) == 1
        total = int(totals[0]['votes'])
        assert total == int(ctl['votes'])
        natives = [r for r in cells if r['role'] == 'native']
        known = sum(int(r['votes']) for r in natives if r['votes'] != '')
        unknown = [r['source_key'] for r in natives if r['raw_source_mark'] == 'X']
        difference = known - total
        if difference or unknown:
            exceptional.append({'source_id': sid, 'candidate': candidate,
                                'known_native_sum_minus_printed_TOTAL': difference,
                                'literal_X_source_keys': unknown,
                                'qualification': 'Known numeric sum is not an allocation to an X-marked source cell.'})
        stage = 'special' if ctl['election_date'] == '2018-11-06' else 'runoff'
        state_native[(stage, candidate)] += known
        state_controls[(stage, candidate)] += total
        source_checks.append({'source_id': sid, 'candidate': candidate,
                              'stage': stage, 'county_fips': ctl['fips'],
                              'source_raw_sha256': ctl['raw_sha256'],
                              'printed_TOTAL_page': int(totals[0]['source_page']),
                              'printed_TOTAL_physical_column': int(totals[0]['source_column']),
                              'printed_TOTAL': total, 'own_county_control': int(ctl['votes']),
                              'known_native_sum': known, 'literal_X_native_count': len(unknown),
                              'known_native_minus_printed_TOTAL': difference})

    assert len(source_checks) == 492
    assert roles == {'native': 10632, 'TOTAL': 492, 'unused': 2530, 'administrative': 8}
    assert marks == {'X': 6}
    assert len(columns) == 4554
    assert len(page_renders) == 414
    assert {(e['source_id'], e['candidate'], e['known_native_sum_minus_printed_TOTAL']) for e in exceptional if e['known_native_sum_minus_printed_TOTAL']} == {
        ('sos-2018-county-leflore', 'Mike Espy', -10)}
    assert sum(len(e['literal_X_source_keys']) for e in exceptional) == 6
    render_checks = []
    for (sid, page), (path, digest) in sorted(page_renders.items()):
        data = (BASE / path).read_bytes()
        assert sha(data) == digest
        render_checks.append({'source_id': sid, 'source_pdf_page': int(page),
                              'path': path, 'sha256': digest, 'bytes': len(data)})
    output = {
        'scope': 'Read-only audit of the independent peer\'s frozen full 2018 native derivative against this worker\'s independently original-read 164 county-stage TOTAL controls. It is not this worker\'s direct original transcription of all native cells or a current geographic crosswalk.',
        'peer_snapshot_path': str(SNAPSHOT.relative_to(BASE)),
        'peer_snapshot_sha256': SNAPSHOT_SHA,
        'peer_flat_pin': flat_pin,
        'peer_ledger_pin': ledger_pin,
        'own_independent_county_controls_path': 'data/turnout/historical-county-candidate-votes.csv',
        'own_independent_county_controls_sha256': sha((OUT / 'historical-county-candidate-votes.csv').read_bytes()),
        'source_views': 164, 'counties': 82,
        'candidate_source_controls': len(source_checks),
        'native_observations_across_distinct_stages': len([c for c in columns.values() if c[0] == 'native']),
        'source_columns_across_distinct_stages': len(columns),
        'candidate_or_null_positions': len(rows),
        'roles_by_candidate_position': dict(roles),
        'literal_source_marks': dict(marks),
        'full_original_render_count_hash_checked': len(render_checks),
        'source_checks': source_checks,
        'exceptions': exceptional,
        'stage_candidate_known_native_sums': [{'stage': k[0], 'candidate': k[1], 'votes': v} for k, v in sorted(state_native.items())],
        'stage_candidate_county_control_sums': [{'stage': k[0], 'candidate': k[1], 'votes': v} for k, v in sorted(state_controls.items())],
        'source_render_sha256_by_page': render_checks,
        'accepted_new_own_original_native_cells_from_this_audit': 0,
    }
    savejson(OUT / '2018-full-peer-native-scope-audit.json', output)
    print('full peer 2018 source audit', len(source_checks), 'candidate controls; exceptions', len(exceptional))


if __name__ == '__main__':
    main()
