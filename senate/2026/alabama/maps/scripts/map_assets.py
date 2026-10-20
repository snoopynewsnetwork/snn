"""Final asset-focused pass: published map/PDF/image anchors and embedded objects only."""
from acquire import fetch
from html_tools import ROOT,entity,links
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from urllib.parse import urljoin,urlsplit,urldefrag
import json,re
BAD=re.compile(r'contact|mailto:|tel:|login|signin|auth|partner|admin|account|donat|facebook|twitter|instagram|linkedin|youtube|reddit|pinterest|/submit|/share|apply|application|voterview|myinfo|property|parcel|payment|permit|procure|/search|google|goo.gl|logo|icon|banner|badge|seal|sample|ballot|result|report|calendar',re.I)
MAP=re.compile(r'precinct|polling|map|district',re.I)
ASSET=re.compile(r'\.pdf(?:[?#]|$)|\.(?:zip|png|jpe?g|tiff?)(?:[?#]|$)|showpublisheddocument|DocumentCenter/View',re.I)
class Embed(HTMLParser):
 def __init__(self,base):super().__init__();self.base=base;self.rows=[]
 def handle_starttag(self,t,a):
  d=dict(a)
  if t=='base' and d.get('href'):self.base=urljoin(self.base,d['href'])
  if t in ['img','iframe','embed','object']:
   u=d.get('src',d.get('data',''))
   if u:self.rows.append({'url':urljoin(self.base,u),'href':u,'text':d.get('alt') or d.get('title') or '','tag':self.get_starttag_text(),'line':self.getpos()[0],'column':self.getpos()[1]})
existing={};jobs={}
for p in sorted((ROOT/'source').glob('*.receipt.json')):
 r=json.loads(p.read_text());existing[r['requested_url']]=str(p.relative_to(ROOT))
for path in sorted((ROOT/'county-chains').glob('*.json')):
 x=json.loads(path.read_text());county=x['county']
 for o in x['observations']:
  if o['status']!=200:continue
  rr,b=entity(o['receipt'])
  if b.startswith((b'%PDF',b'PK')):continue
  parentmap=bool(MAP.search(urlsplit(o['url']).path))
  rows=links(o['receipt'])
  if parentmap:
   ep=Embed(rr['final_url']);ep.feed(b.decode('utf-8',errors='replace'));rows+=ep.rows
  for a in rows:
   u=urldefrag(a['url'])[0];text=a['text']+' '+u
   if not u.startswith(('http://','https://')) or BAD.search(text):continue
   direct=ASSET.search(u) and (MAP.search(text) or parentmap)
   directory=('/uploads/Polls/' in u or '/uploads/Districts/' in u) and not ASSET.search(u)
   if direct or directory:
    if u not in jobs:jobs[u]={'county':county,'url':u,'parent':{'receipt':o['receipt'],'anchor':a},'directory':bool(directory)}
def one(job):
 u=job['url']
 if u in existing:p=existing[u];r,_=entity(p)
 else:p,r=fetch(u,job['parent'])
 return {**job,'receipt':p,'status':r['status']}
with ThreadPoolExecutor(max_workers=3) as pool:out=list(pool.map(one,jobs.values()))
# Download every PDF under actually returned map-directory anchors, no guessed filenames.
second={}
for o in out:
 if o['directory'] and o['status']==200:
  for a in links(o['receipt']):
   if ASSET.search(a['url']) and not BAD.search(a['url']):second[a['url']]={'county':o['county'],'url':a['url'],'parent':{'receipt':o['receipt'],'anchor':a},'directory':False}
with ThreadPoolExecutor(max_workers=3) as pool:out+=list(pool.map(one,second.values()))
(ROOT/'map-asset-observations.json').write_text(json.dumps(out,indent=2)+'\n');print('asset-focused observations',len(out),'counties',len(set(o['county'] for o in out)),flush=True)
