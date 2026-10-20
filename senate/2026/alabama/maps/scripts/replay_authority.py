"""Independent whole-body replay. Authority is read in memory and referenced by path only."""
import csv,gzip,hashlib,io,json,tarfile,sys
from pathlib import Path
from collections import Counter
S=Path(__file__).resolve().parents[2]
AUTH=S/'data/coordinator-priority-acceptance.json'
CONTRACT='data/turnout/priority-set.json'
def sha(b): return hashlib.sha256(b).hexdigest()
def canon(v): return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def sem(v): return sha(canon(v))
def pairs(rows):
 d={}
 for k,v in rows:
  if k in d: raise ValueError('duplicate JSON key '+k)
  d[k]=v
 return d
def loads(b): return json.loads(b,object_pairs_hook=pairs,parse_constant=lambda v:(_ for _ in ()).throw(ValueError(v)))
def read(b,p):
 if p.endswith('.gz'): b=gzip.decompress(b)
 if p.endswith(('.csv','.csv.gz')): return list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))
 if '.jsonl' in p: return [loads(x) for x in b.splitlines() if x]
 return loads(b)
def run():
 a=loads(AUTH.read_bytes()); cache={}; checks=Counter()
 def pin(r):
  p=r['path'];b=(S/p).read_bytes()
  assert len(b)==r['bytes'] and sha(b)==r['sha256'],p
  assert len(b)<40000000,p
  checks['whole_pins']+=1
  return b
 c=loads(pin(a['frozen_contract']))
 assert a['frozen_contract']=={'path':CONTRACT,'bytes':15257023,'sha256':'a3d53415e3379a512b88a1f5f81506ac337a92f45870dd616038b9e23bf71850'}
 for r in a['frozen_file_pins']: pin(r);checks['fixed_files']+=1
 for r in a['complete_source_companion_files']:
  v=read(pin(r),r['path']);cache[r['path']]=v
  assert sem(v)==r['full_semantic_sha256']
  assert len(v)==r['complete_length'] and type(v).__name__==r['semantic_type']
  checks['whole_companions']+=1
 for r,(k,v) in zip(a['complete_root_field_semantics'],c.items()):
  assert r=={'pointer':'/'+k,'full_recursive_semantic_sha256':sem(v)}
  checks['roots']+=1
 assert len(c)==len(a['complete_root_field_semantics'])==29
 def walk(file,v,p=''):
  if isinstance(v,(dict,list)):
   yield file,p,sem(v)
   for k,x in v.items() if isinstance(v,dict) else enumerate(v):
    if isinstance(x,(dict,list)):yield from walk(file,x,p+'/'+str(k).replace('~','~0').replace('/','~1'))
 def expected():
  for k,v in c.items():yield CONTRACT,'/'+k,sem(v)
  for r in a['complete_source_companion_files']:yield from walk(r['path'],cache[r['path']])
 want=iter(expected());byfile=Counter()
 for part in a['complete_source_object_reference_bodies']:
  body=gzip.decompress(pin(part));assert len(body)==part['complete_reconstructed_bytes'] and sha(body)==part['complete_reconstructed_sha256']
  n=0
  for line in body.splitlines():
   r=loads(line);f,p,h=next(want)
   assert r=={'file':f,'pointer':p,'full_recursive_semantic_sha256':h},(f,p)
   n+=1;byfile[f]+=1
  assert n==part['complete_object_count'];checks['recursive_objects']+=n;checks['ordered_partitions']+=1
 assert next(want,None) is None and dict(byfile)==a['source_objects_by_file']
 assert checks['recursive_objects']==a['complete_source_object_count']==1608035
 archive_groups={}
 for r in a['historical_full_body_resolvers']:
  st=r['storage']
  if st['kind']=='tar_gzip_member':archive_groups.setdefault(st['archive']['path'],(st['archive'],[]))[1].append(r)
  else:assert st['kind']=='immutable_original_reference' and pin(st['file'])==pin({'path':st['file']['path'],'bytes':r['bytes'],'sha256':r['sha256']});checks['individual_history_refs']+=1
 for path,(p,rows) in archive_groups.items():
  with tarfile.open(fileobj=io.BytesIO(pin(p)),mode='r:gz') as tf:
   members=[m for m in tf if m.isfile()];assert len(members)==len(rows)
   for m,r in zip(members,rows):
    b=tf.extractfile(m).read();assert m.name==r['storage']['member']==r['path'] and len(b)==r['bytes'] and sha(b)==r['sha256'];checks['history_members']+=1
   assert all(m.isfile() or m.isdir() for m in tf.getmembers())
  checks['complete_archives']+=1
 # Reconstruct all external entity bodies from each exact original receipt/reference.
 manifest=cache['data/turnout/asset-manifest.json']
 for r in manifest['external_originals']:
  path=Path(r['path']);path=Path.cwd()/path if str(path).startswith('senate/') else S/path
  b=path.read_bytes();assert len(b)==r['stored_bytes'] and sha(b)==r['stored_sha256']
  raw=gzip.decompress(b);assert len(raw)==r['original_bytes'] and sha(raw)==r['original_sha256'];checks['whole_external_originals']+=1
 units=c['units'];keys=[u['key'] for u in units];priority=set(c['ordered_priority_keys']);den=sum(u['reported_candidate_votes'] for u in units)
 assert len(keys)==len(set(keys))==2085 and keys==a['ordered_full_keys']==c['full_order']==c['certified_statewide_native_order']
 assert c['ordered_priority_keys']==c['priority_keys']==keys[:887]==a['ordered_priority_keys']
 assert c['remainder_keys']==keys[887:]==a['ordered_remainder_keys'] and len(keys[887:])==1198
 assert sorted(units,key=lambda u:(-u['reported_candidate_votes'],u['key']))==units
 assert den==2265090 and sum(u['reported_candidate_votes'] for u in units[:15])==115428
 assert sum(u['reported_candidate_votes'] for u in units[:886])==1811981
 assert sum(u['reported_candidate_votes'] for u in units[:887])==1812818
 assert 5*1811981<4*den<=5*1812818 and units[886]['reported_candidate_votes']==837
 assert units[886]['native_label']=='OAK GROVE BAPT' and units[886]['county']=='Calhoun'
 assert len(c['parents'])==67
 for i,p in enumerate(c['parents']):
  children=[u for u in units if u['county_fips']==p['county_fips']];r=a['all_parent_ordered_child_arrays'][p['parent_key']]
  assert r['complete_parent_contract_pointer']=='/parents/'+str(i) and r['complete_original_parent_semantic_sha256']==sem(p)
  assert r['full_source_rank_ordered_children']==[u['key'] for u in children]
  assert r['ordered_priority_children']==[u['key'] for u in children if u['key'] in priority]
  assert r['ordered_remainder_children']==[u['key'] for u in children if u['key'] not in priority]
  assert p['constituent_keys']==[u['key'] for u in sorted(children,key=lambda u:u['column_1based'])]
  assert p['priority_constituent_keys']==[k for k in p['constituent_keys'] if k in priority]
  assert p['remainder_constituent_keys']==[k for k in p['constituent_keys'] if k not in priority]
  checks['complete_parents']+=1
 assert list(dict.fromkeys(u['county_fips'] for u in units[:887]))==a['ordered_priority_parent_fips'] and a['priority_parent_count']==63
 assert not c['coordinator_acceptance'] and not c['legal_geographic_approval_2026'] and not c['current_2026_crosswalk_complete']
 return {'status':'PASS','authority_path':str(AUTH.relative_to(S)),'contract':a['frozen_contract'],'checks':dict(checks),'full':2085,'priority':887,'remainder':1198,'priority_parents':63,'denominator':den,'scope':'Whole historical bodies and exact ordered recursive source semantics; no scenario/calculator/target/outcome or future-peer equality claim.','current_approval':False}
if __name__=='__main__':
 result=run();body=json.dumps(result,indent=2)+'\n'
 if len(sys.argv)>1:Path(sys.argv[1]).write_text(body)
 else:print(body)
