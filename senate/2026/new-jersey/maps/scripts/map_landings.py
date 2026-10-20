from acquire import *
from concurrent.futures import ThreadPoolExecutor
import re
jobs=[];seen=set()
for c in json.loads((BASE/'derived/county-first-map-links.json').read_bytes()):
 for x in c['candidates']:
  if x['url'] in seen:continue
  if re.search(r'\bMaps\b|district maps|Re-Warding|polling.*PDF|polling.*Map',x['text'],re.I) and not re.search(r'Surrogate|Historic|grave|google|svrs',x['text']+' '+x['url'],re.I):
   seen.add(x['url']);jobs.append(('county-map-%02d'%len(jobs),x['url'],x['parent_receipt'],x['literal_href']))
jobs += [('state-election-service','https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/ArcGIS/rest/services/Election_Districts_for_New_Jersey/FeatureServer','actual search result official attribution NJ Division of Elections'),('burlington-election-service','https://gisportal.co.burlington.nj.us/hosting/rest/services/Elections/MapServer','actual search result Burlington county GIS'),('morris-election-service','https://morrisgisapps.co.morris.nj.us/arcgis105/rest/services/ELECTIONS/ElectionsFS/FeatureServer','actual search result Morris county GIS'),('salem-resources','https://elections.salemcountynj.gov/resources-voter-information/','actual search result official county Board of Elections'),('map-rules','https://www.nj.gov/state/dos-statutes-elections-15.shtml','actual search result official NJAC15:10-3')]
write(BASE/'derived/map-landing-jobs.json',jobs)
with ThreadPoolExecutor(max_workers=6) as e:list(e.map(lambda j:fetch(*j),jobs))
