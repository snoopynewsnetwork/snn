"""New immutable public observations; no authentication, browser bypass or collector."""
from common import *
from datetime import datetime,timezone
import urllib.request,urllib.error,urllib.parse,sys

def now():return datetime.now(timezone.utc).isoformat()
def prohibited(url):
    u=urllib.parse.urlsplit(url)
    return u.scheme not in ('https','http') or any(x in (u.netloc+u.path).lower() for x in ['login','sign-in','signin','challenge','facebook.com','twitter.com','x.com/','/admin','/account','/auth/'])
def acquire(name,url,parent=None,literal=None):
    receipt=R/'acquired'/f'{name}.receipt.json'
    assert not receipt.exists(),receipt
    assert not prohibited(url),url
    hops=[]
    class Redirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,req,fp,code,msg,headers,newurl):
            target=urllib.parse.urljoin(req.full_url,newurl)
            hops.append(dict(url=req.full_url,status=code,headers=list(headers.items()),location=target))
            if prohibited(target):raise RuntimeError('Stopped unexpected account/challenge/security redirect: '+target)
            return super().redirect_request(req,fp,code,msg,headers,newurl)
    headers={'User-Agent':'Election-source-research/1.0','Accept':'*/*','Accept-Encoding':'identity'}
    r=dict(id=name,method='GET',url=url,parent_observation=parent,literal_provenance=literal,
        configured_request_headers=headers,submitted_body=None,started_at_utc=now(),redirects=hops,
        transport_framing_retained=False,request_headers_scope='configured headers; urllib also supplies Host and Connection',
        body_complete=False)
    try:
        req=urllib.request.Request(url,headers=headers,method='GET')
        try:response=urllib.request.build_opener(Redirect()).open(req,timeout=30)
        except urllib.error.HTTPError as e:response=e
        with response:
            body=response.read();r.update(status=response.code,final_url=response.url,response_headers=list(response.headers.items()))
        r.update(body_complete=True,raw_bytes=len(body),raw_sha256=sha(body),retrieved_at_utc=now())
        stored=gzip.compress(body,mtime=0)
        # Reuse any earlier own immutable original of the same entity.
        p=R/'acquired'/f'{sha(body)}.body.gz'
        if not p.exists():write(p,stored)
        else:assert gzip.decompress(p.read_bytes())==body
        r.update(stored_path=str(p.relative_to(S)),stored_sha256=sha(p.read_bytes()),stored_bytes=p.stat().st_size,compression='gzip')
        assert len(stored)<40000000,'Large object must use ordered <40M lossless parts before sealing'
    except Exception as e:r.update(error_type=type(e).__name__,error=str(e),retrieved_at_utc=now())
    write(receipt,dump(r));print(name,r.get('status'),r.get('raw_bytes'),r.get('error',''))
    return r
if __name__=='__main__':acquire(*sys.argv[1:])
