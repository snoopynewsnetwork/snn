#!/usr/bin/env python3
"""Bounded public HTTP acquisition; retain complete entities and every redirect response."""
import argparse,datetime,gzip,hashlib,json,urllib.request,urllib.error
from pathlib import Path
HERE=Path(__file__).resolve().parent
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*a,**k): return None
def sha(x):return hashlib.sha256(x).hexdigest()
def acquire(id,url,parent=None):
 opener=urllib.request.build_opener(NoRedirect);hops=[];initial=url
 request_headers={'User-Agent':'Virginia-election-research/1.0 public-source-audit','Accept-Encoding':'identity'}
 for i in range(8):
  now=datetime.datetime.now(datetime.timezone.utc).isoformat();req=urllib.request.Request(url,headers=request_headers)
  try:
   try:r=opener.open(req,timeout=40)
   except urllib.error.HTTPError as e:r=e
   with r:
    body=r.read();status=r.code;headers=list(r.headers.raw_items());location=r.headers.get('Location');final=r.geturl()
   packed=gzip.compress(body,mtime=0);assert len(packed)<40000000
   p=HERE/'source/acquired'/f'{id}.hop{i}.gz';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(packed)
   hops.append({'request_url':url,'request_method':'GET','request_headers':request_headers,'retrieved_at_utc':now,'response_url':final,'status':status,'response_headers':headers,'body_path':str(p.relative_to(HERE)),'raw_sha256':sha(body),'stored_sha256':sha(packed),'raw_bytes':len(body),'stored_bytes':len(packed),'storage':'gzip of complete response entity; Accept-Encoding identity requested; no decoding transformation'})
   if status in [301,302,303,307,308] and location:url=urllib.parse.urljoin(url,location);continue
   break
  except Exception as e:
   hops.append({'request_url':url,'request_headers':request_headers,'retrieved_at_utc':now,'status':None,'error_type':type(e).__name__,'error':str(e),'body_path':None});break
 rec={'id':id,'requested_url':initial,'parent_source':parent,'hops':hops,'final_url':url,'source_status':'as published; no status inferred solely from HTTP','retrieval_clock':'UTC'}
 (HERE/'source/acquired'/f'{id}.receipt.json').write_text(json.dumps(rec,indent=2)+'\n')
 print(id,hops[-1].get('status'),hops[-1].get('raw_bytes'),url,flush=True)
 return rec
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('id');p.add_argument('url');p.add_argument('--parent');a=p.parse_args();acquire(a.id,a.url,a.parent)
