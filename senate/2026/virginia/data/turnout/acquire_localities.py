#!/usr/bin/env python3
"""One bounded full-state original native/method control inventory from source-linked IDs."""
import concurrent.futures,gzip,json
from pathlib import Path
from acquire import acquire
HERE=Path(__file__).resolve().parent
p=HERE/'source/acquired';o=json.loads(gzip.decompress((p/'enr-2024-senate.hop0.gz').read_bytes()))
def run(pair):
 i,b=pair;code=b['locality']['mapFeatureId'];id='enr-native-'+code
 if (p/f'{id}.receipt.json').exists():
  r=json.loads((p/f'{id}.receipt.json').read_text())
  if r['hops'][-1].get('status')==200:return
 u=f"https://enr.elections.virginia.gov/results/public/api/elections/{b['locality']['shortName']}/2024NovemberGeneral/data/ballot-item/{b['parentBallotItemId']}"
 acquire(id,u,f'enr-2024-senate /ballotItemWithBreakdown/breakdownResults/{i}; enr-services-js getData')
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as e:list(e.map(run,enumerate(o['ballotItemWithBreakdown']['breakdownResults'])))
