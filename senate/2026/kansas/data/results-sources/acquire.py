#!/usr/bin/env python3
"""Public read-only HTTP capture. Writes only this owned evidence directory.
python3 acquire.py tasks.json; tasks are explicit observed URLs, never guessed IDs.
"""
import concurrent.futures,datetime,gzip,hashlib,json,pathlib,sys,threading,urllib.parse
import requests
from bs4 import BeautifulSoup
ROOT=pathlib.Path(__file__).resolve().parent
STATE=ROOT.parent.parent
LOCK=threading.Lock()
def sha(b): return hashlib.sha256(b).hexdigest()
def writej(p,j): p.write_text(json.dumps(j,indent=2,ensure_ascii=False)+'\n')
def shared_index():
 out={}
 for p in STATE.rglob('*.gz'):
  if ROOT in p.parents: continue
  try:
   b=gzip.decompress(p.read_bytes()); out.setdefault(sha(b),p)
  except Exception: pass
 for p in (ROOT/'raw').glob('*.gz'):
  try: out.setdefault(sha(gzip.decompress(p.read_bytes())),p)
  except Exception: pass
 return out
INDEX=shared_index()
def body(meta):
 p=ROOT/meta['body_path']
 return gzip.decompress(p.read_bytes())
def fetch(t):
 mid=t['id']; mp=ROOT/'raw'/f'{mid}.meta.json'
 if mp.exists() and not t.get('refetch'): return json.loads(mp.read_text())
 m={**t,'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'body_semantics':'complete HTTP entity after requests Content-Encoding decoding; no truncation; error bodies retained','source_time':None,'source_timezone':None,'source_status':None}
 try:
  r=requests.get(t['url'],timeout=(15,50),headers={'User-Agent':'Mozilla/5.0 (compatible; public election research)','Accept-Encoding':'identity'})
  b=r.content
  m.update(status=r.status_code,requested_url=t['url'],final_url=r.url,headers=dict(r.headers),redirects=[{'url':h.url,'status':h.status_code,'headers':dict(h.headers)} for h in r.history],original_sha256=sha(b),original_bytes=len(b),content_encoding=r.headers.get('Content-Encoding','identity'))
  with LOCK:
   p=INDEX.get(sha(b))
   if p is None:
    p=ROOT/'raw'/f'{mid}.body.gz'; z=gzip.compress(b,mtime=0)
    if len(z)>=40000000: raise ValueError('stored artifact exceeds exclusive bound; exact ordered split required')
    p.write_bytes(z); INDEX[sha(b)]=p
   m.update(body_path=pathlib.os.path.relpath(p,ROOT),stored_sha256=sha(p.read_bytes()),stored_bytes=p.stat().st_size,reuse=ROOT not in p.parents)
  if 'html' in r.headers.get('Content-Type','').lower() or b.lstrip().lower().startswith((b'<!doctype html',b'<html')):
   s=BeautifulSoup(b,'html.parser'); links=[]
   for i,a in enumerate(s.find_all(['a','iframe','script','link'])):
    attr='href' if a.name in ['a','link'] else 'src'
    if a.get(attr): links.append({'position':i,'tag':a.name,'label':a.get_text(' ',strip=True),'literal':a[attr],'url':urllib.parse.urljoin(r.url,a[attr])})
   writej(ROOT/'extracts'/f'{mid}.links.json',links)
   for x in s(['script','style']): x.decompose()
   (ROOT/'extracts'/f'{mid}.txt').write_text(s.get_text('\n',strip=True))
   m['title']=s.title.get_text(' ',strip=True) if s.title else None
  elif b.startswith(b'%PDF'):
   import subprocess
   q=ROOT/'extracts'/f'{mid}.pdf';q.write_bytes(b)
   subprocess.run(['pdftotext','-layout',str(q),str(q.with_suffix('.txt'))],check=True)
   q.unlink()
 except Exception as e: m['error']=repr(e)
 writej(mp,m); return m
if __name__=='__main__':
 tasks=json.loads(pathlib.Path(sys.argv[1]).read_text())
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  for m in pool.map(fetch,tasks): print(m['id'],m.get('status'),m.get('original_bytes'),m.get('title'),m.get('error',''))
