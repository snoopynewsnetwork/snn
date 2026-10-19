"""Freeze and compare the independent84-packet replay, retaining metadata gaps."""
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
DEST = DATA / 'coordinator-qa/native-replay-84views'
TURNOUT = DATA / 'turnout/qa/milestones/native-2024-84views'
NAMES = {'Ty_Pinkins': 'Ty Pinkins', 'Roger_F_Wicker': 'Roger F. Wicker'}
ROLE = {'native_reporting_constituent': 'source_native_reporting_constituent',
        'source_TOTAL': 'source_TOTAL', 'unused_template_column': 'unused_template_column',
        'parallel_native_observation': 'parallel_native_observation'}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(path):
    b = path.read_bytes()
    return {'path': str(path.relative_to(ROOT)), 'bytes': len(b), 'sha256': sha(b)}


def freeze(path):
    target = DEST / (path.name + ('' if path.suffix == '.gz' else '.gz'))
    if not target.exists():
        raw = path.read_bytes()
        assert path.read_bytes() == raw
        target.write_bytes(raw if path.suffix == '.gz' else gzip.compress(raw, mtime=0))
    stored = target.read_bytes()
    raw = gzip.decompress(stored)
    return raw, {'source_path': str(path.relative_to(ROOT)), 'snapshot_path': str(target.relative_to(ROOT)),
                 'stored_bytes': len(stored), 'stored_sha256': sha(stored),
                 'original_bytes': len(raw), 'original_sha256': sha(raw)}


