"""Single bounded public observations; no polling, guesses or authentication."""
from pathlib import Path
import gzip,hashlib,json,requests,datetime,urllib.parse,sys
BASE=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def store(b):
 h=sha(b);c=gzip.compress(b,mtime=0);parts=[]
 for i in range(0,len(c),39000000):
  name='originals/'+h+('.gz' if len(c)<40000000 else '.gz.part%04d'%(i//39000000));p=BASE/name
  if p.exists():assert p.read_bytes()==c[i:i+39000000]
  else:p.write_bytes(c[i:i+39000000])
  parts.append({'path':name,'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())})
 return {'raw_bytes':len(b),'raw_sha256':h,'stored_parts':parts,'storage':'ordered concatenate then gzip decompress'}
def body(r):
 b=gzip.decompress(b''.join((BASE/x['path']).read_bytes() for x in r['stored_parts']))
 assert sha(b)==r['raw_sha256'] and len(b)==r['raw_bytes'];return b

def fetch(id,url,parent,literal_href=None,params=None,method='GET',data=None):
 p=BASE/'receipts'/f'{id}.json'
 if p.exists():return json.loads(p.read_bytes())
 o={'id':id,'parent':parent,'literal_href':literal_href if literal_href is not None else url,'requested_url':url,'query':params,'method':method,'request_body':data,'retrieval_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hops':[],'source_clock_note':'HTTP Date/Last-Modified retained independently; no inferred election validity or cadence'}
 try:
  req=requests.Request(method,url,params=params,data=data,headers={'User-Agent':'Public map research; one bounded observation','Accept-Encoding':'identity'}).prepare()
  for _ in range(8):
   o['actual_requested_url']=req.url if not o['hops'] else o['actual_requested_url']
   r=requests.Session().send(req,allow_redirects=False,timeout=(20,90),stream=True);b=r.raw.read(decode_content=False)
   hop={'requested_url':req.url,'method':req.method,'request_headers':dict(req.headers),'request_body':req.body,'status':r.status_code,'reason':r.reason,'response_headers':list(r.raw.headers.items()),'final_url':r.url,**store(b)};o['hops'].append(hop)
   if r.status_code not in [301,302,303,307,308] or not r.headers.get('Location'):break
   nexturl=urllib.parse.urljoin(r.url,r.headers['Location']);req=requests.Request('GET',nexturl,headers={'User-Agent':'Public map research; one bounded observation','Accept-Encoding':'identity'}).prepare()
  o['status']=o['hops'][-1]['status'];o['final_url']=o['hops'][-1]['final_url']
 except Exception as e:o['error']=repr(e)
 o['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();write(p,o);print(id,o.get('status'),o.get('error',''),(o['hops'][-1] if o['hops'] else {}).get('raw_bytes',0),flush=True);return o

def content(id):
 r=json.loads((BASE/'receipts'/f'{id}.json').read_bytes());h=r['hops'][-1];b=body(h);headers=dict(h['response_headers']);enc=next((v for k,v in h['response_headers'] if k.lower()=='content-encoding'),'')
 if enc=='gzip':b=gzip.decompress(b)
 elif enc=='br':
  import brotli;b=brotli.decompress(b)
 return b

def links(id):
 from html.parser import HTMLParser
 class Parser(HTMLParser):
  def __init__(self):super().__init__(convert_charrefs=True);self.out=[];self.active=None
  def handle_starttag(self,tag,attrs):
   a=dict(attrs);h=a.get('href') if tag=='a' else a.get('src') if tag in ['iframe','script'] else None
   if h and not h.lower().startswith(('mailto:','tel:','javascript:')):
    x={'text':'','literal_href':h,'url':urllib.parse.urljoin(r['final_url'],h)};self.out.append(x)
    if tag=='a':self.active=x
  def handle_endtag(self,tag):
   if tag=='a':self.active=None
  def handle_data(self,s):
   if self.active is not None:self.active['text']+=s
 r=json.loads((BASE/'receipts'/f'{id}.json').read_bytes());parser=Parser();parser.feed(content(id).decode('utf-8',errors='replace'));out=parser.out
 for x in out:x['text']=' '.join(x['text'].split())
 write(BASE/'derived'/f'{id}-links.json',out);return out
if __name__=='__main__':
 if sys.argv[1]=='fetch':fetch(*sys.argv[2:])
 elif sys.argv[1]=='links':
  for x in links(sys.argv[2]):
   if len(sys.argv)<4 or __import__('re').search(sys.argv[3],x['text']+' '+x['url'],__import__('re').I):print(json.dumps(x,ensure_ascii=False))
