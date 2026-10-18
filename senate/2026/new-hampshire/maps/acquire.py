#!/usr/bin/env python3
"""Append-only primary response capture. See source/SCHEMA.md. No peer writes."""
import argparse,datetime,gzip,hashlib,json,pathlib,re,requests
ROOT=pathlib.Path(__file__).resolve().parent
LIMIT=30_000_000

def sha(b):return hashlib.sha256(b).hexdigest()
def fetch(id,url,parent=None,note='',kind=None):
 p=ROOT/'source'/f'{id}.meta.json'
 if p.exists():return json.loads(p.read_text())
 now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
 m=dict(id=id,requested_url=url,parent=parent,note=note,requested_utc=now(),request_headers={'User-Agent':'Election geography research; public sources','Accept-Encoding':'identity'},redirects=[])
 try:
  r=requests.get(url,headers=m['request_headers'],timeout=(20,90),allow_redirects=True)
  m.update(status=r.status_code,final_url=r.url,response_headers=dict(r.headers),redirects=[dict(url=x.url,status=x.status_code,headers=dict(x.headers)) for x in r.history])
  b=r.content
  suffix=kind or ('pdf' if b.startswith(b'%PDF-') else 'zip' if b.startswith(b'PK\x03\x04') else 'json' if b.lstrip()[:1] in (b'{',b'[') else 'xml' if b.lstrip().startswith(b'<?xml') else 'html')
  m.update(original_bytes=len(b),original_sha256=sha(b),format=suffix,content_decoding='requests content decoded per Content-Encoding; original means complete HTTP entity after decoding, not wire framing')
  # Split the original ordered byte stream only if required; compress each complete segment losslessly.
  segs=[b[i:i+LIMIT] for i in range(0,len(b),LIMIT)] or [b'']
  objects=[]
  for i,seg in enumerate(segs):
   name=f'{id}.{suffix}'+(f'.part{i:04d}.gz' if len(segs)>1 else '' if suffix in ['pdf','zip'] and len(seg)<40_000_000 else '.gz')
   path=ROOT/'source'/name;stored=gzip.compress(seg,mtime=0) if name.endswith('.gz') else seg
   assert len(stored)<40_000_000
   path.write_bytes(stored);objects.append(dict(path=str(path.relative_to(ROOT)),bytes=len(stored),sha256=sha(stored),decoded_bytes=len(seg),decoded_sha256=sha(seg),encoding='gzip' if name.endswith('.gz') else 'identity',order=i))
  m['objects']=objects
 except requests.RequestException as e:m.update(status=None,error=str(e),objects=[])
 m['completed_utc']=now();p.write_text(json.dumps(m,indent=2)+'\n')
 print(id,m.get('status'),m.get('original_bytes'),flush=True)
 return m

def body(id):
 m=json.loads((ROOT/'source'/f'{id}.meta.json').read_text());return b''.join(gzip.decompress((ROOT/x['path']).read_bytes()) if x['encoding']=='gzip' else (ROOT/x['path']).read_bytes() for x in m['objects'])

def links(id):
 from html.parser import HTMLParser
 from urllib.parse import urljoin
 class P(HTMLParser):
  def __init__(self):super().__init__();self.a=None;self.out=[]
  def handle_starttag(self,t,a):
   d=dict(a)
   if t=='a' and 'href'in d:self.a={'href':d['href'],'text':''}
  def handle_data(self,d):
   if self.a:self.a['text']+=d
  def handle_endtag(self,t):
   if t=='a'and self.a:self.out.append(self.a);self.a=None
 p=P();p.feed(body(id).decode('utf-8','replace'));m=json.loads((ROOT/'source'/f'{id}.meta.json').read_text())
 for x in p.out:x['url']=urljoin(m['final_url'],x['href'])
 (ROOT/'derived'/f'{id}-links.json').write_text(json.dumps(p.out,indent=2)+'\n');return p.out

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('id');p.add_argument('url');p.add_argument('--parent');p.add_argument('--note',default='');a=p.parse_args();fetch(a.id,a.url,a.parent,a.note)
