from acquire import fetch,links
from concurrent.futures import ThreadPoolExecutor
jobs=[]
for x in links('doe-publications'):
 if x['text'] in ['NJ Congressional Districts 2022-2031','NJ Legislative Districts 2022-2030','Statutes & Rules','New Jersey District Level Reporting Guide']:
  if any(j[1]==x['url'] for j in jobs):continue
  jobs.append(('state-companion-%02d'%len(jobs),x['url'],'doe-publications',x['literal_href']))
for x in links('njgin-products'):
 if x['text'].startswith('Zip file of all 2020'):jobs.append(('njgin-census-geography',x['url'],'njgin-products',x['literal_href']))
jobs+=[('census-vtd-zip','https://www2.census.gov/geo/tiger/TIGER2020PL/LAYER/VTD/2020/tl_2020_34_vtd20.zip','actual resource downloadURL in Census catalog search result','https://www2.census.gov/geo/tiger/TIGER2020PL/LAYER/VTD/2020/tl_2020_34_vtd20.zip'),('census-vtd-schema','https://meta.geo.census.gov/data/existing/decennial/GEO/GPMB/TIGERline/Archived_19110/tl_2020_vtd.shp.ea.iso.xml','actual Census catalog describedBy resource','https://meta.geo.census.gov/data/existing/decennial/GEO/GPMB/TIGERline/Archived_19110/tl_2020_vtd.shp.ea.iso.xml')]
with ThreadPoolExecutor(max_workers=5) as e:list(e.map(lambda j:fetch(*j),jobs))
