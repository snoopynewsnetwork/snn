#!/usr/bin/env python3
"""Retain HTTP entity bytes losslessly, headers and redirect chain. No response truncation."""
import concurrent.futures,datetime,gzip,hashlib,json,pathlib,urllib.request,urllib.error,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]; OUT=ROOT/'source'
def sha(b): return hashlib.sha256(b).hexdigest()
class Redirects(urllib.request.HTTPRedirectHandler):
 def __init__(self):self.chain=[]
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  self.chain.append({'url':req.full_url,'status':code,'headers':dict(headers),'location':newurl})
  return super().redirect_request(req,fp,code,msg,headers,newurl)
def fetch(r):
 target=OUT/(r['id']+'.body.gz');meta=OUT/(r['id']+'.http.json')
 if target.exists() and meta.exists():return json.loads(meta.read_text())
 handler=Redirects();opener=urllib.request.build_opener(handler);start=datetime.datetime.now(datetime.timezone.utc).isoformat()
 try:
  data=r.get('post_data');req=urllib.request.Request(r['url'],data=data.encode() if data is not None else None,headers={'User-Agent':'Mozilla/5.0 (election historical research)','Accept-Encoding':'identity'})
  try:res=opener.open(req,timeout=90)
  except urllib.error.HTTPError as e:res=e
  b=res.read();stored=gzip.compress(b,mtime=0)
  if len(stored)>=40000000: raise RuntimeError('Asset must be split losslessly before storage')
  target.write_bytes(stored)
  m={**r,'retrieved_at_utc':start,'completed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':res.code,'final_url':res.geturl(),'headers':dict(res.headers),'redirects':handler.chain,'entity_bytes':len(b),'raw_sha256':sha(b),'stored_bytes':len(stored),'stored_sha256':sha(stored),'asset':str(target.relative_to(ROOT)),'byte_scope':'HTTP entity bytes returned by urllib; Accept-Encoding: identity; gzip storage mtime=0'}
 except Exception as e:m={**r,'retrieved_at_utc':start,'error':str(e),'redirects':handler.chain}
 meta.write_text(json.dumps(m,indent=2)+'\n');return m
if __name__=='__main__':
 rs=json.loads(pathlib.Path(sys.argv[1]).read_text())
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for m in pool.map(fetch,rs):print(m['id'],m.get('status',m.get('error')),m.get('entity_bytes'))
