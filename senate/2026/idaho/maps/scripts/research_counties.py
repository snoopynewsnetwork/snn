#!/usr/bin/env python3
"""Bounded official hierarchy traversal: only exact published links and explicit HTTPS upgrades."""
import concurrent.futures,json,re,sys
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit
from acquire import fetch,MAPS
ROOT=MAPS.parent

def run(county):
 k=county['key'];name=county['county'];link=county['sos_website'];records=[]
 def get(key,url,parent,href,purpose):
  try:x=fetch(key,url,parent,href,purpose);records.append(x['id']);return x
  except Exception as e:
   p=MAPS/'source'/f'{key}.transport-error.json';p.write_text(json.dumps(dict(id=key,requested_url=url,parent=parent,literal_href=href,method='GET',transport_error=repr(e),http_status=None),indent=2)+'\n');records.append(key+'.transport-error');return None
 x=get('county-'+k,link['url'],'sos-county-authority',link['href'],'County authority root, not a map approval')
 if link['url'].startswith('http:') and (x is None or x['status']>=400 or len(x.get('links',[]))==0):
  url='https:'+link['url'][5:];x=get('county-'+k+'-https',url,'county-'+k,'explicit transport-only HTTPS upgrade of published HTTP URL','County authority root transport alternative')
 if county['priority_children'] and x:
  seen={x['requested_url'],x['final_url']};queue=[x]
  for depth in range(3):
   nxt=[]
   for parent in queue:
    candidates=[]
    for l in parent.get('links',[]):
     label=(l['text']+' '+l['href']).lower();u=l['url'];ext=urlsplit(u).path.lower()
     if not u.startswith(('http:','https:')) or u in seen or any(t in label for t in ['mailto:','facebook','twitter','instagram','/cdn-cgi','calendar','results','sample-ballot','sample_ballot']):continue
     maplike=bool(re.search(r'precinct|polling.place|district.map|gis|voting.location',label))
     election=bool(re.search(r'election|county.clerk|clerk.auditor',label))
     if maplike or (depth<2 and election): candidates.append((0 if maplike else 1,l))
    candidates.sort(key=lambda q:q[0])
    for _,l in candidates[:(5 if depth else 3)]:
     if l['url'] in seen:continue
     seen.add(l['url']);key='county-'+k+'-follow-'+str(len(records))
     out=get(key,l['url'],parent['id'],l['href'],'Published county map/precinct/election link; inspect actual content and vintage')
     if out and out['status']==200 and 'links' in out:nxt.append(out)
   queue=nxt[:3]
  county['investigation']='Actual county/root and bounded three-depth published map/election-link requests; all attempts retained. No inferred leaf crosswalk.'
 county['request_ids']=records
 return county

def main():
 c=json.loads((ROOT/'data/turnout/priority-set.json').read_text());d=json.loads((MAPS/'source/sos-county-authority.receipt.json').read_text())
 links=[x for x in d['links'] if x['text']=='Website'];assert len(links)==44
 # Directory headings and Website links independently checked in literal HTML order.
 from acquire import Parser
 import gzip
 raw=gzip.decompress((ROOT/d['stored_path']).read_bytes()).decode();names=re.findall(r'(?<![A-Za-z])(?:Ada|Adams|Bannock|Bear Lake|Benewah|Bingham|Blaine|Boise|Bonner|Bonneville|Boundary|Butte|Camas|Canyon|Caribou|Cassia|Clark|Clearwater|Custer|Elmore|Franklin|Fremont|Gem|Gooding|Idaho|Jefferson|Jerome|Kootenai|Latah|Lemhi|Lewis|Lincoln|Madison|Minidoka|Nez Perce|Oneida|Owyhee|Payette|Power|Shoshone|Teton|Twin Falls|Valley|Washington) County\s*</div>',raw)
 names=[re.sub(r'\s*</div>','',n) for n in names];assert names==[p['county'] for p in c['all_county_constituents']],names
 counties=[dict(key=p['key'],county=p['county'],priority_children=len(c['ordered_priority_child_keys_by_parent'][p['key']]),historical_children=len(p['president_contexts']),sos_website=l,authority_parent='sos-county-authority',hierarchy_scope='county election authority; physical precinct and historical admin scopes differ') for p,l in zip(c['all_county_constituents'],links)]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  out=list(pool.map(run,counties))
 (MAPS/'county-investigations.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps(dict(counties=len(out),priority_parents=sum(bool(x['priority_children']) for x in out),requests=sum(len(x['request_ids']) for x in out))))
if __name__=='__main__':main()
