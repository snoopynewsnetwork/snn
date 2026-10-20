"""Independent, read-only full source replay. Authority is PATH ONLY downstream."""
from common import *
import collections,sys

def replay():
 a=load(AUTH);checks=0;cache={};tars={};historical={}
 def ck(v):
  nonlocal checks
  checks+=1
  if not v:raise AssertionError('source replay invariant '+str(checks))
 def read(r):
  # Each individual immutable body may be reused once; current authority is never cached to disk.
  key=(r['path'],r['sha256'])
  if key not in cache:cache[key]=exact(r)
  ck(len(cache[key])==r['bytes']);return cache[key]
 c=json.loads(read(a['frozen_contract']));ck(len(c)==23)
 for k,r in zip(c,a['complete_root_field_semantics']):ck(r['pointer']=='/'+k and semantic(c[k])==r['full_recursive_semantic_sha256'])
 for r in a['frozen_first_pair_assets']:read(r)
 files={r['path']:r for r in a['complete_source_companion_files']};ck(len(files)==1994)
 parsed={}
 for path,r in files.items():
  b=read(r);b=gzip.decompress(b) if path.endswith('.gz') else b
  if '.jsonl' in path:x=[json.loads(l) for l in b.splitlines() if l]
  elif '.json' in path:x=json.loads(b)
  else:x=list(csv.reader(io.StringIO(b.decode('utf-8-sig'),newline='')))
  ck(type(x).__name__==r['semantic_type'] and len(x)==r['complete_length'] and semantic(x)==r['full_semantic_sha256']);ck(r['complete_body_required'] and not r['projection_or_subset_substitution']);parsed[path]=x
 seen=[];active=None;it=iter(());n=0;counts=collections.Counter()
 for r in a['complete_source_object_reference_bodies']:
  b=gzip.decompress(read(r));ck(len(b)==r['complete_reconstructed_bytes'] and sha(b)==r['complete_reconstructed_sha256']);pc=collections.Counter()
  for line in b.splitlines():
   z=json.loads(line);path=z['source_path']
   if path!=active:
    ck(next(it,None) is None);ck(path not in seen);seen.append(path);active=path;it=iter(walk(parsed[path]))
   p,x=next(it);ck(z['ordinal']==n);ck(p==z['pointer'] and len(x)==z['complete_length'] and type(x).__name__==z['semantic_type'] and semantic(x)==z['full_recursive_semantic_sha256']);n+=1;counts[path]+=1;pc[path]+=1
  ck(dict(pc)==r['source_objects_by_file'] and sum(pc.values())==r['complete_object_count'])
 ck(next(it,None) is None);ck(n==495672 and dict(counts)==a['source_objects_by_file'])
 for capture in a['immutable_historical_snapshot_body_resolvers']:
  read(capture['capture'])
  for r in capture['complete_records']:
   if r['storage']=='tar_gzip_member':
    t=r['immutable_container'];key=(t['path'],t['sha256'])
    if key not in tars:tars[key]=tarfile.open(fileobj=io.BytesIO(read(t)),mode='r:gz')
    b=tars[key].extractfile(r['member']).read()
   else:
    b=read(r['immutable_stored_body']);b=gzip.decompress(b) if r['storage']=='lossless_gzip_body' else b
   ck(len(b)==r['original_bytes'] and sha(b)==r['original_sha256']);key=(r['original_path'],r['original_sha256']);historical[key]=b
 for t in tars.values():t.close()
 ck(len(a['all_complete_parent_objects'])==36 and a['all_complete_parent_objects']==c['all_36_county_parents']);ck(len(a['known_ordered_native_keys'])==510 and a['known_ordered_native_keys']==c['known_source_universe']['full_ordered_keys']);ck(len(a['unavailable_parent_keys'])==31)
 for k in ['certified_native_full_order','certified_native_top15','certified_native_minimum80','ordered_priority_keys','canonical_remainder_keys']:ck(a[k] is None)
 # Independently open all four source-format roles; no producer imports/writers or optional review inputs.
 result={'authority_path':AUTH,'status':'pass','checks':checks,'roots':len(c),'whole_companions':len(files),'recursive_objects':n,'ordered_ledgers':len(a['complete_source_object_reference_bodies']),'fixed_whole_file_pins':len(a['frozen_first_pair_assets']),'historical_records':sum(len(t['complete_records']) for t in a['immutable_historical_snapshot_body_resolvers']),'historical_distinct_path_hash':len(historical),'optional_reviews_read':False,'producer_imports_or_writes':False,'current_body_substitution':False}
 return result
if __name__=='__main__':
 r=replay()
 if '--write' in sys.argv:save('maps/qa/source-replay.json',r)
 print(json.dumps(r))
