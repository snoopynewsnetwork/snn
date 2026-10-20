"""Independent read-only replay of every complete source authority body and ledger node."""
from pathlib import Path
import json,gzip,hashlib,csv,io,collections,tarfile
S=Path(__file__).resolve().parents[1];D=S/'data';N=0

def sha(b):return hashlib.sha256(b).hexdigest()
def ck(x,why):
 global N
 N+=1
 if not x:raise AssertionError(why)
def semantic(x):return sha(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def read(ref):
 b=(S/ref['path']).read_bytes();ck(len(b)==ref['bytes'] and sha(b)==ref['sha256'],'exact full file '+ref['path']);return b

def parse(ref):
 raw=read(ref);name=ref['path'];raw=gzip.decompress(raw) if name.endswith('.gz') else raw
 if '.jsonl' in name:return [json.loads(l) for l in raw.splitlines() if l]
 if '.json' in name:return json.loads(raw)
 return list(csv.reader(io.StringIO(raw.decode('utf-8-sig'),newline='')))
def nodes(x):
 stack=[('',x)]
 while stack:
  pointer,v=stack.pop()
  if not isinstance(v,(dict,list)):continue
  yield pointer,v
  children=list(v.items()) if isinstance(v,dict) else list(enumerate(v))
  for k,w in reversed(children):
   if isinstance(w,(dict,list)):stack.append((pointer+'/'+str(k).replace('~','~0').replace('/','~1'),w))
def main():
 a=json.loads((D/'coordinator-source-research-acceptance.json').read_bytes());c=json.loads(read(a['frozen_contract']));ck(len(c)==len(a['complete_root_field_semantics'])==23,'all contract fields')
 for r,(k,v) in zip(a['complete_root_field_semantics'],c.items()):ck(r['pointer']=='/'+k.replace('~','~0').replace('/','~1') and semantic(v)==r['full_recursive_semantic_sha256'],'whole root recursive semantics')
 for r in a['frozen_first_pair_assets']+a['independent_coordinator_reviews']:read(r)
 files={r['path']:r for r in a['complete_source_companion_files']};ck(len(files)==len(a['complete_source_companion_files'])==1994,'all whole companions')
 for r in files.values():
  x=parse(r);ck(type(x).__name__==r['semantic_type'] and len(x)==r['complete_length'] and semantic(x)==r['full_semantic_sha256'],'whole companion recursive semantics '+r['path']);ck(r['complete_body_required'] and not r['projection_or_subset_substitution'],'no projection')
 counts=collections.Counter();ordinal=0;active=None;it=None;seen=[]
 for ref in a['complete_source_object_reference_bodies']:
  z=read(ref);h=hashlib.sha256();n=0;part_counts=collections.Counter();size=0
  with gzip.GzipFile(fileobj=io.BytesIO(z)) as f:
   for line in f:
    h.update(line);size+=len(line);r=json.loads(line);path=r['source_path']
    if path!=active:
     if it is not None:ck(next(it,None) is None,'previous complete source walk exhausted')
     ck(path not in seen,'single complete contiguous source body');seen.append(path);it=iter(nodes(parse(files[path])));active=path
    expected=next(it,None);ck(expected is not None and r['ordinal']==ordinal,'complete ordered ledger ordinal');pointer,obj=expected;ck(pointer==r['pointer'] and len(obj)==r['complete_length'] and type(obj).__name__==r['semantic_type'] and semantic(obj)==r['full_recursive_semantic_sha256'],'every full recursive object and field');counts[path]+=1;part_counts[path]+=1;ordinal+=1;n+=1
  ck(n==ref['complete_object_count'] and dict(part_counts)==ref['source_objects_by_file'],'entire partition object coverage');ck(size==ref['complete_reconstructed_bytes'] and h.hexdigest()==ref['complete_reconstructed_sha256'],'whole decoded partition bytes')
 ck(next(it,None) is None,'last full source walk exhausted');ck(ordinal==a['complete_source_object_count']==495672 and dict(counts)==a['source_objects_by_file'],'all ordered source objects')
 # Every historical old path+SHA resolves its own immutable captured body, not current replacements.
 archives={};virtual=0
 for capture in a['immutable_historical_snapshot_body_resolvers']:
  read(capture['capture'])
  for r in capture['complete_records']:
   if r['storage']=='tar_gzip_member':
    container=r['immutable_container'];key=(container['path'],container['sha256'])
    if key not in archives:archives[key]=tarfile.open(fileobj=io.BytesIO(read(container)),mode='r:gz')
    b=archives[key].extractfile(r['member']).read()
   else:
    b=read(r['immutable_stored_body'])
    if r['storage']=='lossless_gzip_body':b=gzip.decompress(b)
   ck(len(b)==r['original_bytes'] and sha(b)==r['original_sha256'],'entire original historical body '+r['original_path']);virtual+=1
 for tar in archives.values():tar.close()
 ck(a['all_county_research_parents']==len(c['all_36_county_parents'])==36,'all parents');ck(a['all_complete_parent_objects']==c['all_36_county_parents'],'whole parent objects');ck(a['known_ordered_native_keys']==c['known_source_universe']['full_ordered_keys'] and len(a['known_ordered_native_keys'])==510,'complete known source order');ck(len(a['unavailable_parent_keys'])==31,'all unknown parent cases')
 for k in ['certified_native_full_order','certified_native_top15','certified_native_minimum80','ordered_priority_keys','canonical_remainder_keys']:ck(a[k] is None,'canonical unavailable '+k)
 for k in ['current_geography_approved','current_November_returns_admitted','current_choice_or_reporting_IDs_approved','legal_native_80_robustness_approved','live_cadence_or_exact_remainder_approved','collector_or_probability_approval']:ck(a[k] is False,'no current approval '+k)
 result={'status':'pass_complete_available_source_authority_replay','checks':N,'complete_roots':23,'whole_companions':1994,'recursive_complete_objects':ordinal,'complete_ledger_partitions':len(a['complete_source_object_reference_bodies']),'frozen_current_file_pins':len(a['frozen_first_pair_assets']),'historical_virtual_bodies':virtual,'all_parents':36,'known_2024native':510,'unknown_native_parents':31,'canonical_native_priority':None,'producer_writes':False,'scope':'Every full source body, ordered recursive container and historical expected path+hash is checked. Current/eligible/geo/November admission remains false.'}
 (D/'coordinator-source-coverage-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
