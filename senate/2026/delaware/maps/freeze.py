"""Launch-only external contract validation. Offline builds use frozen references.
External acceptance is path-only in all written objects; never hashed/copied there.
"""
from common import *
def main():
 a=read(S/'data/coordinator-priority-acceptance.json')
 c=read(S/a['frozen_contract']['path']);verify(a['frozen_contract'])
 cache={a['frozen_contract']['path']:c};checks=0
 for f in a['complete_source_companion_files']:
  raw=verify(f);v=read(S/f['path']);cache[f['path']]=v
  assert len(v)==f['complete_length'] and semantic(v)==f['full_semantic_sha256'];checks+=3
  if 'complete_header'in f:assert v[0]==f['complete_header'];checks+=1
  if 'complete_reconstructed_bytes'in f:
   b=gzip.decompress(raw);assert len(b)==f['complete_reconstructed_bytes'] and sha(b)==f['complete_reconstructed_sha256'];checks+=2
 for f in a['complete_root_field_semantics']:
  assert semantic(pointer(c,f['pointer']))==f['full_recursive_semantic_sha256'];checks+=1
 for f in a['complete_source_object_references']:
  if f['file'] not in cache:cache[f['file']]=read(S/f['file'])
  v=cache[f['file']];v=v[f['JSONL_record']-1] if 'JSONL_record'in f else pointer(v,f['pointer'])
  assert semantic(v)==f['full_recursive_semantic_sha256'];checks+=1
 assets={}
 for seal in a['producer_seals']:
  verify(seal);v=read(S/seal['path']);items=v['owned']+v['shared_originals'] if 'owned'in v else v['assets']
  for r in items:
   p=S/r['path'] if 'owned'in v else (S/'data/baselines'/r['path']).resolve();actual=pin(p)
   assert actual['bytes']==r['bytes'] and actual['sha256']==r['sha256'];assets[actual['path']]=actual;checks+=1
 refs=dict(external_acceptance_path='data/coordinator-priority-acceptance.json',contract=a['frozen_contract'],root_fields=a['complete_root_field_semantics'],companions=a['complete_source_companion_files'],objects=a['complete_source_object_references'],producer_seals=a['producer_seals'],producer_assets=list(assets.values()),projection_allowed=False)
 write('source/frozen-references.json.gz',refs)
 # Freeze individual original receipts in full, independently checking each original.
 receipts=read(S/'data/news/coordinator-map-preparation/acquisition-complete-v1.json')
 for r in receipts:body(r)
 write('source/reused-original-receipts.json',receipts)
 write('source/historical-receipts.json',read(S/'data/turnout/extracts/source-references.json'))
 write('source/reconstruction-override.json',dict(run_legacy_producers=False,mutable_aggregate_dependency=False,override='Use complete pinned source/original-inputs and source-references bodies and all producer assets from frozen-references; never consult mutable news manifest.',acceptance='data/coordinator-priority-acceptance.json',optional_coordinator_review_dependency=False,peer_dependency=False))
 write('qa/launch-validation.json',dict(status='pass',checks=checks,root_fields=len(c),companions=len(refs['companions']),objects=len(refs['objects']),producer_assets=len(assets),reused_individual_receipts=len(receipts)))
 print('PASS',checks,len(assets),'producer assets;',len(receipts),'individual originals')
if __name__=='__main__':main()
