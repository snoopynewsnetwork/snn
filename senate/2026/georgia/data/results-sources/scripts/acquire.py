#!/usr/bin/env python3
"""Append-only public acquisition. Exact entity bytes, including failures; no live IDs guessed."""
import argparse,concurrent.futures,datetime,gzip,hashlib,json,pathlib,urllib.request,urllib.error
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def fetch(q):
 receipts=ROOT/'raw'/q['id']; meta=receipts.with_suffix('.http.json')
 if meta.exists():return json.loads(meta.read_text())
 redirects=[]
 class Redirect(urllib.request.HTTPRedirectHandler):
  def redirect_request(self,req,fp,code,msg,headers,newurl):
   redirects.append({'url':req.full_url,'status':code,'headers':dict(headers),'location':newurl})
   return super().redirect_request(req,fp,code,msg,headers,newurl)
 start=datetime.datetime.now(datetime.timezone.utc).isoformat()
 r={**q,'retrieved_at_utc':start,'redirects':redirects,'byte_scope':'HTTP entity after transfer decoding; Accept-Encoding identity'}
 try:
  req=urllib.request.Request(q['url'],headers={'User-Agent':'Mozilla/5.0 (public election research)','Accept-Encoding':'identity'})
  try:res=urllib.request.build_opener(Redirect).open(req,timeout=35)
  except urllib.error.HTTPError as e:res=e
  with res:b=res.read();r.update(status=res.code,final_url=res.geturl(),headers=dict(res.headers))
  packed=gzip.compress(b,mtime=0);assert len(packed)<40000000
  # Reuse exact successful original entities already retained by other Georgia researchers.
  refs=json.loads((ROOT/'shared-inputs.json').read_text()) if (ROOT/'shared-inputs.json').exists() else []
  same=next((x for x in refs if x.get('raw_sha256')==sha(b)),None)
  if same:r.update(shared_path=same['path'],stored_bytes=same['stored_bytes'],stored_sha256=same['stored_sha256'])
  else:
   body=receipts.with_suffix('.body.gz');body.write_bytes(packed)
   r.update(path=str(body.relative_to(ROOT)),stored_bytes=len(packed),stored_sha256=sha(packed))
  r.update(raw_bytes=len(b),raw_sha256=sha(b))
 except Exception as e:r.update(status=None,error=repr(e))
 r['completed_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save(meta,r);return r
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--ids',nargs='*');args=ap.parse_args()
 qs=json.loads((ROOT/'requests.json').read_text());qs=[q for q in qs if not args.ids or q['id'] in args.ids]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
  for r in ex.map(fetch,qs):print(r['id'],r.get('status'),r.get('raw_bytes'),r.get('error',''),flush=True)
