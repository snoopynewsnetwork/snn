#!/usr/bin/env python3
"""Append-only, bounded primary acquisition. Run with python -B; never overwrites originals."""
import argparse, datetime, gzip, hashlib, json, pathlib, urllib.parse
import requests

ROOT = pathlib.Path(__file__).resolve().parent
STATE = ROOT.parent

def sha(b): return hashlib.sha256(b).hexdigest()
def savejson(p, d): p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n')
def fetch(key, url, parent=None):
    receipt = ROOT/'source'/f'{key}.receipt.json'
    if receipt.exists(): return json.loads(receipt.read_text())
    d = dict(id=key, requested_url=url, parent_source_id=parent, request_method='GET',
             retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    try:
        r=requests.get(url, timeout=(15,60), headers={'User-Agent':'Mississippi precinct map research; bounded archive acquisition', 'Accept-Encoding':'identity'})
        b=r.content
        d.update(status=r.status_code, final_url=r.url, headers=dict(r.headers),
                 redirects=[dict(url=h.url,status=h.status_code,headers=dict(h.headers)) for h in r.history],
                 raw_bytes=len(b),raw_sha256=sha(b))
        # Deduplicate exact raw bodies, including read-only coordinator originals.
        shared=json.loads((STATE/'data/coordinator-map-preparation/source-ledger.json').read_text())
        existing=shared+[json.loads(p.read_text()) for p in (ROOT/'source').glob('*.receipt.json')]
        same=next((x for x in existing if x.get('raw_sha256')==sha(b) and x.get('path')),None)
        if same:
            d.update(path=same['path'],stored_bytes=same['stored_bytes'],stored_sha256=same['stored_sha256'],storage='exact-existing-readonly-reference')
        else:
            packed=gzip.compress(b,mtime=0)
            if len(packed)<40000000:
                p=ROOT/'source'/f'{key}.body.gz';p.write_bytes(packed)
                d.update(path=str(p.relative_to(STATE)),stored_bytes=len(packed),stored_sha256=sha(packed),storage='gzip')
            else:
                seg=[]
                for i in range(0,len(b),30000000):
                    p=ROOT/'source'/f'{key}.part-{i//30000000:03}.bin';part=b[i:i+30000000];p.write_bytes(part)
                    seg.append(dict(path=str(p.relative_to(STATE)),bytes=len(part),sha256=sha(part)))
                d.update(segments=seg,storage='ordered-raw-byte-segments')
    except Exception as e:
        d.update(status=0,error_type=type(e).__name__,error=str(e))
    savejson(receipt,d)
    print(key,d.get('status'),d.get('raw_bytes'),flush=True)
    return d

def body(d):
    if 'segments' in d:return b''.join((STATE/x['path']).read_bytes() for x in d['segments'])
    b=(STATE/d['path']).read_bytes()
    assert len(b)==d['stored_bytes'] and sha(b)==d['stored_sha256']
    b=gzip.decompress(b) if d['path'].endswith('.gz') else b
    assert len(b)==d['raw_bytes'] and sha(b)==d['raw_sha256']
    return b

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('id');p.add_argument('url');p.add_argument('--parent');a=p.parse_args()
    fetch(a.id,a.url,a.parent)
