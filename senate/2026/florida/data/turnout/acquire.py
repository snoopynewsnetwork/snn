#!/usr/bin/env python3
"""Retain complete public response bodies and exact HTTP receipts; no hidden caches.
Usage: python3 acquire.py ID URL [PARENT_URL]
"""
import datetime,gzip,hashlib,json,sys,urllib.request,urllib.error
from pathlib import Path
D=Path(__file__).resolve().parent
def sha(b): return hashlib.sha256(b).hexdigest()
def fetch(sid,url,parent=None):
    stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; public election research)','Accept-Encoding':'identity'})
    hops=[]
    class Redirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,req,fp,code,msg,headers,newurl):
            hops.append({'requested_url':req.full_url,'status':code,'headers':list(headers.items()),'location':newurl})
            return super().redirect_request(req,fp,code,msg,headers,newurl)
    try:
        response=urllib.request.build_opener(Redirect()).open(request,timeout=45)
    except urllib.error.HTTPError as e: response=e
    except Exception as e:
        receipt={'id':sid,'requested_url':url,'parent_url':parent,'retrieved_utc':stamp,'error':repr(e),'redirects':hops}
        (D/'source'/f'{sid}.receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');return receipt
    raw=response.read();stored=gzip.compress(raw,mtime=0)
    assert len(stored)<40000000
    path=D/'source'/f'{sid}.body.gz';path.write_bytes(stored)
    receipt={'id':sid,'requested_url':url,'final_url':response.url,'parent_url':parent,'retrieved_utc':stamp,'status':response.code,'headers':list(response.headers.items()),'redirects':hops,'raw_bytes':len(raw),'raw_sha256':sha(raw),'stored_path':str(path.relative_to(D)),'stored_bytes':len(stored),'stored_sha256':sha(stored),'storage':'gzip; gzip.decompress restores exact HTTP entity bytes'}
    (D/'source'/f'{sid}.receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');return receipt
if __name__=='__main__': print(json.dumps(fetch(*sys.argv[1:]),indent=2))
