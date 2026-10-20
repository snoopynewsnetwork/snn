"""Bounded source investigation follows exact published anchors, never guessed routes."""
from acquire import fetch
from html_tools import links,ROOT,entity
from urllib.parse import urlsplit,urldefrag
from concurrent.futures import ThreadPoolExecutor
import json,re
P='source/2026-10-20T202602680185+0000-5c50be815434.receipt.json'
seeds=[r for r in links(P) if 247<=r['line']<=300]
assert len(seeds)==54
BAD=re.compile(r'contact|mailto:|tel:|login|signin|sign-in|auth|partner|admin/|account|register|donat|/form|facebook|twitter|instagram|linkedin|youtube|apply|application|voterview|myinfo|property|parcel|tax[-_ ]|payment|pay[-_ ]|permit|bid[-_ ]|procure',re.I)
GOOD=re.compile(r'precinct|polling|election|registrar|probate|\bgis\b|/gis|maps|mapping|district|voting|departments|government',re.I)
def score(r):
 t=r['text']+' '+r['url'];return 100*bool(re.search('precinct|polling',t,re.I))+30*bool(re.search('election|registrar|voting',t,re.I))+10*bool(re.search('probate',t,re.I))+5*bool(re.search('gis|map',t,re.I))
def one(seed):
 county=seed['text'].strip();queue=[(seed['url'],{'receipt':P,'anchor':seed},0)];seen=set();obs=[];skipped=[]
 while queue and len(obs)<14:
  queue.sort(key=lambda x:-score(x[1].get('anchor',{'url':x[0],'text':''})))
  url,parent,depth=queue.pop(0);url=urldefrag(url)[0]
  if url in seen:continue
  seen.add(url)
  if BAD.search(url):skipped.append({'url':url,'reason':'excluded route'});continue
  p,r=fetch(url,parent);item={'url':url,'receipt':p,'status':r['status'],'depth':depth};obs.append(item)
  if r['status']!=200 or not r.get('entity'):continue
  _,body=entity(p)
  if body.startswith((b'%PDF',b'PK\x03\x04')):item['asset_magic']='PDF' if body.startswith(b'%PDF') else 'ZIP';continue
  if depth>=3:continue
  candidates=[]
  for a in links(p):
   text=a['text']+' '+a['url']
   if a['url'].startswith(('http://','https://')) and not BAD.search(text) and GOOD.search(text) and a['url'] not in seen:
    candidates.append(a)
  uniq={a['url']:a for a in candidates};candidates=sorted(uniq.values(),key=score,reverse=True)
  item['relevant_published_anchors']=candidates
  for a in candidates:queue.append((a['url'],{'receipt':p,'anchor':a},depth+1))
 out={'county':county,'seed':seed,'observations':obs,'unfetched_queue':[{'url':u,'parent':p,'depth':d} for u,p,d in queue if u not in seen],'excluded':skipped,'bound':'14 successful/failed requests, maximum three linked child edges; no personal/account/contact requests','qualification':'County sources investigated, but historical result-label/polygon joins and current/legal/physical identity remain unknown.'}
 p=ROOT/'county-chains'/(county.replace(' ','_')+'.json');p.parent.mkdir(exist_ok=True);p.write_text(json.dumps(out,indent=2)+'\n');print(county,len(obs),[x['asset_magic'] for x in obs if 'asset_magic' in x],flush=True)
 return {'county':county,'path':str(p.relative_to(ROOT))}
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=4) as pool:out=list(pool.map(one,seeds))
 (ROOT/'county-chain-index.json').write_text(json.dumps(out,indent=2)+'\n')
