"""Compare two complete eleven-candidate original readings with independent ledgers."""
from pathlib import Path
import gzip
import hashlib
import json
import review_alcorn_native as alcorn
import review_coahoma_updated as coahoma

DATA = Path(__file__).resolve().parent
ROOT = DATA.parent
DEST = DATA / 'coordinator-qa/native-allfield-two-views'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def frozen(relative):
    source = DATA / relative
    path = DEST / (source.name + '.gz')
    if not path.exists():
        b = source.read_bytes()
        assert source.read_bytes() == b
        path.write_bytes(gzip.compress(b,mtime=0))
    stored = path.read_bytes()
    raw = gzip.decompress(stored)
    return json.loads(raw), {'source_path':str(source.relative_to(ROOT)),
        'snapshot_path':str(path.relative_to(ROOT)), 'original_bytes':len(raw),
        'original_sha256':sha(raw), 'stored_bytes':len(stored), 'stored_sha256':sha(stored)}


def main():
    DEST.mkdir(exist_ok=True)
    ledger, ledger_pin = frozen('turnout/native-allfield-readings.json')
    controls, controls_pin = frozen('turnout/native-allfield-controls.json')
    reciprocal, reciprocal_pin = frozen('turnout/native-allfield-peer-reconciliation.json')
    assert len(ledger['sources']) == controls['source_views'] == len(reciprocal['results']) == 2
    comparisons = []
    for sid, manual, native_count, review_path in [
        ('sos-2024-county-alcorn',alcorn.MANUAL,17,'coordinator-alcorn-native-review.json'),
        ('sos-2024-county-coahoma-updated',coahoma.MANUAL,18,'coordinator-coahoma-native-review.json')]:
        own = ledger['sources'][sid]
        review = json.loads((DATA / review_path).read_bytes())
        expected_source_sha = review['source_pin']['raw_sha256']
        assert own['raw_sha256'] == expected_source_sha
        assert len(own['pages']) == 2
        numeric = nulls = 0
        for index, page in enumerate(own['pages']):
            assert page['page'] == index+2 and len(page['fields']) == 11
            assert {r['candidate'] for r in page['fields']} == set(manual)
            for field in page['fields']:
                first, second, total = manual[field['candidate']]
                expected = first if index == 0 else second+[total]+[None]*(10-len(second))
                assert field['values'] == expected
                assert len(field['values']) == len(field['cell_bounds']) == 11
                for column, bounds in enumerate(field['cell_bounds']):
                    assert bounds == [page['physical_numeric_grid_x'][column],field['row_bounds'][1],
                                      page['physical_numeric_grid_x'][column+1],field['row_bounds'][3]]
                numeric += sum(v is not None for v in expected)
                nulls += sum(v is None for v in expected)
        control = next(r for r in controls['checks'] if r['source_id'] == sid)
        totals = {name:triplet[2] for name,triplet in manual.items()}
        assert control['native_sums'] == control['printed_TOTAL_values'] == control['county_primary_controls'] == totals
        peer_result = next(r for r in reciprocal['results'] if r['source_id'] == sid)
        assert peer_result['differences'] == []
        assert peer_result['numeric_positions'] == numeric
        assert peer_result['null_unused_positions'] == nulls
        assert peer_result['own_pin']['sha256'] == ledger_pin['original_sha256']
        comparisons.append({'source_id':sid,'raw_sha256':expected_source_sha,'native_constituents':native_count,
                            'named_candidate_fields':11,'numeric_positions_including_TOTAL':numeric,
                            'unused_null_positions':nulls,'prior_independent_original_review':review_path,
                            'all11_vectors_close_printed_TOTAL_and_primary_county_controls':True})
    assert sum(r['numeric_positions_including_TOTAL'] for r in comparisons) == 407
    assert sum(r['unused_null_positions'] for r in comparisons) == 77
    output = {'status':'pass_407_numeric_and_77_unused_null_positions_two_bounded_source_views',
        'snapshot_pins':[ledger_pin,controls_pin,reciprocal_pin], 'comparisons':comparisons,
        'numeric_positions_including_TOTAL':407,'unused_null_positions':77,
        'scope':'The independently typed coordinator full-original readings for Alcorn and Coahoma Updated match the frozen turnout ledger at all484 explicit candidate positions, including407 numeric cells and77 unused/null cells. Each of22 candidate vectors closes its printed source TOTAL and primary county control. This includes the corrected Alcorn Sonski Bethel1/Wenasoga1 readings; the earlier compensating0/2 witness remains unchanged. Target boxes are checked as physical positions in the retained source render, not current reporting IDs or geographic joins. Only two original source views are covered; statewide native and presidential completion remain open.'}
    (DATA / 'coordinator-allfield-two-view-review.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({k:output[k] for k in ['status','numeric_positions_including_TOTAL','unused_null_positions']}))


if __name__ == '__main__':
    main()
