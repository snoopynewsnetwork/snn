"""External full-field historical source dispatch, no producer modification."""
from pathlib import Path
from collections import Counter
import csv,gzip,hashlib,io,json
S=Path(__file__).resolve().parents[1];D=S/'data';T=D/'turnout';B=D/'baselines'
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def semantic(v):return sha(canonical(v))
def pin(p):
 b=p.read_bytes();assert len(b)<40000000;return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))
def escaped(v):return str(v).replace('~','~0').replace('/','~1')
def read(p):
 b=p.read_bytes();b=gzip.decompress(b)if p.suffix=='.gz'else b
 if '.csv'in p.name:return list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))
 if '.jsonl'in p.name:return [json.loads(l)for l in b.splitlines()if l]
 return json.loads(b)
class Ledger:
 def __init__(self):self.parts=[];self.total=0;self.by_file=Counter();self.start()
 def start(self):self.buffer=io.BytesIO();self.gz=gzip.GzipFile(fileobj=self.buffer,mode='wb',mtime=0,filename='');self.digest=hashlib.sha256();self.size=0;self.count=0;self.files=Counter()
 def emit(self,file,locator,value):
  if self.count>=150000:self.close();self.start()
  line=canonical(dict(file=file,**locator,full_recursive_semantic_sha256=semantic(value)))+b'\n';self.gz.write(line);self.digest.update(line);self.size+=len(line);self.count+=1;self.total+=1;self.files[file]+=1;self.by_file[file]+=1
 def walk(self,file,value,pointer=''):
  if isinstance(value,(dict,list)):
   self.emit(file,dict(pointer=pointer),value)
   for k,v in (value.items()if isinstance(value,dict)else enumerate(value)):
    if isinstance(v,(dict,list)):self.walk(file,v,pointer+'/'+escaped(k))
 def close(self):
  self.gz.close();b=self.buffer.getvalue();assert len(b)<40000000
  p=D/f'coordinator-full-source-object-refs-v1-{len(self.parts)+1:04}.jsonl.gz'
  if p.exists():assert p.read_bytes()==b
  else:p.write_bytes(b)
  self.parts.append(dict(**pin(p),complete_reconstructed_bytes=self.size,complete_reconstructed_sha256=self.digest.hexdigest(),complete_object_count=self.count,source_objects_by_file=dict(self.files),format='Every ordered JSONL reference in this complete partition must be replayed; not a sample.'))
