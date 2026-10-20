#!/usr/bin/env python3
from pathlib import Path
import json,gzip,hashlib
D=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 out=D/'source/pre-peer-witness.json'
 if out.exists():raise SystemExit('Immutable original-first witness already exists; never overwrite')
 native=json.loads((D/'extract/native-contests.json').read_text());rows=[r for c in native['2024-senate'] for r in c['rows']];ranked=sorted(rows,key=lambda r:(-r['numeric_sum'],r['key']));total=sum(r['numeric_sum'] for r in rows);cum=0;order=[];cut=None
 for rank,r in enumerate(ranked,1):
  cum+=r['numeric_sum'];order.append({'rank':rank,'key':r['key'],'county':r['county'],'label':r['label'],'candidate_votes':r['numeric_sum'],'cumulative_votes':cum})
  if cut is None and 5*cum>=4*total:cut=rank
 priority={'basis':'2024-senate six published candidate columns; no write-in allocation','tie_order':'descending integer candidate_votes then exact source-position key lexical','total':total,'threshold_integer':(4*total+4)//5,'minimum_count':cut,'before_votes':order[cut-2]['cumulative_votes'],'crossing_votes':order[cut-1]['cumulative_votes'],'order':order,'priority_keys':[r['key'] for r in order[:cut]],'remainder_keys':[r['key'] for r in order[cut:]],'accepted_by_coordinator':False}
 (D/'priority-set.json').write_text(json.dumps(priority,indent=2)+'\n')
 snaps=D/'source/original-first-bodies';snaps.mkdir(exist_ok=True);pins=[]
 for p in [D/'source/original-references.json',D/'extract/native-contests.json',D/'extract/county-candidate-controls.json',D/'extract/ballot-records.json',D/'extract/turnout-controls.json',D/'extract/clerk-2020-section.json',D/'priority-set.json',D/'scripts/extract_originals.py']:
  b=p.read_bytes();q=snaps/(p.name+'.gz');q.write_bytes(gzip.compress(b,mtime=0));pins.append({'path':str(p.relative_to(D)),'sha256':sha(b),'bytes':len(b),'frozen_body':str(q.relative_to(D)),'stored_sha256':sha(q.read_bytes()),'stored_bytes':q.stat().st_size})
 out.write_text(json.dumps({'phase':'independent-original-first before any peer derivative read','pins':pins,'original_receipts_sha256':sha((D/'source/original-references.json').read_bytes()),'peer_read':False},indent=2)+'\n');print(json.dumps({'witness':sha(out.read_bytes()),'priority':sha((D/'priority-set.json').read_bytes()),'total':total,'cut':cut,'before':priority['before_votes'],'crossing':priority['crossing_votes']}))
if __name__=='__main__':main()
