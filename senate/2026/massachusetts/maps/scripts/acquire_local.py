from acquire import *
from html.parser import HTMLParser
import re,json,concurrent.futures,urllib.parse
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.active=None;self.title='';self.intitle=False;self.text=[]
 def handle_starttag(self,t,a):
  if t=='title':self.intitle=True
  if t=='a':self.active=dict(attrs=a,href=dict(a).get('href',''),text='')
 def handle_data(self,d):
  self.text.append(d)
  if self.intitle:self.title+=d
  if self.active:self.active['text']+=d
 def handle_endtag(self,t):
  if t=='title':self.intitle=False
  if t=='a'and self.active:self.links.append(self.active);self.active=None

def safe(u):
 p=urllib.parse.urlsplit(u)
 return p.scheme in ['http','https']and not re.search(r'(?i)(admin|login|logon|sign.?in|password|account|auth|facebook|twitter|instagram|linkedin|youtube|mailto|cart|subscribe|challenge|incapsula|safelinks|\.mp3|\.mp4|birth|death|marriage|licenses)',u)
def parse_local_nav():
 req=json.loads((M/'local-requests.json').read_bytes());byid={x['requested_link_id']:x for x in req if x['requested_link_id']};found={}
 for p in sorted((M/'web').glob('local-navigation-*.txt')):
  for block in p.read_text().split('\n--------------------------------------------------------------------------------\n'):
   k=re.search(r'Source: click\(\{"ref_id":"turn8view0","id":(\d+)\}',block);u=re.search(r'^.*?\((https?://[^\n]+)\)\n',block)
   if not u:u=re.search(r'Failed to fetch (https?://[^\s]+?)(?=: |$)',block)
   if k and u and int(k[1])in byid:
    x=byid[int(k[1])];found[x['parent_literal']]=dict(parent_literal=x['parent_literal'],url=u[1],navigation=str(p.relative_to(M)),in_priority=x['in_priority'])
 dump(M/'local-targets.json',list(found.values()));dump(M/'local-navigation-gaps.json',[x for x in req if x['parent_literal']not in found]);return found

def work(x):
 stem='local-'+sha(x['parent_literal'].encode())[:12];seen=set();queue=[(x['url'],x['navigation'],None,0)];out=[]
 while queue and len(out)<10:
  u,parent,literal,depth=queue.pop(0)
  if u in seen or not safe(u):continue
  seen.add(u);key=stem+'-%02d'%len(out);b,r=fetch(key,u,parent=parent,literal_href=literal);p=Links();is_pdf=b.startswith(b'%PDF-');parse_error=None
  ctype=r.get('exchanges',[{}])[-1].get('response_headers',{}).get('Content-Type','')if r.get('exchanges')else ''
  if 'html'in ctype.lower()or b'<html'in b[:1000].lower():
   try:p.feed(b.decode('utf-8',errors='replace'))
   except (AssertionError,ValueError)as e:parse_error=str(e)
  shell=any(k in b[:20000].lower()for k in [b'_incapsula_resource',b'cf-chl-',b'access denied'])
  row=dict(url=u,receipt='receipts/'+key+'.json',status=r.get('status'),title=p.title,depth=depth,complete_pdf=is_pdf,challenge_shell=shell,parse_error=parse_error,content_type=ctype,all_literal_links=p.links,complete_text=' '.join(p.text),source_date=None,source_clock_timezone=None)
  out.append(row)
  if not shell and not is_pdf and depth<3 and r.get('status')==200:
   candidates=[]
   for a in p.links:
    href=a['href']
    if not isinstance(href,str)or not href:continue
    v=urllib.parse.urljoin(r['final_url'],href);label=a['text']+' '+href
    if not safe(v)or '#'==href[:1]or v in seen:continue
    if re.search(r'(?i)(ward|precinct|re.?district|re.?precinct)',label):rank=0
    elif re.search(r'(?i)(election|voting|town.?clerk|city.?clerk)',label):rank=1
    elif re.search(r'(?i)(geographic|gis|maps)',label):rank=2
    else:continue
    candidates.append((rank,v,href))
   chosen=[]
   for rank,v,href in sorted(candidates):
    if v not in [a[0]for a in chosen]:chosen.append((v,href))
   for v,href in chosen[:4 if depth==0 else 2]:queue.append((v,row['receipt'],href,depth+1))
 result=dict(**x,steps=out,bound='at most 10 exact-linked public resources; depth <=3; preferred ward/precinct, elections/clerk, GIS',signed_current_crosswalk=None)
 dump(M/'parents'/(sha(x['parent_literal'].encode())[:12]+'.json'),result);return result
if __name__=='__main__':
 found=parse_local_nav();tasks=[x for x in found.values()if x['in_priority']and not (M/'parents'/(sha(x['parent_literal'].encode())[:12]+'.json')).exists()];print('priority local targets',len(tasks),flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=5)as ex:
  for row in ex.map(work,tasks):dump(M/'parents'/(sha(row['parent_literal'].encode())[:12]+'.json'),row)
 print('done',len(tasks))
