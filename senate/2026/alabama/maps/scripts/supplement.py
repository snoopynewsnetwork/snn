from acquire import fetch
from html_tools import ROOT,links,entity
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlsplit,urldefrag
import json,re
# These are observed search results, never synthetic county slugs.
SEEDS=[('Barbour','https://www.barbourcountyal.gov/27/County-Government'),('Bullock','https://bullockal.com/'),('Choctaw','https://www.choctawcountyal.org/board-of-registrars/'),('Clay','https://www.claycountyrevenue.com/home/links/'),('Hale','https://www.halecountyal.gov/county-commission'),('Lamar','https://lamarcountyal.gov/probate-judge/'),('Marion','https://www.marioncountyal.org/home/departments/probate-office/elections/'),('Perry','https://www.perrycountyal.gov/government/county-commission/committees'),('Pickens','https://pickens.alacourt.gov/phone-directory/'),('Winston','https://winston.alacourt.gov/circuit-clerk/'),('Greene','https://greene.alacourt.gov/absentee-voting/'),('Conecuh','https://alabamamaps.ua.edu/contemporarymaps/special/atrc/conecuh.pdf')]
BAD=re.compile(r'contact|mailto:|tel:|login|signin|sign-in|auth|partner|/admin|account|register|donat|/form|facebook|twitter|instagram|linkedin|youtube|reddit|pinterest|/submit|/share|apply|application|voterview|myinfo|property|parcel|payment|permit|procure|/search|google|goo.gl',re.I)
FOCUS=re.compile(r'precinct|polling|map|registrar|election|voting|district|probate|departments',re.I)
MAP=re.compile(r'precinct|polling|map|district',re.I)
def candidates(p):
 out={}
 for a in links(p):
  if a['url'].startswith(('http://','https://')) and not BAD.search(a['url']+' '+a['text']) and FOCUS.search(a['text']+' '+urlsplit(a['url']).path.rsplit('/',1)[-1]):out[a['url']]=a
 return sorted(out.values(),key=lambda a:(-bool(MAP.search(a['text']+' '+a['url'])),-bool(re.search('precinct|polling',a['text']+' '+a['url'],re.I))))
def one(job):
 county,url=job;queue=[(url,{'observed_public_search_result':url},0)];seen=set();out=[]
 while queue and len(out)<16:
  url,parent,d=queue.pop(0);url=urldefrag(url)[0]
  if url in seen or BAD.search(url):continue
  seen.add(url);p,r=fetch(url,parent);obs={'url':url,'receipt':p,'status':r['status'],'depth':d};out.append(obs)
  if r['status']!=200:continue
  _,b=entity(p)
  if b.startswith((b'%PDF',b'PK\x03\x04')):obs['asset_magic']='PDF' if b.startswith(b'%PDF') else 'ZIP';continue
  if d>=3:continue
  cs=candidates(p);obs['relevant_published_anchors']=cs
  queue.extend((a['url'],{'receipt':p,'anchor':a},d+1) for a in cs)
 path=ROOT/'county-chains'/(county.replace(' ','_')+'.supplement.json');path.write_text(json.dumps({'county':county,'observations':out,'unfetched_queue':[{'url':u,'parent':p,'depth':d} for u,p,d in queue if u not in seen],'bound':'16 requests and three linked child edges from exact observed official/official-context source'},indent=2)+'\n');print(county,len(out),flush=True)
 return str(path.relative_to(ROOT))
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=4) as pool:out=list(pool.map(one,SEEDS))
 (ROOT/'supplement-index.json').write_text(json.dumps(out,indent=2)+'\n')
