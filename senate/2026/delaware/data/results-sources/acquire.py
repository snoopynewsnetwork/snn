"""Bounded, explicit public requests. No endpoint enumeration or collector.

Usage: python acquire.py ID URL [PARENT_ID LITERAL_HREF]
Each request is immutable; another observation needs another ID.
Standard library only. Response bodies include redirect and HTTP error entities.
"""
from pathlib import Path
import datetime,gzip,hashlib,json,sys,urllib.request,urllib.error
ROOT=Path(__file__).resolve().parent
def sha(b): return hashlib.sha256(b).hexdigest()
def save(p,b):
    assert len(b)<40_000_000
    if p.exists(): assert p.read_bytes()==b, str(p)
    else: p.write_bytes(b)
class Redirect(urllib.request.HTTPRedirectHandler):
    def __init__(self): self.history=[]
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        b=fp.read(20_000_001); assert len(b)<=20_000_000
        self.history.append(dict(url=req.full_url,status=code,headers=list(headers.items()),body_hex=b.hex()))
        return super().redirect_request(req,fp,code,msg,headers,newurl)
def fetch(sid,url,parent=None,href=None):
    out=ROOT/'raw'/f'{sid}.receipt.json'
    if out.exists(): return json.loads(out.read_bytes())
    redirect=Redirect(); request=urllib.request.Request(url,headers={'User-Agent':'Delaware election source research (bounded public request)','Accept-Encoding':'identity'})
    r=dict(id=sid,requested_url=url,parent_source_id=parent,literal_href=href,method='GET',query=urllib.parse.urlsplit(url).query,body=None,request_headers=dict(request.header_items()),retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),entity_scope='complete urllib HTTP entity; transfer encoding removed; Accept-Encoding identity',redirects=[])
    try:
        try: response=urllib.request.build_opener(redirect).open(request,timeout=45)
        except urllib.error.HTTPError as e: response=e
        with response:
            b=response.read(20_000_001); assert len(b)<=20_000_000,'bounded response exceeded'
            r.update(final_url=response.url,status=response.code,response_headers=list(response.headers.items()))
    except Exception as e:
        b=b'';r.update(final_url=None,status=None,error_type=type(e).__name__,error=str(e))
    for i,h in enumerate(redirect.history):
        rb=bytes.fromhex(h.pop('body_hex')); rp=ROOT/'raw'/f'{sid}.redirect-{i}.body.gz';z=gzip.compress(rb,mtime=0);save(rp,z)
        h.update(asset=str(rp.relative_to(ROOT)),raw_bytes=len(rb),raw_sha256=sha(rb),stored_bytes=len(z),stored_sha256=sha(z));r['redirects'].append(h)
    p=ROOT/'raw'/f'{sid}.body.gz';z=gzip.compress(b,mtime=0);save(p,z)
    r.update(asset=str(p.relative_to(ROOT)),raw_bytes=len(b),raw_sha256=sha(b),stored_bytes=len(z),stored_sha256=sha(z),November_counts_admitted=False)
    save(out,(json.dumps(r,indent=2,ensure_ascii=False)+'\n').encode());return r
if __name__=='__main__':
    if sys.argv[1]=='--plan':
        for j in json.loads((ROOT/sys.argv[2]).read_bytes()):
            r=fetch(j['id'],j['url'],j.get('parent'),j.get('href'));print(r['id'],r['status'],r['raw_bytes'],r.get('error',''),flush=True)
    else:
        r=fetch(*sys.argv[1:]);print(r['id'],r['status'],r['raw_bytes'],r.get('error',''))
