from acquire import *
from concurrent.futures import ThreadPoolExecutor
import re
D=json.loads((BASE/'authority-directory.json').read_bytes());jobs=[];summary=[]
for c in D:
 out={'county':c['county'],'candidates':[]}
 for r in c['roles']:
  for x in r['links']:
   id=x['receipt_id'];rec=json.loads((BASE/'receipts'/f'{id}.json').read_bytes())
   # The same published resource with HTTPS transport; no path/identifier guess.
   if x['url'].startswith('http:') and rec.get('status') in [403,404]:jobs.append((id+'-https','https:'+x['url'][5:],id+'; same published URI with HTTPS transport',x['literal_href']))
   if rec.get('status')==200:
    for l in links(id):
     if re.search(r'map|district|precinct|polling|redistrict|gis|boundar|ward',l['text'],re.I) and not re.search(r'contact|direction|career|social|sitemap|google.com/maps|mailto|login',l['text']+' '+l['url'],re.I):
      l['parent_receipt']=id;out['candidates'].append(l)
 summary.append(out)
write(BASE/'derived/county-first-map-links.json',summary)
with ThreadPoolExecutor(max_workers=6) as e:list(e.map(lambda j:fetch(*j),jobs))
for c in summary:
 print(c['county'],json.dumps(c['candidates'],ensure_ascii=False)[:5500])
