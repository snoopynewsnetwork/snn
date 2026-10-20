"""Independent complete authority walk; no producer imports, writes or current-peer discovery."""
from common import *
from collections import Counter,defaultdict
import tarfile,zipfile

def walk(x,p=''):
 if isinstance(x,(dict,list)):
  yield p,x
  for k,v in x.items() if isinstance(x,dict) else enumerate(x):
   if isinstance(v,(dict,list)):yield from walk(v,p+'/'+str(k).replace('~','~0').replace('/','~1'))
def run():
 a=json.loads((S/AUTHORITY).read_bytes());c=parsed(S/a['frozen_contract']['path']);verify((S/a['frozen_contract']['path']).read_bytes(),a['frozen_contract'])
 n=Counter();byfile=Counter()
 for p in a['frozen_file_pins']:verify((S/p['path']).read_bytes(),p);n['current_pins']+=1
 for (k,v),r in zip(c.items(),a['complete_root_field_semantics'],strict=True):
  assert r['pointer']=='/'+k and semantic(v)==r['full_recursive_semantic_sha256'];n['roots']+=1
 def refs():
  for r in a['complete_source_object_reference_bodies']:
   b=(S/r['path']).read_bytes();verify(b,r);raw=gzip.decompress(b)
   assert len(raw)==r['complete_reconstructed_bytes'] and sha(raw)==r['complete_reconstructed_sha256']
   lines=raw.splitlines();assert len(lines)==r['complete_object_count'];n['partitions']+=1
   for line in lines:yield json.loads(line)
 it=iter(refs())
 def check(file,ptr,obj):
  assert next(it)==dict(file=file,pointer=ptr,full_recursive_semantic_sha256=semantic(obj)),(file,ptr)
  n['recursive_objects']+=1;byfile[file]+=1
 for k,v in c.items():check(a['frozen_contract']['path'],'/'+k,v)
 for r in a['complete_source_companion_files']:
  b=(S/r['path']).read_bytes();verify(b,r);x=parsed(S/r['path'])
  assert semantic(x)==r['full_semantic_sha256'] and type(x).__name__==r['semantic_type'] and len(x)==r['complete_length']
  for ptr,obj in walk(x):check(r['path'],ptr,obj)
  n['whole_companions']+=1
 assert next(it,None) is None and dict(byfile)==a['source_objects_by_file'] and n['recursive_objects']==a['complete_source_object_count']
 groups=defaultdict(list)
 for r in a['historical_full_body_resolvers']:
  st=r['storage'];kind=st['kind']
  if kind=='immutable_original_reference':
   b=(S/st['file']['path']).read_bytes();verify(b,st['file']);verify(b,r);n['historical_bodies']+=1
  else:groups[(kind,canon(st.get('archive',st.get('parts'))))].append(r)
 for (kind,_),rows in groups.items():
  st=rows[0]['storage']
  if kind=='tar_gzip_member':
   z=(S/st['archive']['path']).read_bytes();verify(z,st['archive'])
  else:
   parts=[]
   for p in st['parts']:
    b=(S/p['path']).read_bytes();verify(b,p);parts.append(b)
   z=b''.join(parts);assert sha(z)==st['gzip_sha256']
  raw=gzip.decompress(z)
  if kind=='ordered_tar_gzip_member':assert sha(raw)==st['tar_sha256']
  with tarfile.open(fileobj=io.BytesIO(raw),mode='r:') as tf:
   for r in rows:verify(tf.extractfile(r['storage']['member']).read(),r);n['historical_bodies']+=1
  n['historical_archives']+=1
 seen=set();zipn=0;members=0
 for mf in ['data/turnout/asset-manifest.json','data/baselines/asset-manifest.json']:
  for r in parsed(S/mf)['external_original_references']:
   key=r['stored_sha256']
   if key in seen:continue
   b=(S/r['path']).read_bytes();assert len(b)==r['stored_bytes'] and sha(b)==r['stored_sha256']
   raw=gzip.decompress(b) if r.get('compression')=='gzip' else b
   assert len(raw)==r['raw_bytes'] and sha(raw)==r['raw_sha256'];seen.add(key)
   if raw[:4]==b'PK\x03\x04':
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
     assert z.testzip() is None
     for zi in z.infolist():assert len(z.read(zi))==zi.file_size;members+=1
    zipn+=1
 n['unique_full_originals']=len(seen);n['original_zip_entities_including_workbooks']=zipn;n['original_zip_members_including_workbooks']=members
 full=c['complete_descending_order'];inv=c['all_source_native_constituents'];priority=c['ordered_priority_keys']
 assert [x['key'] for x in full]==a['ordered_full_keys']
 assert priority==a['ordered_priority_keys']==[x['key'] for x in full[:242]]
 assert [x['key'] for x in full[242:]]==a['ordered_remainder_keys']
 assert full==sorted(full,key=lambda x:(-x['votes'],int(x['source_anchor']['byte_offset'])))
 assert len(full)==458 and len(inv)==497 and sum(x['votes'] for x in full)==491948
 assert sum(x['votes'] for x in full[:241])==393066 and sum(x['votes'] for x in full[:242])==394072
 assert sum(x['votes'] for x in full[242:])==97876 and sum(x['votes']==0 for x in full)==15
 assert (full[241]['native_code'],full[241]['source_anchor']['byte_offset'],full[241]['source_anchor']['line'],full[241]['votes'])==('0804',1075900,4061,1006)
 assert sum(x['contests']['Senator in Congress']['total'] is None for x in inv)==39
 parents=c['municipal_and_administrative_parent_sensitivity']['full_inventory']
 for i,p in enumerate(parents):
  rows=[x for x in full if x['parent_key']==p['key']]
  assert a['all_parent_ordered_child_arrays'][p['key']]==dict(original_ordered_native_inventory_keys=p['native_keys'],full_source_rank_ordered_children=[x['key'] for x in rows],ordered_priority_children=[x['key'] for x in rows if x['key'] in priority],ordered_remainder_children=[x['key'] for x in rows if x['key'] not in priority],complete_parent_contract_pointer='/municipal_and_administrative_parent_sensitivity/full_inventory/'+str(i))
 n['parents']=len(parents)
 return dict(status='pass',authority_path=AUTHORITY,counts=dict(n),scope='Full immutable historical graph and originals, exact historical path+SHA resolution; no future/model/report equality implied.',current_approval=False)
if __name__=='__main__':
 import sys
 result=run()
 if '--write' in sys.argv:dump(M/'qa/authority-replay.json',result)
 print(json.dumps(result))
