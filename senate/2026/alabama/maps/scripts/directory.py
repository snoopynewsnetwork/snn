"""Fetch only actually published public county-directory anchors."""
from acquire import fetch
from html_tools import links,ROOT
from concurrent.futures import ThreadPoolExecutor
import json
P='source/2026-10-20T202456277858+0000-091445f51437.receipt.json'
rows=[r for r in links(P) if r['href'].startswith('/city-county-lookup/') and r['line']>=797 and r['line']<=995]
assert len(rows)==67
def one(r):
 p,q=fetch(r['url'],{'receipt':P,'anchor':r});return {'county':r['text'].strip(),'receipt':p,'status':q['status'],'url':r['url'],'parent_anchor':r}
with ThreadPoolExecutor(max_workers=4) as pool:out=list(pool.map(one,rows))
(ROOT/'directory-observations.json').write_text(json.dumps(out,indent=2)+'\n');print('county directories acquired',len(out))
