"""Map-only complete entity storage and explicit public HTTP observations."""
from pathlib import Path
import gzip,hashlib,json,datetime,urllib.request,urllib.error,urllib.parse
S=Path(__file__).resolve().parents[1]; M=S/'maps'
def sha(b):return hashlib.sha256(b).hexdigest()
def write(p,o):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def pin(p):
 b=p.read_bytes();return {'path':str(p.relative_to(S)),'bytes':len(b),'sha256':sha(b)}
def store(b,typ=''):
 h=sha(b); base=M/'originals';base.mkdir(exist_ok=True)
 # Direct PDF/ZIP for offline use; huge bodies use exact ordered byte chunks.
 ext='.pdf' if b.startswith(b'%PDF-') else '.zip' if b.startswith(b'PK\x03\x04') else '.gz'
 if len(b)<40000000:
  z=gzip.compress(b,mtime=0)if ext=='.gz' else b
  p=base/(h+ext)
  if not p.exists():p.write_bytes(z)
  return dict(**pin(p),raw_bytes=len(b),raw_sha256=h,encoding='gzip' if ext=='.gz' else 'identity')
 parts=[]
 for i,start in enumerate(range(0,len(b),25000000)):
  q=b[start:start+25000000];z=gzip.compress(q,mtime=0);p=base/(h+f'.part{i+1:04d}.gz');p.write_bytes(z)
  parts.append(dict(**pin(p),raw_bytes=len(q),raw_sha256=sha(q),encoding='gzip',byte_offset=start))
 return dict(raw_bytes=len(b),raw_sha256=h,encoding='ordered_exact_byte_parts',parts=parts)
def body(ref):
 if ref['encoding']=='ordered_exact_byte_parts':b=b''.join(body(p)for p in ref['parts'])
 else:
  z=(S/ref['path']).read_bytes();assert len(z)==ref['bytes']and sha(z)==ref['sha256'];b=gzip.decompress(z)if ref['encoding']=='gzip'else z
 assert len(b)==ref['raw_bytes']and sha(b)==ref['raw_sha256'];return b
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*a,**k):return None
opener=urllib.request.build_opener(NoRedirect())
def fetch(name,url,parent=None,basis=None,timeout=50):
 p=M/'receipts'/(name+'.json')
 if p.exists():return json.loads(p.read_bytes())
 r=dict(id=name,requested_url=url,parent=parent,discovery_basis=basis,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),requests=[],publisher_time=None,publisher_timezone=None)
 cur=url
 for hop in range(9):
  headers={'User-Agent':'Public election geographic research; bounded originals','Accept-Encoding':'identity'}
  wire=urllib.parse.quote(cur,safe=":/?&=%#+@,;!$'()*[]");req=urllib.request.Request(wire,headers=headers);event={'url':cur,'wire_url':wire,'method':'GET','request_headers':dict(req.header_items())}
  try:
   try:res=opener.open(req,timeout=timeout)
   except urllib.error.HTTPError as e:res=e
   with res:
    event.update(status=res.code,response_headers=list(res.headers.items()),response_url=res.geturl());b=res.read();event['body']=store(b)
   r['requests'].append(event)
   if event['status']in (301,302,303,307,308)and res.headers.get('Location'):
    event['location_literal']=res.headers['Location'];cur=urllib.parse.urljoin(cur,event['location_literal']);continue
   r.update(status=event['status'],final_url=cur,body=event['body'],error=None);break
  except Exception as e:
   event['error']=repr(e);r['requests'].append(event);r.update(status=None,final_url=cur,error=repr(e));break
 else:r['error']='bounded redirect limit'
 r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();write(p,r);return r
def original(name):
 r=json.loads((M/'receipts'/(name+'.json')).read_bytes());return body(r['body'])if r.get('body')else b''
class Document(__import__('html.parser',fromlist=['HTMLParser']).HTMLParser):
 def __init__(self,b):
  super().__init__(convert_charrefs=True);self.nodes=[];self.stack=[];self.feed(b.decode('utf-8-sig',errors='replace'))
 def handle_starttag(self,tag,attrs):
  n={'tag':tag,'attrs':dict(attrs),'text':'','parent':self.stack[-1]if self.stack else None,'position':self.getpos()};self.nodes.append(n)
  if tag not in ('area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'):self.stack.append(len(self.nodes)-1)
 def handle_endtag(self,tag):
  for i in range(len(self.stack)-1,-1,-1):
   if self.nodes[self.stack[i]]['tag']==tag:self.stack=self.stack[:i];break
 def handle_data(self,data):
  for i in self.stack:self.nodes[i]['text']+=data
 def descendants(self,i):
  out=[]
  for k,n in enumerate(self.nodes):
   p=n['parent']
   while p is not None:
    if p==i:out.append(n);break
    p=self.nodes[p]['parent']
  return out
def document(name):return Document(original(name))
def links(name):
 r=json.loads((M/'receipts'/(name+'.json')).read_bytes());d=document(name)
 return [dict(text=' '.join(n['text'].split()),href=n['attrs']['href'],url=urllib.parse.urljoin(r['final_url'],n['attrs']['href']),attrs=n['attrs'],position=n['position'])for n in d.nodes if n['tag']=='a'and n['attrs'].get('href')]