def main():
 c=read(T/'priority-set.json');assert pin(T/'priority-set.json')['sha256']=='606115d18e8fe1c6a30a34d4aeab5fdf6e3716fc55c3daa534769d678ed27237';assert c['independent_peer_agreement']is True and not c['coordinator_accepted']and not c['current_geometry_approved']
 assert (len(c['all_unit_order']),len(c['ordered_priority_keys']),len(c['ordered_remainder_keys']),len(c['all_parent_child_maps']))==(2394,1470,924,351)
 summary=c['summary'];assert (summary['statewide_votes'],summary['top15_votes'],summary['preceding_votes'],summary['minimum80_votes'],summary['crossing_votes'])==(3407108,58012,2725231,2726450,1219)
 review_names=['coordinator-turnout-final-review.json','coordinator-baseline-final-review.json','coordinator-first-pair-math-review.json','coordinator-live-input-review/review.json']
 for n in review_names:assert read(D/n)['status'].startswith('pass')
 seals=[]
 for root,n,extra in [(T,524,['turnout.md','data/county-turnout.csv']),(B,257,['county-partisanship.md','data/county-baselines.csv'])]:
  m=read(root/'asset-manifest.json');rows=m['owned_assets'];assert len(rows)==n
  actual={str(p.relative_to(S))for p in root.rglob('*')if p.is_file()and p!=root/'asset-manifest.json'}|set(extra);assert actual=={r['path']for r in rows}
  for r in rows:assert pin(S/r['path'])==r
  refkey='reused_originals'if root==T else'reused_readonly_inputs';refs=m[refkey]
  for r in refs:
   b=(S/r['path']).read_bytes()
   if 'stored_sha256'in r:
    assert len(b)==r['stored_bytes']and sha(b)==r['stored_sha256'];raw=gzip.decompress(b);assert len(raw)==r['raw_bytes']and sha(raw)==r['raw_sha256']
   else:assert pin(S/r['path'])==r
  seals.append(dict(**pin(root/'asset-manifest.json'),owned_field='owned_assets',owned_entries=n,owned_path_resolution='state-relative',original_reference_field=refkey,original_reference_path_resolution='state-relative',every_complete_listed_body_required=True))
 ledger=Ledger();file='data/turnout/priority-set.json'
 for k,v in c.items():ledger.emit(file,dict(pointer='/'+escaped(k)),v)
 for f in ['all_unit_order','all_parent_child_maps']:
  for i,v in enumerate(c[f]):ledger.walk(file,v,'/'+f+'/'+str(i))
 paths=set()
 for root in [T,B]:
  for folder in ['extract','orders']:
   for p in (root/folder).glob('*'):
    if p.is_file()and p.name.endswith(('.json','.json.gz','.jsonl.gz','.csv','.csv.gz')):paths.add(p)
  for p in (root/'source').glob('*.json'):paths.add(p)
 for rel in ['controls.json','ranking-summaries.json','sensitivity-impacts.json','writein-scope-bounds.json','peer-audit/comparison.json']:
  p=T/rel
  if p.exists():paths.add(p)
 for rel in ['controls.json','priority-set.json','municipal-baselines.csv','statistics-controls.json','peer-audit/comparison.json','peer-audit/statistics-comparison.json','scenarios/settings.json','scenarios/state-targets.csv','scenarios/priority-sensitivity.json']:
  p=B/rel
  if p.exists():paths.add(p)
 for p in (B/'scenarios').glob('*'):
  if p.is_file()and p.name.endswith(('.csv','.json','.json.gz')):paths.add(p)
 companions=[]
 for p in sorted(paths):
  r=pin(p);b=p.read_bytes()
  if p.suffix=='.gz':
   b=gzip.decompress(b);r.update(complete_reconstructed_bytes=len(b),complete_reconstructed_sha256=sha(b))
  value=read(p);r.update(full_semantic_sha256=semantic(value),complete_length=len(value),semantic_type=type(value).__name__,complete_body_required=True,projection_or_subset_substitution=False);file=str(p.relative_to(S))
  if '.csv'in p.name:
   r['complete_header']=value[0]
   for i,row in enumerate(value,1):ledger.emit(file,dict(CSV_row_1based_including_header=i),row)
  elif '.jsonl'in p.name:
   for i,row in enumerate(value,1):ledger.walk(file,row,'/'+str(i-1))
  else:ledger.walk(file,value)
  companions.append(r)
 ledger.close()
 keys=[r['native_key']for r in c['all_unit_order']];priority=set(c['ordered_priority_keys']);remainder=set(c['ordered_remainder_keys']);assert not(priority&remainder);parents={};priorityparents=[]
 for k in c['ordered_priority_keys']:
  name=json.loads(k)[0]
  if name not in priorityparents:priorityparents.append(name)
 assert len(priorityparents)==287
 for p in c['all_parent_child_maps']:
  children=p['native_keys_source_order'];ranked=[k for k in keys if json.loads(k)[0]==p['literal_city_town']];assert set(children)==set(ranked)
  parents[p['municipal_key']]=dict(literal_city_town=p['literal_city_town'],original_source_ordered_children=children,canonical_rank_ordered_children=ranked,ordered_priority_children=[k for k in ranked if k in priority],ordered_remainder_children=[k for k in ranked if k in remainder])
 first=['turnout.md','county-partisanship.md','data/county-turnout.csv','data/county-baselines.csv','data/turnout/validation.json','data/turnout/final-seal.json','data/turnout/source/SCHEMA.md','data/baselines/validation.json','data/baselines/final-seal.json','data/baselines/source/SCHEMA.md','data/baselines/calculate.py','data/baselines/synthetic/validation.json']
 result=dict(schema='MA-external-complete-historical-source-dispatch-v1',status='accepted_complete_historical_named_source_research_dispatch_only',coordinator_agent_id='d0fc3534-1613-4883-b48b-21a233fcfd9e',state='MA',authority='PATH ONLY in downstream worker packages; never copy or reverse-pin this acceptance or modify frozen producer flags.',frozen_contract=pin(T/'priority-set.json'),producer_seals=seals,frozen_first_pair_assets=[pin(S/p)for p in first],independent_coordinator_reviews=[pin(D/p)for p in review_names],primary_scope=c['candidate_universe'],source_candidate_denominator=3407108,top15_votes=58012,minimum80=dict(count=1470,votes=2726450,preceding_count=1469,preceding_votes=2725231,crossing_key=summary['crossing_key'],crossing_votes=1219),remainder=dict(count=924,votes=680658),full_native_source_groups=2394,all_source_municipal_parents=351,priority_municipal_parents=287,ordered_full_keys=keys,ordered_priority_keys=c['ordered_priority_keys'],ordered_remainder_keys=c['ordered_remainder_keys'],ordered_priority_parent_literals=priorityparents,derived_ordered_child_arrays_by_parent=parents,complete_root_field_semantics=[dict(pointer='/'+escaped(k),full_recursive_semantic_sha256=semantic(v))for k,v in c.items()],complete_source_companion_files=companions,complete_source_object_reference_bodies=ledger.parts,complete_source_object_count=ledger.total,source_objects_by_file=dict(ledger.by_file),full_field_rule='Reconstruct every complete root/companion/ledger object and every producer sealed input/body/schema/position/null/admin field. Ledger partitions together are complete, not samples. Source bodies reused immutably; no votes-only or selected-only projection, mutable news aggregate, producer writer or unfinished proof dependency.',source_partitions=dict(native_by_contest={'2024-senate':2394,'2020-senate':2173,'2022-governor':2390,'2024-president':2394},municipal_each=351,full_native_contest_records=9351,full_numeric_source_positions=75566,municipal_native_column_balances=9828,baseline_full_orders=32,turnout_full_orders=24,empty_WardPct_2022_unallocated_municipal_contexts=118,state_scenarios=36,unit_target_rows=36702),source_qualifications=['2020Markey Senate sameClassII;2024Warren Senate otherClassI;2024President separate;2022Governor actual midterm, no invented2022Senate. No candidate-effect/current native or crossyear join.', 'Printed WarrenDeaton3407108 named source universe only. AllOthers6221 generic/Blanks99601/TBC3512930 separate; no eligible or namedwritein allocation/legal80 robustness. Same full-generic membership does not establish robustness;955outside/2277inside bounds counterfactual only.', 'All2394 literal tuple/ordinal keys and351 full municipal arrays preserved, no county substitution. The2022native118 sole emptyWardPct records remain municipal-level/unallocated, not fabricated precincts. Methods/admin/numericIDs/registration/under-over remain unknown where absent.', '2022Governor14countyHTML differs CSV and samepage footer by[-3189,+90,-39,-12,-13,-3163], unallocated. CSV/HTML candidate party-WriteIn metadata remain distinct.', '2020PD43 turnout+33 and2024method source-64 remain unallocated. Supplemental browser registration347rows versus351 andcounty controls retain missing4towns/sixcounty field differences; direct statistical originals403. No native allocation or registration-minus-votes outstanding estimate.', 'Reciprocal scopes frozen exactly: baseline compared earlier turnout original-first; final turnout captures all257finalbaseline assets+manifest and18inputpins. All old109/198 witnesses exact; no false future body equality.', 'Current official general candidate browser list is bounded metadata, not signed exhaustive ballot/writein/currentnumeric feed/geometry approval. All future legal/current/feed/calibration qualifications remain external.'],dispatch_requirements=['Inventory actual state and all351 municipal election/canvass authorities/raw directory fields; deeply investigate all287priority source-parent chains using bounded actual public source requests, with1470ordered complete investigations plus924remainder/all2394/full351 hierarchy.', 'Acquire actual official/linked map assets and qualified complete-state historical fallback. Every1470source observation has specific shared-resource/source-vintage/finer/physical/current-ID/access gaps; no invented result-label/physical/legal/current match or spatial vote allocation.', 'First independently verify exact acceptance/contract bytes then consume entire acceptance in memory. Acceptance authority PATH ONLY, no reverse hash/body dependency; replay every complete root/companion/partitioned reference/source body, originals and full schemas. No producer/shared writes, newagents, Git or unfinished peer/coordinator build dependency.'],current_geography_approved=False,current_November_returns_admitted=False,current_choice_or_reporting_IDs_approved=False,legal_native_80_robustness_approved=False,live_cadence_or_exact_remainder_approved=False,collector_or_probability_approval=False)
 p=D/'coordinator-priority-acceptance.json';b=(json.dumps(result,indent=2,ensure_ascii=False)+'\n').encode();assert len(b)<40000000
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
 print(dict(acceptance=pin(p),root_fields=len(c),companions=len(companions),objects=ledger.total,ledger_parts=len(ledger.parts),priority_parents=287))
if __name__=='__main__':main()
