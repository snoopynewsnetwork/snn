from common import *
import concurrent.futures,re
jobs=[]
for name,pattern in [('map-hop-35049-1',r'^2026 Precinct Map'),('map-election-35027',r'^Lincoln County Precinct map$'),('map-election-35055',r'^New Commission Districts and Precincts'),('map-election-35061',r'^Maps$')]:
 for l in links(name):
  if re.search(pattern,l['text'],re.I):jobs.append((name+'-precinct-original',l['url'],name,l));break
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
  for r in pool.map(lambda x:fetch(*x,timeout=60),jobs):print(r['id'],r.get('status'),r.get('error'),r.get('body',{}).get('raw_bytes'),flush=True)
