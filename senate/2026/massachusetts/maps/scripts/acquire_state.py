from acquire import *
import json
b,r=load(M/'receipts/portal-search.json');o=json.loads(b)
x=next(x for x in o['results']if x['title']=='Wards and Precincts (2022) (Feature Service)')
fetch('wards-item','https://www.arcgis.com/sharing/rest/content/items/'+x['id'],parent='receipts/portal-search.json',literal_href='result.id via ArcGIS item constructor',params={'f':'pjson'})
fetch('wards-service',x['url'],parent='receipts/portal-search.json',literal_href=x['url'],params={'f':'pjson'})
b,r=fetch('subprecinct-search','https://www.arcgis.com/sharing/rest/search',parent='hub-config.json',literal_href='public portal search constructor',params={'f':'json','q':'title:Subprecincts AND orgid:hGdibHYSPO59RG1h','num':100});print([(x['id'],x['title'],x.get('url'))for x in json.loads(b).get('results',[])])
