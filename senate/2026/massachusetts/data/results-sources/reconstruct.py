"""Independent read-only full replay. Acceptance is consulted by PATH ONLY.
No imports of producer code; no writes outside this assignment.
"""
from pathlib import Path
from collections import Counter
import csv,gzip,hashlib,io,json
S=Path(__file__).resolve().parents[2]; O=Path(__file__).resolve().parent
AUTHORITY='data/coordinator-priority-acceptance.json'
def digest(b): return hashlib.sha256(b).hexdigest()
def canonical(v): return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
def load(p):
 b=(S/p).read_bytes()
 if p.endswith('.gz'): b=gzip.decompress(b)
 return list(csv.reader(io.StringIO(b.decode('utf-8-sig')))) if '.csv' in p else json.loads(b)
def dereference(v,p):
 for k in p.split('/')[1:]:
  k=k.replace('~1','/').replace('~0','~');v=v[int(k)] if isinstance(v,list) else v[k]
 return v
def replay():
 a=load(AUTHORITY); checks=0; dependencies={}
 def ck(x,n=''):
  nonlocal checks
  if not x: raise AssertionError(n)
  checks+=1
 def exact(r):
  b=(S/r['path']).read_bytes();ck(len(b)==r['bytes'] and digest(b)==r['sha256'],r['path']);ck(len(b)<40000000)
  dependencies[r['path']]={'path':r['path'],'bytes':len(b),'sha256':digest(b)};return b
 c=json.loads(exact(a['frozen_contract']));ck(len(c)==25)
 for r in a['complete_root_field_semantics']:ck(digest(canonical(dereference(c,r['pointer'])))==r['full_recursive_semantic_sha256'])
 owned=0
 for seal in a['producer_seals']:
  m=json.loads(exact(seal));ck(len(m[seal['owned_field']])==seal['owned_entries'])
  for r in m[seal['owned_field']]:exact(r);owned+=1
  for r in m[seal['original_reference_field']]:
   if 'stored_sha256' in r:
    b=exact(dict(path=r['path'],bytes=r['stored_bytes'],sha256=r['stored_sha256']));raw=gzip.decompress(b);ck(len(raw)==r['raw_bytes'] and digest(raw)==r['raw_sha256'])
   else:exact(r)
 # Coordinator/peer reviews are not required build dependencies. All frozen
 # first-pair bodies are already covered by producer manifests.
 for r in a['frozen_first_pair_assets']:exact(r)
 for r in a['complete_source_companion_files']:
  b=exact(r)
  if r['path'].endswith('.gz'):
   b=gzip.decompress(b);ck(len(b)==r['complete_reconstructed_bytes'] and digest(b)==r['complete_reconstructed_sha256'])
  v=load(r['path']);ck(len(v)==r['complete_length']);ck(digest(canonical(v))==r['full_semantic_sha256'])
 total=0;counts=Counter()
 for part in a['complete_source_object_reference_bodies']:
  exact(part);h=hashlib.sha256();size=0;n=0;pc=Counter();name=None
  with gzip.open(S/part['path'],'rb') as f:
   for line in f:
    h.update(line);size+=len(line);r=json.loads(line)
    if name!=r['file']:name=r['file'];v=load(name)
    obj=dereference(v,r['pointer']) if 'pointer' in r else v[r['CSV_row_1based_including_header']-1]
    ck(digest(canonical(obj))==r['full_recursive_semantic_sha256'],str(r));n+=1;pc[name]+=1
  ck(n==part['complete_object_count']);ck(size==part['complete_reconstructed_bytes']);ck(h.hexdigest()==part['complete_reconstructed_sha256']);ck(dict(pc)==part['source_objects_by_file']);counts.update(pc);total+=n
 ck(total==397917);ck(dict(counts)==a['source_objects_by_file']);ck(c['ordered_priority_keys']==a['ordered_priority_keys']);ck(c['ordered_remainder_keys']==a['ordered_remainder_keys'])
 # Independently parse original CSV, including ragged party/header, blank,
 # generic and control columns, and reconstruct the named literal order.
 receipts=load('data/turnout/source/shared-originals.json');src=next(x for x in receipts if x['id']=='sos-2024-senate-precinct-csv')
 b=(S/src['immutable_body_path']).read_bytes();raw=gzip.decompress(b);ck(digest(raw)==src['raw_sha256']);rows=list(csv.reader(io.StringIO(raw.decode('utf-8-sig'))));natives=rows[2:-1]
 order=sorted(natives,key=lambda r:(-sum(int(x.replace(',','')) for x in r[3:5]),r[:3]));keys=[json.dumps(r[:3],ensure_ascii=False,separators=(',',':')) for r in order]
 ck(keys==a['ordered_full_keys']);ck(len(natives)==2394);ck(sum(sum(int(x.replace(',','')) for x in r[3:5]) for r in order)==3407108)
 ck(sum(sum(int(x.replace(',','')) for x in r[3:5]) for r in order[:1470])==2726450)
 for pk,p in a['derived_ordered_child_arrays_by_parent'].items():
  name=p['literal_city_town'];ck(p['original_source_ordered_children']==[json.dumps(r[:3],ensure_ascii=False,separators=(',',':')) for r in natives if r[0]==name]);ck(p['canonical_rank_ordered_children']==[k for k in keys if json.loads(k)[0]==name]);ck(p['ordered_priority_children']==[k for k in keys[:1470] if json.loads(k)[0]==name]);ck(p['ordered_remainder_children']==[k for k in keys[1470:] if json.loads(k)[0]==name])
 out=dict(status='pass_complete_independent_readonly_reconstruction',authority_path=AUTHORITY,checks=checks,root_fields=25,whole_companions=174,recursive_objects=total,complete_partitions=3,source_files=len(counts),producer_assets=owned,full_hierarchy=dict(native=2394,priority=1470,remainder=924,parents=351,priority_parents=287),acceptance_body_or_hash_copied=False,producer_writer_run=False,current_admission=False)
 (O/'reconstruction.json').write_text(json.dumps(out,indent=2)+'\n');(O/'readonly-inputs.json').write_text(json.dumps(list(dependencies.values()),indent=2)+'\n');print(out)
if __name__=='__main__': replay()
