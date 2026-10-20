from acquire import *
from concurrent.futures import ThreadPoolExecutor
jobs=[]
for parent in ['state-election-service','burlington-election-service']:
 for x in links(parent):
  if x['text'] in ['JSON','Govt_admin_election_district','Election Wards and Districts']:
   suffix='meta-pre' if x['text']=='JSON' else 'layer-page';jobs.append((parent+'-'+suffix,x['url'],parent,x['literal_href']))
with ThreadPoolExecutor(max_workers=4) as e:list(e.map(lambda j:fetch(*j),jobs))
for parent in ['state-election-service','burlington-election-service']:
 for x in links(parent+'-layer-page'):
  if x['text']=='JSON':fetch(parent+'-layer-pre',x['url'],parent+'-layer-page',x['literal_href'])
  elif x['text']=='Query':fetch(parent+'-query-form',x['url'],parent+'-layer-page',x['literal_href'])
