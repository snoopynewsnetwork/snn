"""Independent complete source-coverage authority replay, no producer writer/import."""
from pathlib import Path
import csv,gzip,hashlib,io,json
from collections import Counter
S=Path(__file__).resolve().parents[1];D=S/'data';N=0
sha=lambda b:hashlib.sha256(b).hexdigest()
def ck(v,note=''):
 global N
 assert v,note
 N+=1
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))
def read(p):
 b=p.read_bytes();b=gzip.decompress(b)if p.suffix=='.gz'else b
 return list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))if'.csv'in p.name else json.loads(b)
def semantic(v):return sha(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def locate(v,pointer):
 if not pointer:return v
 for k in pointer[1:].split('/'):
  k=k.replace('~1','/').replace('~0','~');v=v[int(k)]if isinstance(v,list)else v[k]
 return v
def main():
 a=read(D/'coordinator-source-research-acceptance.json');ck(a['status']=='accepted_complete_source_coverage_research_certified_native_priority_unavailable')
 c=read(S/a['frozen_contract']['path']);ck(pin(S/a['frozen_contract']['path'])==a['frozen_contract']);ck(len(c)==len(a['complete_root_field_semantics'])==31)
 for r in a['complete_root_field_semantics']:ck(semantic(locate(c,r['pointer']))==r['full_recursive_semantic_sha256'])
 ck(len(c['constituents'])==2201 and len(c['county_contexts'])==33);ck(c['ordered_priority_keys']==a['ordered_priority_keys']==[])
 for name in ['certified_native_full_order','certified_native_top15','certified_native_minimum80']:ck(a[name]is None and c[name]is None)
 for name in ['current_geography_approved','current_November_returns_admitted','current_choice_or_reporting_IDs_approved','legal_native_80_robustness_approved','live_cadence_or_exact_remainder_approved','collector_or_probability_approval']:ck(a[name]is False)
 ck(not c['accepted_for_dispatch']and not a['county_dispatch_substitution_authorized'])
 manifests=0
 for seal in a['producer_seals']:
  p=S/seal['path'];ck(pin(p)=={k:seal[k]for k in ['path','bytes','sha256']});m=read(p);rows=m[seal['owned_field']];ck(len(rows)==seal['owned_entries'])
  for r in rows+m[seal['original_reference_field']]:ck(pin(S/r['path'])=={k:r[k]for k in ['path','bytes','sha256']});manifests+=1
 for r in a['frozen_first_pair_assets']+a['independent_coordinator_reviews']:ck(pin(S/r['path'])==r)
 companions={r['path']:r for r in a['complete_source_companion_files']};ck(len(companions)==68)
 for file,r in companions.items():
  p=S/file;ck(pin(p)=={k:r[k]for k in ['path','bytes','sha256']});v=read(p);ck(len(v)==r['complete_length'] and semantic(v)==r['full_semantic_sha256'])
 total=0;files=Counter();current_file=None;value=None
 for part in a['complete_source_object_reference_bodies']:
  p=S/part['path'];ck(pin(p)=={k:part[k]for k in ['path','bytes','sha256']});digest=hashlib.sha256();size=count=0;perfile=Counter()
  with gzip.open(p,'rb')as f:
   for line in f:
    digest.update(line);size+=len(line);row=json.loads(line);file=row['file']
    if file!=current_file:current_file=file;value=c if file==a['frozen_contract']['path']else read(S/file)
    if 'CSV_row_1based_including_header'in row:obj=value[row['CSV_row_1based_including_header']-1]
    else:obj=locate(value,row['pointer'])
    ck(semantic(obj)==row['full_recursive_semantic_sha256']);perfile[file]+=1;files[file]+=1;count+=1;total+=1
  ck(count==part['complete_object_count']and size==part['complete_reconstructed_bytes']and digest.hexdigest()==part['complete_reconstructed_sha256']);ck(dict(perfile)==part['source_objects_by_file'])
 ck(total==a['complete_source_object_count']==403993);ck(dict(files)==a['source_objects_by_file'])
 history=0
 for snapshot in a['immutable_historical_snapshot_body_resolvers']:
  ck(pin(S/snapshot['capture']['path'])==snapshot['capture'])
  for r in snapshot['complete_records']:
   p=S/r['immutable_stored_body']['path'];ck(pin(p)==r['immutable_stored_body']);z=p.read_bytes();raw=gzip.decompress(z)if r['storage']=='lossless_gzip_body'else z
   ck(len(raw)==r['original_bytes']and sha(raw)==r['original_sha256']);history+=1
 ck(history==196)
 allkeys=[r['key']for r in c['constituents']];ck(allkeys==a['source_ordered_all_native_keys']);ck(set(allkeys)==set(a['complete_coverage_sequence_keys'])and len(set(allkeys))==2201)
 for key,parent in a['derived_full_child_arrays_by_parent'].items():ck(parent['complete_source_ordered_children']==[r['key']for r in c['constituents']if r['parent_key']==key])
 out=dict(status='pass_complete_qualified_source_authority_independent_replay',checks=N,root_fields=31,complete_companions=68,complete_recursive_objects=total,complete_ordered_partitions=len(a['complete_source_object_reference_bodies']),producer_body_and_original_pins=manifests,complete_historical_virtual_bodies=history,all_native_source_entries=2201,all_research_parents=33,canonical_certified_priority=None,private_allocation_or_county_substitution=False,authority=pin(D/'coordinator-source-research-acceptance.json'),producer_flags_unchanged=True,current_approvals_false=True)
 p=D/'coordinator-source-acceptance-validation.json';p.write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':main()
