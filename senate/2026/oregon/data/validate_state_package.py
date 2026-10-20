"""Coordinator whole historical/source package seal; --check is read-only."""
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
 specs=[('turnout','data/turnout/asset-manifest.json','owned_assets',4367,['turnout.md','data/county-turnout.csv']),('baselines','data/baselines/asset-manifest.json','assets',599,['county-partisanship.md','data/county-baselines.csv']),('official','data/results-sources/asset-manifest.json','files',766,['official-results.md','data/official-results-sources.csv']),('maps','maps/asset-manifest.json','files',1493,['precinct-maps.md'])]
 for role,name,key,count,extra in specs:
  p=S/name;m=load(p);rows=m[key];actual={str(q.relative_to(S)) for q in p.parent.rglob('*') if q.is_file() and q!=p}|set(extra)
  assert len(rows)==len({r['path'] for r in rows})==count and actual=={r['path'] for r in rows},role
  for r in rows:assert pin(S/r['path'])=={k:r[k] for k in ['path','bytes','sha256']} and r['bytes']<40000000,r['path'];n+=1
  seals.append({'role':role,'manifest':pin(p),'owned_entries_excluding_manifest':count})
 a=load(D/'coordinator-source-research-acceptance.json');c=load(D/'turnout/priority-set.json');assert pin(D/'turnout/priority-set.json')==a['frozen_contract'];assert len(c)==23 and len(a['complete_source_companion_files'])==1994 and a['complete_source_object_count']==495672 and len(a['complete_source_object_reference_bodies'])==4
 assert len(c['all_36_county_parents'])==36 and a['all_complete_parent_objects']==c['all_36_county_parents']
 assert len(a['known_ordered_native_keys'])==510 and a['known_ordered_native_keys']==c['known_source_universe']['full_ordered_keys'] and len(a['unavailable_parent_keys'])==31
 for k in ['certified_native_full_order','certified_native_top15','certified_native_minimum80','ordered_priority_keys','canonical_remainder_keys']:assert a[k] is None
 for k in ['current_geography_approved','current_November_returns_admitted','current_choice_or_reporting_IDs_approved','legal_native_80_robustness_approved','live_cadence_or_exact_remainder_approved','collector_or_probability_approval']:assert a[k] is False
 reviews=['coordinator-turnout-original-review.json','coordinator-turnout-reciprocal-final-review.json','coordinator-baseline-source-review.json','coordinator-baseline-math-review.json','coordinator-baseline-input-review/review.json','coordinator-baseline-repair-review.json','coordinator-source-coverage-validation.json','coordinator-official-final-review.json','coordinator-official-visual-review.json','coordinator-maps-final-review.json']
 for name in reviews:
  status=load(D/name)['status'];assert status.startswith('pass'),(name,status)
 syntax=links=0;fragment=S/'data/results-sources/report-body.md'
 for p in S.rglob('*'):
  assert not {'__pycache__','node_modules','.venv','venv','.pytest_cache'}.intersection(p.relative_to(S).parts),p
  if not p.is_file():continue
  assert p.stat().st_size<40000000,p
  if p.suffix=='.py':ast.parse(p.read_bytes(),filename=str(p));syntax+=1
  if p.suffix!='.md':continue
  for target in re.findall(r'\[[^\]\n]*\]\(([^\n)]+)\)',p.read_text()):
   target=target.split(' "')[0].strip('<>');u=urllib.parse.urlsplit(target)
   if u.scheme or u.netloc or not u.path:continue
   base=S if p==fragment else p.parent;dest=(base/urllib.parse.unquote(u.path)).resolve()
   assert dest.exists() or (not check and dest in [manifest.resolve(),validation.resolve()]),(p,target)
   links+=1
 result={'status':'pass_complete_four_question_bounded_historical_source_research','actual_question_workers_finished':4,'producer_seals':seals,'exact_question_owned_hash_checks':n,'independent_reviews':[pin(D/name) for name in reviews],'qualified_source_authority':pin(D/'coordinator-source-research-acceptance.json'),'frozen_contract':pin(D/'turnout/priority-set.json'),'complete_roots':23,'whole_companions':1994,'recursive_full_objects':495672,'ordered_ledgers':4,'whole_source_pins':5029,'historical_virtual_bodies':5261,'known_native_observations':510,'all_county_parents':36,'unavailable_native_parent_cases':31,'canonical_statewide_native_order_top15_min80_priority_remainder':None,'known_source_only_sensitivity':{'reported_votes':1128521,'minimum80':213,'prefix_votes':904600,'preceding_votes':902447},'county_only_sensitivity':{'reported_votes':2244493,'minimum80':11,'prefix_votes':1814630,'preceding_votes':1764398},'independent_official_checks':20094,'independent_map_checks':248456,'native_map_services':18,'native_nonadditive_features':2174,'native_ID_pages_max50':54,'binary_SHP_layers':3,'binary_features':253,'binary_XY_IEEE754_values':416896,'map_PDFs':135,'automatic_PDF_pages':416,'coordinator_manual_PDF_pages':2,'coordinator_manual_native_previews':1,'static_HTML_atlas_pages':40,'Python_AST_files':syntax,'local_Markdown_links':links,'all_producer_bytes_unchanged':True,'inferred_current_result_polygon_joins':0,'current_November_counts_cadence_eligible_pool_probability_approved':False,'whole_manifest_excludes_only':'data/coordinator-asset-manifest.json','validation_has_no_reverse_manifest_pin':True,'qualifications':'All36parent chains and full510known source objects/31unavailable cases are preserved. No synthetic native records or known/county dispatch substitute. Historical closure/Douglas differences, generic Misc eligibility, participation/ballot discrepancies, source request-metadata/access gaps, curves/empty geometries and map vintage/currency limits survive. Genuine November production/choice/reporting IDs, physical/legal/current joins, later roster/law/docket completeness, measured cadence, eligible remainder, collector and calibrated probability remain false/unknown external qualifications.'}
 b=(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode()
 if check:assert validation.read_bytes()==b
 else:validation.write_bytes(b)
 CACHE.pop(validation.resolve(),None)
 rows=[pin(p) for p in sorted(S.rglob('*')) if p.is_file() and p!=manifest];whole={'schema':'OR-coordinator-whole-source-state-assets-v1','assets':rows,'excludes_only':'data/coordinator-asset-manifest.json','total_files':len(rows),'total_bytes':sum(r['bytes'] for r in rows),'maximum_stored_bytes':max(r['bytes'] for r in rows),'all_producer_bytes_unchanged':True,'validation_has_no_reverse_manifest_pin':True}
 b=(json.dumps(whole,ensure_ascii=False,indent=2)+'\n').encode()
 if check:assert manifest.read_bytes()==b
 else:manifest.write_bytes(b)
 print(json.dumps({'status':result['status'],'validation':pin(validation),'files_excluding_manifest':len(rows),'total_bytes':whole['total_bytes'],'largest':whole['maximum_stored_bytes']}))
if __name__=='__main__':main('--check' in sys.argv)
