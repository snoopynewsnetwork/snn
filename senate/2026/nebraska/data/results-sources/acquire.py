#!/usr/bin/env python3
"""Bounded, explicit public requests. No ID enumeration or election collector.

python3 acquire.py ID URL PARENT_ID DISCOVERY_BASIS
Existing receipt IDs are immutable; a new observation needs a new ID.
Only complete response entities are stored, using deterministic gzip.
"""
import datetime, gzip, hashlib, json, pathlib, sys, urllib.error, urllib.request

D = pathlib.Path(__file__).resolve().parent
def sha(b): return hashlib.sha256(b).hexdigest()
def readj(p): return json.loads(p.read_bytes())
def writej(p, v): p.write_text(json.dumps(v, indent=2, ensure_ascii=False)+'\n')
class Redirects(urllib.request.HTTPRedirectHandler):
    def __init__(self): self.chain=[]
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.chain.append(dict(requested_url=req.full_url,status=code,headers=list(headers.items()),location=newurl))
        return super().redirect_request(req,fp,code,msg,headers,newurl)
def fetch(sid, url, parent=None, basis=None):
    assert sid and all(c.isalnum() or c in '-_' for c in sid)
    folder=D/'receipts';folder.mkdir(exist_ok=True);(D/'originals').mkdir(exist_ok=True)
    p=folder/(sid+'.json')
    if p.exists():
        r=readj(p);assert r['requested_url']==url;return r
    start=datetime.datetime.now(datetime.timezone.utc).isoformat();h=Redirects()
    req=urllib.request.Request(url,headers={'User-Agent':'Public election-source research; bounded manual audit','Accept-Encoding':'identity'})
    r=dict(id=sid,requested_url=url,parent_source_id=parent,discovery_basis=basis,retrieved_utc=start,redirects=h.chain)
    try:
        try: response=urllib.request.build_opener(h).open(req,timeout=28)
        except urllib.error.HTTPError as e: response=e
        with response:
            raw=response.read()
            r.update(http_status=response.code,final_url=response.url,headers=list(response.headers.items()))
        z=gzip.compress(raw,mtime=0);parts=[]
        for i in range(0,len(z),39000000):
            name=f'originals/{sid}'+(f'.part-{i//39000000:03}' if len(z)>=40000000 else '')+'.gz'
            part=z[i:i+39000000];(D/name).write_bytes(part);parts.append(dict(path=name,bytes=len(part),sha256=sha(part)))
        r.update(raw_bytes=len(raw),raw_sha256=sha(raw),stored_parts=parts,encoding='concatenate stored parts then gzip.decompress; exact response entity',entity_complete=True)
    except Exception as e:
        r.update(http_status=None,final_url=None,headers=[],error_type=type(e).__name__,error=str(e),entity_complete=False,stored_parts=[])
    r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();writej(p,r)
    return r
def body(sid):
    r=readj(D/'receipts'/(sid+'.json'))
    return gzip.decompress(b''.join((D/x['path']).read_bytes() for x in r['stored_parts'])) if r['stored_parts'] else b''
def decoded(sid):
    """Derived HTTP content decoding; raw entity pins above never change."""
    b=body(sid)
    if b.startswith(b'\x1f\x8b'):return gzip.decompress(b)
    return b
if __name__=='__main__':
    r=fetch(*sys.argv[1:]);print(json.dumps({k:r.get(k) for k in ['id','http_status','raw_bytes','error']}))
