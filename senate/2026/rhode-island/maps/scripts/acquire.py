"""Explicit public GET/POST capture. Redirects retained individually; no authentication."""
from common import *
import urllib.request,urllib.error,urllib.parse,datetime,ssl,socket
from html.parser import HTMLParser
class Links(HTMLParser):
 def __init__(self,b):super().__init__();self.rows=[];self.tag=None;self.feed(b.decode('utf-8','replace'))
 def handle_starttag(self,t,a):
  d=dict(a)
  for k in ('href','src'):
   if k in d:self.rows.append(dict(tag=t,attribute=k,url=d[k]))
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*a):return None
opener=urllib.request.build_opener(NoRedirect())
def fetch(name,url,parent=None,body=None,method='GET'):
 target=M/'requests'/f'{name}.json'
 if target.exists():return parsed(target)
 literal_url=url
 url=urllib.parse.quote(url,safe=':/?&=%#@+;,[]')
 headers={'User-Agent':'RhodeIslandHistoricalMapsResearch/1.0','Accept':'*/*','Accept-Encoding':'identity'}
 if body is not None:headers['Content-Type']='application/x-www-form-urlencoded'
 rec=dict(id=name,parent=parent,requested_url=url,literal_url=literal_url,request_method=method,configured_headers=headers,request_body=body,utc_start=datetime.datetime.now(datetime.timezone.utc).isoformat(),hops=[])
 current=url
 for hop in range(8):
  row=dict(url=current,method=method,utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
  if any(s in urllib.parse.urlparse(current).path.lower() for s in ('/login','/signin','/challenge','/oauth','/authorize')):
   row['stopped']='unexpected authentication/challenge redirect';rec['hops'].append(row);break
  try:
   req=urllib.request.Request(current,data=body.encode() if body is not None else None,headers=headers,method=method)
   try:r=opener.open(req,timeout=65)
   except urllib.error.HTTPError as e:r=e
   b=r.read();row.update(status=r.code,headers=list(r.headers.items()),raw_bytes=len(b),raw_sha256=sha(b),parts=[])
   for i,start in enumerate(range(0,len(b),32000000)):
    raw=b[start:start+32000000];z=gzip.compress(raw,mtime=0);assert len(z)<40000000
    path=Path('originals')/(sha(z)+'.gz');(M/path).parent.mkdir(parents=True,exist_ok=True)
    if not (M/path).exists():(M/path).write_bytes(z)
    row['parts'].append(dict(path=str(path),stored_bytes=len(z),stored_sha256=sha(z),raw_bytes=len(raw),raw_sha256=sha(raw),part=i))
   sample=b[:100000].lower()
   row['challenge_observed']=any(s in sample for s in (b'cf-chl-',b'just a moment...',b'verify you are human'))
   row['complete_entity']=True
   rec['hops'].append(row)
   if r.code in (301,302,303,307,308):
    loc=r.headers.get('Location')
    if not loc:break
    current=urllib.parse.urljoin(current,loc)
    if r.code==303:body=None;method='GET'
    continue
   break
  except Exception as e:row['error']=repr(e);rec['hops'].append(row);break
 rec['utc_end']=datetime.datetime.now(datetime.timezone.utc).isoformat();dump(target,rec)
 return rec
def last(r):return r['hops'][-1]
def read(r):return original(last(r)) if 'parts' in last(r) else b''
def links(r):return [dict(x,url=urllib.parse.urljoin(last(r)['url'],x['url'])) for x in Links(read(r)).rows]
if __name__=='__main__':
 import sys
 r=fetch(*sys.argv[1:]);print(json.dumps(dict(id=r['id'],status=last(r).get('status'),bytes=last(r).get('raw_bytes'),error=last(r).get('error'))))

def blocked(r):
 h=last(r);b=read(r)[:100000].lower()
 return h.get('status') in (401,403) or any(k.lower()=='cf-mitigated' and v.lower()=='challenge' for k,v in h.get('headers',[])) or any(s in b for s in (b'cf-chl-',b'just a moment...',b'verify you are human')) or bool(h.get('stopped'))
