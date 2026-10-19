"""Freeze peer layout hints without any vote, label, or candidate-value import.

This is source targeting only. Numeric extraction renders original PDFs anew.
"""
import argparse
import gzip
import json
from acquire_sources import BASE,OUT,sha,savejson

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--version',choices=['v1','v2','v3','v4','v5','v6','v7'],default='v1');args=ap.parse_args()
    source_version={'v1':'40views-v1','v2':'50views-v1','v3':'65views-v1','v4':'70views-v1','v5':'85views-v1','v6':'95views-v1','v7':'104views-v1'}[args.version]
    expected_count={'v1':38,'v2':48,'v3':63,'v4':68,'v5':83,'v6':93,'v7':102}[args.version]
    snapshot=json.loads((BASE/f'data/baselines/source/native-2020-{source_version}/snapshot.json').read_text())
    pin=next(p for p in snapshot['pins'] if p['original_path']=='data/baselines/native-2020-additional-readings.json')
    frozen=(BASE/pin['stored_path']).read_bytes()
    assert len(frozen)==pin['stored_bytes'] and sha(frozen)==pin['stored_sha256']
    peer_bytes=gzip.decompress(frozen)
    assert len(peer_bytes)==pin['original_bytes'] and sha(peer_bytes)==pin['original_sha256']
    original=json.loads(peer_bytes)
    sources=[]
    for s in original['sources']:
        pages=[]
        for p in s['pages']:
            pages.append(dict(page=p['page'],render_size=p['render_size'],render_scale=p['render_scale'],rotation_ccw=p['rotation_ccw'],deskew_angle_ccw=p['deskew_angle_ccw'],columns=[dict(source_column=c['source_column'],header_bounds=c['header_bounds'],role=c['role']) for c in p['columns']],candidate_rows=[dict(candidate=f['candidate'],row_bounds=f['row_bounds']) for f in p['fields']]))
        sources.append(dict(source_id=s['source_id'],source_raw_sha256=s['raw_sha256'],pages=pages))
    assert len(sources)==expected_count and len({s['source_id'] for s in sources})==expected_count
    data=dict(scope='Peer source/page/physical-column/candidate-row geometry only; no votes, source labels, native IDs, or candidate controls. Numeric evidence requires separately rendered original PDF.',peer_source_sha256=sha(peer_bytes),sources=sources)
    serialized=json.dumps(data,ensure_ascii=False)
    assert not any(k in serialized for k in ['"values"','"votes"','"candidate_values"','"label_literal"','"literal_printed_id"'])
    path=OUT/f'source/2020-native-position-hints-{args.version}.json'
    savejson(path,data)
    print('positions-only 2020 hints',args.version,len(sources),sha(path.read_bytes()))
if __name__=='__main__':main()
