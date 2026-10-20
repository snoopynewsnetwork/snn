"""Read complete external acceptance by path; independently replay every referenced object.
Never writes or pins acceptance; no producer code is executed. Complete bodies remain at immutable original paths.
"""
from common import *
from collections import Counter

def exact(p,base=STATE):
 b=(base/p['path']).read_bytes();assert len(b)==p['bytes']<40000000,(p['path'],'size');assert sha(b)==p['sha256'],(p['path'],'hash');return b

def main(write_output=True):
 a=json.loads(ACCEPTANCE.read_bytes());contract=json.loads(exact(a['frozen_contract']));checks=0
 for f in a['complete_root_field_semantics']:
  assert sem(pointer(contract,f['pointer']))==f['full_recursive_semantic_sha256'];checks+=1
 assert len(contract)==len(a['complete_root_field_semantics'])==31
 refs={}
 for k in ['frozen_first_pair_assets','independent_coordinator_reviews','complete_source_companion_files']:
  for p in a[k]:
   b=exact(p);refs[p['path']]=p;checks+=1
   if 'complete_reconstructed_bytes' in p:
    z=gzip.decompress(b);assert len(z)==p['complete_reconstructed_bytes'] and sha(z)==p['complete_reconstructed_sha256'];checks+=1
   if 'full_semantic_sha256' in p:assert sem(parsefile(STATE/p['path']))==p['full_semantic_sha256'];checks+=1
 seal_counts=[]
 for p in a['producer_seals']:
  seal=json.loads(exact(p));refs[p['path']]=p
  for x in seal[p['owned_field']]:exact(x);refs[x['path']]=x;checks+=1
  base=STATE if p['original_reference_path_resolution']=='state-relative' else STATE/'data/baselines'
  for x in seal[p['original_reference_field']]:
   exact(x,base);y=dict(x,path=str((base/x['path']).resolve().relative_to(STATE.resolve())));refs[y['path']]=y;checks+=1
  seal_counts.append({'seal_path':p['path'],'owned_entries':len(seal[p['owned_field']]),'original_references':len(seal[p['original_reference_field']])})
 total=0;seen=Counter()
 for p in a['complete_source_object_reference_bodies']:
  exact(p);refs[p['path']]=p;digest=hashlib.sha256();n=0;cur=None;value=None
  with gzip.open(STATE/p['path'],'rb') as f:
   for line in f:
    digest.update(line);n+=len(line);r=json.loads(line)
    if r['file']!=cur:cur=r['file'];value=parsefile(STATE/cur)
    if 'pointer' in r:v=pointer(value,r['pointer'])
    elif 'JSONL_record_1based' in r:v=value[r['JSONL_record_1based']-1]
    else:v=value[r['CSV_row_1based_including_header']-1]
    assert sem(v)==r['full_recursive_semantic_sha256'],r;total+=1;seen[cur]+=1
  assert n==p['complete_reconstructed_bytes'] and digest.hexdigest()==p['complete_reconstructed_sha256'];assert dict(seen)==p['source_objects_by_file']
 assert total==a['complete_source_object_count']==554096
 assert all(a[k] is False for k in ['current_geography_approved','current_November_returns_admitted','current_choice_or_reporting_IDs_approved','legal_native_80_robustness_approved','live_cadence_or_exact_remainder_approved','collector_or_probability_approval'])
 result=dict(acceptance_path=str(ACCEPTANCE.relative_to(STATE)),status='pass',complete_root_fields=31,complete_companions=116,complete_recursive_source_objects=total,source_object_files=dict(seen),producer_seals=seal_counts,checks=checks+total,external_authority='path only; consulted at replay, not copied or pinned',producer_code_executed=False)
 if write_output:write(HERE/'frozen-replay.json',result)
 # These are individual immutable producer assets, never a copy/pin of acceptance.
 if write_output:write(HERE/'original-asset-references.json',dict(scope='complete producer assets and original references; external acceptance excluded',assets=[{'path':k,'bytes':v['bytes'],'sha256':v['sha256']} for k,v in sorted(refs.items())]))
 print(json.dumps(dict(objects=total,checks=checks+total,assets=len(refs))))
 return result
if __name__=='__main__':main()
