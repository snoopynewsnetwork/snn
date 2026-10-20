#!/usr/bin/env python3
"""Freeze shared original receipts; acquire bounded new primary observations.

No shared writes. Stored bodies are full requests-decoded HTTP entities, gzip mtime=0.
Run --pin once, --fetch URL KEY [PARENT] for a new observation (never overwrites).
"""
import datetime, gzip, hashlib, json, sys
from pathlib import Path

D=Path(__file__).resolve().parent
STATE=D.parent.parent
def sha(b): return hashlib.sha256(b).hexdigest()
def dump(p,obj): p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def pin():
    rows=json.loads((STATE/'data/news/manifest.json').read_bytes())
    wanted=[r for r in rows if r['id'].startswith(('sos-','state-elections'))]
    out=[]
    for r in wanted:
        p=STATE/'data/news'/r['asset']; z=p.read_bytes(); b=gzip.decompress(z)
        assert sha(z)==r['stored_sha256'] and sha(b)==r['raw_sha256'] and len(b)==r['bytes']
        out.append(dict(r,immutable_body_path=p.relative_to(STATE).as_posix(),receipt_origin='data/news/manifest.json (individual receipt frozen; no runtime manifest dependency)'))
    p=D/'source/shared-originals.json'
    assert not p.exists();dump(p,out)
    print('pinned',len(out),'complete original entities')
def fetch(url,key,parent=None):
    import requests
    p=D/'source'/f'{key}.receipt.json'; assert not p.exists(),p
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        r=requests.get(url,timeout=50)
    except requests.RequestException as e:
        dump(p,dict(id=key,requested_url=url,parent=parent,retrieved_at_utc=start,transport_error=str(e)))
        print(key,'transport error');return
    b=r.content;z=gzip.compress(b,mtime=0);assert len(z)<40_000_000
    body=D/'source'/f'{key}.body.gz';body.write_bytes(z)
    obj=dict(id=key,requested_url=url,final_url=r.url,parent=parent,method='GET',retrieved_at_utc=start,
             completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status=r.status_code,
             redirects=[dict(url=x.url,status=x.status_code,headers=dict(x.headers))for x in r.history],
             headers=dict(r.headers),raw_sha256=sha(b),raw_bytes=len(b),stored_sha256=sha(z),stored_bytes=len(z),
             body_path=body.relative_to(STATE).as_posix(),entity_encoding='requests-decoded response entity; lossless gzip')
    dump(p,obj); print(key,r.status_code,len(b),sha(b))
if __name__=='__main__':
    if sys.argv[1]=='--pin':pin()
    elif sys.argv[1]=='--fetch':fetch(*sys.argv[2:])
    else:raise SystemExit('use --pin or --fetch URL KEY [PARENT]')
