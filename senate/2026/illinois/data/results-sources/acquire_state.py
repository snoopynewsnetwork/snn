from common import *
from concurrent.futures import ThreadPoolExecutor
# Each exact URL is either user-specified official root, captured immutable navigation, or primary-search discovery.
seed=[('state-home','https://www.elections.il.gov/',None,None,'official publisher root'),('state-directory','https://www.elections.il.gov/ElectionOperations/ElectionAuthorities.aspx?MID=cQHxtxVEmuo%3D',None,None,'primary official directory discovered by web search'),('state-november','https://www.elections.il.gov/ElectionOperations/ElectionInformation.aspx?ElectionID=sejIrI%2bQmww%3d','data/baselines/source/current-home-public-retry-7190fa509f74.gz','/ElectionOperations/ElectionInformation.aspx?ElectionID=sejIrI%2bQmww%3d','exact captured homepage navigation'),('state-results-search','https://www.elections.il.gov/electionoperations/votetotalsearch.aspx',None,None,'official source specified in first-pair and newsroom reports')]
def work(x):
 id,url,p,h,b=x;m=fetch(id,url,p,h,basis=b);inspect(m);return id,m.get('status'),m.get('error')
# A prior sandbox DNS failure is retained under its exact receipt, not overwritten.
for x in seed:
 p=HERE/'receipts'/f'{x[0]}.json'
 if p.exists() and not json.loads(p.read_bytes()).get('complete'):
  p.rename(p.with_name(p.stem+'-sandbox-dns.json'))
with ThreadPoolExecutor(max_workers=3) as pool:
 for x in pool.map(work,seed):print(x,flush=True)
