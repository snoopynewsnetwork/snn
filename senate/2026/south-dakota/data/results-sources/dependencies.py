#!/usr/bin/env python3
"""Independently check every frozen pin and preserve complete object semantics.
External coordinator acceptance is resolved by PATH ONLY; never pinned backwards.
"""
from common import *
import collections,csv,zlib
ACCEPTANCE='data/coordinator-priority-acceptance.json'
CONTRACT='data/turnout/priority-set.json'
def semantic(x):
 # Every key, type, null, value, array member and order participates.
 return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def walk(x):
 yield x
 if isinstance(x,dict):
  for v in x.values():yield from walk(v)
 elif isinstance(x,list):
  for v in x:yield from walk(v)
def verify():
 a=json.loads((STATE/ACCEPTANCE).read_bytes());refs={};seen=set();queue=[a]
 def check(o):
  p=STATE/o['path'];b=p.read_bytes();assert len(b)==o['bytes'],o['path'];assert hashlib.sha256(b).hexdigest()==o['sha256'],o['path'];assert len(b)<40000000,o['path'];refs[o['path']]=o
 while queue:
  obj=queue.pop()
  for o in walk(obj):
   if isinstance(o,dict) and all(k in o for k in ['path','bytes','sha256']):
    if o['path']==ACCEPTANCE:raise AssertionError('reverse acceptance pin')
    check({k:o[k] for k in ['path','bytes','sha256']})
    if o['path'].endswith('.json') and o['path'] not in seen:
     seen.add(o['path']);queue.append(json.loads((STATE/o['path']).read_bytes()))
 # News original references contain asset names and stored hashes, not pin triplets.
 news=json.loads((STATE/'data/news/manifest.json').read_text())
 rawchecks=[]
 for e in news:
  if not e['id'].startswith('sos-'):continue
  if 'asset_parts' in e:
   parts=e['asset_parts']; print('parts schema',parts[0]) if False else None
   dec=zlib.decompressobj(16+zlib.MAX_WBITS);rh=hashlib.sha256();zh=hashlib.sha256();rn=zn=0
   for part in parts:
    name=part.get('path',part.get('asset'));p=STATE/'data/news'/name;b=p.read_bytes();expected=part.get('sha256',part.get('stored_sha256'));assert hashlib.sha256(b).hexdigest()==expected;refs[str(p.relative_to(STATE))]=pin(p);zh.update(b);zn+=len(b);d=dec.decompress(b);rh.update(d);rn+=len(d)
   d=dec.flush();rh.update(d);rn+=len(d);assert dec.eof
   assert rh.hexdigest()==e['raw_sha256'];assert rn==e['bytes']
   if 'stored_sha256' in e:assert zh.hexdigest()==e['stored_sha256']
   rawchecks.append({'id':e['id'],'raw_bytes':rn,'raw_sha256':rh.hexdigest(),'ordered_parts':len(parts)})
  elif 'asset' in e:
   p=STATE/'data/news'/e['asset'];b=p.read_bytes();assert hashlib.sha256(b).hexdigest()==e['stored_sha256'];raw=gzip.decompress(b);assert hashlib.sha256(raw).hexdigest()==e['raw_sha256'];assert len(raw)==e['bytes'];refs[str(p.relative_to(STATE))]=pin(p);rawchecks.append({'id':e['id'],'raw_bytes':len(raw),'raw_sha256':hashlib.sha256(raw).hexdigest()})
 c=json.loads((STATE/CONTRACT).read_bytes());units=c['all_units'];parents=c['county_parents']
 assert len(units)==691 and len(parents)==66
 assert [u['key'] for u in units]==a['ordered_full_keys']==c['complete_ordered_keys']
 assert c['ordered_priority_keys']==a['ordered_priority_keys']==[u['key'] for u in units[:304]]
 assert [u['key'] for u in units[304:]]==a['ordered_remainder_keys']
 assert c['ordered_priority_parent_keys']==a['ordered_priority_parent_keys']
 assert semantic(parents)==semantic(a['all66_parent_objects'])
 assert sum(u['contest_votes'] for u in units)==428728
 assert sum(u['contest_votes'] for u in units[:304])==343402
 assert sum(u['contest_votes'] for u in units[:303])==342947
 for p in parents:
  us=[u for u in units if u['county_parent_key']==p['parent_key']]
  assert [u['key'] for u in us]==p['ordered_all_native_keys']
  assert [u['key'] for u in us if u['priority80']]==p['ordered_priority_native_keys']
  assert len(us)==p['source_native_rows']
 for u in units:assert sum(u['candidate_votes'].values())==u['contest_votes']
 assert c['coordinator_acceptance']['accepted'] is False
 assert c['certification_robustness']['proven'] is False
 assert a['certified_minimum_or_membership_approved'] is False
 objects=[]
 def add(pointer,x):objects.append({'contract':CONTRACT,'JSON_pointer':pointer,'recursive_semantic_sha256':semantic(x)})
 add('',c)
 for i,u in enumerate(units):add('/all_units/'+str(i),u)
 for i,p in enumerate(parents):add('/county_parents/'+str(i),p)
 for y,h in c['separate_historical_native_universes'].items():
  add('/separate_historical_native_universes/'+y,h)
  for k,v in h.items():
   if isinstance(v,list):
    for i,x in enumerate(v):add('/separate_historical_native_universes/'+y+'/'+k+'/'+str(i),x)
 add('/explicit_unavailable_cases',c['explicit_unavailable_cases'])
 return {'authority_path_only':ACCEPTANCE,'contract':a['frozen_contract'],'exact_read_only_references':sorted(refs.values(),key=lambda x:x['path']),'complete_semantic_objects':objects,'original_raw_checks':rawchecks,'all_acceptance_fields_consumed_semantically':True,'review_note':'Initial wrong-PDF-family coordinator locator check corrected; worker source locators unchanged.'}
if __name__=='__main__':
 o=verify();dump('dependency-verification.json',o);print('verified',len(o['exact_read_only_references']),'pins;',len(o['complete_semantic_objects']),'recursive complete objects')
