from common import *
import concurrent.futures,re
jobs=[]
for x in json.loads(original('rgis-sos-directory'))['results']:
 if 'Voting Precinct' in x['description']and any(y in x['description']for y in ['2026','2024']):
  year='2026'if '2026'in x['description']else'2024'
  for fmt in ['zip']:
   for d in x['downloads']:
    if fmt in d:jobs.append((f'rgis-{year}-{fmt}',d[fmt],'rgis-sos-directory',x))
  jobs.append((f'rgis-{year}-metadata',x['metadata'][0]['FGDC-STD-001-1998']['xml'],'rgis-sos-directory',x['metadata'][0]))
for x in json.loads(original('webmap-data'))['operationalLayers']:
 if x['title']=='Political Subdivisions':jobs.append(('political-service-pre',x['url']+'?f=pjson','webmap-data',x))
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:
  for r in pool.map(lambda x:fetch(*x,timeout=180),jobs):print(r['id'],r.get('status'),r.get('body',{}).get('raw_bytes'),r.get('error'),flush=True)
