from acquire import fetch,body,R
from inspect_sources import inspect
import json,re,concurrent.futures
r=json.loads((R/'requests/sos-county-bluebook.json').read_bytes());s=body(r).decode()
options=re.findall(r'<option value="([^"]+)">([^<]+) County</option>',s)
assert len(options)==36
items=[('bluebook-'+v.removesuffix('.aspx'),'https://sos.oregon.gov/blue-book/government/Pages/'+v,'sos-county-bluebook') for v,n in options]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 for x in ex.map(lambda args:fetch(*args),items):
  d=inspect(x);print(d['key'],d['status'])
