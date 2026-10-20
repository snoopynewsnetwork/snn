"""Independent full frozen graph replay; no producer code import or writes."""
from common import *
import csv,io,collections
AUTHORITY='data/coordinator-source-research-acceptance.json'
def semantic(v):return sha(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def parse(p):
 b=p.read_bytes();b=gzip.decompress(b)if p.suffix=='.gz'else b
 return list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))if '.csv'in p.name else json.loads(b)
def at(obj,path):
 for item in path.split('/')[1:]if path else []:
  item=item.replace('~1','/').replace('~0','~');obj=obj[int(item)]if isinstance(obj,list)else obj[item]
 return obj
def run():
 a=json.loads((S/AUTHORITY).read_bytes());checks=0;refs={}
 def verify(r):
  nonlocal checks
  p=S/r['path'];actual=pin(p);assert actual=={k:r[k]for k in actual},r['path'];checks+=1;refs[(r['path'],r['sha256'])]=actual
 verify(a['frozen_contract']);c=parse(S/a['frozen_contract']['path'])
 assert len(c)==31 and len(c['constituents'])==2201 and len(c['county_contexts'])==33
 for f in a['complete_root_field_semantics']:assert semantic(at(c,f['pointer']))==f['full_recursive_semantic_sha256'];checks+=1
 bodypins=0;original_entities=[];original_raw_checks=0
 for seal in a['producer_seals']:
  verify(seal);v=parse(S/seal['path']);rows=v[seal['owned_field']]+v[seal['original_reference_field']]
  assert len(rows)==seal['owned_entries']+seal['original_entries']
  for r in rows:
   verify(r);bodypins+=1
   if 'raw_sha256'in r:
    z=(S/r['path']).read_bytes();raw=gzip.decompress(z)if r['path'].endswith('.gz')else z
    assert sha(raw)==r['raw_sha256']
    if 'raw_bytes'in r:assert len(raw)==r['raw_bytes']
    original_entities.append(r);original_raw_checks+=1;checks+=1
 for r in a['complete_source_companion_files']:
  verify(r);v=parse(S/r['path']);assert len(v)==r['complete_length']and semantic(v)==r['full_semantic_sha256'];checks+=1
 total=0;filecounts=collections.Counter();loaded=None;v=None
 for part in a['complete_source_object_reference_bodies']:
  verify(part);digest=hashlib.sha256();size=0;counts=collections.Counter()
  with gzip.open(S/part['path'],'rb')as stream:
   for line in stream:
    digest.update(line);size+=len(line);r=json.loads(line)
    if r['file']!=loaded:loaded=r['file'];v=parse(S/loaded)
    obj=v[r['CSV_row_1based_including_header']-1]if 'CSV_row_1based_including_header'in r else at(v,r['pointer'])
    assert semantic(obj)==r['full_recursive_semantic_sha256'],r
    checks+=1;counts[loaded]+=1;filecounts[loaded]+=1;total+=1
  assert sum(counts.values())==part['complete_object_count']and dict(counts)==part['source_objects_by_file']
  assert size==part['complete_reconstructed_bytes']and digest.hexdigest()==part['complete_reconstructed_sha256'];checks+=3
 assert total==403993 and dict(filecounts)==a['source_objects_by_file']
 history=0
 for snap in a['immutable_historical_snapshot_body_resolvers']:
  verify(snap['capture'])
  for r in snap['complete_records']:
   verify(r['immutable_stored_body']);b=(S/r['immutable_stored_body']['path']).read_bytes();b=gzip.decompress(b)if r['storage']=='lossless_gzip_body'else b
   assert len(b)==r['original_bytes']and sha(b)==r['original_sha256'];history+=1;checks+=1
 assert history==196
 assert c['ordered_priority_keys']==[] and all(c[k]is None for k in ['certified_native_full_order','certified_native_minimum80','certified_native_top15'])
 keys=[r['key']for r in c['constituents']];assert keys==a['source_ordered_all_native_keys']and set(keys)==set(a['complete_coverage_sequence_keys'])and len(set(keys))==2201
 for p in c['county_contexts']:
  children=[r['key']for r in c['constituents']if r['parent_key']==p['key']]
  assert children==p['source_native_constituent_keys']==a['derived_full_child_arrays_by_parent'][p['key']]['complete_source_ordered_children'];checks+=1
 # Independent bodies are pinned, never replaced by producer writer dependencies.
 out={'authority_path':AUTHORITY,'frozen_contract':a['frozen_contract'],'complete_companions':a['complete_source_companion_files'],'complete_object_ledgers':a['complete_source_object_reference_bodies'],'immutable_historical_snapshot_body_resolvers':a['immutable_historical_snapshot_body_resolvers'],'complete_body_pins':list(refs.values()),'complete_original_entity_references':original_entities}
 write(M/'immutable-inputs.json',out)
 proof=dict(status='pass',authority_path=AUTHORITY,checks=checks,contract_root_fields=len(c),companions=68,recursive_objects=total,ledger_partitions=3,producer_and_original_pins=bodypins,historical_virtual_bodies=history,original_entity_raw_checks=original_raw_checks,observations=2201,parents=33,certified_priority=None,priority_keys=[],bounded_memory='one parsed whole companion at a time plus one streamed JSONL line; original byte bodies verified individually')
 write(M/'replay-proof.json',proof);print(proof)
if __name__=='__main__':run()
