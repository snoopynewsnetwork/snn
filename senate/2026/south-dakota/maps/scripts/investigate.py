"""Full saved-HTML link inventory; generates bounded jobs only from actual hrefs."""
from common import *
from bs4 import BeautifulSoup
from urllib.parse import urljoin,urldefrag
import re,sys
def receipts():return load('source/reused-receipts.json')+[json.loads(p.read_bytes()) for p in sorted((MAPS/'raw').glob('*.receipt.json'))]
def links(e):
 b=original(e)
 if b.startswith(b'%PDF') or b.startswith(b'PK') or not b.strip().startswith(b'<'):return []
 s=BeautifulSoup(b,'html.parser');out=[];seen=set();base=e.get('final_url') or e['url']
 if s.find('base',href=True):base=urljoin(base,s.find('base',href=True)['href'])
 for a in s.select('a[href],iframe[src],img[src],script[src]'):
  href=a.get('href',a.get('src'));u=urljoin(base,href);text=a.get_text(' ',strip=True)
  if (href,text) in seen:continue
  seen.add((href,text));out.append(dict(tag=a.name,literal_href=href,url=u,text=text))
 return out
def relevant(l):
 h=(l['literal_href']+' '+l['text']).lower()
 return bool(re.search(r'precinct|election.?district.?map|voting.?district|voting.?center|vote.?center|interactive.?map|\bgis\b',h)) and not any(s in h for s in ['maps.google','generateMap','register','weather','fire danger','hometownlocator'])
def main():
 es=receipts();ix=[]
 for e in es:
  ls=links(e);ix.append(dict(id=e['id'],url=e['url'],status=e['status'],all_links=ls,relevant_links=[l for l in ls if relevant(l)]))
 dump('source/link-inventory.json',ix)
 if sys.argv[1:]==['--inventory-only']:return
 if len(sys.argv)>1:
  known={urldefrag(e['url'])[0] for e in es};jobs=[];seen=set()
  for e,x in zip(es,ix):
   # Acquire precinct map assets and map landing pages, not property/search/nav boilerplate.
   for l in x['relevant_links']:
    u=urldefrag(l['url'])[0]; h=(l['text']+' '+l['literal_href']).lower()
    if u in known or u in seen or not u.startswith(('http://','https://')):continue
    if l['tag']!='a':continue
    if not re.search('precinct|election.?district.?map|voting.?center|vote.?center|voting.?wards|voting.?districts',h):continue
    if any(s in h for s in ['committeeman','committeewoman','committeemen','committeewomen','login','security/index.jsp','election-results','election-precinct-by-precinct-results']):continue
    if any(s in u.lower() for s in ['facebook.com','twitter.com','linkedin.com','reddit.com']):continue
    if any(s in h for s in ['voter_registration','electionresults.sd.gov']):continue
    if 'peer-local' not in e['id'] and not e['id'].startswith(('map-','follow-','search-parent-','primary-')):continue
    f=e.get('county_fips')
    if not f:
     m=re.search('(46[0-9]{3})',e['id']);f=m[1] if m else None
    c=json.loads((STATE/CONTRACT).read_bytes())
    if f and f not in c['ordered_priority_parent_keys']:continue
    seen.add(u);jobs.append(dict(id=f'map-{f or "shared"}-{sha(u.encode())[:12]}',url=u,parent_id=e['id'],literal_href=l['literal_href'],anchor=l['text'],county_fips=f))
  dump(sys.argv[1],jobs[:80]);print('jobs',len(jobs[:80]))
 else:
  c=json.loads((STATE/CONTRACT).read_bytes())
  for f in c['ordered_priority_parent_keys']:
   print(f, next(p['county'] for p in c['county_parents'] if p['parent_key']==f))
   for x in ix:
    if f in x['id'] and x['relevant_links']:print(x['id'],x['status'],[(l['url'],l['text']) for l in x['relevant_links']])
if __name__=='__main__':main()
