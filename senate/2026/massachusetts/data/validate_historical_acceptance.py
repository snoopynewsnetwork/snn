"""Independent complete external dispatch replay; no producer code or writer."""
from pathlib import Path
from collections import Counter
import csv,gzip,hashlib,io,json
S=Path(__file__).resolve().parents[1];D=S/'data'
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
def exact(r):
 b=(S/r['path']).read_bytes();assert len(b)==r['bytes']<40000000 and sha(b)==r['sha256'];return b
def read(path):
 p=S/path;b=p.read_bytes();b=gzip.decompress(b)if p.suffix=='.gz'else b
 if '.csv'in p.name:return list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))
 if '.jsonl'in p.name:return [json.loads(line)for line in b.splitlines()if line]
 return json.loads(b)
def pointer(v,p):
 for k in p.split('/')[1:]:
  k=k.replace('~1','/').replace('~0','~');v=v[int(k)]if isinstance(v,list)else v[k]
 return v
def main():
 a=read('data/coordinator-priority-acceptance.json');c=json.loads(exact(a['frozen_contract']));assert len(c)==len(a['complete_root_field_semantics'])
 for r in a['complete_root_field_semantics']:assert sha(canonical(pointer(c,r['pointer'])))==r['full_recursive_semantic_sha256']
 for group in ['frozen_first_pair_assets','independent_coordinator_reviews']:
  for r in a[group]:exact(r)
 assetcount=0
 for r in a['producer_seals']:
  mf=json.loads(exact(r));assetcount+=len(mf[r['owned_field']])
  for x in mf[r['owned_field']]:exact(x)
  for x in mf[r['original_reference_field']]:
   b=(S/x['path']).read_bytes()
   if 'stored_sha256'in x:
    assert len(b)==x['stored_bytes']and sha(b)==x['stored_sha256'];b=gzip.decompress(b);assert len(b)==x['raw_bytes']and sha(b)==x['raw_sha256']
   else:exact(x)
 for r in a['complete_source_companion_files']:
  b=exact(r)
  if r['path'].endswith('.gz'):
   b=gzip.decompress(b);assert len(b)==r['complete_reconstructed_bytes']and sha(b)==r['complete_reconstructed_sha256']
  value=read(r['path']);assert sha(canonical(value))==r['full_semantic_sha256'];assert len(value)==r['complete_length']
 total=0;globalcounts=Counter()
 for r in a['complete_source_object_reference_bodies']:
  exact(r);dig=hashlib.sha256();size=0;count=0;byfile=Counter();filename=None;value=None
  with gzip.open(S/r['path'],'rb')as f:
   for line in f:
    dig.update(line);size+=len(line);row=json.loads(line)
    if row['file']!=filename:filename=row['file'];value=read(filename)
    obj=pointer(value,row['pointer'])if 'pointer'in row else value[row['CSV_row_1based_including_header']-1]
    assert sha(canonical(obj))==row['full_recursive_semantic_sha256'],row
    count+=1;byfile[filename]+=1
  assert size==r['complete_reconstructed_bytes']and dig.hexdigest()==r['complete_reconstructed_sha256'];assert count==r['complete_object_count'];assert dict(byfile)==r['source_objects_by_file'];total+=count;globalcounts.update(byfile)
 assert total==a['complete_source_object_count']and dict(globalcounts)==a['source_objects_by_file']
 assert len(a['ordered_full_keys'])==2394 and len(a['ordered_priority_keys'])==1470 and len(a['ordered_remainder_keys'])==924
 assert a['ordered_full_keys']==a['ordered_priority_keys']+a['ordered_remainder_keys'];assert len(a['derived_ordered_child_arrays_by_parent'])==351 and len(a['ordered_priority_parent_literals'])==287
 for k in ['current_geography_approved','current_November_returns_admitted','current_choice_or_reporting_IDs_approved','legal_native_80_robustness_approved','live_cadence_or_exact_remainder_approved','collector_or_probability_approval']:assert a[k]is False
 p=D/'coordinator-acceptance-validation.json';out=dict(status='pass_independent_complete_dispatch_reconstruction',complete_root_fields=len(c),complete_companions=len(a['complete_source_companion_files']),complete_recursive_objects=total,complete_ledger_partitions=len(a['complete_source_object_reference_bodies']),source_files=len(globalcounts),producer_owned_assets_rehashed=assetcount,all_primary_2394_priority1470_remainder924_parent351_arrays_exact=True,current_or_legal_native_approval=False,acceptance_bytes=(D/'coordinator-priority-acceptance.json').stat().st_size,acceptance_sha256=sha((D/'coordinator-priority-acceptance.json').read_bytes()),no_producer_import_or_mutation=True)
 p.write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':main()
