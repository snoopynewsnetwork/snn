#!/usr/bin/env python3
"""Bounded public GET acquisition, explicit observed URLs only; no endpoint generation.
Use: python3 acquire.py request-plan.json. Offline build never imports this module.
"""
import urllib.parse
import concurrent.futures,datetime,gzip,hashlib,json,sys,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parent; STATE=ROOT.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 plan=json.loads(Path(sys.argv[1]).read_text()); receipts=ROOT/'acquisition.json'; old=json.loads(receipts.read_text()) if receipts.exists() else []
 known={x['id'] for x in old}; plan=[x for x in plan if x['id'] not in known]
 # Reference existing exact originals instead of storing duplicates.
 pool={}
 for directory in ['turnout/source','baselines/source','news']:
  for p in (STATE/'data'/directory).glob('*.gz'):
   try:
    raw=gzip.decompress(p.read_bytes());pool.setdefault(sha(raw),p.relative_to(STATE).as_posix())
   except (OSError,EOFError):pass
 def fetch(q):
  r=dict(q,method='GET',request_body=None,retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),redirects=[])
  class Redirect(urllib.request.HTTPRedirectHandler):
   def redirect_request(self,req,fp,code,msg,headers,newurl):
    r['redirects'].append({'url':req.full_url,'status':code,'headers':dict(headers),'location':newurl});return super().redirect_request(req,fp,code,msg,headers,newurl)
  opener=urllib.request.build_opener(Redirect())
  request_url=urllib.parse.quote(q['url'],safe=":/?&=%#[]@!$'()*+,;~-._")
  r['requested_url']=request_url
  req=urllib.request.Request(request_url,headers={'User-Agent':'Mozilla/5.0 (public election source research)','Accept-Encoding':'identity'})
  try:
   try: response=opener.open(req,timeout=30)
   except urllib.error.HTTPError as e: response=e
   with response:
    raw=response.read();r.update(status=response.code,final_url=response.url,headers=dict(response.headers),error=None)
  except Exception as e:
   raw=b'';r.update(status=None,final_url=q['url'],headers={},error=type(e).__name__+': '+str(e))
  r.update(raw_bytes=len(raw),raw_sha256=sha(raw),entity_definition='Complete urllib bytes including any HTTP Content-Encoding; outer gzip separate; no truncation')
  return r,raw
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
  for r,raw in ex.map(fetch,plan):
   h=sha(raw)
   if raw:
    path=pool.get(h)
    if path is None:
     p=ROOT/'source'/f'{h}.body.gz';p.parent.mkdir(exist_ok=True);p.write_bytes(gzip.compress(raw,mtime=0));path=p.relative_to(STATE).as_posix();pool[h]=path
    p=STATE/path;r.update(body_path=path,stored_bytes=p.stat().st_size,stored_sha256=sha(p.read_bytes()))
   else:r.update(body_path=None,stored_bytes=0,stored_sha256=None)
   old.append(r); print(r['id'],r['status'],r['raw_bytes'],r['final_url'],flush=True)
   receipts.write_text(json.dumps(old,indent=2,ensure_ascii=False)+'\n')
if __name__=='__main__':main()
