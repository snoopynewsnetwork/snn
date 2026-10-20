"""Standard-library provenance and literal HTML helpers. No network during build."""
from pathlib import Path
import csv,datetime,gzip,hashlib,html,io,json,re,ssl,urllib.request,urllib.error
from html.parser import HTMLParser
D=Path(__file__).resolve().parents[1]
STATE=D.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
class Page(HTMLParser):
 def __init__(self,b):
  super().__init__(convert_charrefs=True);self.links=[];self.tables=[];self.rows=[];self.cells=[];self.text=[];self.scripts={};self.stack=[];self.skip=0;self.link=None;self.cell=None;self.script=None;self.feed(b.decode('utf-8-sig',errors='replace'))
 def handle_starttag(self,t,a):
  a=dict(a)
  if t in ('script','style'):self.skip+=1
  if t=='script':self.script=a.get('id');self.scripts.setdefault(self.script,[])
  if t=='a':self.link=[a.get('href',''),[]]
  if t=='table':self.stack.append(self.rows);self.rows=[]
  if t=='tr':self.cells=[]
  if t in ('td','th'):self.cell=[]
 def handle_data(self,s):
  if self.script is not None:self.scripts[self.script].append(s)
  if not self.skip:self.text.append(s)
  if self.link is not None:self.link[1].append(s)
  if self.cell is not None:self.cell.append(s)
 def handle_endtag(self,t):
  if t=='a' and self.link:self.links.append((self.link[0],' '.join(''.join(self.link[1]).split())));self.link=None
  if t in ('td','th')and self.cell is not None:self.cells.append(' '.join(''.join(self.cell).split()));self.cell=None
  if t=='tr' and self.cells:self.rows.append(self.cells)
  if t=='table':self.tables.append(self.rows);self.rows=self.stack.pop()if self.stack else []
  if t in ('script','style'):self.skip=max(0,self.skip-1);self.script=None
 def plain(self):return ' '.join(' '.join(self.text).split())
 def next(self):return json.loads(''.join(self.scripts['__NEXT_DATA__']))
def manifest():return json.loads((D/'acquisition.json').read_text())if(D/'acquisition.json').exists()else []
def body(id):
 r=next(x for x in manifest()if x['id']==id);p=STATE/r['asset'];s=p.read_bytes();assert sha(s)==r['stored_sha256'];b=gzip.decompress(s)if r.get('compression')=='gzip'else s;assert sha(b)==r['raw_sha256']and len(b)==r['bytes'];return b
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*a,**k):return None
opener=urllib.request.build_opener(NoRedirect)
def acquire(id,url,parent=None,basis=None,referer=None):
 old=next((r for r in manifest()if r['id']==id),None)
 if old:assert old['url']==url;return body(id)
 records=manifest();chain=[];u=url
 for n in range(10):
  h={'User-Agent':'Mozilla/5.0 (compatible; election-history-research)'}
  if referer:h['Referer']=referer
  at=datetime.datetime.now(datetime.timezone.utc).isoformat();req=urllib.request.Request(u,headers=h)
  try:r=opener.open(req,timeout=50)
  except urllib.error.HTTPError as e:r=e
  b=r.read();s=gzip.compress(b,mtime=0);digest=sha(b)
  # Exact hash reuse, including shared originals, avoids duplicate entities.
  asset=None
  candidates=records+json.loads((STATE/'data/news/manifest.json').read_text())
  for q in candidates:
   if q.get('raw_sha256')==digest:
    pp=STATE/q['asset']if q in records else STATE/'data/news'/q['asset']
    if pp.exists():asset=str(pp.relative_to(STATE));s=pp.read_bytes();break
  if asset is None:
   asset='data/turnout/source/'+digest+'.gz';(STATE/asset).write_bytes(s)
  assert len(s)<40_000_000
  one=dict(url=u,retrieved_at_utc=at,status=r.code,headers=dict(r.headers.items()),request_headers=h,bytes=len(b),raw_sha256=digest,asset=asset,stored_sha256=sha(s),stored_bytes=len(s),compression='gzip')
  chain.append(one)
  if r.code not in (301,302,303,307,308):break
  u=urllib.parse.urljoin(u,r.headers['Location'])
 else:raise ValueError('redirect bound')
 row=dict(id=id,url=url,final_url=u,parent_source_id=parent,discovery_basis=basis,redirects=chain[:-1],**{k:v for k,v in chain[-1].items()if k!='url'})
 records.append(row);dump(D/'acquisition.json',records);print(id,r.code,len(b),flush=True);return b
def reuse(id):
 if any(r['id']==id for r in manifest()):return body(id)
 m=next(r for r in json.loads((STATE/'data/news/manifest.json').read_text())if r['id']==id);s=(STATE/'data/news'/m['asset']).read_bytes();b=gzip.decompress(s);assert sha(b)==m['raw_sha256']and sha(s)==m['stored_sha256'];r=dict(m);r['asset']='data/news/'+m['asset'];r['compression']='gzip';r['stored_bytes']=len(s);r['reuse']='Read-only original entity, exact hash; independently parsed by turnout worker';records=manifest();records.append(r);dump(D/'acquisition.json',records);return b
