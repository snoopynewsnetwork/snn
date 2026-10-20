"""Owned, bounded public evidence and deterministic lossless JSON helpers."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin
import csv,gzip,hashlib,io,json,re,datetime,requests
HERE=Path(__file__).resolve().parent
STATE=HERE.parent.parent
ACCEPTANCE=STATE/'data/coordinator-priority-acceptance.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def encode(x):return (json.dumps(x,ensure_ascii=False,sort_keys=True,allow_nan=False,separators=(',',':'))+'\n').encode()
def write(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(encode(x))
def gzwrite(p,b):Path(p).write_bytes(gzip.compress(b,mtime=0))
def parsefile(p):
 p=Path(p);b=p.read_bytes()
 if p.suffix=='.gz':b=gzip.decompress(b);p=p.with_suffix('')
 if p.suffix=='.csv':return list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))
 if p.suffix=='.jsonl':return [json.loads(v) for v in b.splitlines() if v]
 return json.loads(b)
def sem(x):return sha(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode())
def pointer(x,p):
 if not p:return x
 for part in p[1:].split('/'):
  part=part.replace('~1','/').replace('~0','~');x=x[int(part)] if isinstance(x,list) else x[part]
 return x
class HTML(HTMLParser):
 def __init__(self,s):
  super().__init__(convert_charrefs=True);self.links=[];self.scripts=[];self.inputs=[];self.selects=[];self.rows=[];self.text=[];self._a=None;self._sel=None;self._opt=None;self._row=None;self._cell=None;self.feed(s)
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t in ('a','iframe') and ('href' in a or 'src' in a):self._a={'tag':t,'attrs':a,'literal_href':a.get('href',a.get('src')),'text':''};self.links.append(self._a)
  if t=='script':self.scripts.append(a)
  if t=='input':self.inputs.append(a)
  if t=='select':self._sel={'attrs':a,'options':[]};self.selects.append(self._sel)
  if t=='option' and self._sel is not None:self._opt={'attrs':a,'text':''};self._sel['options'].append(self._opt)
  if t=='tr':self._row={'attrs':a,'cells':[]};self.rows.append(self._row)
  if t in ('td','th') and self._row is not None:self._cell={'tag':t,'attrs':a,'text':'','links':[]};self._row['cells'].append(self._cell)
  if t=='a' and self._cell is not None:self._cell['links'].append(a)
 def handle_endtag(self,t):
  if t in ('a','iframe'):self._a=None
  if t=='select':self._sel=None
  if t=='option':self._opt=None
  if t in ('td','th'):self._cell=None
  if t=='tr':self._row=None
 def handle_data(self,d):
  self.text.append(d)
  for o in [self._a,self._opt,self._cell]:
   if o is not None:o['text']+=d
 def summary(self):return dict(links=self.links,scripts=self.scripts,selects=self.selects,inputs=self.inputs,rows=self.rows,text=' '.join(self.text))
def fetch(id,url,parent=None,literal_href=None,method='GET',data=None,basis=None,limit=15000000):
 """One attempt; no retry/challenge workaround. Complete decoded entities or explicit failure."""
 from boundary_guard import allowed_public_url
 if not allowed_public_url(url):raise ValueError('navigation outside bounded public research scope: '+url)
 receipt=HERE/'receipts'/f'{id}.json'
 if receipt.exists():return json.loads(receipt.read_bytes())
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();r=None
 meta=dict(id=id,url=url,parent=parent,literal_href=literal_href,discovery_basis=basis,method=method,request_body=data,request_headers={'User-Agent':'Mozilla/5.0 (public election research; bounded requests)','Accept-Encoding':'gzip, deflate'},retrieved_at_utc=start,byte_scope='complete requests-decoded response entity; headers retain transport encodings',limit_bytes=limit)
 try:
  r=requests.request(method,url,data=data,headers=meta['request_headers'],timeout=(10,25),stream=True)
  meta.update(status=r.status_code,final_url=r.url,headers=list(r.raw.headers.items()),redirects=[dict(url=h.url,status=h.status_code,headers=list(h.raw.headers.items()),body_hex=h.content.hex()) for h in r.history])
  b=bytearray()
  for c in r.iter_content(65536):
   b.extend(c)
   if len(b)>limit:raise ValueError('bounded response exceeded limit; partial body not admitted')
  b=bytes(b);z=gzip.compress(b,mtime=0);p=HERE/'raw'/f'{id}-{sha(b)[:16]}.gz';p.write_bytes(z)
  meta.update(raw_bytes=len(b),raw_sha256=sha(b),stored_bytes=len(z),stored_sha256=sha(z),path=str(p.relative_to(STATE)),complete=True)
 except Exception as e:meta.update(error=str(e),complete=False)
 finally:
  if r is not None:r.close()
 meta['finished_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();write(receipt,meta);return meta
def body(m):return gzip.decompress((STATE/m['path']).read_bytes()) if m.get('complete') else b''
def inspect(m):
 b=body(m)
 if b.startswith((b'%PDF',b'PK',b'\x89PNG',b'\xff\xd8')):
  h=HTML('');gzwrite(HERE/'parsed'/f"{m['id']}.json.gz",encode(dict(format='binary artifact; complete raw body retained',raw_path=m.get('path'),links=[],scripts=[],selects=[],inputs=[],rows=[],text='')));return h
 s=b.decode('utf-8',errors='replace');h=HTML(s);gzwrite(HERE/'parsed'/f"{m['id']}.json.gz",encode(h.summary()));return h
if __name__=='__main__':
 import sys
 m=fetch(sys.argv[1],sys.argv[2],basis='explicit source URL supplied to bounded helper');print(json.dumps({k:v for k,v in m.items() if k not in ['headers','request_headers']}))
