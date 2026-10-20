"""Independent complete ordered authority replay; no builder or producer import."""
from pathlib import Path
from collections import Counter,defaultdict
import csv,gzip,hashlib,io,json,tarfile,sys
S=Path(__file__).resolve().parents[1];D=S/'data';AL=S.name=='alabama';N=0

def ck(v,label=''):
 global N
 N+=1
 assert v,(N,label)
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def checked(r):
 b=(S/r['path']).read_bytes();ck(len(b)==r['bytes']<40000000 and sha(b)==r['sha256'],r['path']);return b
def parsed(r):
 b=checked(r);name=r['path'];b=gzip.decompress(b) if name.endswith('.gz') else b
 if name.endswith(('.csv','.csv.gz')):return list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))
 return [json.loads(x) for x in b.splitlines() if x] if '.jsonl' in name else json.loads(b)
a=json.loads((D/'coordinator-priority-acceptance.json').read_bytes());pins={r['path']:r for r in a['frozen_file_pins']}
ck(len(pins)==len(a['frozen_file_pins']))
for r in pins.values():checked(r)
for r in a['independent_coordinator_reviews']:checked(r)
c=parsed(a['frozen_contract']);ck(len(c)==len(a['complete_root_field_semantics'])==(29 if AL else 18))
for r in a['complete_root_field_semantics']:ck(sha(canonical(c[r['pointer'][1:]]))==r['full_recursive_semantic_sha256'],'full root')
for r in a['complete_source_companion_files']:
 v=parsed(r);ck(sha(canonical(v))==r['full_semantic_sha256'] and (len(v) if isinstance(v,(list,dict)) else None)==r['complete_length'],'whole companion')
archives={};members=defaultdict(set)
for r in a['historical_full_body_resolvers']:
 st=r['storage']
 if st['kind']=='immutable_original_reference':b=checked(st['file'])
 else:
  p=st['archive'];key=(p['path'],p['sha256'])
  if key not in archives:archives[key]=tarfile.open(fileobj=io.BytesIO(checked(p)),mode='r:gz')
  b=archives[key].extractfile(st['member']).read();members[key].add(st['member'])
 ck(len(b)==r['bytes'] and sha(b)==r['sha256'],'every original path+digest body')
for key,tf in archives.items():ck(members[key]=={m.name for m in tf if m.isfile()},'EVERY archive member enumerated')

def walk(file,value,pointer=''):
 if not isinstance(value,(list,dict)):return
 yield file,pointer,value
 for k,v in value.items() if isinstance(value,dict) else enumerate(value):
  if isinstance(v,(list,dict)):yield from walk(file,v,pointer+'/'+str(k).replace('~','~0').replace('/','~1'))
def allobjects():
 for k,v in c.items():yield 'data/turnout/priority-set.json','/'+k,v
 for r in a['complete_source_companion_files']:yield from walk(r['path'],parsed(r))
expected=allobjects();byfile=Counter();total=0
for part in a['complete_source_object_reference_bodies']:
 raw=gzip.decompress(checked(part));ck(len(raw)==part['complete_reconstructed_bytes'] and sha(raw)==part['complete_reconstructed_sha256'],'entire ledger partition')
 count=0
 for line in raw.splitlines():
  r=json.loads(line);file,pointer,v=next(expected)
  ck(r['file']==file and r['pointer']==pointer and r['full_recursive_semantic_sha256']==sha(canonical(v)),'EVERY ordered recursive full object, no omission or projection')
  byfile[file]+=1;total+=1;count+=1
 ck(count==part['complete_object_count'],'full partition count')
try:next(expected);raise AssertionError('source traversal not exhausted')
except StopIteration:pass
ck(total==a['complete_source_object_count'] and dict(byfile)==a['source_objects_by_file'],'entire original object traversal exhausted')
full=c['units'] if AL else c['full_order'];parents=c['parents'] if AL else c['all75parents'];keys=[u['key'] for u in full];n,pr,rest,den,top,preceding,cross=(2085,887,1198,2265090,115428,1811981,1812818) if AL else (2841,1056,1785,1182676,40031,946007,946377)
ck(keys==a['ordered_full_keys'] and len(keys)==len(set(keys))==n and keys[:pr]==a['ordered_priority_keys'] and keys[pr:]==a['ordered_remainder_keys'] and len(keys[pr:])==rest)
votes=[u['reported_candidate_votes'] if AL else u['votes'] for u in full]
ck(sum(votes)==den and sum(votes[:15])==top and sum(votes[:pr-1])==preceding and sum(votes[:pr])==cross and 5*preceding<4*den<=5*cross,'independent integer crossing')
for i,(u,v) in enumerate(zip(full,votes)):
 ck(u['rank']==i+1 and u['cumulative_votes']==sum(votes[:i+1]) and (i==0 or votes[i-1]>=v),'entire numeric source ranking')
for parent,r in a['all_parent_ordered_child_arrays'].items():
 units=[u for u in full if u['county_fips']==r['county_fips']];ks=[u['key'] for u in units];p=c['parents' if AL else 'all75parents'][int(r['complete_parent_contract_pointer'].split('/')[-1])]
 ck(sha(canonical(p))==r['complete_original_parent_semantic_sha256'] and r['full_source_rank_ordered_children']==ks)
 ck(r['ordered_priority_children']==[k for k in ks if k in set(keys[:pr])] and r['ordered_remainder_children']==[k for k in ks if k not in set(keys[:pr])])
ck(len(parents)==len(a['all_parent_ordered_child_arrays'])==(67 if AL else 75) and len(a['ordered_priority_parent_fips'])==(63 if AL else 68))
for r in a['producer_seals']:
 m=parsed(r);rows=m[r['owned_field']];ck(len(rows)==r['owned_entries']);root=(S/r['path']).parent
 extra=['turnout.md','data/county-turnout.csv'] if root.name=='turnout' else ['county-partisanship.md','data/county-baselines.csv']
 ck({v['path'] for v in rows}=={str(p.relative_to(S)) for p in root.rglob('*') if p.is_file() and p!=S/r['path']}|set(extra),'complete sealed producer membership')
 for p in rows:checked(p)
for k in ['current_geography_approved','current_November_returns_admitted','current_choice_or_reporting_IDs_approved','legal_native80_robustness_approved','live_cadence_or_exact_remainder_approved','collector_or_probability_approval']:ck(a[k] is False)
out={'status':'pass_independent_complete_exhaustive_source_authority_replay','checks':N,'complete_roots':len(c),'complete_companions':len(a['complete_source_companion_files']),'every_recursive_object':total,'every_ordered_partition':len(a['complete_source_object_reference_bodies']),'entire_source_traversal_exhausted':True,'fixed_files':len(pins),'historical_body_resolvers':len(a['historical_full_body_resolvers']),'complete_archives':len(archives),'all_native':n,'priority':pr,'remainder':rest,'parents':len(parents),'priority_parents':len(a['ordered_priority_parent_fips']),'producer_writes':False,'current_or_legal_or_live_approval':False}
b=(json.dumps(out,indent=2)+'\n').encode();p=D/'coordinator-priority-validation.json'
if '--check' in sys.argv:ck(p.read_bytes()==b,'frozen proof exact')
else:p.write_bytes(b)
print(json.dumps(out))
