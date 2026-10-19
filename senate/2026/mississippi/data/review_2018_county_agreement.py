"""Compare the two independently read 2018 county ledgers against exact originals."""
from pathlib import Path
import gzip
import hashlib
import json

DATA = Path(__file__).resolve().parent
ROOT = DATA.parent
EXPECTED = {
    '2018-11-06': {'Tobey Bernard Bartee': 13852, 'Mike Espy': 386742,
                   'Cindy Hyde-Smith': 389995, 'Chris McDaniel': 154878},
    '2018-11-27': {'Mike Espy': 420819, 'Cindy Hyde-Smith': 486769},
}


def main():
    paths = [DATA / 'turnout/historical-county-readings.json',
             DATA / 'baselines/county-2018-readings.json']
    inputs = [p.read_bytes() for p in paths]
    turnout, baselines = [json.loads(b) for b in inputs]
    left = {r['source_id']: r for r in turnout['readings']}
    right = {r['source_id']: r for r in baselines['readings']}
    assert len(left) == len(right) == 164 and left.keys() == right.keys()
    acquisition = {r['id']: r for r in json.loads((DATA / 'turnout/source/acquisition.json').read_bytes())}
    counts = {date: {name: 0 for name in votes} for date, votes in EXPECTED.items()}
    compared = 0
    pins = []
    locator_differences = []
    for sid, a in left.items():
        b = right[sid]
        source = acquisition[sid]
        assert source['status'] == 200
        raw_stored = (ROOT / source['path']).read_bytes()
        raw = gzip.decompress(raw_stored)
        assert len(raw) == source['bytes']
        assert len(raw_stored) == source['stored_bytes']
        assert hashlib.sha256(raw_stored).hexdigest() == source['stored_sha256']
        assert hashlib.sha256(raw).hexdigest() == source['raw_sha256'] == a['raw_sha256'] == b['raw_sha256']
        assert raw.startswith(b'%PDF-')
        assert a['page'] == b['source_positions']['page']
        if a['source_column'] != b['source_positions']['source_column']:
            locator_differences.append({
                'source_id': sid, 'source_page': a['page'],
                'turnout_source_column': a['source_column'],
                'baseline_source_column': b['source_positions']['source_column'],
                'turnout_source_positions': a['source_positions'],
                'baseline_source_positions': b['source_positions'],
                'qualification': 'Literal column ordinals differ and are retained separately. Candidate counts, original bytes and PDF page agree; this comparison does not silently normalize the ordinal.',
            })
        assert a['candidate_votes'] == b['candidate_values']
        date = a['election_date']
        assert set(a['candidate_votes']) == set(EXPECTED[date])
        assert b['stage'] == ('special' if date == '2018-11-06' else 'runoff')
        for name, value in a['candidate_votes'].items():
            counts[date][name] += value
            compared += 1
        pins.append({'source_id': sid, 'source_path': source['path'],
                     'raw_sha256': source['raw_sha256'], 'stored_sha256': source['stored_sha256'],
                     'source_page': a['page'],
                     'turnout_source_TOTAL_column': a['source_column'],
                     'baseline_source_TOTAL_column': b['source_positions']['source_column'],
                     'candidate_values': a['candidate_votes']})
    assert compared == 492 and counts == EXPECTED
    assert not locator_differences
    corrected_ordinals = {}
    for sid in ['sos-2018-runoff-county-leake', 'sos-2018-county-desoto']:
        assert left[sid]['source_column'] == right[sid]['source_positions']['source_column'] == 9
        assert left[sid]['source_positions']['proposed_source_column'] == 8
        corrected_ordinals[sid] = {
            'accepted_physical_TOTAL_column': 9,
            'retained_discovery_aid_proposed_source_column': 8,
            'worker_metadata_correction_history': left[sid]['metadata_correction_history'],
            'scope': 'The worker independently reread eight preceding printed columns. Earlier discovery-aid ordinal and bounds remain unchanged; this coordinator comparison does not claim an additional visual reread of these two pages.',
        }
    assert all(sum(r['election_date'] == date for r in left.values()) == 82 for date in EXPECTED)
    # A concurrent worker edit must never produce a silently mixed comparison.
    assert [p.read_bytes() for p in paths] == inputs
    manual_path = DATA / 'coordinator-2018-disputed-cell-review.json'
    manual_bytes = manual_path.read_bytes()
    manual = json.loads(manual_bytes)
    for sid, values in manual['independent_manual_readings'].items():
        assert left[sid]['candidate_votes'] == values['TOTAL']
    out = {
        'status': 'pass_164_originals_492_candidate_values_and_all_TOTAL_ordinals',
        'input_pins': [{'path': str(p.relative_to(ROOT)), 'bytes': len(b),
                        'sha256': hashlib.sha256(b).hexdigest()} for p, b in zip(paths, inputs)],
        'independent_bounded_original_reading_pin': {
            'path': str(manual_path.relative_to(ROOT)), 'bytes': len(manual_bytes),
            'sha256': hashlib.sha256(manual_bytes).hexdigest()},
        'originals_verified': len(pins), 'compared_candidate_values': compared,
        'complete_stage_state_candidate_sums': counts,
        'complete_stage_candidate_totals': {date: sum(v.values()) for date, v in counts.items()},
        'source_positions_and_values': pins,
        'literal_column_ordinal_differences': locator_differences,
        'resolved_physical_ordinal_corrections': corrected_ordinals,
        'scope': 'This verifies candidate-count agreement, exact original hashes, PDF pages, accepted physical TOTAL ordinals and state sums across the two independently read county ledgers. Leake runoff and DeSoto November6 accepted ordinals are9 after independent worker rereads; their discovery-aid proposed ordinals8 remain raw evidence. Coordinator visual review is bounded to the separately pinned Choctaw/Quitman pages; it is not a claim that the coordinator visually reread all164 originals. Earlier competing numeric readings were transcription errors. Complete statewide constituent-level native verification and current geography remain separate open gates.',
    }
    (DATA / 'coordinator-2018-county-agreement.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in ['status', 'originals_verified',
          'compared_candidate_values', 'complete_stage_candidate_totals']}))


if __name__ == '__main__':
    main()
