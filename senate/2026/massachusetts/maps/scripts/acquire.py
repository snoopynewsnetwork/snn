"""Explicit linked public GETs only; complete transport-decoded entities by hash."""
from pathlib import Path
import requests,hashlib,gzip,json,datetime,urllib.parse,sys,re
M=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def store(b):
 h=sha(b);z=gzip.compress(b,mtime=0);parts=[]
 for n,i in enumerate(range(0,len(z),39000000)):
  p=M/'originals'/((h+'.gz')if len(z)<40000000 else (h+'.gz.part%04d'%n));p.parent.mkdir(exist_ok=True);p.write_bytes(z[i:i+39000000]);parts.append(dict(path=str(p.relative_to(M)),bytes=p.stat().st_size,sha256=sha(p.read_bytes())))
 return dict(raw_bytes=len(b),raw_sha256=h,storage='gzip_then_ordered_byte_parts',parts=parts)
def fetch(key,url,parent=None,literal_href=None,params=None):
 p=M/'receipts'/(key+'.json')
 if p.exists():return load(p)
 rct=dict(requested_url=url,method='GET',query=params,body=None,parent=parent,literal_href=literal_href,retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),clock_timezone='UTC',source_status=None,source_date=None)
 try:
  r=requests.get(url,params=params,headers={'User-Agent':'Massachusetts historical map research','Accept-Encoding':'identity'},timeout=(20,75),allow_redirects=False)
  history=[]
  while r.is_redirect:
   target=urllib.parse.urljoin(r.url,r.headers['Location'])
   if re.search(r'(?i)/(?:user/)?(?:admin|login|logon|signin|password|account|auth)(?:/|\?|$)',target):
    rct['blocked_redirect_target']=target;break
   history.append(r);assert len(history)<=10
   r=requests.get(target,headers={'User-Agent':'Massachusetts historical map research','Accept-Encoding':'identity'},timeout=(20,75),allow_redirects=False)
  r.history=history
  rct['exchanges']=[]
  for x in [*r.history,r]:rct['exchanges'].append(dict(request_url=x.request.url,request_headers=dict(x.request.headers),request_body=x.request.body,status=x.status_code,response_headers=dict(x.headers),**store(x.content)))
  rct.update(final_url=r.url,status=r.status_code,**store(r.content));b=r.content
 except requests.RequestException as e:rct.update(error=str(e),status=None);b=b''
 dump(p,rct);print(key,rct.get('status'),len(b),flush=True);return b,rct
 def_unused=None

def body(r):return gzip.decompress(b''.join((M/x['path']).read_bytes()for x in r['parts']))
def load(p):
 r=json.loads(p.read_text());return (body(r)if 'parts'in r else b''),r
if __name__=='__main__':fetch(*sys.argv[1:])
