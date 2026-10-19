"""One-time copy of small receipt metadata; reference complete originals by hash.
Never runs another owner's writer, and never copies their large originals.
"""
from common import *
def main():
 out=MAPS/'source/reused-receipts.json'
 assert not out.exists(),'Frozen metadata exists; do not replace snapshots'
 prep=STATE/'data/coordinator-map-preparation';a=json.loads((prep/'acquisition-Census-stage-v2.json').read_bytes())
 # Original snapshot is read fully; build depends on individual frozen receipts below,
 # not the mutable aggregate and not a coordinator script.
 for e in a:original(e)
 d=[]
 for name in ['sos-election-root','sos-auditor-resources','county-directory','sdaco','sdaco-counties']:
  d.append(STATE/'data/results-sources/raw'/f'{name}.receipt.json')
 c=json.loads((STATE/CONTRACT).read_bytes())
 for p in c['county_parents']:
  f=p['parent_key']
  for kind in ['local','local-detail','local-election']:
   q=STATE/'data/results-sources/raw'/f'{kind}-{f}.receipt.json'
   if q.exists():d.append(q)
 for p in d:
  e=json.loads(p.read_bytes());e['receipt_pin']=pin(p)
  e['stored_objects']=[dict(x,path='data/results-sources/'+x['path']) for x in e['stored_parts']]
  e['id']='peer-'+e['id'];original(e);a.append(e)
 dump('source/reused-receipts.json',a)
 dump('source/preparation-individual-pins.json',[pin(prep/n) for n in ['primary-web-reader-discovery.json','Census2020-native-structure.json.gz','PDF-original-inspection.json','bounded-visual-review.json']]+[pin(STATE/'data/coordinator-map-native-preparation-review.json')])
 print(len(a),'individually audited original receipts')
if __name__=='__main__':main()
