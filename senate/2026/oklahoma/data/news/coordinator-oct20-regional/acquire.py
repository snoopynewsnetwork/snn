"""Bounded public newsroom GETs and actual results links; no account/media crawler."""
from pathlib import Path
import datetime,gzip,hashlib,json,urllib.request,urllib.error,urllib.parse
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor
R=Path(__file__).resolve().parent

def sha(b):return hashlib.sha256(b).hexdigest()
def js(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def body(b):
 h=sha(b);p=R/(h+'.entity.gz');z=gzip.compress(b,mtime=0);assert len(z)<40000000
 if not p.exists():p.write_bytes(z)
 assert p.read_bytes()==z
 return {'path':p.name,'raw_bytes':len(b),'raw_sha256':h,'stored_bytes':len(z),'stored_sha256':sha(z),'encoding':'gzip'}
class Links(HTMLParser):
 def __init__(self,b):super().__init__(convert_charrefs=True);self.links=[];self.active=[];self.feed(b.decode('utf-8',errors='replace'))
 def handle_starttag(self,tag,attrs):
  if tag=='a':self.active.append({'attrs':attrs,'text':'','position':self.getpos()})
 def handle_data(self,s):
  for a in self.active:a['text']+=s
 def handle_endtag(self,tag):
  if tag=='a' and self.active:
   a=self.active.pop();a['text']=' '.join(a['text'].split());self.links.append(a)
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):return None

def fetch(key,url,parent=None,literal=None):
 p=R/(key+'.receipt.json')
 if p.exists():return json.loads(p.read_bytes())
 o={'id':key,'requested_url':url,'parent':parent,'literal_discovery':literal,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hops':[]};op=urllib.request.build_opener(NoRedirect());current=url
 for i in range(6):
  headers={'User-Agent':'Public election newsroom source research; bounded original retention','Accept-Encoding':'identity'};h={'requested_url':current,'method':'GET','request_headers':headers,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  try:
   req=urllib.request.Request(current,headers=headers)
   try:r=op.open(req,timeout=45)
   except urllib.error.HTTPError as e:r=e
   with r:b=r.read();h.update(status=r.code,final_url=r.geturl(),response_headers=list(r.headers.items()),body=body(b))
   o['hops'].append(h)
   if h['status'] in [301,302,303,307,308] and r.headers.get('Location'):
    literal=r.headers['Location'];dest=urllib.parse.urljoin(current,literal);h['redirect_location_literal']=literal
    if any(x in urllib.parse.urlsplit(dest).path.lower() for x in ['/login','/account','/signin','/subscribe']):o['access_gap']='unexpected account redirect retained but not followed';break
    current=dest;continue
   o.update(status=h['status'],final_url=h['final_url'],body=h['body']);break
  except Exception as e:h['error']=repr(e);o['hops'].append(h);o['error']=repr(e);break
 o['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();js(p,o)
 if o.get('body'):
  z=gzip.decompress((R/o['body']['path']).read_bytes());links=Links(z).links;selected=[a for a in links if 'election' in a['text'].lower() or 'result' in a['text'].lower()];js(R/(key+'.election-links.json'),selected)
 return o

def main():
 roots=[('kswo-home','https://www.kswo.com/'),('enid-home','https://www.enidnews.com/'),('newson6-home','https://www.newson6.com/')]
 with ThreadPoolExecutor(max_workers=3) as ex:rs=list(ex.map(lambda x:fetch(*x),roots))
 for key,url in roots:
  p=R/(key+'.election-links.json')
  if not p.exists():continue
  links=json.loads(p.read_bytes());chosen=[a for a in links if a['text'].lower()=='election results']
  if chosen:
   a=chosen[0];href=dict(a['attrs']).get('href')
   if href:fetch(key.replace('-home','-results'),urllib.parse.urljoin(url,href),key,a)
 receipts=[json.loads(p.read_bytes()) for p in sorted(R.glob('*.receipt.json'))];js(R/'acquisition-complete-v1.json',{'scope':'Bounded primary newsroom public pages and literal results links only; full original receipts/entities; old shared ledger unchanged.','receipts':receipts,'actual_requests':len(receipts),'outreach_accounts_auth_media':False,'current_November_admission':False});print([(r['id'],r.get('status'),r.get('error')) for r in receipts])
if __name__=='__main__':main()
