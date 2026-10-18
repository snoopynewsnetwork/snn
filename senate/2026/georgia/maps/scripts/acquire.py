#!/usr/bin/env python3
"""Immutable HTTP captures; exact entity bytes, losslessly stored under the cap."""
import argparse, datetime, gzip, hashlib, json, pathlib, urllib.parse
import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
STATE = ROOT.parent
CAP = 39_000_000

def sha(b): return hashlib.sha256(b).hexdigest()
def dump(p, d):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n')
def read_record(name): return json.loads((ROOT/'receipts'/f'{name}.json').read_text())
def entity(rec):
    if isinstance(rec, str): rec = read_record(rec)
    return b''.join(gzip.decompress((ROOT/p['path']).read_bytes()) if p.get('encoding','gzip')=='gzip'
                    else (ROOT/p['path']).read_bytes() for p in rec['storage'])

def capture(name, url, parent=None, note=None, force=False, headers=None):
    receipt = ROOT/'receipts'/f'{name}.json'
    if receipt.exists() and not force: return read_record(name)
    if receipt.exists(): raise ValueError('Capture IDs are immutable; use a new ID')
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    rec = dict(id=name, requested_url=url, method='GET', parent=parent, note=note,
               retrieved_start_utc=start, source_clock=None, source_timezone=None,
               source_approval='unestablished; HTTP metadata is not election approval')
    try:
        r=requests.get(url, timeout=(45,150), headers={'User-Agent':'GeorgiaPrecinctResearch/1.0 public-source audit',**(headers or {})}, allow_redirects=True)
        b=r.content
        rec.update(final_url=r.url, status=r.status_code, headers=dict(r.headers),
                   redirects=[dict(status=x.status_code,url=x.url,headers=dict(x.headers)) for x in r.history])
    except requests.RequestException as e:
        b=b'';rec.update(final_url=None,status=None,headers={},redirects=[],error=str(e))
    rec.update(retrieved_end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
               entity_bytes=len(b),entity_sha256=sha(b),storage=[])
    packed=gzip.compress(b,mtime=0)
    # Exact ordered slices of the entity; each slice is independently gzip encoded.
    chunks=[b] if len(packed)<CAP else [b[i:i+30_000_000] for i in range(0,len(b),30_000_000)]
    for i,chunk in enumerate(chunks):
        z=gzip.compress(chunk,mtime=0);assert len(z)<40_000_000
        p=ROOT/'objects'/f'{sha(z)}.gz'
        p.parent.mkdir(parents=True,exist_ok=True)
        if not p.exists(): p.write_bytes(z)
        rec['storage'].append(dict(path=str(p.relative_to(ROOT)),encoding='gzip',order=i,entity_bytes=len(chunk),
                                   entity_sha256=sha(chunk),stored_bytes=len(z),stored_sha256=sha(z)))
    dump(receipt,rec)
    return rec

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('id');p.add_argument('url');p.add_argument('--parent');p.add_argument('--note')
    a=p.parse_args();r=capture(a.id,a.url,a.parent,a.note)
    print(json.dumps({k:r.get(k) for k in ['id','status','final_url','entity_bytes','entity_sha256']}))