def main():
    DEST.mkdir(exist_ok=True)
    own = {}
    own_pins = []
    for name in ['native-2024-senate-reviewed-84views.json', 'native-2024-senate-reviewed-84views.csv',
                 'native-2024-senate-reviewed-controls-84views.json']:
        raw, p = freeze(DATA / 'baselines' / name)
        own[name] = raw
        own_pins.append(p)
    replay = json.loads(own['native-2024-senate-reviewed-84views.json'])
    controls = json.loads(own['native-2024-senate-reviewed-controls-84views.json'])
    reference_pins = json.loads((TURNOUT / 'snapshot.json').read_bytes())
    reference_path = TURNOUT / 'native-reviewed-2024.json'
    ref_raw = reference_path.read_bytes()
    ref_pin = next(p for p in reference_pins['pins'] if p['path'].endswith('/native-reviewed-2024.json'))
    assert (len(ref_raw), sha(ref_raw)) == (ref_pin['bytes'], ref_pin['sha256'])
    assert replay['checkpoint_reference_sha256'] == sha(ref_raw)
    reference = json.loads(ref_raw)
    left = {s['source_id']: s for s in replay['sources']}
    assert left.keys() == reference['sources'].keys() and len(left) == 84
    hints = []
    hinted = set()
    for name in ['native-reviewed-25view-positions.json.gz', 'native-reviewed-extension-positions.json.gz',
                 'native-reviewed-60views-positions.json.gz', 'native-reviewed-84views-positions.json.gz']:
        raw, p = freeze(DATA / 'baselines/source' / name)
        h = json.loads(raw)
        hints.append(p)
        for source in h['sources']:
            assert set(source) == {'source_id', 'raw_sha256', 'pages'}
            assert source['source_id'] not in hinted
            hinted.add(source['source_id'])
            assert source['raw_sha256'] == left[source['source_id']]['raw_sha256']
            for page in source['pages']:
                assert set(page) == {'page', 'render_size', 'rotation_ccw', 'deskew_angle_ccw', 'columns'}
                for c in page['columns']:
                    assert set(c) == {'source_column', 'header_bounds', 'candidate_bounds'}
                    assert set(c['candidate_bounds']) == set(NAMES.values())
    assert hinted == set(left)
    positions = {}
    role_counts, numeric_bases, header_bases = Counter(), Counter(), Counter()
    boxes, labels, optional_ids = [], [], []
    raster_pins, evidence = [], {}
    source_checks = {}
    for sid, source in left.items():
        expected = reference['sources'][sid]
        assert source['raw_sha256'] == expected['raw_sha256']
        assert len(source['pages']) == len(expected['pages'])
        sums = dict.fromkeys(NAMES.values(), 0)
        totals = []
        native = parallel = 0
        for page, target_page in zip(source['pages'], expected['pages']):
            assert page['page'] == target_page['page']
            assert max(abs(a-b) for a,b in zip(page['render_size'], target_page['render_size'])) <= 1
            raster = pin(ROOT / page['raster_path'])
            assert raster['sha256'] == page['raster_sha256']
            raster_pins.append(raster)
            assert len(page['columns']) == len(target_page['columns'])
            for c, target in zip(page['columns'], target_page['columns']):
                assert c['source_column'] == target['source_column']
                assert c['role'] == ROLE[target['role']]
                assert c['header_bounds'] == target['header_bounds']
                role_counts[c['role']] += 1
                header_bases[c['header_reading_basis']] += 1
                assert re.sub(r'\s', '', c['label_literal']) == re.sub(r'\s', '', target['label_literal'])
                if c['label_literal'] != target['label_literal']:
                    labels.append({'source_id': sid, 'page': page['page'], 'source_column': c['source_column'],
                                   'own_literal': c['label_literal'], 'frozen_turnout_literal': target['label_literal']})
                if c['printed_native_id'] != target['printed_native_id']:
                    assert c['printed_native_id'] == '' and target['printed_native_id'] is None
                    optional_ids.append({'source_id': sid, 'page': page['page'], 'source_column': c['source_column']})
                values = {}
                for field, name in NAMES.items():
                    f = c['fields'][name]
                    assert f['value'] == target[field]
                    values[name] = f['value']
                    numeric_bases[f['reading_basis']] += 1
                    key = (sid, page['page'], c['source_column'], name)
                    assert key not in positions
                    positions[key] = (source, page, c, f)
                    if f['source_box'] != target['candidate_bounds'][name]:
                        assert sid == 'sos-2024-county-itawamba'
                        boxes.append({'source_id': sid, 'page': page['page'], 'source_column': c['source_column'],
                                      'candidate': name, 'own_box': f['source_box'], 'turnout_box': target['candidate_bounds'][name]})
                    if f.get('manual_evidence'):
                        p = DATA / 'baselines' / f['manual_evidence']
                        evidence[str(p.relative_to(ROOT))] = pin(p)
                    if c['role'] == 'unused_template_column':
                        assert f['value'] is None
                    else:
                        assert type(f['value']) is int and f['value'] >= 0
                if c['role'] == 'source_native_reporting_constituent':
                    native += 1
                    for n, v in values.items():
                        sums[n] += v
                elif c['role'] == 'source_TOTAL':
                    totals.append(values)
                elif c['role'] == 'parallel_native_observation':
                    parallel += 2
        assert totals == [sums]
        source_checks[sid] = {'native': native, 'component_sums': sums, 'parallel_candidate_observations': parallel}
    assert len(raster_pins) == 211 and len(positions) == 4642
    assert role_counts == {'source_native_reporting_constituent': 1779, 'source_TOTAL': 84,
                           'unused_template_column': 447, 'parallel_native_observation': 11}
    assert len(boxes) == 58 and len(optional_ids) == 2075
    assert len(replay['current_checkpoint_box_differences']) == len(controls['current_checkpoint_box_differences']) == 58
    assert controls['empty_ID_representation_scope']['count'] == 2075
    assert controls['complete_2024_named_Senate_native_source_inventory'] is True
    assert controls['all_candidate_native_complete'] is False and controls['historical_native_complete'] is False
    assert controls['current2026_identity_approved'] is False
    assert controls['preferred82_native_constituents'] == 1736
    assert controls['preferred82_candidate_sums'] == {'Ty Pinkins': 451980, 'Roger F. Wicker': 763420}
    assert controls['native_minus_certified'] == {'Ty Pinkins': -1, 'Roger F. Wicker': 0}
    for c in controls['source_controls']:
        own_source = source_checks[c['source_id']]
        assert c['native_constituents'] == own_source['native']
        assert c['component_sums'] == c['printed_TOTAL'] == own_source['component_sums']
        assert c['parallel_candidate_observations'] == own_source['parallel_candidate_observations']
        if any(c['native_minus_county_control'].values()):
            assert c['source_id'] in ['sos-2024-county-tunica', 'sos-2024-county-pike']
    csv_rows = list(csv.DictReader(io.StringIO(own['native-2024-senate-reviewed-84views.csv'].decode(), newline='')))
    seen = set()
    for r in csv_rows:
        key = (r['source_id'], int(r['source_page']), int(r['source_column']), r['candidate'])
        assert key not in seen and key in positions
        seen.add(key)
        source, page, c, f = positions[key]
        assert r['raw_sha256'] == source['raw_sha256']
        assert r['native_label_literal'] == c['label_literal'] and r['role'] == c['role']
        assert r['printed_native_id'] == ('' if c['printed_native_id'] is None else str(c['printed_native_id']))
        assert r['votes'] == ('' if f['value'] is None else str(f['value']))
        assert json.loads(r['accepted_reading_candidate_bounds']) == f['source_box']
        assert json.loads(r['header_bounds']) == c['header_bounds']
    assert seen == set(positions)
    supporting = []
    for name in ['replay-84views-comparison.json', 'replay-84views-manual-repairs.json',
                 'replay-84views-header-repairs.json', 'replay-84views-label-comparison.json']:
        raw, p = freeze(DATA / 'baselines' / name)
        supporting.append(p)
        if name == 'replay-84views-comparison.json':
            comparison = json.loads(raw)
            assert len(comparison['peer_reference']['sources']) == 24
            for s in comparison['sources']:
                pth = ROOT / s['independent_artifact']
                assert pin(pth)['sha256'] == s['independent_artifact_sha256']
                evidence[str(pth.relative_to(ROOT))] = pin(pth)
    snapshot = {'files': own_pins, 'hint_snapshots': hints, 'supporting_snapshots': supporting}
    (DEST / 'snapshot-pins.json').write_text(json.dumps(snapshot, indent=2) + '\n')
    reverse_raw, reverse_pin = freeze(DATA / 'turnout/native-reviewed-peer-reconciliation-84views.json')
    reverse = json.loads(reverse_raw)
    own_csv_pin = next(p for p in own_pins if p['source_path'].endswith('.csv'))
    assert reverse['compared_candidate_positions'] == 4642
    assert reverse['peer_csv']['sha256'] == own_csv_pin['original_sha256']
    assert reverse['own_frozen_ledger']['sha256'] == sha(ref_raw)
    assert not reverse['differences'] and len(reverse['accepted_reading_box_differences']) == 58
    assert reverse['role_candidate_position_counts'] == {
        'native_reporting_constituent': 3558, 'source_TOTAL': 168,
        'unused_template_column': 894, 'parallel_native_observation': 22}
    out = {
        'status': 'pass_84view_reciprocal_4642_positions_with_explicit_box_and_optional_ID_qualifications',
        'source_views': 84, 'county_coverage': 82, 'source_pages': len(raster_pins),
        'role_counts': dict(role_counts), 'candidate_positions': len(positions),
        'turnout_snapshot_manifest': pin(TURNOUT / 'snapshot.json'), 'turnout_reference_pin': ref_pin,
        'baseline_frozen_pins': snapshot, 'source_controls': source_checks,
        'reciprocal_turnout_proof': reverse_pin,
        'numeric_reading_basis_counts': dict(numeric_bases), 'header_reading_basis_counts': dict(header_bases),
        'literal_whitespace_representation_differences': labels,
        'explicit_wrap_representation_aliases': replay['explicit_wrap_representation_aliases'],
        'candidate_box_differences': boxes, 'optional_blank_vs_null_ID_positions': optional_ids,
        'optional_ID_qualification': controls['empty_ID_representation_scope'],
        'original_raster_pins': raster_pins, 'manual_and_independent_artifact_pins': evidence,
        'preferred82_native_constituents': 1736, 'preferred82_candidate_sums': controls['preferred82_candidate_sums'],
        'native_minus_certified': controls['native_minus_certified'],
        'scope': 'Independent original-derived worker ledgers agree at all4642 same-source/hash/page/physical-column candidate numeric/null positions and literal labels subject to explicitly retained wraps. Four strict positions-only hint sets cover84 sources without peer labels/roles/IDs/values. There are58 candidate-box differences, all Itawamba; these are preserved rather than asserted equivalent.2075 blank/null optional-ID representations are not positive printed-ID agreement. Two alternative county packets and11 Kemper parallel columns remain non-additive. Tunica one Pinkins vote remains unallocated. This coordinator comparison hashes retained original rasters/evidence and audits both extractions; it does not claim fresh coordinator OCR or visual reading of all glyphs. Presidential, historical native, generic-write-in/method and current geographic/reporting gates remain open.'}
    (DATA / 'coordinator-native-replay-84view-review.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in ['status', 'source_views', 'source_pages', 'role_counts', 'candidate_positions']}))


if __name__ == '__main__':
    main()
