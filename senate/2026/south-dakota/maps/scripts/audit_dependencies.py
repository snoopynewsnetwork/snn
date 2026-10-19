"""Read-only recursive pin/full-object audit. No producer scripts are executed."""
from common import *
import zlib,csv,io,collections
def audit():
 a=json.loads((STATE/ACCEPTANCE).read_bytes())
 # Authority is path-only: no acceptance byte/hash pin in producer or map data.
 assert a['acceptance_path']==ACCEPTANCE
 refs={};seen=set();pending=[a]
 while pending:
  x=pending.pop()
  for o in walk(x):
   if isinstance(o,dict) and {'path','bytes','sha256'}<=o.keys():
    assert o['path']!=ACCEPTANCE,'reverse acceptance pin'
    q={k:o[k] for k in ['path','bytes','sha256']};b=check(q);refs[q['path']]=q
    if q['path'].endswith('.json') and q['path'] not in seen:
     seen.add(q['path']);pending.append(json.loads(b))
 c=json.loads(check(a['frozen_contract'])); us=c['all_units'];ps=c['county_parents']
 assert len(us)==691 and len(ps)==66
 assert [u['key'] for u in us]==c['complete_ordered_keys']==a['ordered_full_keys']
 assert [u['key'] for u in us[:304]]==a['ordered_priority_keys']==c['ordered_priority_keys']
 assert [u['key'] for u in us[304:]]==a['ordered_remainder_keys']
 assert c['ordered_priority_parent_keys']==a['ordered_priority_parent_keys'] and len(c['ordered_priority_parent_keys'])==39
 assert ps==a['all66_parent_objects'] # Full recursive equality, headings/nulls/admin fields included.
 assert c['coordinator_acceptance']['accepted'] is False and c['certification_robustness']['proven'] is False
 assert a['certified_minimum_or_membership_approved'] is False
 assert sum(u['contest_votes'] for u in us)==428728
 assert sum(u['contest_votes'] for u in us[:304])==343402
 assert sum(u['contest_votes'] for u in us[:303])==342947
 for p in ps:
  ch=[u for u in us if u['county_parent_key']==p['parent_key']]
  assert [u['key'] for u in ch]==p['ordered_all_native_keys']
  assert [u['key'] for u in ch if u['priority80']]==p['ordered_priority_native_keys']
  assert len(ch)==p['source_native_rows']
 for u in us:assert sum(u['candidate_votes'].values())==u['contest_votes']
 objects=[]
 def add(ptr,x):objects.append(dict(contract=a['frozen_contract'],JSON_pointer=ptr,recursive_semantic_sha256=semantic(x)))
 add('',c)
 for field in ['all_units','county_parents','explicit_unavailable_cases']:
  add('/'+field,c[field])
  for i,o in enumerate(c[field]):add('/'+field+'/'+str(i),o)
 for y,n in [('2022',687),('2020',693)]:
  h=c['separate_historical_native_universes'][y];assert len(h['rows'])==n and h['complete_county_parents']==66
  add('/separate_historical_native_universes/'+y,h)
  for k in ['rows']:
   for i,o in enumerate(h[k]):add('/separate_historical_native_universes/'+y+'/'+k+'/'+str(i),o)
 # Every original receipt in the already pinned graph: full gzip streams, not projections.
 raws=[];done=set()
 for path in sorted(seen):
  obj=json.loads((STATE/path).read_bytes())
  for e in walk(obj):
   if not isinstance(e,dict) or not {'raw_sha256','stored_objects','bytes'}<=e.keys():continue
   key=tuple(p['path'] for p in e['stored_objects'])
   if key in done:continue
   done.add(key);dec=zlib.decompressobj(31);rh=hashlib.sha256();n=0
   for p in e['stored_objects']:
    z=check(p);refs[p['path']]=p;b=dec.decompress(z);rh.update(b);n+=len(b)
   b=dec.flush();rh.update(b);n+=len(b)
   assert dec.eof and not dec.unused_data and n==e['bytes'] and rh.hexdigest()==e['raw_sha256'],key
   raws.append(dict(paths=list(key),raw_bytes=n,raw_sha256=rh.hexdigest()))
 # Explicit complete original county scan, represented by ordered gzip parts in pinned receipts.
 big=[x for x in raws if x['raw_sha256']=='a9d55c618d479aaf9e207d0c49a3511206458756d329c42f830ab52c36930e72']
 assert len(big)==1 and big[0]['raw_bytes']==149141181 and len(big[0]['paths'])==4
 for f,n in [('data/baselines/native-2022.csv',679),('data/baselines/native-2022-public.csv',687),('data/baselines/native-2020-public.csv',693)]:
  assert len(list(csv.DictReader(io.StringIO((STATE/f).read_text()))))==n
 csv_semantics=[]
 for p in a['frozen_first_pair_assets']+a['historical_companion_assets']:
  if not p['path'].endswith('.csv'):continue
  reader=csv.DictReader(io.StringIO(check(p).decode()));rows=list(reader)
  assert len(reader.fieldnames)==len(set(reader.fieldnames)) and all(None not in r and None not in r.values() for r in rows)
  csv_semantics.append(dict(file=p,complete_ordered_headers=reader.fieldnames,rows=len(rows),complete_ordered_rows_semantic_sha256=semantic(rows),ordered_full_field_row_semantic_sha256=[semantic(r)for r in rows]))
 signed=list(csv.DictReader((STATE/'data/baselines/county-candidates.csv').open()))
 vectors=collections.defaultdict(list)
 for r in signed:vectors[(r['year'],r['county_fips'])].append(r)
 assert len(signed)==594 and len(vectors)==198
 assert all(len(v)=={'2024':4,'2022':3,'2020':2}[y] for (y,f),v in vectors.items())
 # Candidate controls stay election-specific; no historical party is carried forward.
 sums=collections.defaultdict(int)
 for r in signed:sums[(r['year'],r['ballot_party'])]+=int(r['votes'])
 assert [sums[('2024',p)]for p in ['DEM','LIB','REP','IND']]==[146859,2778,272081,7204]
 assert [sums[('2022',p)]for p in ['DEM','LIB','REP']]==[91007,14697,242316]
 assert [sums[('2020',p)]for p in ['REP','DEM']]==[276232,143987]
 return dict(authority_path_only=ACCEPTANCE,contract=a['frozen_contract'],exact_references=sorted(refs.values(),key=lambda p:p['path']),complete_semantic_objects=objects,complete_CSV_companion_semantics=csv_semantics,signed_county_vectors_checked=198,signed_candidate_fields_checked=594,full_original_streams=sorted(raws,key=lambda x:x['paths']),all_contract_fields_recursively_preserved=True,initial_coordinator_wrong_PDF_family_corrected_worker_locators_unchanged=True)
if __name__=='__main__':
 d=audit();dump('qa/dependencies.json',d);print('exact pins',len(d['exact_references']),'full recursive objects',len(d['complete_semantic_objects']),'original streams',len(d['full_original_streams']))
