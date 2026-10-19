"""Audit frozen reciprocal40-view readings without upgrading statewide coverage."""
from pathlib import Path
from collections import Counter
import csv
import gzip
import hashlib
import io
import json
import re

DATA = Path(__file__).resolve().parent
ROOT = DATA.parent
REPLAY = DATA / 'coordinator-qa/native-replay-40views'
TURNOUT = DATA / 'turnout/qa/milestones/native-2024-40views'
NAMES = {'Ty_Pinkins': 'Ty Pinkins', 'Roger_F_Wicker': 'Roger F. Wicker'}
ROLES = {'native_reporting_constituent': 'source_native_reporting_constituent',
         'source_TOTAL': 'source_TOTAL', 'unused_template_column': 'unused_template_column'}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(path):
    b = path.read_bytes()
    return {'path': str(path.relative_to(ROOT)), 'bytes': len(b), 'sha256': sha(b)}


def main():
    replay_pins = json.loads((REPLAY / 'snapshot-pins.json').read_bytes())
    replay_files = {}
    for p in replay_pins['files']:
        b = (ROOT / p['snapshot_path']).read_bytes()
        raw = gzip.decompress(b)
        assert (len(b), sha(b)) == (p['stored_bytes'], p['stored_sha256'])
        assert (len(raw), sha(raw)) == (p['original_bytes'], p['original_sha256'])
        replay_files[Path(p['source_path']).name] = raw
    reference_pins = json.loads((TURNOUT / 'snapshot.json').read_bytes())
    reference_files = {}
    for p in reference_pins['pins']:
        b = (ROOT / p['path']).read_bytes()
        assert (len(b), sha(b)) == (p['bytes'], p['sha256'])
        reference_files[Path(p['path']).name] = b
    reference = json.loads(reference_files['native-reviewed-2024.json'])
    replay = json.loads(replay_files['native-2024-senate-reviewed-40views.json'])
    controls = json.loads(replay_files['native-2024-senate-reviewed-controls-40views.json'])
    assert controls['statewide_native_complete'] is False
    left = {s['source_id']: s for s in replay['sources']}
    assert len(left) == len(reference['sources']) == 40 and left.keys() == reference['sources'].keys()
    hint_pins = []
    hinted = set()
    for name in ['native-reviewed-25view-positions.json.gz', 'native-reviewed-extension-positions.json.gz']:
        original = DATA / 'baselines/source' / name
        copy = REPLAY / name
        if not copy.exists():
            copy.write_bytes(original.read_bytes())
        hints = json.loads(gzip.decompress(copy.read_bytes()))
        hint_pins.append(pin(copy))
        assert hints['reference_original_sha256'] in {p['original_sha256'] for p in replay['peer_references']}
        for s in hints['sources']:
            assert set(s) == {'source_id', 'raw_sha256', 'pages'}
            assert s['source_id'] not in hinted
            hinted.add(s['source_id'])
            for page in s['pages']:
                assert set(page) == {'page', 'render_size', 'rotation_ccw', 'deskew_angle_ccw', 'columns'}
                for column in page['columns']:
                    assert set(column) == {'source_column', 'header_bounds', 'candidate_bounds'}
                    assert set(column['candidate_bounds']) == set(NAMES.values())
    assert hinted == set(left)
    reference_inputs = []
    for p in replay['peer_references']:
        b = (ROOT / p['path']).read_bytes()
        assert sha(gzip.decompress(b)) == p['original_sha256']
        reference_inputs.append({**pin(ROOT / p['path']), 'original_sha256': p['original_sha256']})
    roles = Counter()
    numbers = Counter()
    headers = Counter()
    cells = Counter()
    labels = []
    wraps = []
    rasters = []
    evidence = {}
    positional_rows = {}
    for sid, s in left.items():
        target = reference['sources'][sid]
        assert s['raw_sha256'] == target['raw_sha256']
        assert len(s['pages']) == len(target['pages'])
        for page, expected_page in zip(s['pages'], target['pages']):
            assert page['page'] == expected_page['page']
            assert max(abs(a-b) for a,b in zip(page['render_size'], expected_page['render_size'])) <= 1
            raster = ROOT / page['raster_path']
            assert pin(raster)['sha256'] == page['raster_sha256']
            rasters.append(pin(raster))
            assert len(page['columns']) == len(expected_page['columns'])
            for c, expected in zip(page['columns'], expected_page['columns']):
                assert c['source_column'] == expected['source_column']
                assert c['role'] == ROLES[expected['role']]
                roles[c['role']] += 1
                headers[c['header_reading_basis']] += 1
                a, b = c['label_literal'], expected['label_literal']
                # Physical source hash/page/column is already identical; this is
                # a reading representation comparison, never a geographic join.
                assert re.sub(r'\s', '', a) == re.sub(r'\s', '', b)
                if a != b:
                    labels.append({'source_id':sid, 'page':page['page'], 'source_column':c['source_column'],
                                   'baseline_label_literal':a, 'turnout_frozen_label_literal':b})
                if ' '.join(a.split()) != ' '.join(b.split()):
                    assert (sid, page['page'], c['source_column']) in {
                        ('sos-2024-county-smith',2,5), ('sos-2024-county-jones',6,3)}
                    wraps.append(labels[-1])
                assert c['printed_native_id'] == expected['printed_native_id'] or (
                    c['printed_native_id'] == '' and expected['printed_native_id'] is None)
                for key, name in NAMES.items():
                    field = c['fields'][name]
                    assert field['value'] == expected[key]
                    assert field['source_box'] == expected['candidate_bounds'][name]
                    numbers[field['reading_basis']] += 1
                    cells[c['role']] += 1
                    if c['role'] == 'unused_template_column':
                        assert field['value'] is None
                    position = (sid,page['page'],c['source_column'],name)
                    assert position not in positional_rows
                    positional_rows[position] = field['value']
                    if field.get('manual_evidence'):
                        p = DATA / 'baselines' / field['manual_evidence']
                        evidence[str(p.relative_to(ROOT))] = pin(p)
    assert roles == {'source_native_reporting_constituent':985, 'source_TOTAL':40, 'unused_template_column':196}
    assert cells == {'source_native_reporting_constituent':1970, 'source_TOTAL':80, 'unused_template_column':392}
    assert len(positional_rows) == 2442 and len(rasters) == 111
    assert len(wraps) == 2
    assert numbers == {'independent_original_OCR_agrees_frozen_peer_visual_reading':1987,
                       'independent_original_visual_cell_reading':63,
                       'blank_source_template_cell_null_not_zero':392}
    assert headers == {'independent_original_header_OCR_agrees_frozen_peer_visual_reading':1016,
                       'independent_original_visual_reading':205}
    csv_rows = list(csv.DictReader(io.StringIO(replay_files['native-2024-senate-reviewed-40views.csv'].decode(), newline='')))
    csv_seen = set()
    for row in csv_rows:
        key = (row['source_id'],int(row['source_page']),int(row['source_column']),row['candidate'])
        assert key not in csv_seen and key in positional_rows
        csv_seen.add(key)
        value = positional_rows[key]
        assert row['votes'] == ('' if value is None else str(value))
        source = left[key[0]]
        page = next(p for p in source['pages'] if p['page'] == key[1])
        column = next(c for c in page['columns'] if c['source_column'] == key[2])
        assert row['raw_sha256'] == source['raw_sha256']
        assert row['native_label_literal'] == column['label_literal']
        assert row['printed_native_id'] == column['printed_native_id']
        assert row['role'] == column['role']
        assert json.loads(row['candidate_bounds']) == column['fields'][key[3]]['source_box']
        assert json.loads(row['header_bounds']) == column['header_bounds']
    assert csv_seen == set(positional_rows)
    assert all(s['component_sums'] == s['printed_TOTAL'] == s['county_control'] for s in controls['sources'])
    output = {
        'status':'pass_frozen_40view_reciprocal_2442_positions_not_statewide_complete',
        'turnout_snapshot_manifest':pin(TURNOUT / 'snapshot.json'),
        'turnout_frozen_pins':reference_pins['pins'], 'baseline_frozen_pins':replay_pins,
        'replay_position_reference_inputs':reference_inputs,
        'strict_positions_only_hint_snapshots':hint_pins,
        'source_views':40, 'source_pages':111, 'role_counts':dict(roles),
        'candidate_position_counts':dict(cells), 'all_candidate_positions':2442,
        'baseline_CSV_full_position_validation':True,
        'numeric_reading_basis_counts':dict(numbers), 'header_reading_basis_counts':dict(headers),
        'literal_label_whitespace_representation_differences':labels,
        'explicit_physical_header_wrap_aliases':wraps, 'parsed_printed_ID_differences':[],
        'own_original_raster_pins':rasters, 'manual_original_evidence_pins':evidence,
        'parsed_printed_id_scope':replay['parsed_printed_id_scope'],
        'prior25_witness':pin(DATA / 'coordinator-native-replay-25view-review.json'),
        'scope':'Frozen40-view ledgers agree at every source hash/page/physical column and all2442 numeric/null candidate positions. Whitespace is compared only inside the identical physical source position, and the Smith/Jones line wraps are explicit. Printed IDs are historical source-scoped metadata, not current or cross-year identities. The prior25-view witness and its104 parsed-ID omissions are retained unchanged; the expanded40-view replay closes those omissions. Exact whitelist checks exclude peer labels, roles, IDs and vote values from the two targeting-hint snapshots. This coordinator check verifies retained rasters/evidence and independent ledger agreement, not a fresh coordinator OCR run or visual reading of every glyph. Only two Senate fields across40 source views are covered. Statewide native, presidential, generic-write-in/method and current geographic/reporting gates remain open.'}
    (DATA / 'coordinator-native-replay-40view-review.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({k:output[k] for k in ['status','source_views','source_pages','candidate_position_counts','all_candidate_positions']}))


if __name__ == '__main__':
    main()
