"""Compare already recorded direct-original Coahoma cells to frozen peer evidence."""
import gzip
import json
from acquire_sources import BASE, OUT, sha, savejson


def norm(s):
    return ' '.join(s.split())


def main():
    own_path = OUT / '2020-coahoma-two-publication-native-original-readings.json'
    own_bytes = own_path.read_bytes()
    own = json.loads(own_bytes)
    snap_path = BASE / 'data/baselines/source/native-2020-104views-v1/snapshot.json'
    snap_bytes = snap_path.read_bytes()
    snap = json.loads(snap_bytes)
    pin = next(p for p in snap['pins'] if p['original_path'] ==
               'data/baselines/coahoma-2020-amendment-readings.json')
    stored = (BASE / pin['stored_path']).read_bytes()
    assert len(stored) == pin['stored_bytes'] and sha(stored) == pin['stored_sha256']
    peer_bytes = gzip.decompress(stored)
    assert len(peer_bytes) == pin['original_bytes'] and sha(peer_bytes) == pin['original_sha256']
    peer = json.loads(peer_bytes)
    peer_sources = {s['source_id']: s for s in peer['sources']}
    assert set(peer_sources) == {s['source_id'] for s in own['sources']}
    differences = []
    compared = 0
    for source in own['sources']:
        q = peer_sources[source['source_id']]
        assert q['raw_sha256'] == source['source_raw_sha256']
        assert q['native_constituents'] == source['native_constituents'] == 18
        pages = {p['page']: p for p in q['pages']}
        for row in source['rows']:
            page = pages[row['source_pdf_page']]
            column = next(c for c in page['columns'] if c['source_column'] ==
                          row['physical_source_column'])
            field = next(f for f in page['fields'] if f['candidate'] == row['candidate'])
            value = field['values'][row['physical_source_column'] - 1]
            compared += 1
            if (value, column['role'], norm(column['label_literal'])) != (
                    row['votes'], row['role'], norm(row['literal_source_header'])):
                differences.append(dict(source_id=source['source_id'],
                                        page=row['source_pdf_page'],
                                        column=row['physical_source_column'],
                                        candidate=row['candidate'],
                                        own_value=row['votes'], peer_value=value,
                                        own_role=row['role'], peer_role=column['role'],
                                        own_label=row['literal_source_header'],
                                        peer_label=column['label_literal']))
    assert compared == 132 and not differences, differences[:10]
    result = dict(scope='Post-transcription exact source/page/physical-column/candidate/vote/role/whitespace-folded literal-header comparison. Independently rendered rasters and pixel boxes are not asserted equal. Two publication-native universes remain distinct.',
                  own_original_reading_path=str(own_path.relative_to(BASE)),
                  own_original_reading_sha256=sha(own_bytes),
                  peer_snapshot_path=str(snap_path.relative_to(BASE)),
                  peer_snapshot_sha256=sha(snap_bytes),
                  peer_original_path=pin['original_path'],
                  peer_original_sha256=sha(peer_bytes),
                  peer_stored_path=pin['stored_path'],
                  peer_stored_sha256=sha(stored),
                  publication_count=2, native_source_observations=36,
                  compared_candidate_positions=compared,
                  differences=differences)
    savejson(OUT / '2020-coahoma-two-publication-native-peer-reconciliation.json', result)
    print('Coahoma 2020 original/amended:', compared, 'independent source positions agree')


if __name__ == '__main__':
    main()
