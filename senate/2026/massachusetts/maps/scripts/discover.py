from acquire import *
import re,urllib.parse
# Portal host and organization from official __SITE; searchItems constructor in linked runtime.
hub,r=load(M/'receipts/hub.json');s=hub.decode();cfg=json.loads(urllib.parse.unquote(re.search(r'window\.__SITE="([^"]+)',s)[1]));dump(M/'hub-config.json',cfg)
b,r=fetch('portal-search','https://www.arcgis.com/sharing/rest/search',parent='receipts/hub-vendor.json',literal_href='searchItems({q,...}); portalBaseUrl from hub-runtime',params={'f':'json','q':'title:"Wards and Precincts" AND orgid:hGdibHYSPO59RG1h','num':100})
if r.get('status')==200:
 o=json.loads(b);print([(x['id'],x['title'],x.get('url'))for x in o.get('results',[])])
