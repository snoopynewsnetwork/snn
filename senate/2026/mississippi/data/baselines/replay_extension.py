"""Freeze a new peer layout checkpoint, then independently read ORIGINAL bytes.

The lossless peer reference is comparison evidence only. Extraction receives
source IDs/hashes/transforms/boxes, and no peer label/role/vote/OCR field.
Previously frozen25 views are excluded from this extension.
"""
import concurrent.futures,gzip,json
from sources import OUT,BASE,sha,save
from replay_reviewed_native import hint_snapshot,read_source,independent_fields
from replay_native_headers import run as read_headers
def snapshot():
    dest=OUT/'source/native-reviewed-extension-positions.json.gz'
    if dest.exists():return json.loads(gzip.decompress(dest.read_bytes()))
    path=BASE/'data/turnout/native-reviewed-2024.json';raw=path.read_bytes();x=json.loads(raw);prior={s['source_id'] for s in hint_snapshot()['sources']};ref=OUT/'source'/f'peer-native-review-reference-{sha(raw)[:16]}.json.gz';ref.write_bytes(gzip.compress(raw,mtime=0));sources=[]
    for key,s in x['sources'].items():
        if key in prior:continue
        pages=[]
        for p in s['pages']:
            pages.append({k:p[k] for k in ['page','render_size','rotation_ccw','deskew_angle_ccw']}|{'columns':[{'source_column':c['source_column'],'header_bounds':c['header_bounds'],'candidate_bounds':c['candidate_bounds']} for c in p['columns']]})
        sources.append(dict(source_id=key,raw_sha256=s['raw_sha256'],pages=pages))
    result=dict(reference_original_path=str(path.relative_to(BASE)),reference_path=str(ref.relative_to(BASE)),reference_original_sha256=sha(raw),reference_original_bytes=len(raw),reference_stored_sha256=sha(ref.read_bytes()),reference_stored_bytes=ref.stat().st_size,qualification='Frozen peer comparison reference. Extraction hints only contain source ID/hash/page/transform/physicalboxes. No peer labels/values/roles/OCR imported as extraction input.',sources=sources)
    dest.write_bytes(gzip.compress(json.dumps(result).encode(),mtime=0));return result
def main():
    x=snapshot();print('frozen extension',len(x['sources']),x['reference_original_sha256'],flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for s in pool.map(read_source,x['sources']):
            dest=OUT/'extracts/reviewed-replay'/s['source_id']/'independent-fields.json.gz';dest.write_bytes(gzip.compress(json.dumps(independent_fields(s),ensure_ascii=False).encode(),mtime=0));print('independent numeric',s['source_id'],flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for k in pool.map(read_headers,x['sources']):print('independent headers',k,flush=True)
if __name__=='__main__':main()
