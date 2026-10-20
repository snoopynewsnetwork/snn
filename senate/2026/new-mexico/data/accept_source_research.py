"""External full-field source coverage authority; certified native priority unavailable."""
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
 c=read(T/'priority-set.json');assert pin(T/'priority-set.json')['sha256']=='e61fb2a61fca45892171b3c8de1e7fe3ceedefb3dd4fa957ff5d94a6a5581c5a'
 assert len(c)==31 and not c['accepted_for_dispatch'] and c['ordered_priority_keys']==[]
 assert all(c[k]is None for k in ['certified_native_top15','certified_native_minimum80','certified_native_full_order'])
 assert len(c['constituents'])==2201 and len(c['county_contexts'])==33
 review_names=['coordinator-turnout-original-review.json','coordinator-turnout-final-review.json','coordinator-baseline-source-review.json','coordinator-first-pair-math-review.json','coordinator-live-input-review/review.json']
 for name in review_names:assert read(D/name)['status'].startswith('pass')
 live=read(D/'coordinator-live-input-review/review.json');assert live['actual_cases']==21 and live['previously_failing_cases']==16 and live['all_exact_actual_failures_resolved']
 assert pin(B/'calculator.py')['sha256']=='825fd61c5fd3fc5d1a3fbbc3826484998a908c8ef53c5aa9de285f0eabd26cc9'
 seals=[]
 for root,key,count,original_key,extra in [(T,'owned_assets',256,'source_assets',['turnout.md','data/county-turnout.csv']),(B,'owned',342,'external_original_assets',['county-partisanship.md','data/county-baselines.csv'])]:
  m=read(root/'asset-manifest.json');listed=m[key];assert len(listed)==count
  actual={str(p.relative_to(S))for p in root.rglob('*')if p.is_file()and p!=root/'asset-manifest.json'}|set(extra)
  assert actual=={r['path']for r in listed}
  for r in listed+m[original_key]:assert pin(S/r['path'])=={k:r[k]for k in ['path','bytes','sha256']}
  seals.append(dict(**pin(root/'asset-manifest.json'),owned_field=key,owned_entries=count,original_reference_field=original_key,original_entries=len(m[original_key]),all_complete_bodies_required=True,path_resolution='state-relative'))
 assert pin(B/'asset-manifest.json')['sha256']=='ff03786a45ddb3485d71edbe8f2f28f610ef8dd7adfec30d62d05c675a5fd390'
 ledger=Ledger();file='data/turnout/priority-set.json'
 for k,v in c.items():ledger.emit(file,dict(pointer='/'+escaped(k)),v)
 for f in ['constituents','county_contexts','known_observation_scope']:
  if isinstance(c[f],list):
   for i,v in enumerate(c[f]):ledger.walk(file,v,'/'+f+'/'+str(i))
  else:ledger.walk(file,c[f],'/'+f)
 paths=set()
 for root in [T,B]:
  for p in root.iterdir():
   if p.is_file()and p.suffix in ['.json','.csv']and p.name not in ['asset-manifest.json','priority-set.json']:paths.add(p)
  for p in (root/'source').glob('*.json'):paths.add(p)
 for name in ['history/turnout-pre-peer/capture.json','history/baseline-final-peer/capture.json']:paths.add(T/name)
 for name in ['repair-history/pre-input-validation-v1/freeze.json','repair-regressions/results.json']:paths.add(B/name)
 paths|={S/'data/county-turnout.csv',S/'data/county-baselines.csv'}
 companions=[]
 for p in sorted(paths):
  r=pin(p);v=read(p);r.update(full_semantic_sha256=semantic(v),complete_length=len(v),semantic_type=type(v).__name__,complete_body_required=True,projection_or_subset_substitution=False);file=str(p.relative_to(S))
  if '.csv'in p.name:
   r['complete_header']=v[0]
   for i,row in enumerate(v,1):ledger.emit(file,dict(CSV_row_1based_including_header=i),row)
  else:ledger.walk(file,v)
  companions.append(r)
 ledger.close()
 allkeys=[r['key']for r in c['constituents']];assert len(allkeys)==len(set(allkeys))==2201 and set(allkeys)==set(c['complete_coverage_order'])
 parents={}
 for p in c['county_contexts']:
  kids=[r['key']for r in c['constituents']if r['parent_key']==p['key']];assert kids==p['source_native_constituent_keys'];parents[p['key']]=dict(fips=p['fips'],literal_county=p['source_label'],complete_source_ordered_children=kids,coverage_sequence_children=[k for k in c['complete_coverage_order']if k in set(kids)],all_children_research_scope=True,canonical_priority_children=None,current_geometry_crosswalk=None)
 # Historical snapshot references bind old bytes, never the mutable current path of a repaired file.
 history=[]
 for rel in ['history/turnout-pre-peer/capture.json','history/baseline-final-peer/capture.json']:
  cp=T/rel;cap=read(cp);records=[]
  for r in cap['records']:
   if r['storage']=='lossless_gzip_body':
    p=S/r['body'];z=p.read_bytes();raw=gzip.decompress(z);assert sha(z)==r['stored_sha256']and len(z)==r['stored_bytes'];stored=pin(p)
   else:p=S/r['path'];raw=p.read_bytes();stored=pin(p)
   assert sha(raw)==r['sha256']and len(raw)==r['bytes'];records.append(dict(original_path=r['path'],original_bytes=r['bytes'],original_sha256=r['sha256'],storage=r['storage'],immutable_stored_body=stored,reconstruction='gzip decompress'if r['storage']=='lossless_gzip_body'else'exact stored primary file'))
  history.append(dict(capture=pin(cp),complete_records=records,all_records_required=True,current_path_replacement_prohibited=True))
 first=['turnout.md','county-partisanship.md','data/county-turnout.csv','data/county-baselines.csv','data/turnout/validation.json','data/turnout/final-seal.json','data/turnout/source/SCHEMA.md','data/baselines/validation.json','data/baselines/final-seal.json','data/baselines/source/SCHEMA.md','data/baselines/calculator.py','data/baselines/repair-regressions/results.json']
 result=dict(schema='NM-external-complete-qualified-source-coverage-research-v1',status='accepted_complete_source_coverage_research_certified_native_priority_unavailable',state='NM',coordinator_agent_id='d0fc3534-1613-4883-b48b-21a233fcfd9e',authority='PATH ONLY in downstream owned outputs; never copy/reverse-pin acceptance body or hash or change frozen producer flags.',frozen_contract=pin(T/'priority-set.json'),producer_seals=seals,frozen_first_pair_assets=[pin(S/p)for p in first],independent_coordinator_reviews=[pin(D/p)for p in review_names],all_source_native_observations=2201,all_county_research_parents=33,source_ordered_all_native_keys=allkeys,complete_coverage_sequence_keys=c['complete_coverage_order'],coverage_sequence_is_certified_vote_order=False,ordered_research_parent_keys=[p['key']for p in c['county_contexts']],derived_full_child_arrays_by_parent=parents,certified_native_full_order=None,certified_native_top15=None,certified_native_minimum80=None,ordered_priority_keys=[],county_dispatch_substitution_authorized=False,source_candidate_denominator=903311,known_source_observation_scope=c['known_observation_scope'],unavailable_source_keys=c['unavailable_order_keys'],source_qualifications=['All2201source rows and33county parents retained, including33VoterPrivacy administrative aggregates and20masked candidate rows/30candidate+6control masks. Every protected literal/value remains null orasterisk, no reverse reconstruction or residual allocation. No certified native vote order/top15/min80 exists in this approval.', 'Observed2181completecandidate rows902421votes/scoped1392=722113 after1391=721760/Valencia36+353 andtop1514647 are descriptive only. Knownprefix againststate903311 reaches1394/722817, NOT certified minimum/membership. County10/725900 andcountyTop15806821 are separate sensitivities, nevernative dispatch.', '2020sameII Senate,2024otherI Senate,2024President separate andactual2022Governor/noSenate: all33countycontrols/495PDFcandidatecells close primary state. Native1959/2201/2202/2196 include33privacyaggregate rows each. Otero18 appearspresident but absentSenate, notSenate0.', 'Actualballots2024=928290 and2022=714754 close all33PDF/portal/native/service;2020PDF928172 versusportal928230/net-58 across7counties remainsunallocated. CandidateexportTotalBallotsCast canmirrorcandidate scope orzero nexttomasks, not actualwholeballots.', '2022SandovalPCT051EligibleVoters-3 literal. Oct31/Nov26registration stocks/sourceclocks/partyblanks/nulls/native-countydifferences retained; no current/native method/crossyear/geographicjoin.', '73sharedoriginalreceipt captures plus fullsource parties/headers/positions/rawmetadata/cells/controls survive. Superseded supplementalbaselineHTMLmetadata receipt gaps remain explicit; allentitybytes and finalfreshsource receipts retained, no invented earlier UTC/headers.', 'Turnoutsourceaudit captures older finalbaseline104bodies exactly, excludes later repaired calculator/report/MF outcomes. Historical snapshots below are immutable virtual references by oldpath+SHA, never assumed equal to repaired current baseline paths. All original witnesses/histories retained. Baselineinput repair resolves21actualCLIcases/16failures and132own regressions; historicalscenario/sourcebytes unchanged.', 'Current2917candidateportal allfourstatusrows/primary2911/historical ElectionStats namespaces separate. No signed/later statewide roster/writeinexhaustion, current numericchoice/reporting/unit/methodIDs, legal/native80robustness, physical/currentgeometry/feed/cadence/eligiblepool/collector/probability approval.'],complete_root_field_semantics=[dict(pointer='/'+escaped(k),full_recursive_semantic_sha256=semantic(v))for k,v in c.items()],complete_source_companion_files=companions,complete_source_object_reference_bodies=ledger.parts,complete_source_object_count=ledger.total,source_objects_by_file=dict(ledger.by_file),immutable_historical_snapshot_body_resolvers=history,full_field_rule='Reconstruct every31rootfield, everywholecurrent source/schema/control/candidate/null/rawposition companion and everyordered object across allcomplete ledger partitions. All producer seals/inputbodies/histories/schema bytes remainrequired. Historical oldpath+SHA references resolve exact captured bytes, notcurrent repaired paths. No projection, truncation, mutable newsroom aggregate, producer writer orunfinishedoptionalproofdependency.',source_partitions=dict(native_by_contest={'2024-senate':2201,'2020-senate':1959,'2022-governor':2196,'2024-president':2202},county_each=33,county_rows=132,source_candidate_control_positions=50179,independent_county_PDF_candidate_cells=495,native_ballot_eligible_rows=6257,registration_shared_rows=4470,additional_original_registration_grand_totals=2,source_scoped_orders=18,state_scenarios=32,county_target_rows=1056,native_target_rows=17116),dispatch_requirements=['Officialsource worker inventories actualstate/all33countyroles/fields/links/blanks and deeply followsALL33parent publicchains, then2201complete sourcecoverage investigations with explicitadmin/masked/unavailablecases. These are sharedparent investigations, not2201livefeeds and not a certifiedprioritysubset.', 'Maps worker investigates all33sourceparents and preservesall2201full source observations/coveragehierarchy, actual qualifiedshared resources/native snapshots/historicalfallback and perentry access/vintage/legal/finer/physical/currentIDgaps. No fabricatedpolygon or candidate/private/registration allocation.', 'First independently verify externalacceptance/contract exactbytes/hashes in memory; downstreamauthority PATHONLY/no reversehash/body dependency. Independently replay allcomplete fields/companions/ordered objectpartitions/producerseals/originalbodies/fullschemas and historicalsnapshot virtualreferences. No producer/sharedwrites/Git/newagents/finishedpeercontact or optionalunfinished proofdependency.'],current_geography_approved=False,current_November_returns_admitted=False,current_choice_or_reporting_IDs_approved=False,legal_native_80_robustness_approved=False,live_cadence_or_exact_remainder_approved=False,collector_or_probability_approval=False)
 p=D/'coordinator-source-research-acceptance.json';b=(json.dumps(result,indent=2,ensure_ascii=False)+'\n').encode();assert len(b)<40000000
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
 print(dict(acceptance=pin(p),roots=len(c),companions=len(companions),objects=ledger.total,parts=len(ledger.parts),source_native=2201,parents=33,certified_priority=None))
if __name__=='__main__':main()
