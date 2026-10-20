from acquire import fetch
from html_tools import links,ROOT
from concurrent.futures import ThreadPoolExecutor
import json,re
P='source/2026-10-20T202605375836+0000-e93c846f62ee.receipt.json'
rows=[x for x in links(P) if re.fullmatch(r'tl_2020_01\d{3}_vtd20.zip',x['href'])];assert len(rows)==67
def one(r):
 p,q=fetch(r['url'],{'receipt':P,'anchor':r});return {'county_fips':re.search(r'2020_(\d{5})_',r['href']).group(1),'receipt':p,'status':q['status'],'parent_anchor':r,'role':'2020 Census VTD historical context only; no result-label join or current/legal/native-precinct approval'}
with ThreadPoolExecutor(max_workers=4) as pool:out=list(pool.map(one,rows))
(ROOT/'census-observations.json').write_text(json.dumps(out,indent=2)+'\n');print('full Census originals',len(out),[r for r in out if r['status']!=200])
