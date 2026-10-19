#!/usr/bin/env python3
"""Two observed public map constructors plus exact clerk links; no API guesses."""
import json,gzip,re,datetime
from acquire import MAPS,fetch
jobs=[]
for rid,pattern,key in [('additional-16073-map-0-146',r'"class":"et_pb_blurb_17","url":"([^"]+)"','owyhee-configured-precinct-pdf')]:
 r=json.loads((MAPS/'source'/f'{rid}.receipt.json').read_text());b=gzip.decompress((MAPS.parent/r['stored_path']).read_bytes()).decode();u=re.search(pattern,b).group(1);jobs.append((key,u,rid,'Observed Divi et_pb_blurb_17 literal public URL constructor: Precinct Map','Published county precinct map, independently inspected vintage'))
for rid,word,key in [('additional-16079-discovery','Clerk','shoshone-clerk'),('additional-16085-discovery','What is My Voter Precinct?','valley-voter-map')]:
 r=json.loads((MAPS/'source'/f'{rid}.receipt.json').read_text());l=next(x for x in r['links'] if x['text']==word);jobs.append((key,l['url'],rid,l['href'],'Exact official-published clerk/map link'))
for args in jobs:
 r=fetch(*args);print(r['id'],r['status'],r['stored_path'])
# Follow exact Shoshone clerk map/election links only once.
r=json.loads((MAPS/'source/shoshone-clerk.receipt.json').read_text())
for i,l in enumerate(r.get('links',[])):
 if re.search(r'election|precinct',l['text'],re.I) and not re.search('result|candidate|register|mailto|sos.|voteidaho',l['url'],re.I) and l['url'].startswith(('http:','https:')):
  out=fetch('shoshone-clerk-link-'+str(i),l['url'],r['id'],l['href'],'Exact public Shoshone election/precinct link');print(out['id'],out['status'])
