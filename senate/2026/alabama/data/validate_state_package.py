"""Whole-state coordinator publication inventory; --check performs no writes."""
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
 mf=D/'coordinator-asset-manifest.json';validation=D/'coordinator-validation.json';seals=[];n=0
 for role,path,key,count,extras in [('turnout','data/turnout/asset-manifest.json','assets',295,['turnout.md','data/county-turnout.csv']),('baselines','data/baselines/asset-manifest.json','assets',306,['county-partisanship.md','data/county-baselines.csv']),('official','data/results-sources/asset-manifest.json','files',1522,['official-results.md','data/official-results-sources.csv']),('maps','maps/asset-manifest.json','assets',5239,['precinct-maps.md'])]:
  p=S/path;rows=load(p)[key];actual={str(f.relative_to(S)) for f in p.parent.rglob('*') if f.is_file() and f!=p}|set(extras)
  assert len(rows)==len({v['path'] for v in rows})==count and {v['path'] for v in rows}==actual,role
  for v in rows:assert pin(S/v['path'])=={k:v[k] for k in ['path','bytes','sha256']} and v['bytes']<40000000,v['path'];n+=1
  seals.append({'role':role,'manifest':pin(p),'targets_excluding_only_manifest':count})
 a=load(D/'coordinator-priority-acceptance.json');c=load(D/'turnout/priority-set.json');assert pin(D/'turnout/priority-set.json')==a['frozen_contract']
 assert len(a['complete_root_field_semantics'])==29 and len(a['complete_source_companion_files'])==303 and a['complete_source_object_count']==1608035
 assert len(a['complete_source_object_reference_bodies'])==11 and len(a['frozen_file_pins'])==612 and len(a['historical_full_body_resolvers'])==634
 assert len(c['units'])==2085 and len(c['parents'])==67 and a['ordered_full_keys']==c['full_order'] and a['ordered_priority_keys']==c['ordered_priority_keys'] and a['ordered_remainder_keys']==c['remainder_keys']
 assert a['primary_source_denominator']==2265090 and a['top15_votes']==115428 and a['priority_parent_count']==63
 for k in ['current_geography_approved','current_November_returns_admitted','current_choice_or_reporting_IDs_approved','legal_native80_robustness_approved','live_cadence_or_exact_remainder_approved','collector_or_probability_approval']:assert a[k] is False
 names=['coordinator-first-pair-original-review.json','coordinator-first-pair-history-review.json','coordinator-baseline-math-review.json','coordinator-baseline-cli-review.json','coordinator-turnout-reciprocal-final-review.json','coordinator-turnout-isolated-replay-review.json','coordinator-priority-validation.json','coordinator-newsroom-original-review.json','coordinator-audit-source-review.json','coordinator-official-final-review.json','coordinator-maps-final-review.json']
 for name in names:assert load(D/name)['status'].startswith('pass'),name
 syntax=links=0
 for p in S.rglob('*'):
  assert not {'__pycache__','node_modules','.venv','venv','.pytest_cache'}&set(p.relative_to(S).parts),p
  if not p.is_file():continue
  assert p.stat().st_size<40000000 and not p.is_symlink(),p
  if p.suffix=='.py':ast.parse(p.read_bytes(),filename=str(p));syntax+=1
  if p.suffix!='.md':continue
  for target in re.findall(r'\[[^\]\n]*\]\(([^\n)]+)\)',p.read_text()):
   target=target.split(' "')[0].strip('<>');u=urllib.parse.urlsplit(target)
   if u.scheme or u.netloc or not u.path:continue
   base=S if p.name=='report-template.md' else p.parent;dest=(base/urllib.parse.unquote(u.path)).resolve()
   assert dest.exists() or (not check and dest in [mf.resolve(),validation.resolve()]),(p,target)
   links+=1
 old_readme=__import__('gzip').decompress((D/'coordinator-final-integration-history/README.md.gz').read_bytes()).decode();tracker=old_readme[old_readme.index('## Seat details'):];current=(S/'README.md').read_text();assert current[current.index('## Seat details'):]==tracker
 result={'status':'pass_complete_four_question_bounded_historical_source_research','actual_original_workers_finished':4,'producer_seals':seals,'exact_question_owned_hash_checks':n,'independent_reviews':[pin(D/name) for name in names],'full_historical_authority':pin(D/'coordinator-priority-acceptance.json'),'frozen_contract':pin(D/'turnout/priority-set.json'),'complete_roots':29,'whole_companions':303,'every_recursive_object':1608035,'ordered_partitions':11,'fixed_files':612,'historical_whole_body_resolvers':634,'native_contexts':2085,'all_parents':67,'priority':887,'remainder':1198,'priority_parent_chains':63,'denominator':2265090,'top15_votes':115428,'minimum80_votes':1812818,'preceding_votes':1811981,'integer80threshold':1812072,'official_inventory_rows':68,'literal_office_records':278,'official_source_requests':450,'full_official_response_hops':499,'official_PDF_originals':113,'current_county_specimens':67,'Mobile_positive_pre_election_setup_is_not_November_admission':True,'map_acquisition_receipts':975,'map_complete_hop_bodies':1060,'map_complete_SHP_ZIP_audits':46,'map_every_XY_double_value':2516662,'map_every_DBF_token':36657,'native_service_polygons':79,'native_service_actual_polling_points':78,'map_PDF_originals':242,'all_map_PDF_pages_automatically_rendered':2087,'county_map_context_download_parents':26,'approved_leaf_polygon_joins':0,'root_actual_whole_map_pages_viewed':2,'root_actual_official_whole_pages_viewed':2,'genuine_November_counts_admitted':False,'existing_race_tracker_tail_sha256':hashlib.sha256(tracker.encode()).hexdigest(),'all_producer_bytes_unchanged':True,'Python_AST_files':syntax,'relative_Markdown_links':links,'whole_manifest_excludes_only':'data/coordinator-asset-manifest.json','validation_no_reverse_manifest_pin':True,'qualification':'Completed bounded historical/source research only. Generic eligible write-ins, ballot/registration/null/under-over source gaps, final later signed roster/operative code/act/order exhaustion, Madison target-app endorsement, historical/current identity/geometry, genuine updates, measured cadence, eligible remaining pool and collector/forecast/calibration stay unknown or unapproved. Twenty-two full TIGER challenge failures and separate source-generalized cartographic fallback retained; no spatial allocation. Legacy preparation helpers/diagnostics are history/leads, not final reconstruction dependencies.'}
 b=(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode()
 if check:assert validation.read_bytes()==b
 else:validation.write_bytes(b)
 CACHE.pop(validation.resolve(),None);rows=[pin(p) for p in sorted(S.rglob('*')) if p.is_file() and p!=mf]
 whole={'schema':'AL-coordinator-complete-state-inventory-v1','assets':rows,'excludes_only':'data/coordinator-asset-manifest.json','total_files':len(rows),'total_bytes':sum(v['bytes'] for v in rows),'maximum_stored_bytes':max(v['bytes'] for v in rows),'all_producer_bytes_unchanged':True,'validation_no_reverse_manifest_pin':True}
 b=(json.dumps(whole,ensure_ascii=False,indent=2)+'\n').encode()
 if check:assert mf.read_bytes()==b
 else:mf.write_bytes(b)
 print(json.dumps({'status':result['status'],'validation':pin(validation),'files_excluding_only_manifest':len(rows),'total_bytes':whole['total_bytes'],'maximum_stored_bytes':whole['maximum_stored_bytes']}))
if __name__=='__main__':main('--check' in sys.argv)
