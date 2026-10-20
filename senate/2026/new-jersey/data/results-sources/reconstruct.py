"""Read-only independent complete historical replay. Authority is external PATH ONLY."""
from pathlib import Path
from collections import Counter
import csv,gzip,hashlib,io,json,os
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
ACCEPTANCE='data/coordinator-priority-acceptance.json'
def digest(b):return hashlib.sha256(b).hexdigest()
def canon(v):return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
def exact(r):
 b=(ROOT/r['path']).read_bytes();assert len(b)==r['bytes']<40000000 and digest(b)==r['sha256'],r['path'];return b
def load(p):
 b=(ROOT/p).read_bytes()
 if p.endswith('.gz'):b=gzip.decompress(b)
 if '.csv' in p:return list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))
 return [json.loads(x) for x in b.splitlines() if x] if '.jsonl' in p else json.loads(b)
def ptr(v,p):
 for x in p.split('/')[1:]:
  x=x.replace('~1','/').replace('~0','~');v=v[int(x)] if isinstance(v,list) else v[x]
 return v
def walk(v,p=''):
 if isinstance(v,(dict,list)):
  yield p,v
  it=v.items() if isinstance(v,dict) else enumerate(v)
  for k,x in it:yield from walk(x,p+'/'+str(k).replace('~','~0').replace('/','~1'))
def main():
 a=load(ACCEPTANCE);contract=json.loads(exact(a['frozen_contract']))
 assert len(contract)==24
 for r in a['complete_root_field_semantics']:assert digest(canon(ptr(contract,r['pointer'])))==r['full_recursive_semantic_sha256']
 pins={};parsed={};ledger_counts=Counter();counts=Counter()
 for group in ['producer_seals','frozen_first_pair_assets','independent_coordinator_reviews']:
  for r in a[group]:
   b=exact(r);pins[r['path']]={'path':r['path'],'bytes':len(b),'sha256':digest(b)}
   if group=='producer_seals':
    m=json.loads(b);assert len(m[r['owned_field']])==r['owned_entries_excluding_manifest']
    for e in m[r['owned_field']]:exact(e);pins[e['path']]=e;counts['producer_listed_bodies']+=1
 for r in a['complete_source_companion_files']:
  b=exact(r)
  if r['path'].endswith('.gz'):
   b=gzip.decompress(b);assert len(b)==r['complete_reconstructed_bytes'] and digest(b)==r['complete_reconstructed_sha256']
  v=load(r['path']);assert len(v)==r['complete_length'] and digest(canon(v))==r['full_semantic_sha256'];counts['complete_companions']+=1
 # All original dependency entries, including failures, retain their complete embedded receipts.
 refs=load('data/baselines/source/original-references.json');assert len(refs)==417
 for r in refs:
  if r.get('inherited_receipt_path'):
   p=ROOT/'data/baselines/source'/r['inherited_receipt_path'];b=p.read_bytes();assert digest(b)==r['inherited_receipt_sha256'];pins[str(p.resolve().relative_to(ROOT))]={'path':str(p.resolve().relative_to(ROOT)),'bytes':len(b),'sha256':digest(b)}
  if r.get('body_reference'):
   p=(ROOT/'data/baselines/source'/r['body_reference']).resolve();b=p.read_bytes();raw=gzip.decompress(b) if p.suffix=='.gz' else b
   assert len(b)==r['stored_bytes']<40000000 and digest(b)==r['stored_sha256'];assert len(raw)==r['raw_bytes'] and digest(raw)==r['raw_sha256']
   pins[os.path.relpath(p,ROOT)]={'path':os.path.relpath(p,ROOT),'bytes':len(b),'sha256':digest(b)}
 # Generate independent full preorder records, then compare every line in all five ledgers in order.
 def generated():
  files=['data/turnout/priority-set.json']+[r['path'] for r in a['complete_source_companion_files']]
  for f in files:
   v=load(f)
   if f=='data/turnout/priority-set.json':
    for k,x in v.items():yield {'file':f,'pointer':'/'+k,'full_recursive_semantic_sha256':digest(canon(x))}
    for field in ['all_units','county_coverage']:
     for i,x in enumerate(v[field]):
      for pp,obj in walk(x,'/'+field+'/'+str(i)):yield {'file':f,'pointer':pp,'full_recursive_semantic_sha256':digest(canon(obj))}
   elif '.csv' in f:
    for i,row in enumerate(v,1):yield {'file':f,'CSV_row_1based_including_header':i,'full_recursive_semantic_sha256':digest(canon(row))}
   else:
    for p,obj in walk(v):yield {'file':f,'pointer':p,'full_recursive_semantic_sha256':digest(canon(obj))}
 gen=iter(generated());n=0
 for r in a['complete_source_object_reference_bodies']:
  b=exact(r);raw=gzip.decompress(b);assert len(raw)==r['complete_reconstructed_bytes'] and digest(raw)==r['complete_reconstructed_sha256']
  local=Counter()
  for line in raw.splitlines():
   row=json.loads(line);expected=next(gen);assert row==expected,(row,expected);n+=1;local[row['file']]+=1
  assert sum(local.values())==r['complete_object_count'] and dict(local)==r['source_objects_by_file'];ledger_counts.update(local)
 assert next(gen,None) is None and n==724943 and dict(ledger_counts)==a['source_objects_by_file']
 units=contract['all_units'];ordered=sorted(units,key=lambda u:(-u['volume'],u['key']));keys=[u['key'] for u in ordered]
 assert ordered==units and keys==a['ordered_full_keys']==contract['complete_ordered_keys']
 assert keys[:233]==a['ordered_priority_keys'] and keys[233:]==a['ordered_remainder_keys']
 assert sum(u['volume'] for u in units)==4031795 and sum(u['volume'] for u in units[:233])==3229453
 assert sum(u['volume'] for u in units[:232])==3224325 and sum(u['volume'] for u in units[:15])==631518
 for f,p in a['derived_ordered_child_arrays_by_parent'].items():
  us=[u for u in units if u['county_fips']==f];assert [u['key'] for u in us]==p['canonical_rank_ordered_children']
  assert [u['key'] for u in us if u['in_minimum80']]==p['ordered_priority_children'];assert [u['key'] for u in us if not u['in_minimum80']]==p['ordered_remainder_children']
  assert [u['key'] for u in sorted(us,key=lambda u:(u['source_id'],u['page'],u['line']))]==p['original_source_ordered_children']
 # No acceptance hash/body/pin enters downstream owned outputs.
 out={'authority_path':ACCEPTANCE,'status':'pass_independent_complete_original_reconstruction','root_fields':24,'complete_companions':counts['complete_companions'],'recursive_objects':n,'ordered_ledger_partitions':5,'producer_listed_bodies':counts['producer_listed_bodies'],'producer_manifest_files':2,'original_dependency_entries':len(refs),'complete_dependency_failures':sum(not r.get('body_reference') for r in refs),'units':575,'priority':233,'remainder':342,'parents':21,'source_objects_by_file':dict(ledger_counts),'producer_writers_executed':False}
 (OUT/'historical-reconstruction.json').write_text(json.dumps(out,indent=2)+'\n')
 (OUT/'individual-source-pins.json').write_text(json.dumps(sorted(pins.values(),key=lambda r:r['path']),indent=2)+'\n')
 print({k:v for k,v in out.items() if k!='source_objects_by_file'})
if __name__=='__main__':main()
