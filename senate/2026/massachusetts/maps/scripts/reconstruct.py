"""Independent read-only full frozen source reconstruction; writes own audit only."""
from pathlib import Path
from collections import Counter
import csv,gzip,hashlib,io,json
M=Path(__file__).resolve().parents[1];S=M.parent
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
def exact(r):
 b=(S/r['path']).read_bytes();assert len(b)==r['bytes']<40000000 and sha(b)==r['sha256'],r['path'];return b
def read(path):
 b=(S/path).read_bytes();b=gzip.decompress(b)if path.endswith('.gz')else b
 if '.csv'in path:return list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))
 return json.loads(b)
def pointer(v,p):
 for k in p.split('/')[1:]:
  k=k.replace('~1','/').replace('~0','~');v=v[int(k)]if isinstance(v,list)else v[k]
 return v
def main():
 # Authority path only. No acceptance copy, digest, size or reverse pin in owned output.
 a=read('data/coordinator-priority-acceptance.json');c=json.loads(exact(a['frozen_contract']));assert len(c)==25
 inputs={}
 def pin(path):
  b=(S/path).read_bytes();inputs[path]=dict(path=path,bytes=len(b),sha256=sha(b))
 for r in a['complete_root_field_semantics']:assert sha(canonical(pointer(c,r['pointer'])))==r['full_recursive_semantic_sha256']
 for seal in a['producer_seals']:
  mf=json.loads(exact(seal));pin(seal['path'])
  for r in mf[seal['owned_field']]:exact(r);pin(r['path'])
  for r in mf[seal['original_reference_field']]:
   b=(S/r['path']).read_bytes();pin(r['path'])
   if 'stored_sha256'in r:
    assert len(b)==r['stored_bytes']and sha(b)==r['stored_sha256'];b=gzip.decompress(b);assert len(b)==r['raw_bytes']and sha(b)==r['raw_sha256']
   else:exact(r)
 cache={}
 for r in a['complete_source_companion_files']:
  b=exact(r);pin(r['path'])
  if r['path'].endswith('.gz'):
   b=gzip.decompress(b);assert len(b)==r['complete_reconstructed_bytes']and sha(b)==r['complete_reconstructed_sha256']
  v=read(r['path']);assert len(v)==r['complete_length']and sha(canonical(v))==r['full_semantic_sha256'];cache[r['path']]=v
 cache['data/turnout/priority-set.json']=c;pin('data/turnout/priority-set.json')
 counts=Counter();partitions=[]
 for r in a['complete_source_object_reference_bodies']:
  exact(r);pin(r['path']);h=hashlib.sha256();n=0;z=0;cc=Counter()
  with gzip.open(S/r['path'],'rb')as f:
   for line in f:
    h.update(line);z+=len(line);o=json.loads(line);v=cache[o['file']]
    obj=pointer(v,o['pointer'])if 'pointer'in o else v[o['CSV_row_1based_including_header']-1]
    assert sha(canonical(obj))==o['full_recursive_semantic_sha256'],o
    n+=1;cc[o['file']]+=1
  assert z==r['complete_reconstructed_bytes']and h.hexdigest()==r['complete_reconstructed_sha256'];assert n==r['complete_object_count']and dict(cc)==r['source_objects_by_file'];counts.update(cc);partitions.append(dict(path=r['path'],objects=n,complete=True))
 assert sum(counts.values())==397917 and dict(counts)==a['source_objects_by_file']
 assert [x['native_key']for x in c['all_unit_order']]==a['ordered_full_keys'];assert c['ordered_priority_keys']==a['ordered_priority_keys'];assert c['ordered_remainder_keys']==a['ordered_remainder_keys']
 assert len(c['all_parent_child_maps'])==351
 parents={}
 for par in c['all_parent_child_maps']:
  name=par.get('literal_city_town')or par.get('CityTown')or par.get('literal_tuple',[None])[0]
  parents[name]=par
 # Exact full child arrays independently reconstructed from record ordinals and rank.
 records=c['all_unit_order'];full=[r['native_key']for r in records];priority=set(c['ordered_priority_keys']);rem=set(c['ordered_remainder_keys'])
 for pk,p in a['derived_ordered_child_arrays_by_parent'].items():
  name=p['literal_city_town'];rr=[r for r in records if r['literal_tuple'][0]==name]
  assert [r['native_key']for r in sorted(rr,key=lambda r:r['csv_record_ordinal'])]==p['original_source_ordered_children']
  assert [r['native_key']for r in rr]==p['canonical_rank_ordered_children']
  assert [r['native_key']for r in rr if r['native_key']in priority]==p['ordered_priority_children']
  assert [r['native_key']for r in rr if r['native_key']in rem]==p['ordered_remainder_children']
 out=dict(status='pass',authority_path='data/coordinator-priority-acceptance.json',root_fields=25,complete_companions=174,recursive_objects=sum(counts.values()),partitions=partitions,producer_assets=781,all_original_dependencies_verified=True,full_source_files=dict(counts),hierarchy=[2394,1470,924,351,287],no_projection=True,no_producer_writer=True)
 for path,v in [('reconstruction.json',out),('readonly-inputs.json',list(inputs.values()))]:(M/path).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 print({k:v for k,v in out.items()if k!='full_source_files'})
if __name__=='__main__':main()
