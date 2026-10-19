"""Complete original-page visual readings, including compensating cell differences."""
from pathlib import Path
import gzip
import hashlib
import json

DATA = Path(__file__).resolve().parent
ROOT = DATA.parent
MANUAL = {
    'Kamala D. Harris': [[138,3,104,197,299,155,80,16,94,167,107], [129,98,474,39,121,107], 2328],
    'Chase Oliver': [[0,0,1,0,3,4,1,0,7,2,2], [2,0,0,2,1,1], 26],
    'Jill Stein': [[1,0,0,0,2,1,1,0,0,5,0], [1,0,0,0,1,0], 12],
    'Randall Terry': [[1,0,1,1,2,1,0,0,0,1,1], [0,0,0,1,1,1], 11],
    'Donald J. Trump': [[1203,84,703,411,883,1393,815,349,1493,865,321], [779,758,457,969,690,484], 12657],
    'Shiva Ayyadurai': [[0,0,0,0,0,1,0,0,0,0,0], [0,1,0,0,1,0], 3],
    'Claudia De la Cruz': [[0,0,0,1,0,0,0,0,0,0,0], [2,0,0,0,0,0], 3],
    'Robert F. Kennedy Jr.': [[6,0,1,2,6,6,5,1,6,9,0], [2,0,6,3,2,3], 58],
    'Peter Sonski': [[1,1,0,0,2,0,0,0,1,2,2], [0,1,1,0,1,2], 14],
    'Ty Pinkins': [[134,3,101,182,278,155,84,24,99,153,97], [134,101,466,48,126,95], 2280],
    'Roger F. Wicker': [[1199,85,687,413,899,1379,806,322,1475,887,335], [766,745,464,948,679,487], 12576],
}
LABELS = [
    ['2nd District Central\nPrecinct', 'Bethel', 'Biggersville', 'College Hill',
     'East Corinth', 'Five Points 1st Dist', 'Glen', 'Jacinto', 'Kossuth',
     'North Corinth', 'Pinecrest'],
    ['Rienzi', 'Shady Grove', 'South Corinth', 'Union Center', 'Wenasoga', 'West Corinth'],
]


def main():
    renders = json.loads((DATA / 'coordinator-qa/alcorn-renders.json').read_bytes())
    assert len(renders) == 2
    source = renders[0]['source']
    stored = (ROOT / source['path']).read_bytes()
    raw = gzip.decompress(stored)
    assert hashlib.sha256(stored).hexdigest() == source['stored_sha256']
    assert hashlib.sha256(raw).hexdigest() == source['raw_sha256'] == 'e44a72556b2371270616146d8701b662957d5a596b20be6fbe7d47e8f3e985e4'
    for render in renders:
        b = (ROOT / render['path']).read_bytes()
        assert hashlib.sha256(b).hexdigest() == render['sha256'] and len(b) == render['bytes']
    crops = json.loads((DATA / 'coordinator-qa/alcorn-sonski-reading-crops.json').read_bytes())
    for crop in crops:
        b = (ROOT / crop['path']).read_bytes()
        assert hashlib.sha256(b).hexdigest() == crop['sha256'] and len(b) == crop['bytes']
    peer_path = DATA / 'baselines/alcorn-readings.json'
    peer_bytes = peer_path.read_bytes()
    peer = json.loads(peer_bytes)
    assert peer['source_id'] == source['id'] and peer['raw_sha256'] == source['raw_sha256']
    differences = []
    numeric = 0
    blanks = 0
    for index, page in enumerate(peer['pages']):
        assert page['page'] == index + 2
        labels = LABELS[index] + (['TOTAL', '', '', '', ''] if index else [])
        assert [c['source_column'] for c in page['columns']] == list(range(1,12))
        assert [c['native_label_literal'] for c in page['columns']] == labels
        assert [c['unit_type'] for c in page['columns']] == ['precinct_as_printed'] * len(LABELS[index]) + (['summary_TOTAL'] + ['unused']*4 if index else [])
        for field in page['fields']:
            first, second, total = MANUAL[field['field']]
            expected = first if index == 0 else second + [total,None,None,None,None]
            assert len(field['values']) == len(expected) == 11
            for ordinal, (manual, other) in enumerate(zip(expected, field['values']), 1):
                numeric += manual is not None
                blanks += manual is None
                if manual != other:
                    differences.append({'page': page['page'], 'source_column': ordinal,
                        'source_label_literal': labels[ordinal-1], 'candidate': field['field'],
                        'original_visual_value': manual, 'peer_snapshot_value': other})
    for first, second, total in MANUAL.values():
        assert len(first) == 11 and len(second) == 6 and sum(first+second) == total
    assert numeric == 198 and blanks == 44
    assert peer_path.read_bytes() == peer_bytes
    output = {
        'status': 'original_visual_review_with_peer_cell_differences' if differences else 'pass_complete_original_visual_cell_agreement',
        'source_pin': source, 'complete_page_renders': renders, 'contextual_reading_crops': crops,
        'independent_manual_values': MANUAL, 'independent_labels': LABELS,
        'native_constituents': 17, 'named_candidate_fields': 11,
        'explicit_numeric_cells_including_TOTAL': numeric,
        'explicit_unused_blank_cells': blanks,
        'peer_snapshot_pin': {'path': str(peer_path.relative_to(ROOT)), 'bytes': len(peer_bytes),
                              'sha256': hashlib.sha256(peer_bytes).hexdigest()},
        'peer_reading_snapshot': peer, 'differences': differences,
        'scope': 'All explicit cells on complete original pages2/3 were visually read independently. Sonski Bethel and Wenasoga each print1; compensating0/2 readings would still produce the printed county14 and therefore cannot be accepted from county balance alone. No worker file is changed. TOTAL and four unused columns remain separate; absent generic/write-in/method fields are not zero-filled. This bounded review does not close the statewide native gate or approve current identity/geometry.',
    }
    initial = DATA / 'coordinator-alcorn-native-review-initial.json'
    if not initial.exists():
        initial.write_text(json.dumps(output, indent=2) + '\n')
    initial_bytes = initial.read_bytes()
    output['initial_review_witness'] = {'path': str(initial.relative_to(ROOT)),
        'bytes': len(initial_bytes), 'sha256': hashlib.sha256(initial_bytes).hexdigest(),
        'scope': 'First original-cell comparison retained unchanged, including the two compensating Sonski reading differences.'}
    (DATA / 'coordinator-alcorn-native-review.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({k:output[k] for k in ['status','native_constituents',
        'explicit_numeric_cells_including_TOTAL','explicit_unused_blank_cells','differences']}))


if __name__ == '__main__':
    main()
