"""Source-literal Greene comparison with six explicit capitalization exceptions.

The own complete-original grid is recorded before reading the frozen peer.
Both original p3c1 headers visibly print Mclain; the peer renders McLain.
"""
import csv
import gzip
import io
import json
from PIL import Image
import fitz
from acquire_sources import BASE, OUT, receipts, sha, savejson

SNAP_PATH = BASE / 'data/baselines/source/native-2018-16views-v1/snapshot.json'
SNAP_SHA = 'de741e84c37957905d0bc77f46df7b7eaf984520241b1b97b3bbf8be9266118e'
INITIAL_RAW_SHA = 'fb063bdf2d3c9ca6332c12de81ecfd72208656a353bc583f2c1235f3fd7c9f05'
INITIAL_STORED_SHA = '82a03a33f61d5961c7e12cf1ec3ecfbe861bdf9340a6e924ae92151c7f9ec8dc'
ROLES = {'source_native_reporting_constituent': 'native',
         'source_TOTAL': 'TOTAL', 'unused_template_column': 'unused'}
CROPS = {'sos-2018-county-greene': (1005, 360, 1210, 755),
         'sos-2018-runoff-county-greene': (1010, 460, 1205, 825)}


def main():
    own_path = OUT / '2018-greene-two-stage-native-original-readings.json'
    own_bytes = own_path.read_bytes(); own = json.loads(own_bytes)
    snap_bytes = SNAP_PATH.read_bytes(); assert sha(snap_bytes) == SNAP_SHA
    snap = json.loads(snap_bytes)
    pin = next(x for x in snap['pins'] if x['original_path'] ==
               'data/baselines/native-2018-original-candidate-votes.csv')
    stored = (BASE / pin['stored_path']).read_bytes(); raw = gzip.decompress(stored)
    assert len(stored) == pin['stored_bytes'] and sha(stored) == pin['stored_sha256']
    assert len(raw) == pin['original_bytes'] and sha(raw) == pin['original_sha256']
    ids = {s['source_id'] for s in own['sources']}
    assert ids == set(CROPS)
    peer = {(r['source_id'], int(r['source_page']), int(r['source_column']), r['candidate']): r
            for r in csv.DictReader(io.StringIO(raw.decode())) if r['source_id'] in ids}
    initial_path = OUT / 'source/2018-greene-initial-peer-differences.json.gz'
    initial_stored = initial_path.read_bytes(); initial_raw = gzip.decompress(initial_stored)
    assert sha(initial_stored) == INITIAL_STORED_SHA and sha(initial_raw) == INITIAL_RAW_SHA
    initial = json.loads(initial_raw)
    assert len(initial['disagreements']) == 6
    crop_evidence = []
    for sid, box in CROPS.items():
        receipt = next(r for r in receipts if r['id'] == sid)
        raw_pdf = gzip.decompress((BASE / receipt['path']).read_bytes())
        assert sha(raw_pdf) == receipt['raw_sha256']
        doc = fitz.open(stream=raw_pdf, filetype='pdf')
        full = Image.open(io.BytesIO(doc[2].get_pixmap(
            matrix=fitz.Matrix(4, 4), colorspace=fitz.csGRAY).tobytes('png')))
        crop = full.crop(box).rotate(270, expand=True)
        path = OUT / f'qa/2018-greene-source-literal/{sid}-p3c1-upright-original4x.png'
        path.parent.mkdir(parents=True, exist_ok=True); crop.save(path)
        crop_evidence.append(dict(source_id=sid, source_raw_sha256=receipt['raw_sha256'],
                                  original_pdf_page=3, render_matrix=[4, 4],
                                  original_pixel_crop_box=list(box), rotation_ccw=270,
                                  path=str(path.relative_to(BASE)), sha256=sha(path.read_bytes()),
                                  direct_visual_original_read='Mclain'))
    differences = []
    accepted = []
    rows = [r for s in own['sources'] for r in s['rows']]
    assert len(rows) == len(peer) == 132
    for row in rows:
        key = (row['source_id'], row['source_pdf_page'],
               row['physical_source_column'], row['candidate'])
        q = peer.get(key)
        if q is None:
            differences.append(dict(position=key, reason='peer_missing'))
            continue
        if (('' if row['votes'] is None else str(row['votes'])) != q['votes'] or
                ROLES[row['role']] != q['role'] or
                row['source_raw_sha256'] != q['source_raw_sha256'] or
                row['county_fips'] != q['county_fips']):
            differences.append(dict(position=key, reason='value_role_hash_or_fips',
                                    own=row, peer=q))
        elif row['literal_source_header'] != q['literal_native_label']:
            if (row['source_pdf_page'], row['physical_source_column'],
                    row['literal_source_header'], q['literal_native_label']) == (
                    3, 1, 'Mclain', 'McLain'):
                accepted.append(dict(source_id=row['source_id'], page=3,
                                     physical_column=1, candidate=row['candidate'],
                                     own_original_literal='Mclain', peer_derivative_literal='McLain',
                                     value=row['votes'], role=row['role']))
            else:
                differences.append(dict(position=key, reason='other_label',
                                        own=row['literal_source_header'],
                                        peer=q['literal_native_label']))
    assert not differences and len(accepted) == 6 and len({(x['source_id'], x['candidate']) for x in accepted}) == 6
    assert {(x['position'][0], x['position'][1], x['position'][2], x['position'][3])
            for x in initial['disagreements']} == {
                (x['source_id'], x['page'], x['physical_column'], x['candidate'])
                for x in accepted}
    output = dict(scope='Post-own-original Greene2018 source-position comparison. All132 numeric/null votes, roles, raw hashes and FIPS agree. Six actual original p3c1 glyphs Mclain differ from frozen peer derivative McLain only by capitalization; both literal versions retained. No current or cross-stage ID inference, no exact raster or numeric crop equivalence claim.',
                  county='Greene', own_path=str(own_path.relative_to(BASE)),
                  own_sha256=sha(own_bytes), peer_snapshot_path=str(SNAP_PATH.relative_to(BASE)),
                  peer_snapshot_sha256=SNAP_SHA, peer_flat_original_sha256=sha(raw),
                  source_ids=sorted(ids), source_position_count=len(rows), native_per_stage=13,
                  disagreements=differences, accepted_literal_differences=accepted,
                  original_crop_evidence=crop_evidence,
                  initial_disagreement_archive=dict(path=str(initial_path.relative_to(BASE)),
                                                    stored_sha256=INITIAL_STORED_SHA,
                                                    original_sha256=INITIAL_RAW_SHA,
                                                    original_bytes=len(initial_raw),
                                                    stored_bytes=len(initial_stored)))
    savejson(OUT / '2018-greene-native-peer-reconciliation.json', output)
    print('Greene 2018:', len(rows), 'source positions, six printed capitalization exceptions only')


if __name__ == '__main__':
    main()
