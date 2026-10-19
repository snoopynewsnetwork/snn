"""Read-only full-field historical conservation. Never changes producer/acceptance files."""
import csv,gzip,hashlib,io,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1];STATE=ROOT.parent
ACCEPTANCE='data/coordinator-priority-acceptance.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def semantic(v):return sha(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def load(p):
 b=p.read_bytes();b=gzip.decompress(b) if p.suffix=='.gz' else b
 name=p.name.removesuffix('.gz')
 if name.endswith('.jsonl'):return [json.loads(x) for x in b.splitlines() if x]
 if name.endswith('.csv'):return list(csv.reader(io.StringIO(b.decode())))
 return json.loads(b)
def pointer(o,s):
 for x in s.lstrip('/').split('/'):
  x=x.replace('~1','/').replace('~0','~');o=o[int(x)] if isinstance(o,list) else o[x]
 return o
def run():
 a=load(STATE/ACCEPTANCE);checks=0;cache={};refs=[]
 def verify(pin):
  nonlocal checks
  p=STATE/pin['path'];b=p.read_bytes();assert len(b)==pin['bytes'] and sha(b)==pin['sha256'];checks+=2
  if p.name.endswith('.gz'):
   raw=gzip.decompress(b)
   if 'complete_reconstructed_bytes'in pin:assert len(raw)==pin['complete_reconstructed_bytes'] and sha(raw)==pin['complete_reconstructed_sha256'];checks+=2
  v=load(p);cache[pin['path']]=v
  if 'full_semantic_sha256'in pin:assert semantic(v)==pin['full_semantic_sha256'];checks+=1
  refs.append(dict(path=pin['path'],bytes=len(b),sha256=sha(b),complete_body=True))
 verify(a['frozen_contract']);c=cache[a['frozen_contract']['path']]
 for pin in a['complete_source_companion_files']:verify(pin)
 for pin in a['frozen_first_pair_assets']:
  if pin['path'] in ['data/county-turnout.csv','data/county-baselines.csv']:verify(pin)
 for r in a['complete_root_field_semantics']:assert semantic(pointer(c,r['pointer']))==r['full_recursive_semantic_sha256'];checks+=1
 for r in a['complete_source_object_references']:
  v=cache[r['file']];v=pointer(v,r['pointer']) if 'pointer'in r else v[r['JSONL_record']-1]
  assert semantic(v)==r['full_recursive_semantic_sha256'];checks+=1
 assert len(c['full_order'])==3199 and len(c['county_parents'])==64 and len(c['csv_only_statistics_unavailable'])==16
 assert [x['key'] for x in c['full_order']]==a['ordered_full_keys'];assert c['ordered_priority_keys']==a['ordered_priority_keys'];assert c['ordered_remainder_keys']==a['ordered_remainder_keys'];checks+=6
 assert sorted(c['full_order'],key=lambda x:(-x['candidate_votes'],x['key']))==c['full_order'];checks+=1
 assert sum(x['candidate_votes'] for x in c['full_order'])==3192745
 assert sum(x['candidate_votes'] for x in c['full_order'][:15])==39005
 assert sum(x['candidate_votes'] for x in c['full_order'][:1992])==2554233
 assert sum(x['candidate_votes'] for x in c['full_order'][:1991])==2553363
 assert c['full_order'][1991]['key']=='CO|2024|26499|Summit|2081359007';checks+=5
 remainder=set(a['ordered_remainder_keys'])
 for h in c['county_native_hierarchy']:
  assert [x for x in h['all_native_keys'] if x in remainder]==a['derived_ordered_remainder_child_keys_by_parent'][h['county']];checks+=1
 # Pin individual original bytes, never the mutable news manifest/ledger.
 pins=cache['data/turnout/source/shared-source-pins.json']
 original_refs=[]
 for r in pins:
  p=(STATE/'data/turnout/source'/r['reference_path']).resolve();b=p.read_bytes();raw=gzip.decompress(b)
  assert sha(b)==r['stored_sha256'] and sha(raw)==r['raw_sha256'];checks+=2
  original_refs.append(dict(path=str(p.relative_to(STATE)),bytes=len(b),sha256=sha(b),raw_bytes=len(raw),raw_sha256=sha(raw),provenance=r))
 for r in cache['data/baselines/source/supplemental-originals.json']:
  w=next(x for x in cache['data/baselines/source/reused-originals.json'] if x['id']==r['id']);p=(STATE/'data/baselines'/w['path']).resolve();b=p.read_bytes();raw=gzip.decompress(b)
  assert sha(b)==r['stored_sha256'] and sha(raw)==r['raw_sha256'];checks+=2
  original_refs.append(dict(path=str(p.relative_to(STATE)),bytes=len(b),sha256=sha(b),raw_bytes=len(raw),raw_sha256=sha(raw),provenance=r))
 return dict(acceptance_path=ACCEPTANCE,checks=checks,contract_fields=len(c),companion_bodies=26,recursive_objects=13174,read_only_complete_dependencies=refs,individual_original_references=original_refs,scope='whole bytes plus full recursive semantics; no vote-only projection; acceptance authority is external path only'),c
if __name__=='__main__':
 r,c=run();(ROOT/'historical-conservation.json').write_text(json.dumps(r,indent=2)+'\n');print(r['checks'],len(r['individual_original_references']))
