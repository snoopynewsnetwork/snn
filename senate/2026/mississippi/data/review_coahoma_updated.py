"""Independent complete-page readings; numbers typed from original rendered cells."""
from pathlib import Path
import gzip
import hashlib
import json

DATA = Path(__file__).resolve().parent
ROOT = DATA.parent

# Page2 has eleven actual constituents. Page3 has seven, then TOTAL and blanks.
MANUAL = {
    'Kamala D. Harris': [[64,18,314,532,297,864,83,787,143,55,93], [289,397,94,266,30,32,353], 4711],
    'Chase Oliver': [[0,0,0,0,1,1,0,1,1,0,1], [0,0,0,2,0,0,0], 7],
    'Jill Stein': [[0,0,0,2,0,0,0,0,0,0,0], [0,1,0,2,0,0,0], 5],
    'Randall Terry': [[0,0,0,2,0,0,0,0,0,0,0], [0,0,0,0,3,0,1], 6],
    'Donald J. Trump': [[36,28,180,422,61,55,45,137,25,66,32], [39,23,115,558,144,27,15], 2008],
    'Shiva Ayyadurai': [[0,0,1,0,1,0,0,1,0,0,0], [1,0,0,1,0,0,0], 5],
    'Claudia De la Cruz': [[0,0,2,1,1,0,0,2,0,0,0], [1,0,0,0,0,0,0], 7],
    'Robert F. Kennedy Jr.': [[1,0,1,7,6,6,0,4,1,2,1], [3,2,1,3,0,0,1], 39],
    'Peter Sonski': [[0,0,1,0,0,0,0,1,0,0,0], [0,0,0,0,0,0,0], 2],
    'Ty Pinkins': [[61,18,299,515,284,838,76,743,138,55,88], [277,389,96,254,32,26,344], 4533],
    'Roger F. Wicker': [[41,29,188,438,67,73,50,166,30,66,39], [49,33,112,574,143,29,19], 2146],
}
LABELS = [
    ['Bobo','Cagle Crossing','Clarksdale Courthouse','Clarksdale #2','Clarksdale #3',
     'Clarksdale #4','Clarksdale #4 North','Clarksdale #5','Coahoma','Dublin','Farrell'],
    ['Friars Point','Jonestown','Lula','Lyon','Rena Lara','Roundaway','Sasse Street Fire Station'],
]


def main():
    manifest = json.loads((DATA / 'news/manifest.json').read_bytes())
    source = next(x for x in manifest if x['id'] == 'sos-2024-county-coahoma-updated')
    stored = (DATA / 'news' / source['asset']).read_bytes()
    raw = gzip.decompress(stored)
    assert hashlib.sha256(raw).hexdigest() == source['raw_sha256'] == '12be50887df1118cd6aacbbc22aa867f8704beba617ce077492e9daf296b57ee'
    assert hashlib.sha256(stored).hexdigest() == source['stored_sha256']
    peer = json.loads((DATA / 'baselines/coahoma-updated-readings.json').read_bytes())
    assert peer['raw_sha256'] == source['raw_sha256']
    assert len(peer['pages']) == 2
    numeric = 0
    nulls = 0
    for i, page in enumerate(peer['pages']):
        assert page['page'] == i + 2
        columns = page['columns']
        assert len(columns) == 11
        assert [x['source_column'] for x in columns] == list(range(1,12))
        expected = LABELS[i] + (['TOTAL','','',''] if i else [])
        assert [x['native_label_literal'] for x in columns] == expected
        assert [x['unit_type'] for x in columns] == ['source_native_constituent'] * len(LABELS[i]) + (['summary_TOTAL'] + ['unused']*3 if i else [])
        for left, right in zip(columns, columns[1:]):
            assert left['x_bounds'][1] == right['x_bounds'][0]
        assert len(page['fields']) == 11
        for row in page['fields']:
            left, right, total = MANUAL[row['field']]
            values = left if i == 0 else right + [total,None,None,None]
            assert row['values'] == values
            numeric += sum(x is not None for x in values)
            nulls += sum(x is None for x in values)
    for left, right, total in MANUAL.values():
        assert len(left) == 11 and len(right) == 7 and sum(left + right) == total
    renders = json.loads((DATA / 'coordinator-qa/coahoma-updated-renders.json').read_bytes())
    for x in renders:
        b = (ROOT / x['path']).read_bytes()
        assert len(b) == x['bytes'] and hashlib.sha256(b).hexdigest() == x['sha256']
    out = {
        'status': 'pass_complete_original_pages_and_independent_physical_column_readings',
        'source_pin': source, 'rendered_complete_pages_independently_read': renders,
        'source_pages': [2,3], 'constituents': 18, 'named_fields': 11,
        'compared_numeric_positions_including_TOTAL': numeric, 'preserved_blank_unused_positions': nulls,
        'independent_manual_values': MANUAL, 'independent_labels': LABELS,
        'source_manual_reading_snapshot': peer,
        'first_physical_columns': {'page2_Bobo_Senate': [61,41], 'page3_Friars_Point_Senate': [277,49]},
        'state_Senate_control': {'Ty Pinkins': 4533, 'Roger F. Wicker': 2146},
        'scope': 'The first physical numeric column on both pages is an actual constituent, never a discarded header. TOTAL and three unused columns remain separate; raw earlier machine aids are not rewritten. Every typed numeric cell is explicit on the original, not a residual-derived repair. No current geometry/method join or whole-state native acceptance follows.'
    }
    (DATA / 'coordinator-coahoma-native-review.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k:out[k] for k in ['status','constituents','named_fields','compared_numeric_positions_including_TOTAL','preserved_blank_unused_positions']}))


if __name__ == '__main__':
    main()
