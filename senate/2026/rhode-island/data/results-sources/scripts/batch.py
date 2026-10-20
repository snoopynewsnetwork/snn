from acquire import acquire
from common import *
from concurrent.futures import ThreadPoolExecutor
import sys
requests=parsed(R/sys.argv[1]);unique={}
for r in requests:
    if r['id'] in unique:assert unique[r['id']]['url']==r['url']
    else:unique[r['id']]=r
rows=list(unique.values())
def one(r):
    if (R/'acquired'/f"{r['id']}.receipt.json").exists():return
    return acquire(r['id'],r['url'],r.get('parent'),r.get('literal'))
with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(one,rows))
