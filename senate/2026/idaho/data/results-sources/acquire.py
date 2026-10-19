#!/usr/bin/env python3
"""Bounded public GET acquisition; no guessed URLs/IDs and no polling loop."""
import argparse, concurrent.futures, datetime, gzip, hashlib, json
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
D=Path(__file__).resolve().parent

def sha(b): return hashlib.sha256(b).hexdigest()
def dump(p,x):
 b=(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode(); assert len(b)<40000000
 if p.exists(): assert p.read_bytes()==b, p
 else: p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
def acquire(job):
 p=D/'receipts'/f"{job['id']}.json"
 if p.exists(): return json.loads(p.read_bytes())
 t=datetime.datetime.now(datetime.timezone.utc).isoformat()
 receipt=dict(schema='idaho-official-acquisition-v1',**job,requested_url=job['url'],retrieved_utc=t,method='GET',request_headers={'User-Agent':'Idaho2026Research/1.0 (bounded public source inspection)','Accept-Encoding':'identity'},timeout_seconds=35)
 try:
  r=requests.get(job['url'],headers=receipt['request_headers'],timeout=35)
  body=r.content; packed=gzip.compress(body,mtime=0); assert len(packed)<40000000
  rel='bodies/'+sha(body)+'.gz'; dest=D/rel
  dest.parent.mkdir(exist_ok=True)
  if dest.exists(): assert gzip.decompress(dest.read_bytes())==body
  else: dest.write_bytes(packed)
  receipt.update(final_url=r.url,http_status=r.status_code,response_headers=list(r.raw.headers.items()),redirects=[{'url':q.url,'http_status':q.status_code,'headers':list(q.raw.headers.items())} for q in r.history],raw_bytes=len(body),raw_sha256=sha(body),stored_path=rel,stored_bytes=dest.stat().st_size,stored_sha256=sha(dest.read_bytes()),body_encoding=r.encoding,transport_decoding='requests entity body; Accept-Encoding identity requested; gzip storage is lossless')
  ct=r.headers.get('content-type','')
  if 'html' in ct or body.lstrip().startswith(b'<!'):
   soup=BeautifulSoup(body,'html.parser'); receipt['title']=soup.title.get_text(' ',strip=True) if soup.title else None
   receipt['links']=[dict(href=a.get('href'),text=a.get_text(' ',strip=True),url=urljoin(r.url,a['href'])) for a in soup.find_all('a',href=True)]
   receipt['scripts']=[dict(attributes=dict(a.attrs),url=urljoin(r.url,a['src']) if a.get('src') else None) for a in soup.find_all('script')]
   receipt['frames']=[dict(attributes=dict(a.attrs),url=urljoin(r.url,a['src']) if a.get('src') else None) for a in soup.find_all(['iframe','embed'])]
 except Exception as e: receipt.update(final_url=None,http_status=None,error_type=type(e).__name__,error=str(e),response_headers=[],redirects=[])
 receipt['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();dump(p,receipt)
 return receipt

def main():
 ap=argparse.ArgumentParser();ap.add_argument('jobs');ns=ap.parse_args();jobs=json.loads(Path(ns.jobs).read_bytes())
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
  for r in ex.map(acquire,jobs): print(r['id'],r.get('http_status'),r.get('raw_bytes'),(r.get('title') or '')[:100],r.get('error','')[:120],flush=True)
if __name__=='__main__':main()
