#!/usr/bin/env python3
"""Read every acceptance/review/contract field and recursively audit frozen byte pins."""
import gzip,hashlib,json,pathlib
from acquire import ROOT,STATE,sha,save_json
ACCEPTANCE=STATE/'data/coordinator-priority-acceptance.json'
CONTRACT=STATE/'data/turnout/priority-set.json'

def walk(v,p=''):
 yield p,v
 if isinstance(v,dict):
  for k,x in v.items(): yield from walk(x,p+'/'+str(k).replace('~','~0').replace('/','~1'))
 elif isinstance(v,list):
  for i,x in enumerate(v): yield from walk(x,p+'/'+str(i))
def audit(write=False):
 ab=ACCEPTANCE.read_bytes();assert len(ab)==394627 and sha(ab)=='8052dd61ac55db4c38c7ba78bead30dbad0f0cc321883afaa754cd67009b0a5f'
 a=json.loads(ab);cb=CONTRACT.read_bytes();assert len(cb)==3889923 and sha(cb)=='125fef1c2e13ff4e0464ac5e75e82ec54c9ea5e675b42da7586c4ccfd90d5891';c=json.loads(cb)
 # External historical authority is referenced by PATH ONLY. Its hash never enters producer contract/output graph.
 opaque=[]
 byname={}
 for p in STATE.rglob('*'):
  if p.is_file() and 'maps' not in p.relative_to(STATE).parts:byname.setdefault(p.name,[]).append(p)
 roots=[a['frozen_contract']]+a['frozen_first_pair_assets']+a['independent_coordinator_reviews'];todo=list(roots);seen={};edges=[];scalars=0
 while todo:
  pin=todo.pop();rel=pin['path'];p=STATE/rel
  if rel=='data/news/manifest.json':
   # Frozen producer embeds individual immutable receipts; historical aggregate remains an opaque recorded reference only.
   if pin not in opaque:opaque.append(pin)
   continue
  b=p.read_bytes();assert sha(b)==pin['sha256'],rel
  if 'bytes' in pin:assert len(b)==pin['bytes'],rel
  if rel in seen:continue
  seen[rel]={'path':rel,'bytes':len(b),'sha256':sha(b)}
  try:j=json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
  except (ValueError,UnicodeDecodeError,OSError):continue
  for pointer,x in walk(j):
   if not isinstance(x,(dict,list)):scalars+=1
   if isinstance(x,dict) and isinstance(x.get('asset'),str) and x.get('stored_sha256') and x.get('raw_sha256'):
    matches=[p for p in byname.get(pathlib.Path(x['asset']).name,[]) if sha(p.read_bytes())==x['stored_sha256']]
    assert matches,(rel,pointer,x.get('id'),x['asset'])
    target=matches[0];rb=target.read_bytes();todo.append({'path':str(target.relative_to(STATE)),'bytes':len(rb),'sha256':x['stored_sha256']});edges.append({'from':rel,'pointer':pointer+'/asset','to':str(target.relative_to(STATE)),'reference_kind':'exact individual receipt body, not mutable aggregate'})
   if isinstance(x,dict) and isinstance(x.get('path'),str) and len(str(x.get('sha256','')))==64:
    target=pathlib.Path(x['path']);target=target if target.is_absolute() else STATE/target
    if target.is_file():
     reltarget=str(target.relative_to(STATE));todo.append({**x,'path':reltarget});edges.append({'from':rel,'pointer':pointer,'to':reltarget})
 assert not c['coordinator_acceptance'] and not c['current_geography_approval']
 for k in ['ordered_priority_keys','ordered_full_keys','ordered_remainder_keys','parent_full_child_map','parent_priority_child_map','child_parent_map']:assert a[k]==c[k],k
 assert a['all93_parent_objects']==c['all93_parents']
 units=c['constituents'];assert [u['key'] for u in units]==c['ordered_full_keys'];assert len(units)==1326
 assert len(c['ordered_priority_keys'])==765 and len(c['ordered_remainder_keys'])==561
 assert sum(u['priority_votes_state_scope'] for u in units)==935005
 assert sum(u['priority_votes_state_scope'] for u in units[:765])==748190
 assert sum(u['priority_votes_state_scope'] for u in units[:764])==747645
 assert sum(u['priority_votes_state_scope'] for u in units[:15])==26773
 assert [sum(u['candidate_values'][i] for u in units) for i in range(2)]==[585103,349902]
 assert units[764]['key']=='NE:2024-special:lancaster-pdf:page-685'
 for key,n in [('administrative_and_partial_alternates',329),('additional_native_source_contexts',14),('unavailable_cases',2),('additional_administrative_contexts',2)]:assert len(c[key])==n
 # Exact-byte parent preserves EVERY recursively nested candidate/method/null/clock/reference field.
 refs=[{'file':str(CONTRACT.relative_to(STATE)),'bytes':len(cb),'sha256':sha(cb),'JSON_pointer':'/'+k,'complete_recursive_object':True,'semantic_sha256':sha(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()),'recursive_nodes':sum(1 for _ in walk(v))} for k,v in c.items()]
 out={'schema':'NE-map-frozen-reference-graph-v1','external_historical_authority_path':'data/coordinator-priority-acceptance.json','supplied_acceptance_pin_verified':True,'no_reverse_acceptance_pin':True,'files':sorted(seen.values(),key=lambda x:x['path']),'edges':edges,'opaque_historical_non_dependency_references':opaque,'opaque_reference_policy':'News ledger is not read or required during rebuild/validation. Its complete historical reference remains in the exact frozen parent; individual original receipts and bodies are pinned independently. The ledger pin was independently verified at initial reading only.','complete_contract_fields':refs,'all_review_and_contract_scalar_values_visited':scalars,'qualifications':{k:v for k,v in a.items() if k in ['denominator_scope','writein_qualification','source_disagreements','dispatch_requirements','qualification']}}
 if write:save_json(ROOT/'frozen-references.json',out)
 return a,c,out
if __name__=='__main__':
 a,c,o=audit(True);print('Verified',len(o['files']),'recursive exact pins;',len(o['edges']),'edges; all',len(o['complete_contract_fields']),'complete contract fields preserved')
