#!/usr/bin/env python3
"""Read-only reciprocal comparison against frozen independent peer originals extract."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,gzip,hashlib,collections
D=Path(__file__).resolve().parent;P=D/'peer/stable-extraction-v1';X=D/'extracts'
def main():
 own=[json.loads(l) for l in gzip.decompress((X/'candidate-rows.jsonl.gz').read_bytes()).splitlines()]
 pt=json.loads((P/'extracted/contest-tables.json').read_text());peer=[]
 for t in pt:
  for r in t['rows']:
   peer.append({'year':t['year'],'source_id':t['source_id'],'view':t['view'],'office_key':t['office_key'],'native_key':t['geo_key'] if t['geo_key'] is not None else t['view'],'table_start':t['source_char_start'],'table_end':t['source_char_end'],'row_start':r['source_char_start'],'row_end':r['source_char_end'],'raw_fields':r['fields'],'row_index':r['row_index']})
 def key(r):return (r['year'],r['source_id'],r['view'],r['office_key'],r['native_key'],r['row_start'])
 a={key(r):r for r in own};b={key(r):r for r in peer};assert len(a)==len(own) and len(b)==len(peer)
 differences=[]
 for k in a.keys()&b.keys():
  for field in ['raw_fields','table_start','table_end','row_start','row_end','row_index']:
   if a[k][field]!=b[k][field]:differences.append({'key':k,'field':field,'own':a[k][field],'peer':b[k][field]})
 missing_a=sorted(b.keys()-a.keys());missing_b=sorted(a.keys()-b.keys())
 out={'peer_actual_id':'4724b2aa-c338-4708-8044-c4b606bfaaeb','scope':'five contexts, all five report views, every raw field and table/row source position; own original extraction stabilized before capture','own_rows':len(own),'peer_rows':len(peer),'matched':len(a.keys()&b.keys()),'differences':differences,'unmatched_own':missing_b,'unmatched_peer':missing_a,'pass':not(differences or missing_a or missing_b),'capture_manifest_sha256':hashlib.sha256((P/'capture-manifest.json').read_bytes()).hexdigest()}
 (D/'peer/reconciliation-v1.json').write_text(json.dumps(out,indent=2)+'\n');assert out['pass'];print(json.dumps(out))
def compare_rank():
 import csv
 own=json.loads((D/'stable-ranking-v1.json').read_text());peer=json.loads((D/'peer/ranking-v1/priority-contracts.json').read_text());rr=list(csv.DictReader((D/'peer/ranking-v1/geography-ranking.csv').open()))
 checks=[]
 for key,o in own.items():
  year,office=key.split('|');p=next(p for p in peer if p['year']==int(year) and p['office_key']==office and p['view']=='byelectiondist' and p['metric']=='named_total')
  pr=[p for p in rr if p['year']==year and p['office_key']==office and p['view']=='byelectiondist' and p['metric']=='named_total'];pr.sort(key=lambda r:int(r['rank']))
  order=[[r['geo_key'],int(r['votes'])] for r in pr]
  fields={'full_descending_order_votes':o['order']==order,'native_keys_order':p['descending_order']==[r[0] for r in o['order']],'state_total':p['state_total']==o['total'],'minimum80_count':p['minimum80_count']==o['minimum80_count'],'before_crossing':p['before_crossing']==o['preceding_votes'],'at_crossing':p['at_crossing']==o['priority_votes'],'top15':p['top15_votes']==o['top15_votes']}
  assert all(fields.values()),(key,fields);checks.append({'context':key,'native_rows':len(order),'checks':fields})
 out={'peer_actual_id':'4724b2aa-c338-4708-8044-c4b606bfaaeb','pass':True,'scope':'full literal native-key descending sequence with integer votes, plus threshold and top15 controls for all five contexts','checks':checks,'own_stable_sha256':hashlib.sha256((D/'stable-ranking-v1.json').read_bytes()).hexdigest(),'peer_capture_manifest_sha256':hashlib.sha256((D/'peer/ranking-v1/capture-manifest.json').read_bytes()).hexdigest()}
 (D/'peer/rank-reconciliation.json').write_text(json.dumps(out,indent=2)+'\n');print('full-order peer rank agreement: five contexts pass')
if __name__=='__main__':main();compare_rank()
