#!/usr/bin/env python3
"""Immutable reciprocal input comparisons, never edits peer outputs."""
from pathlib import Path
import gzip,json,hashlib,collections,csv
P=Path(__file__).resolve().parent

def main():
 peer=[json.loads(l) for l in gzip.decompress((P/'peer/candidate-rows.jsonl.gz').read_bytes()).decode().splitlines()]
 own=json.loads((P/'extracted/contest-tables.json').read_text());checks=[];diff=[]
 def key(r):return (r['year'],r['view'],r['office_key'],r['native_key'],r['row_index'])
 peers={key(r):r for r in peer};assert len(peers)==len(peer)
 seen=set();matched=0
 for tb in own:
  for rr in tb['rows']:
   geo=tb['geo_key'] or ('State' if tb['view']=='statewide' else tb['office_key'])
   k=(tb['year'],tb['view'],tb['office_key'],geo,rr['row_index'])
   pr=peers.get(k)
   if pr is None:
    # Peer native keys for horizontally presented county columns are view-office identities.
    options=[p for p in peer if p['year']==tb['year'] and p['view']==tb['view'] and p['office_key']==tb['office_key'] and p['row_index']==rr['row_index']]
    if len(options)==1:pr=options[0];k=key(pr)
   if pr is None:diff.append(dict(type='missing_peer',key=k));continue
   seen.add(k)
   for name,a,b in [('headers_fields',rr['fields'],pr['raw_fields']),('row_start',rr['source_char_start'],pr['row_start']),('row_end',rr['source_char_end'],pr['row_end']),('table_start',tb['source_char_start'],pr['table_start']),('table_end',tb['source_char_end'],pr['table_end'])]:
    if a!=b:diff.append(dict(type=name,key=k,own=a,peer=b))
   matched+=1
 extra=set(peers)-seen
 inv=json.loads((P/'peer/native-inventory.json').read_text());oi=json.loads((P/'extracted/table-inventory.json').read_text());coverage=[]
 for it in inv:
  yr=it['year'];a=set(it['election_districts']);b={r['geo_key'] for r in oi if r['year']==yr and r['view']=='byelectiondist'}
  coverage.append(dict(year=yr,own=len(b),peer=len(a),only_own=sorted(b-a),only_peer=sorted(a-b)));assert a==b
 result=dict(matched_source_rows=matched,own_source_rows=sum(len(tb['rows']) for tb in own),peer_source_rows=len(peer),unmatched_peer_rows=len(extra),differences=diff,native_inventory=coverage,scope='All five contexts; all candidate/raw headers/cells-as-fields and source table/row positions in five overlapping views. Key strings are source scoped. Priority order separately compared after peer ranking is stable.')
 (P/'peer/reconciliation-v1.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='differences'},indent=2));print('differences',len(diff),diff[:2])
if __name__=='__main__':main()
