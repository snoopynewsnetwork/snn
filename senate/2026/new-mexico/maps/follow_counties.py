"""Bounded second map hop; only necessary map/location/legal evidence."""
from common import *
import concurrent.futures,re
jobs=[];records=[]
for row in json.loads((M/'directory-inventory.json').read_bytes()):
 f=row['parent']['fips'];candidates=[]
 pages=['county-'+f]+[p.stem for p in sorted((M/'receipts').glob('local-'+f+'-*.json'))]
 for name in pages:
  if not(M/'receipts'/(name+'.json')).exists():continue
  b=original(name)
  if not b or b.startswith((b'%PDF-',b'PK')):continue
  for l in links(name):
   text=l['text'];url=l['url']
   relevant=re.search(r'precinct|district.{0,10}map|^maps.{0,30}elections|voting location.{0,10}map|polling location|polling place|notice of election|adjusting.precinct',text,re.I)
   if relevant and not re.search(r'parcel|assessor|school|facebook|twitter|mailto:|WhereToVote|registration|\.png|\.jpg',text+' '+url,re.I):candidates.append((name,l))
 seen=set();chosen=[]
 existing={json.loads(p.read_bytes())['requested_url']for p in (M/'receipts').glob('*.json')}
 for name,l in candidates:
  if l['url']in seen or l['url']in existing:continue
  seen.add(l['url']);chosen.append((name,l))
  if len(chosen)==4:break
 for i,(name,l)in enumerate(chosen):jobs.append((f'map-hop-{f}-{i+1}',l['url'],name,l))
 # Election navigation if map not exposed (one bounded county election hop).
 if not chosen:
  for name in pages[:1]:
   if not(M/'receipts'/(name+'.json')).exists():continue
   for l in links(name):
    if re.fullmatch(r'elections?|bureau of elections|election information',l['text'],re.I)and l['url']not in existing:
     jobs.append((f'map-election-{f}',l['url'],name,l));break
 records.append({'fips':f,'complete_relevant_observed_relations':[{'parent':n,'link':l}for n,l in candidates],'selected_relations':[{'parent':n,'link':l}for n,l in chosen]})
write(M/'county-second-hop-relations.json',records)
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=5)as pool:
  for r in pool.map(lambda x:fetch(*x,timeout=35),jobs):print(r['id'],r.get('status'),r.get('error'),r.get('body',{}).get('raw_bytes'),flush=True)
