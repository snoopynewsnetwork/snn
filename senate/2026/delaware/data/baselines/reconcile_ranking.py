#!/usr/bin/env python3
from pathlib import Path
import csv,json,hashlib
P=Path(__file__).resolve().parent

def main():
 b=(P/'peer/stable-ranking-v1.json').read_bytes();assert hashlib.sha256(b).hexdigest()=='0ad49bfbf8ba36f9679c92f7ccdcc03cfa6bb67eb216a97a79c42fe363d0805e';peer=json.loads(b);own=json.loads((P/'priority-contracts.json').read_text());rs=list(csv.DictReader((P/'geography-ranking.csv').open()));checks=[]
 for key,r in peer.items():
  y,o=key.split('|');c=next(x for x in own if x['year']==int(y) and x['office_key']==o and x['view']=='byelectiondist' and x['metric']=='named_total');order=[[z['geo_key'],int(z['votes'])] for z in rs if z['year']==y and z['office_key']==o and z['view']=='byelectiondist' and z['metric']=='named_total'];assert order==r['order'],key
  for a,b in [('state_total','total'),('minimum80_count','minimum80_count'),('before_crossing','preceding_votes'),('at_crossing','priority_votes'),('top15_votes','top15_votes')]:assert c[a]==r[b],(key,a)
  checks.append(dict(key=key,order_count=len(order),full_order_exact=True,total=c['state_total'],minimum80_count=c['minimum80_count'],before=c['before_crossing'],at=c['at_crossing'],top15_votes=c['top15_votes']))
 out=dict(status='pass',peer_snapshot_sha256=hashlib.sha256((P/'peer/stable-ranking-v1.json').read_bytes()).hexdigest(),checks=checks,scope='Independent extraction full-field descending native order and exact minimum80 arithmetic agree. Neither worker accepts November2026 reporting/geometry or coordinator legal geographic approval.')
 (P/'peer/ranking-reconciliation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
