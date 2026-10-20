"""Bounded public acquisition. No retries, credentials, TLS bypass or source repair."""
from common import *
import urllib.request,urllib.error,urllib.parse,datetime,sys,socket
from html.parser import HTMLParser
MAX=160_000_000

def clock():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def store(b):
 z=gzip.compress(b,mtime=0);parts=[]
 for i in range(0,len(z),39_000_000):
  part=z[i:i+39_000_000];p='maps/bodies/'+sha(part)+'.gzpart';q=S/p
  if not q.exists():q.write_bytes(part)
  parts.append(ref(p))
 return {'raw_bytes':len(b),'raw_sha256':sha(b),'stored_bytes':len(z),'stored_sha256':sha(z),'encoding':'gzip_ordered_parts','parts':parts}
class Links(HTMLParser):
 def __init__(self,base):super().__init__(convert_charrefs=True);self.base=base;self.links=[];self.text=[];self.open=None
 def handle_starttag(self,t,attrs):
  d=dict(attrs)
  for name in ['href','src','data-src','data-url']:
   if d.get(name):self.links.append({'tag':t,'attribute':name,'literal':d[name],'url':urllib.parse.urljoin(self.base,d[name]),'text':''})
  if t=='a' and d.get('href'):self.open=len(self.links)-1
 def handle_endtag(self,t):
  if t=='a':self.open=None
 def handle_data(self,d):
  self.text.append(d)
  if self.open is not None:self.links[self.open]['text']+=d

def body_of(r):return original(r['entities'][-1]['body']) if r.get('entities') and r['entities'][-1].get('body') else b''
def links_of(r):
 b=body_of(r)
 if not b:return []
 p=Links(r['final_url']);p.feed(b.decode('utf-8','replace'));return p.links

def fetch(key,url,parent,role='map authority navigation'):
 path='maps/requests/'+key+'.json'
 if (S/path).exists():return load(path)
 r={'key':key,'method':'GET','requested_url':url,'parent':parent,'role':role,'request_headers':{'User-Agent':'Oregon precinct map research; bounded public evidence','Accept-Encoding':'identity'},'started_utc':clock(),'entities':[],'error':None}
 def entity(response,at):
  b=response.read(MAX+1);e={'url':response.geturl(),'status':response.code,'headers':list(response.headers.items()),'retrieved_utc':at,'body':None}
  if len(b)>MAX:e['discarded']='oversized partial attempt; not acquired original';e['observed_prefix_bytes']=len(b)
  else:e['body']=store(b)
  r['entities'].append(e)
 class Redirect(urllib.request.HTTPRedirectHandler):
  def redirect_request(self,req,fp,code,msg,headers,newurl):
   entity(fp,clock());return super().redirect_request(req,fp,code,msg,headers,newurl)
 try:
  req=urllib.request.Request(url,headers=r['request_headers'])
  with urllib.request.build_opener(Redirect()).open(req,timeout=22) as response:entity(response,clock());r['final_url']=response.geturl()
 except urllib.error.HTTPError as e:
  entity(e,clock());r['final_url']=e.geturl();r['error']=str(e)
 except Exception as e:r['error']=type(e).__name__+': '+str(e);r['final_url']=url
 r['finished_utc']=clock();save(path,r);return r

def reuse(path):
 """Freeze one exact individual receipt; independently verify each complete entity."""
 rp=ref(path);r=load(path)
 for e in r.get('entities',[]):
  if e.get('body'):original(e['body'])
 out={'source_receipt':rp,'receipt':r,'map_reuse_observed_utc':clock(),'map_role':'official state/county authority navigation; not current map approval','independently_original_verified':True}
 name='maps/references/'+r['key']+'.json';save(name,out);return r

if __name__=='__main__':
 r=fetch(*sys.argv[1:4]);print(json.dumps({'key':r['key'],'status':[e['status'] for e in r['entities']],'error':r['error'],'bytes':sum(e['body']['raw_bytes'] for e in r['entities'] if e.get('body'))}))
