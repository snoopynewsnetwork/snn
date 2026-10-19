"""Bounded reciprocal source-cell check; never upgrades partial native coverage."""
from pathlib import Path
from collections import Counter
import gzip
import hashlib
import json

DATA = Path(__file__).resolve().parent
ROOT = DATA.parent
FROZEN = DATA / 'coordinator-qa/native-2024-25views'
REPLAY = DATA / 'coordinator-qa/native-replay-25views'
NAMES = {'Ty_Pinkins': 'Ty Pinkins', 'Roger_F_Wicker': 'Roger F. Wicker'}
ROLE_ALIAS = {'native_reporting_constituent': 'source_native_reporting_constituent',
              'source_TOTAL': 'source_TOTAL', 'unused_template_column': 'unused_template_column'}


def main():
    pins = json.loads((REPLAY / 'snapshot-pins.json').read_bytes())
    inputs = {}
    for pin in pins['files']:
        stored = (ROOT / pin['snapshot_path']).read_bytes()
        raw = gzip.decompress(stored)
        assert len(stored) == pin['stored_bytes'] and hashlib.sha256(stored).hexdigest() == pin['stored_sha256']
        assert len(raw) == pin['original_bytes'] and hashlib.sha256(raw).hexdigest() == pin['original_sha256']
        inputs[Path(pin['source_path']).name] = raw
    reference_bytes = gzip.decompress((FROZEN / 'native-reviewed-2024.json.gz').read_bytes())
    assert hashlib.sha256(reference_bytes).hexdigest() == '2501822b1b432b8eaeb1257c47b0d002082089ef86281c0dfa7ff4030ab7015f'
    reference = json.loads(reference_bytes)
    replay = json.loads(inputs['native-2024-senate-reviewed.json'])
    controls = json.loads(inputs['native-2024-senate-reviewed-controls.json'])
    assert replay['peer_original_sha256'] == hashlib.sha256(reference_bytes).hexdigest()
    assert controls['source_views'] == 25 and controls['native_constituents'] == 553
    assert controls['statewide_native_complete'] is False
    left = {s['source_id']: s for s in replay['sources']}
    assert len(left) == len(reference['sources']) == 25 and left.keys() == reference['sources'].keys()
    hint_copy = REPLAY / 'position-hints.json.gz'
    if not hint_copy.exists():
        hint_copy.write_bytes((DATA / 'baselines/source/native-reviewed-25view-positions.json.gz').read_bytes())
    hint_stored = hint_copy.read_bytes()
    hint_raw = gzip.decompress(hint_stored)
    hints = json.loads(hint_raw)
    assert hints['reference_original_sha256'] == hashlib.sha256(reference_bytes).hexdigest()
    # Check a strict whitelist rather than merely searching for sensitive key names.
    assert len(hints['sources']) == 25
    for source in hints['sources']:
        assert set(source) == {'source_id', 'raw_sha256', 'pages'}
        for page in source['pages']:
            assert set(page) == {'page','render_size','rotation_ccw','deskew_angle_ccw','columns'}
            for column in page['columns']:
                assert set(column) == {'source_column','header_bounds','candidate_bounds'}
                assert set(column['candidate_bounds']) == set(NAMES.values())
    role_counts = Counter()
    numeric_bases = Counter()
    header_bases = Counter()
    positions = 0
    native_cells = 0
    total_cells = 0
    null_cells = 0
    whitespace_aliases = []
    source_wrap_aliases = []
    parsed_id_gaps = []
    rasters = []
    manual_evidence = {}
    for sid, source in left.items():
        target = reference['sources'][sid]
        assert source['raw_sha256'] == target['raw_sha256']
        assert len(source['pages']) == len(target['pages'])
        for page, original in zip(source['pages'], target['pages']):
            assert page['page'] == original['page']
            assert max(abs(a-b) for a,b in zip(page['render_size'],original['render_size'])) <= 1
            raster = (ROOT / page['raster_path']).read_bytes()
            assert hashlib.sha256(raster).hexdigest() == page['raster_sha256']
            rasters.append({'path':page['raster_path'],'sha256':page['raster_sha256'],'bytes':len(raster)})
            assert len(page['columns']) == len(original['columns'])
            for column, expected in zip(page['columns'], original['columns']):
                assert column['source_column'] == expected['source_column']
                assert column['role'] == ROLE_ALIAS[expected['role']]
                role_counts[column['role']] += 1
                header_bases[column['header_reading_basis']] += 1
                normalized_label = ' '.join(column['label_literal'].split())
                normalized_expected = ' '.join(expected['label_literal'].split())
                if normalized_label != normalized_expected:
                    assert (sid, page['page'], column['source_column']) == ('sos-2024-county-smith', 2, 5)
                    assert expected['label_literal'] == 'Clear Springs-Pineville'
                    assert column['label_literal'] == 'Clear Springs-\nPineville'
                    source_wrap_aliases.append({'source_id':sid,'PDF_page':page['page'],
                        'physical_column':column['source_column'],
                        'turnout_frozen_label_literal':expected['label_literal'],
                        'baseline_label_literal':column['label_literal'],
                        'scope':'One explicit source hyphen/line-wrap representation difference; frozen bytes are preserved and no general fuzzy label match is used.'})
                if column['label_literal'] != expected['label_literal']:
                    whitespace_aliases.append({'source_id':sid,'PDF_page':page['page'],
                        'physical_column':column['source_column'],
                        'turnout_label_literal':expected['label_literal'],
                        'baseline_label_literal':column['label_literal']})
                if not (column['printed_native_id'] == expected['printed_native_id'] or (
                        column['printed_native_id'] == '' and expected['printed_native_id'] is None)):
                    assert column['printed_native_id'] == '' and expected['printed_native_id'] not in ['',None]
                    parsed_id_gaps.append({'source_id':sid,'PDF_page':page['page'],
                        'physical_column':column['source_column'],
                        'turnout_source_parsed_ID':expected['printed_native_id'],
                        'baseline_source_parsed_ID':column['printed_native_id'],
                        'turnout_label_literal':expected['label_literal'],
                        'baseline_label_literal':column['label_literal']})
                for key, name in NAMES.items():
                    field = column['fields'][name]
                    assert field['value'] == expected[key]
                    assert field['source_box'] == expected['candidate_bounds'][name]
                    numeric_bases[field['reading_basis']] += 1
                    positions += 1
                    if expected['role'] == 'native_reporting_constituent':
                        native_cells += 1
                    elif expected['role'] == 'source_TOTAL':
                        total_cells += 1
                    else:
                        assert field['value'] is None
                        null_cells += 1
                    evidence = field.get('manual_evidence')
                    if evidence:
                        path = DATA / 'baselines' / evidence
                        b = path.read_bytes()
                        manual_evidence[str(path.relative_to(ROOT))] = {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
    assert (positions,native_cells,total_cells,null_cells) == (1386,1106,50,230)
    assert len(source_wrap_aliases) == 1 and len(parsed_id_gaps) == 104
    assert role_counts == {'source_native_reporting_constituent':553,'source_TOTAL':25,'unused_template_column':115}
    assert numeric_bases == {
        'independent_original_OCR_agrees_frozen_peer_visual_reading':1129,
        'independent_original_visual_cell_reading':27,
        'blank_source_template_cell_null_not_zero':230}
    assert header_bases == {'independent_original_header_OCR_agrees_frozen_peer_visual_reading':619,
                            'independent_original_visual_reading':74}
    assert all(r['component_sums'] == r['printed_TOTAL'] == r['county_control'] for r in controls['sources'])
    output = {
        'status':'pass_reciprocal_1386_values_with_104_retained_parsed_ID_gaps_not_statewide_complete',
        'independent_replay_snapshot_pins':pins,
        'reference_turnout_original_sha256':hashlib.sha256(reference_bytes).hexdigest(),
        'position_only_hint_snapshot':{'path':str(hint_copy.relative_to(ROOT)),
            'stored_sha256':hashlib.sha256(hint_stored).hexdigest(),'raw_sha256':hashlib.sha256(hint_raw).hexdigest(),
            'strict_key_whitelist_passed':True},
        'source_views':25,'source_pages':len(rasters),'role_counts':dict(role_counts),
        'all_source_candidate_positions':positions,'native_candidate_cells':native_cells,
        'TOTAL_candidate_cells':total_cells,'unused_null_candidate_cells':null_cells,
        'numeric_reading_basis_counts':dict(numeric_bases),'header_reading_basis_counts':dict(header_bases),
        'literal_label_whitespace_aliases':whitespace_aliases,
        'explicit_source_hyphen_wrap_alias':source_wrap_aliases,
        'unresolved_parsed_ID_field_gaps':parsed_id_gaps,
        'own_original_raster_pins':rasters,'manual_original_evidence_pins':manual_evidence,
        'scope':'This coordinator audit compares the two independently produced source ledgers and checks exact source/page/cell pointers, position-only hint fields and retained rasters/manual evidence. It does not claim the coordinator independently reran every OCR engine or visually reread every glyph. Whitespace-only aliases and one source-specific Smith hyphen wrap are explicit. The104 nonempty turnout parsed-ID fields versus baseline empty fields remain actual metadata gaps, not normalized agreement; their literal headers and counts agree. No numeric/role difference is normalized. Only two named Senate fields across25 source views are covered. Presidential, method, full statewide native, legal valid-write-in and current geographic/reporting gates remain separate and open.'}
    (DATA / 'coordinator-native-replay-25view-review.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({k:output[k] for k in ['status','source_views','source_pages',
        'all_source_candidate_positions','native_candidate_cells','TOTAL_candidate_cells','unused_null_candidate_cells']}))


if __name__ == '__main__':
    main()
