"""Offline exact whole-entity reconstruction; no acceptance, network or producer run.
--verify checks all complete bodies/semantics/objects/sealed assets/individual receipts.
--source ID --output /tmp/original.pdf exports an exact acquired HTTP entity.
"""
from common import *
import argparse

def check():
 refs=read(M/'source/frozen-references.json.gz');cache={};checks=0
 for r in refs['producer_assets']+refs['producer_seals']+[refs['contract']]:verify(r);checks+=1
 c=read(S/refs['contract']['path']);cache[refs['contract']['path']]=c
 for r in refs['companions']:
  raw=verify(r);v=read(S/r['path']);cache[r['path']]=v;assert len(v)==r['complete_length'] and semantic(v)==r['full_semantic_sha256'];checks+=3
  if 'complete_header'in r:assert v[0]==r['complete_header'];checks+=1
  if 'complete_reconstructed_sha256'in r:
   b=gzip.decompress(raw);assert len(b)==r['complete_reconstructed_bytes'] and sha(b)==r['complete_reconstructed_sha256'];checks+=2
 for r in refs['root_fields']:assert semantic(pointer(c,r['pointer']))==r['full_recursive_semantic_sha256'];checks+=1
 for r in refs['objects']:
  if r['file']not in cache:cache[r['file']]=read(S/r['file'])
  v=cache[r['file']];v=v[r['JSONL_record']-1] if 'JSONL_record'in r else pointer(v,r['pointer'])
  assert semantic(v)==r['full_recursive_semantic_sha256'];checks+=1
 for r in read(M/'source/reused-original-receipts.json')+[read(p)for p in sorted((M/'source').glob('*.receipt.json'))]:body(r);checks+=2
 return checks

def main():
 p=argparse.ArgumentParser();p.add_argument('--verify',action='store_true');p.add_argument('--source');p.add_argument('--output');a=p.parse_args()
 if a.verify:print('PASS',check(),'whole-body/reference checks')
 if a.source:
  assert a.output,'--output required';out=Path(a.output);assert not out.exists(),'refusing overwrite'
  rs=[read(p)for p in (M/'source').glob('*.receipt.json')]+read(M/'source/reused-original-receipts.json');r=next(r for r in rs if r['id']==a.source);raw=body(r);out.write_bytes(raw);print(len(raw),sha(raw))
if __name__=='__main__':main()
