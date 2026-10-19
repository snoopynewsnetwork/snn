#!/usr/bin/env python3
"""Explicit public GET; immutable complete entity and individual receipt, errors retained."""
import datetime,gzip,hashlib,json,re,sys
from pathlib import Path
from urllib.parse import urljoin
import requests
from html.parser import HTMLParser
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.frames=[];self.text=[];self.current=None
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="a" and a.get("href"):self.current=dict(text="",href=a["href"]);self.links.append(self.current)
  if tag=="iframe":self.frames.append(a)
 def handle_endtag(self,tag):
  if tag=="a":self.current=None
 def handle_data(self,s):
  self.text.append(s)
  if self.current is not None:self.current["text"]+=s
MAPS=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def fetch(key,url,parent=None,href=None,purpose=None):
 receipt=MAPS/'source'/f'{key}.receipt.json'
 if receipt.exists():return json.loads(receipt.read_text())
 now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 r=requests.get(url,timeout=(15,65),headers={'User-Agent':'Public election geography research (read-only)','Accept-Encoding':'gzip, deflate'})
 b=r.content;h=sha(b);is_pdf=b.startswith(b'%PDF-')
 stored=b if is_pdf else gzip.compress(b,mtime=0)
 assert len(stored)<40000000,(url,len(stored))
 suffix='.pdf' if is_pdf else '.body.gz';asset=MAPS/'source'/f'{h}{suffix}'
 if not asset.exists():asset.write_bytes(stored)
 out=dict(id=key,requested_url=url,final_url=r.url,parent=parent,literal_href=href,constructor=None,method='GET',retrieved_utc=now,status=r.status_code,headers=dict(r.headers),redirects=[dict(url=x.url,status=x.status_code,headers=dict(x.headers)) for x in r.history],body_error=None if r.ok else b[:1000].decode(errors='replace'),raw_bytes=len(b),raw_sha256=h,stored_path=str(asset.relative_to(MAPS.parent)),stored_bytes=len(stored),stored_sha256=sha(stored),encoding='original PDF entity' if is_pdf else 'gzip of complete requests-decoded entity; HTTP encoding retained in headers',purpose=purpose,source_clock=r.headers.get('Last-Modified'),publication_status='public response; status does not establish legal approval')
 if 'html' in r.headers.get('Content-Type',''):
  soup=Parser();soup.feed(b.decode(errors='replace'));out['title']=None
  out['links']=[dict(text=a['text'].strip(),href=a['href'],url=urljoin(r.url,a['href'])) for a in soup.links]
  out['iframes']=soup.frames
  out['body_text']=' '.join(soup.text)[:120000]
 try:
  j=r.json()
  if isinstance(j,dict) and 'error' in j:out['body_error']=j['error']
 except ValueError:pass
 receipt.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');return out
if __name__=='__main__':
 x=fetch(*sys.argv[1:]);print(json.dumps({k:x.get(k) for k in ['id','status','raw_bytes','stored_path','title','body_error']}))
