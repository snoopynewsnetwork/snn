"""Independent read-only complete historical graph replay; path-only acceptance authority.
No producer/coordinator code is imported or executed. Source bodies stay in memory.
"""
from pathlib import Path
from collections import Counter,defaultdict
import csv,gzip,hashlib,io,json,tarfile,sys
STATE=Path(__file__).resolve().parents[2]
AUTH=STATE/'data/coordinator-priority-acceptance.json'
def hashbytes(b):return hashlib.sha256(b).hexdigest()
def noduplicates(pairs):
 d={}
 for k,v in pairs:
  if k in d:raise ValueError('duplicate JSON key')
  d[k]=v
 return d
def loads(b):return json.loads(b,object_pairs_hook=noduplicates,parse_constant=lambda s:(_ for _ in ()).throw(ValueError('nonfinite token')))
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def check(condition,label):
 if not condition:raise AssertionError(label)
def parse_bytes(path,b):
 if path.endswith('.gz'):b=gzip.decompress(b)
 if path.endswith(('.csv','.csv.gz')):return list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))
 if '.jsonl' in path:return [loads(line) for line in b.splitlines() if line]
 return loads(b)
def replay():
 a=loads(AUTH.read_bytes())
 roles=[];seen={};checks=Counter()
 def readpin(p,role):
  raw=(STATE/p['path']).read_bytes()
  check(len(raw)==p['bytes'] and len(raw)<40000000 and hashbytes(raw)==p['sha256'],'immutable whole-file pin '+p['path'])
  checks['whole_file_pins']+=1
  # Individual immutable source roles only, never acceptance digest/body or reverse pin.
  key=(p['path'],p['sha256'],role)
  if key not in seen:
   seen[key]=True;roles.append({'path':p['path'],'bytes':len(raw),'sha256':hashbytes(raw),'role':role})
  return raw
 for p in a['frozen_file_pins']:readpin(p,'frozen complete file')
 for p in a['independent_coordinator_reviews']:readpin(p,'immutable original review')
 contract=parse_bytes(a['frozen_contract']['path'],readpin(a['frozen_contract'],'whole historical contract'))
 check(len(contract)==len(a['complete_root_field_semantics'])==18,'all contract roots')
 for p in a['complete_root_field_semantics']:
  key=p['pointer'][1:];check(hashbytes(canonical(contract[key]))==p['full_recursive_semantic_sha256'],'complete root semantics');checks['roots']+=1
 companions=[]
 for p in a['complete_source_companion_files']:
  v=parse_bytes(p['path'],readpin(p,'complete source companion'))
  check(hashbytes(canonical(v))==p['full_semantic_sha256'],'entire companion semantic identity')
  check((len(v) if isinstance(v,(dict,list)) else None)==p['complete_length'],'entire companion length')
  companions.append(p);checks['companions']+=1
 archives={};members=defaultdict(set)
 for p in a['historical_full_body_resolvers']:
  st=p['storage']
  if st['kind']=='immutable_original_reference':raw=readpin(st['file'],'historical immutable original reference')
  else:
   ar=st['archive'];key=(ar['path'],ar['sha256'])
   if key not in archives:
    archives[key]=tarfile.open(fileobj=io.BytesIO(readpin(ar,'complete historical archive')),mode='r:gz')
   raw=archives[key].extractfile(st['member']).read();members[key].add(st['member'])
   roles.append({'path':p['path'],'bytes':len(raw),'sha256':hashbytes(raw),'role':'exact historical archive member','archive':ar['path'],'archive_sha256':ar['sha256'],'member':st['member']})
  check(len(raw)==p['bytes'] and hashbytes(raw)==p['sha256'],'exact historical body');checks['historical_bodies']+=1
 for key,tf in archives.items():check(members[key]=={m.name for m in tf.getmembers() if m.isfile()},'complete archive membership');checks['archives']+=1
 def objects(file,v,ptr):
  yield file,ptr,v
  if isinstance(v,(dict,list)):
   for k,x in v.items() if isinstance(v,dict) else enumerate(v):
    if isinstance(x,(dict,list)):yield from objects(file,x,ptr+'/'+str(k).replace('~','~0').replace('/','~1'))
 def expected():
  for k,v in contract.items():yield 'data/turnout/priority-set.json','/'+k,v
  for p in companions:
   v=parse_bytes(p['path'],readpin(p,'complete source companion'))
   if isinstance(v,(dict,list)):yield from objects(p['path'],v,'')
 stream=iter(expected());byfile=Counter()
 for p in a['complete_source_object_reference_bodies']:
  raw=gzip.decompress(readpin(p,'complete ordered source-reference partition'))
  check(len(raw)==p['complete_reconstructed_bytes'] and hashbytes(raw)==p['complete_reconstructed_sha256'],'whole partition reconstruction')
  count=0
  for line in raw.splitlines():
   ref=loads(line);file,ptr,v=next(stream)
   check((file,ptr,hashbytes(canonical(v)))==(ref['file'],ref['pointer'],ref['full_recursive_semantic_sha256']),'ordered complete recursive source object')
   byfile[file]+=1;count+=1
  check(count==p['complete_object_count'],'partition object count');checks['partitions']+=1
 try:next(stream);raise AssertionError('source traversal not exhausted')
 except StopIteration:pass
 check(sum(byfile.values())==a['complete_source_object_count'] and dict(byfile)==a['source_objects_by_file'],'all source objects/all partitions exhausted')
 full=contract['full_order'];keys=[x['key'] for x in full];pr=contract['ordered_priority_keys'];re=contract['remainder_keys']
 check(len(keys)==len(set(keys))==2841 and keys==a['ordered_full_keys'] and keys[:1056]==pr==a['ordered_priority_keys'] and keys[1056:]==re==a['ordered_remainder_keys'],'full ordered universe')
 check(full==sorted(full,key=lambda x:(-x['votes'],x['key'])),'full rank tie-break')
 cumulative=0
 for i,u in enumerate(full):
  cumulative+=u['votes'];check(u['rank']==i+1 and cumulative==u['cumulative_votes'],'rank/cumulative')
  check(sum(u['candidates'].values())==u['votes'] and sum(u['methods'].values())==u['votes'],'all own candidate/method counts')
 check(cumulative==1182676 and sum(x['votes'] for x in full[:15])==40031,'denominator/top15')
 check(sum(x['votes'] for x in full[:1055])==946007 and sum(x['votes'] for x in full[:1056])==946377 and 5*946007<4*1182676<=5*946377,'exact crossing')
 check(full[1055]['native_name']=='GRASSEY OUTSIDE' and full[1055]['county_name']=='CLEBURNE' and full[1055]['votes']==370,'crossing identity')
 for key,p in a['all_parent_ordered_child_arrays'].items():
  parent=contract['all75parents'][int(p['complete_parent_contract_pointer'].split('/')[-1])]
  children=[x['key'] for x in full if x['county_fips']==p['county_fips']]
  check(hashbytes(canonical(parent))==p['complete_original_parent_semantic_sha256'],'whole original parent')
  check(children==p['full_source_rank_ordered_children'] and [k for k in children if k in set(pr)]==p['ordered_priority_children'] and [k for k in children if k in set(re)]==p['ordered_remainder_children'],'every full/priority/remainder parent array');checks['parents']+=1
 check(len(contract['all75parents'])==75 and len(set(u['county_fips'] for u in full[:1056]))==len(a['ordered_priority_parent_fips'])==68,'all 75/68 parents')
 for p in a['producer_seals']:
  mf=parse_bytes(p['path'],readpin(p,'immutable original producer manifest'));root=(STATE/p['path']).parent
  rows=mf[p['owned_field']];extra=['turnout.md','data/county-turnout.csv'] if root.name=='turnout' else ['county-partisanship.md','data/county-baselines.csv']
  actual={str(x.relative_to(STATE)) for x in root.rglob('*') if x.is_file() and x!=STATE/p['path']}|set(extra)
  check({x['path'] for x in rows}==actual and len(rows)==p['owned_entries'],'whole original producer membership')
  for x in rows:readpin(x,'complete producer owned file')
 for k in ['current_geography_approved','current_November_returns_admitted','current_choice_or_reporting_IDs_approved','legal_native80_robustness_approved','live_cadence_or_exact_remainder_approved','collector_or_probability_approval']:check(a[k] is False,'no current admission')
 return {'status':'pass','authority_path':str(AUTH.relative_to(STATE)),'scope':'complete historical source graph only; source histories and every recursive field retained, no producer code executed','checks':dict(checks),'recursive_source_objects':sum(byfile.values()),'full':2841,'priority':1056,'remainder':1785,'priority_parents':68,'producer_writes':False,'current_approval':False},roles
if __name__=='__main__':
 proof,roles=replay()
 if '--write' in sys.argv:
  out=Path(__file__).resolve().parents[1]
  (out/'qa/historical-replay.json').write_text(json.dumps(proof,indent=2)+'\n')
  (out/'source-roles.json').write_text(json.dumps(roles,indent=2)+'\n')
 print(json.dumps(proof))
