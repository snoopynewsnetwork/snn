#!/usr/bin/env python3
"""Bounded explicit-URL acquisition. No ID discovery/guessing or background collector."""
import argparse, concurrent.futures, datetime, gzip, hashlib, json, pathlib, re, time
from urllib.parse import urljoin
import requests
from html.parser import HTMLParser
class Links(HTMLParser):
 def __init__(self): super().__init__();self.links=[];self.active=None
 def handle_starttag(self,tag,attrs):
  a=dict(attrs);href=a.get("href") or a.get("src")
  if tag in ["a","iframe","script","link"] and href:
   self.active={"tag":tag,"literal":href,"text":""};self.links.append(self.active)
 def handle_data(self,data):
  if self.active:self.active["text"]+=data
 def handle_endtag(self,tag):
  if tag in ["a","iframe","script","link"]:self.active=None
ROOT=pathlib.Path(__file__).resolve().parent; STATE=ROOT.parent
LIMIT=39_000_000

def sha(b): return hashlib.sha256(b).hexdigest()
def save_json(p,j): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
def fetch(spec):
 ident=spec['id'];rp=ROOT/'receipts'/f'{ident}.json'
 if rp.exists(): return json.loads(rp.read_text())
 now=datetime.datetime.now(datetime.timezone.utc).isoformat();start=time.monotonic()
 try:
  r=requests.get(spec['url'],timeout=(20,90),headers={'User-Agent':'Nebraska election geography research; bounded public original acquisition','Accept-Encoding':'gzip, deflate'},allow_redirects=True)
  b=r.content;status=r.status_code;headers=dict(r.headers);final=r.url;redirects=[{'url':x.url,'status':x.status_code,'headers':dict(x.headers)} for x in r.history];error=None
 except requests.RequestException as e:
  b=str(e).encode();status=None;headers={};final=None;redirects=[];error=str(e)
 is_pdf=b.startswith(b'%PDF') and len(b)<40_000_000
 packed=b if is_pdf else gzip.compress(b,mtime=0);pieces=[]
 for i in range(0,len(packed),LIMIT):
  dest=ROOT/'raw'/f'{ident}-{sha(b)[:12]}.{"pdf" if is_pdf else "gz"}{(".part%03d"%(i//LIMIT)) if len(packed)>LIMIT else ""}'
  dest.parent.mkdir(parents=True,exist_ok=True);p=packed[i:i+LIMIT];dest.write_bytes(p);pieces.append({'path':str(dest.relative_to(STATE)),'bytes':len(p),'sha256':sha(p)})
 links=[]
 if 'html' in headers.get('Content-Type','').lower() or b.lstrip().startswith(b'<!'):
  parser=Links();parser.feed(b.decode('utf-8','replace'))
  links=[{**x,'text':x['text'].strip(),'url':urljoin(final or spec['url'],x['literal'])} for x in parser.links]
 receipt={**spec,'requested_url':spec['url'],'method':'GET','retrieved_utc':now,'elapsed_seconds':round(time.monotonic()-start,3),'status':status,'final_url':final,'redirects':redirects,'headers':headers,'transport_error':error,'source_date_status_timezone':'See complete entity and HTTP headers; HTTP dates are not election-effective dates.','entity_representation':'Complete requests-decoded entity; original PDFs stored identity, other entities losslessly gzip compressed. HTTP content-encoding and length retained separately. Transport error text is not an HTTP response.','original_bytes':len(b),'original_sha256':sha(b),'storage_encoding':'identity' if is_pdf else 'gzip','storage':pieces,'literal_links':links}
 save_json(rp,receipt);return receipt

def body(receipt):
 b=b''.join((STATE/x['path']).read_bytes() for x in receipt['storage']);return b if receipt.get('storage_encoding')=='identity' else gzip.decompress(b)
def main():
 p=argparse.ArgumentParser();p.add_argument('queue');p.add_argument('--workers',type=int,default=3);args=p.parse_args();q=json.loads(pathlib.Path(args.queue).read_text())
 with concurrent.futures.ThreadPoolExecutor(max_workers=min(args.workers,4)) as pool:
  for r in pool.map(fetch,q):print(r['id'],r['status'],r['original_bytes'])
if __name__=='__main__':main()
