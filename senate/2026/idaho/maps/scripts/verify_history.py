#!/usr/bin/env python3
"""Read-only complete byte and recursive semantic validation of external dispatch."""
import csv,gzip,hashlib,io,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ACCEPTANCE='data/coordinator-priority-acceptance.json' # External authority: path only.
def sha(b): return hashlib.sha256(b).hexdigest()
def semantic(v): return sha(json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode())
def pointer(v,p):
 for k in p.split('/')[1:]:
  k=k.replace('~1','/').replace('~0','~');v=v[int(k)] if isinstance(v,list) else v[k]
 return v
def reference_bytes(path):
 p=Path(path).resolve();w=ROOT/'maps/source/frozen-reference-overrides.json'
 if w.exists():
  for e in json.loads(w.read_text())['overrides']:
   if p==(ROOT/e['original_state_relative_path']).resolve():
    stored=(ROOT/e['stored_path']).read_bytes();assert len(stored)==e['stored_bytes'] and sha(stored)==e['stored_sha256']
    b=gzip.decompress(stored);assert len(b)==e['original_bytes'] and sha(b)==e['original_sha256'];return b
 return p.read_bytes()
def checkpin(e,base=ROOT):
 b=(base/e['path']).read_bytes();assert len(b)==e['bytes']<40000000 and sha(b)==e['sha256'],e['path'];return b
def load(p):
 b=(ROOT/p).read_bytes();return json.loads(gzip.decompress(b) if p.endswith('.gz') else b)
def verify():
 a=load(ACCEPTANCE);assert a['status']=='accepted_complete_historical_source_native_research_dispatch_only'
 pins=[a['frozen_contract']]+a['frozen_first_pair_assets']+a['independent_coordinator_reviews']+[s['manifest'] for s in a['producer_seals']]
 for e in pins:checkpin(e)
 c=load(a['frozen_contract']['path']);assert not c['priority_accepted'] and not c['current_geography_approved']
 seal_count=0
 for s in a['producer_seals']:
  m=load(s['manifest']['path']);base=(ROOT/s['manifest']['path']).parent
  entries=m.get('owned_assets',m.get('owned'))
  actual={str(p.relative_to(ROOT)) for p in base.rglob('*') if p.is_file() and p.name!='asset-manifest.json'}
  actual|=({'turnout.md','data/county-turnout.csv'} if s['role']=='turnout' else {'county-partisanship.md','data/county-baselines.csv'})
  assert actual=={e['path'] for e in entries}
  for e in entries:
   b=checkpin(e);seal_count+=1
   if 'reconstructed_sha256' in e:
    raw=gzip.decompress(b);assert sha(raw)==e['reconstructed_sha256'] and len(raw)==e['reconstructed_bytes']
  for e in m.get('read_only_references',[]):
   b=reference_bytes(base/e['path']);assert len(b)==e['stored_bytes']<40000000 and sha(b)==e['stored_sha256']
   if 'raw_sha256' in e:
    raw=gzip.decompress(b);assert len(raw)==e['raw_bytes'] and sha(raw)==e['raw_sha256']
 objects={a['frozen_contract']['path']:c}
 for e in a['complete_source_companion_files']:
  b=checkpin(e)
  if e['path'].endswith('.gz'):
   b=gzip.decompress(b);assert len(b)==e['reconstructed_complete_bytes'] and sha(b)==e['reconstructed_complete_sha256']
  if 'semantic_sha256' in e:
   v=json.loads(b);assert semantic(v)==e['semantic_sha256'];assert type(v).__name__==e['semantic_type'] and len(v)==e['complete_top_level_length'];objects[e['path']]=v
  if 'full_rows_semantic_sha256' in e:
   v=list(csv.reader(io.StringIO(b.decode())));assert v[0]==e['complete_header'] and len(v)-1==e['complete_rows'] and semantic(v)==e['full_rows_semantic_sha256']
 for e in a['complete_root_field_semantics']:assert semantic(pointer(c,e['pointer']))==e['semantic_sha256']
 assert {e['pointer'][1:] for e in a['complete_root_field_semantics']}==set(c)
 for e in a['complete_source_object_references']:
  assert semantic(pointer(objects[e['file']],e['pointer']))==e['semantic_sha256']
 units=[u for p in c['all_county_constituents'] for u in p['president_contexts']]
 order=sorted(units,key=lambda u:(-u['candidate_votes'],u['key']));keys=[u['key'] for u in order]
 assert keys==a['ordered_full_keys']==[x['key'] for x in c['complete_order']]
 assert keys[:528]==c['ordered_priority_keys']==a['ordered_priority_keys'] and keys[528:]==c['ordered_remainder_keys']==a['ordered_remainder_keys']
 assert len(set(keys))==985 and len(c['all_county_constituents'])==44
 assert sum(u['candidate_votes'] for u in order)==905057
 assert sum(u['candidate_votes'] for u in order[:15])==65391
 assert sum(u['candidate_votes'] for u in order[:527])==723753
 assert sum(u['candidate_votes'] for u in order[:528])==724515
 assert order[527]['key']=='ID:2024:pres:16079:11741' and order[527]['candidate_votes']==762
 assert sum(u['candidate_votes'] for u in order[528:])==180542
 for p in c['all_county_constituents']:
  k=p['key'];assert [u['key'] for u in order if u['county_fips']==k]==a['ordered_child_keys_by_parent'][k]
  assert [u['key'] for u in order[:528] if u['county_fips']==k]==a['ordered_priority_child_keys_by_parent'][k]
  assert [u['key'] for u in order[528:] if u['county_fips']==k]==a['ordered_remainder_child_keys_by_parent'][k]
 assert sum(bool(a['ordered_priority_child_keys_by_parent'][k]) for k in a['ordered_parent_keys'])==32
 return dict(status='pass_read_only_complete_history',acceptance_path=ACCEPTANCE,byte_pins=len(pins),sealed_owned_files=seal_count,complete_companions=len(a['complete_source_companion_files']),complete_root_fields=len(c),complete_recursive_objects=len(a['complete_source_object_references']),historical_native=3946,historical_administrative=194,parents=44,observations=985,priority=528,remainder=457)
if __name__=='__main__':print(json.dumps(verify(),indent=2))
