"""Coordinator complete historical state seal. --check reads only; no producer imports."""
from pathlib import Path
import ast,hashlib,json,re,sys,urllib.parse
S=Path(__file__).resolve().parents[1];D=S/'data';CACHE={}
def load(p):return json.loads(p.read_bytes())
def pin(p):
 p=p.resolve()
 if p not in CACHE:
  b=p.read_bytes();CACHE[p]={'path':str(p.relative_to(S)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
 return CACHE[p]
def main(check=False):
 manifest=D/'coordinator-asset-manifest.json';validation=D/'coordinator-validation.json';seals=[];n=0
 specs=[('turnout','data/turnout/asset-manifest.json','owned_assets',256,['turnout.md','data/county-turnout.csv']),('baselines','data/baselines/asset-manifest.json','owned',342,['county-partisanship.md','data/county-baselines.csv']),('official','data/results-sources/manifest.json','owned_files',1010,['official-results.md','data/official-results-sources.csv']),('maps','maps/asset-manifest.json','owned_files',993,['precinct-maps.md'])]
 for role,name,key,count,extra in specs:
  p=S/name;m=load(p);rows=m[key];actual={str(q.relative_to(S)) for q in p.parent.rglob('*') if q.is_file() and q!=p}|set(extra);assert len(rows)==len({r['path'] for r in rows})==count and actual=={r['path'] for r in rows},role
  for r in rows:assert pin(S/r['path'])=={k:r[k] for k in ['path','bytes','sha256']} and r['bytes']<40000000,r['path'];n+=1
  seals.append({'role':role,'manifest':pin(p),'owned_entries_excluding_manifest':count})
 a=load(D/'coordinator-source-research-acceptance.json');c=load(D/'turnout/priority-set.json');assert pin(D/'turnout/priority-set.json')==a['frozen_contract'];assert len(c)==31 and len(a['complete_source_companion_files'])==68 and a['complete_source_object_count']==403993 and len(a['complete_source_object_reference_bodies'])==3
 assert a['complete_coverage_sequence_keys']==c['complete_coverage_order'] and len(c['complete_coverage_order'])==2201 and len(set(c['complete_coverage_order']))==2201
 assert a['source_ordered_all_native_keys']==[r['key'] for r in c['constituents']] and set(a['source_ordered_all_native_keys'])==set(c['complete_coverage_order'])
 for k in ['certified_native_full_order','certified_native_top15','certified_native_minimum80']:assert a[k] is None and c[k] is None
 assert a['ordered_priority_keys']==c['ordered_priority_keys']==[] and len(c['county_contexts'])==33
 for k in ['current_geography_approved','current_November_returns_admitted','current_choice_or_reporting_IDs_approved','legal_native_80_robustness_approved','live_cadence_or_exact_remainder_approved','collector_or_probability_approval']:assert a[k] is False
 reviews=['coordinator-turnout-original-review.json','coordinator-turnout-final-review.json','coordinator-baseline-source-review.json','coordinator-first-pair-math-review.json','coordinator-live-input-review/review.json','coordinator-source-acceptance-validation.json','coordinator-official-final-review.json','coordinator-official-visual-review/review.json','coordinator-maps-final-review.json','coordinator-maps-visual-review.json']
 for name in reviews:
  status=load(D/name)['status'];assert status.startswith('pass') or status.startswith('actual_coordinator'),(name,status)
 syntax=links=0;fragment=S/'data/results-sources/report-template.md'
 for p in S.rglob('*'):
  assert not {'__pycache__','node_modules','.venv','venv','.pytest_cache'}.intersection(p.relative_to(S).parts),p
  if not p.is_file():continue
  assert p.stat().st_size<40000000,p
  if p.suffix=='.py':ast.parse(p.read_bytes(),filename=str(p));syntax+=1
  if p.suffix!='.md':continue
  for target in re.findall(r'\[[^\]\n]*\]\(([^\n)]+)\)',p.read_text()):
   target=target.split(' "')[0].strip('<>');u=urllib.parse.urlsplit(target)
   if u.scheme or u.netloc or not u.path:continue
   base=S if p==fragment else p.parent;dest=(base/urllib.parse.unquote(u.path)).resolve();assert dest.exists() or (not check and dest in [manifest.resolve(),validation.resolve()]),(p,target);links+=1
 result={'status':'pass_complete_four_question_historical_source_research_with_explicit_protected_scope','actual_question_workers_finished':4,'producer_seals':seals,'exact_question_owned_hash_checks':n,'independent_reviews':[pin(D/name) for name in reviews],'qualified_source_authority':pin(D/'coordinator-source-research-acceptance.json'),'frozen_contract':pin(D/'turnout/priority-set.json'),'complete_contract_roots':31,'whole_companions':68,'recursive_full_objects':403993,'ordered_reference_partitions':3,'historical_virtual_bodies':196,'all_source_native_observations':2201,'all_county_parents':33,'protected_candidate_rows':20,'administrative_privacy_rows':33,'certified_native_order_top15_minimum80':None,'canonical_priority_keys':[],'observed_complete_candidate_lane':{'rows':2181,'votes':902421,'top15_votes':14647,'descriptive_minimum80':1392,'preceding_votes':721760,'prefix_votes':722113},'county_sensitivity_not_dispatch':{'minimum80':10,'prefix_votes':725900,'source_votes':903311},'independent_official_checks':38106,'independent_map_checks':113588,'native_ZIP_features':[2169,2177],'native_ZIP_XY_positions_bitwise_compared':2317826,'native_service_features':2177,'service_batches_max50':44,'map_PDFs_automatically_rendered':60,'map_PDF_pages_automatically_rendered':194,'coordinator_manual_map_pages':2,'coordinator_native_previews_viewed':1,'Python_AST_files':syntax,'local_Markdown_links':links,'all_producer_bytes_unchanged':True,'current_or_legal_geographic_joins':None,'current_November_counts_cadence_exact_pool_probability_approved':False,'whole_manifest_excludes_only':'data/coordinator-asset-manifest.json','validation_has_no_reverse_manifest_pin':True,'qualifications':'Complete bounded source research and conditional arithmetic. Masks/unknowns stay unallocated; observed and county sensitivities never dispatch. 2020 ballots-58/seven counties, SandovalEligible-3, registration stocks, OteroPres18, primary/status namespaces and SantaFe180-185 versus179native currency gap survive. Full later signed ballot/write-in/legal/docket scope, genuine November IDs/counts/current geometry/eligible remainder/measured cadence/calibration remain external qualifications.'}
 b=(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode()
 if check:assert validation.read_bytes()==b
 else:validation.write_bytes(b)
 CACHE.pop(validation.resolve(),None)
 rows=[pin(p) for p in sorted(S.rglob('*')) if p.is_file() and p!=manifest];whole={'schema':'NM-coordinator-whole-state-assets-v1','assets':rows,'excludes_only':'data/coordinator-asset-manifest.json','total_files':len(rows),'total_bytes':sum(r['bytes'] for r in rows),'maximum_stored_bytes':max(r['bytes'] for r in rows),'all_producer_bytes_unchanged':True,'validation_has_no_reverse_manifest_pin':True}
 b=(json.dumps(whole,ensure_ascii=False,indent=2)+'\n').encode()
 if check:assert manifest.read_bytes()==b
 else:manifest.write_bytes(b)
 print(json.dumps({'status':result['status'],'validation':pin(validation),'files_excluding_manifest':len(rows),'total_bytes':whole['total_bytes'],'largest':whole['maximum_stored_bytes']}))
if __name__=='__main__':main('--check' in sys.argv)
