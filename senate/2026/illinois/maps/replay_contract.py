"""Independently stream ALL accepted recursive objects; authority is PATH ONLY.
Acceptance body/hashes are read at runtime, never copied into owned outputs.
"""
from common import *
from collections import Counter

def run():
 a=load(S/ACCEPTANCE);p=json.loads(exact(a['frozen_contract']))
 assert len(p)==len(a['complete_root_field_semantics'])==31
 for x in a['complete_root_field_semantics']:assert sem(resolve(p,x['pointer']))==x['full_recursive_semantic_sha256']
 for group in ['producer_seals','frozen_first_pair_assets','independent_coordinator_reviews']:
  for x in a[group]:exact(x)
 for x in a['complete_source_companion_files']:
  b=exact(x)
  if x['path'].endswith('.gz'):
   b=gzip.decompress(b);assert len(b)==x['complete_reconstructed_bytes'] and sha(b)==x['complete_reconstructed_sha256']
  if 'full_semantic_sha256' in x:assert sem(parsed(x['path']))==x['full_semantic_sha256']
 total=0;seen=Counter()
 for pin in a['complete_source_object_reference_bodies']:
  exact(pin);h=hashlib.sha256();n=0;file=None;v=None;counts=Counter()
  with gzip.open(S/pin['path'],'rb') as f:
   for line in f:
    h.update(line);n+=len(line);row=json.loads(line)
    if row['file']!=file:file=row['file'];v=parsed(file)
    if 'pointer' in row:o=resolve(v,row['pointer'])
    elif 'JSONL_record_1based' in row:o=v[row['JSONL_record_1based']-1]
    else:o=v[row['CSV_row_1based_including_header']-1]
    assert sem(o)==row['full_recursive_semantic_sha256'],row
    total+=1;counts[file]+=1;seen[file]+=1
  assert n==pin['complete_reconstructed_bytes'] and h.hexdigest()==pin['complete_reconstructed_sha256']
  assert dict(counts)==pin['source_objects_by_file']
 assert total==a['complete_source_object_count']==554096
 assets=refs=0
 for pin in a['producer_seals']:
  seal=json.loads(exact(pin))
  for x in seal[pin['owned_field']]:exact(x);assets+=1
  base=S if pin['original_reference_path_resolution']=='state-relative' else S/'data/baselines'
  for x in seal[pin['original_reference_field']]:
   b=exact(x,base);refs+=1
   if 'raw_sha256' in x:
    raw=gzip.decompress(b) if x['path'].endswith('.gz') else b
    assert len(raw)==x['raw_bytes'] and sha(raw)==x['raw_sha256']
 assert p['coordinator_acceptance'] is False and p['current_geometry_approved'] is False
 assert a['current_geography_approved'] is False and a['legal_native_80_robustness_approved'] is False
 out=dict(status='pass',external_authority_path=ACCEPTANCE,root_fields=31,complete_companions=116,recursive_objects=total,object_source_files=len(seen),producer_assets=assets,producer_original_references=refs,source_fields_categories_nulls_and_positions='Every full recursive semantic digest compared; no selected-field projection',producer_writes=False,source_reconstruction='Use complete original accepted pins and JSON pointers/CSV or JSONL positions read from external authority at runtime')
 dump('qa/contract-replay.json',out);print(json.dumps(out))
if __name__=='__main__':run()
