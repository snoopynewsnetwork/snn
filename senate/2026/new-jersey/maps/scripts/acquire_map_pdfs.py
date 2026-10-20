from acquire import *
from concurrent.futures import ThreadPoolExecutor
import re
jobs=[];catalog=[];seen=set()
for parent,county in [('county-map-00','Bergen'),('county-map-03','Camden'),('county-map-04','Cumberland'),('county-map-05','Hunterdon'),('county-map-06','Union'),('county-map-08','Union')]:
 for x in links(parent):
  ok= (county=='Bergen' and x['text']=='Map') or (county=='Camden' and '.pdf' in x['url'] and '/uploads/' in x['url'] and re.search(r'\bBoro|Township|City|Borough',x['text'])) or (county=='Cumberland' and 'Voter District Map' in x['text']) or (county=='Hunterdon' and 'Districts (PDF' in x['text']) or (county=='Union' and '.pdf' in x['url'] and '/boe/wp-content/' in x['url'])
  if not ok or x['url'] in seen:continue
  seen.add(x['url']);id='map-original-%03d'%len(jobs);jobs.append((id,x['url'],parent,x['literal_href']));catalog.append({'id':id,'county':county,**x,'parent_receipt':parent,'geographic_relationship':'county-published municipal/ward/election map; no historical source-row/current native-ID join asserted'})
write(BASE/'map-original-catalog.json',catalog)
with ThreadPoolExecutor(max_workers=5) as e:list(e.map(lambda j:fetch(*j),jobs))
