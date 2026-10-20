from common import *
ROOTS={
 'sos-maps':'https://www.sos.nm.gov/sos-archive/maps-archive/',
 'sos-base':'https://www.sos.nm.gov/sos-archive/maps-archive/nm-county-standard-base-maps-archive/',
 'sos-gis':'https://www.sos.nm.gov/sos-archive/maps-archive/gis-voting-district-data-archive/',
 'sos-clerks':'https://www.sos.nm.gov/voting-and-elections/county-clerk-information/'
}
if __name__=='__main__':
 import argparse,concurrent.futures
 a=argparse.ArgumentParser();a.add_argument('--roots',action='store_true');args=a.parse_args()
 if args.roots:
  with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
   for r in pool.map(lambda kv:fetch(*kv,basis='SOS primary directory; URL independently observed in web search'),ROOTS.items()):print(r['id'],r.get('status'),r.get('error'))
 else:
  for p in sorted((M/'receipts').rglob('*.json')):
   r=json.loads(p.read_bytes())
   for e in r['requests']:
    if e.get('body'):body(e['body'])
  print('Offline complete original receipts verified')
