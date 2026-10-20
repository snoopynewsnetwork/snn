"""Bounded public-source acquisition; immutable, complete per-hop receipts."""
import sys,json,hashlib,gzip,urllib.request,urllib.error,urllib.parse,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(b): return hashlib.sha256(b).hexdigest()
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*a,**kw): return None
def acquire(label,url,method='GET',body=None,headers=None,parent=None):
    dst=ROOT/'requests'/f'{label}.json'
    if dst.exists(): return json.loads(dst.read_bytes())
    h={'User-Agent':'PublicElectionResearch/1.0','Accept':'*/*',**(headers or {})}
    out={'label':label,'parent':parent,'request':{'url':url,'method':method,'body':body,'configured_headers':h},'started_utc':now(),'hops':[]}
    opener=urllib.request.build_opener(NoRedirect())
    for index in range(8):
        hop={'url':url,'method':method,'request_body':body,'configured_headers':h,'started_utc':now()}
        try:
            req=urllib.request.Request(url,data=body.encode() if body is not None else None,headers=h,method=method)
            try: resp=opener.open(req,timeout=35)
            except urllib.error.HTTPError as e: resp=e
            with resp:
                raw=resp.read(); hs=list(resp.headers.raw_items()); status=resp.code
            hop.update(status=status,headers=hs,raw_bytes=len(raw),raw_sha256=sha(raw))
            stored=gzip.compress(raw,mtime=0); assert len(stored)<40000000
            asset=ROOT/'bodies'/(sha(raw)+'.gz');asset.parent.mkdir(parents=True,exist_ok=True)
            if not asset.exists(): asset.write_bytes(stored)
            hop.update(asset=asset.relative_to(ROOT).as_posix(),stored_bytes=len(stored),stored_sha256=sha(stored))
        except Exception as e:
            hop.update(status=None,headers=None,raw_bytes=None,raw_sha256=None,asset=None,error=repr(e),response_unavailable=True)
        hop['finished_utc']=now();out['hops'].append(hop)
        if hop['status'] in [301,302,303,307,308]:
            loc=next((v for k,v in hop['headers'] if k.lower()=='location'),None)
            if not loc: break
            url=urllib.parse.urljoin(url,loc)
            if hop['status']==303 or (hop['status'] in [301,302] and method=='POST'): method='GET';body=None
        else:break
    out['finished_utc']=now();dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(json.dumps(out,indent=2)+'\n');return out
def raw(label):
    r=json.loads((ROOT/'requests'/f'{label}.json').read_bytes());hop=r['hops'][-1]
    return gzip.decompress((ROOT/hop['asset']).read_bytes()) if hop['asset'] else b''
if __name__=='__main__':
    if sys.argv[1]=='--batch':
        from concurrent.futures import ThreadPoolExecutor
        jobs=json.loads(Path(sys.argv[2]).read_bytes())
        with ThreadPoolExecutor(max_workers=4) as pool:
            for r in pool.map(lambda job:acquire(**job),jobs):print(json.dumps({'label':r['label'],'hops':[(h['status'],h['raw_bytes']) for h in r['hops']]}),flush=True)
    else:
        r=acquire(*sys.argv[1:]);print(json.dumps({'label':r['label'],'hops':[(h['status'],h['raw_bytes']) for h in r['hops']]}))
