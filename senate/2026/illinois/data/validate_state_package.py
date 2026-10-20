"""Complete coordinator state seal; --check is read-only, no producer code."""
from pathlib import Path
import ast,hashlib,json,re,sys,urllib.parse
S=Path(__file__).resolve().parents[1];D=S/'data'
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def load(p):return json.loads(p.read_bytes())
def main(check=False):
 manifest=D/'coordinator-asset-manifest.json';validation=D/'coordinator-validation.json';seals=[];checks=0
 specs=[('turnout','data/turnout/asset-manifest.json','assets',937,'external_originals',6,['turnout.md','data/county-turnout.csv']),('baselines','data/baselines/asset-manifest.json','owned_assets',248,'source_references',478,['county-partisanship.md','data/county-baselines.csv']),('official','data/results-sources/asset-manifest.json','owned_assets',3047,None,0,['official-results.md','data/official-results-sources.csv']),('maps','maps/asset-manifest.json','assets',1006,None,0,['precinct-maps.md'])]
 for role,path,key,n,refkey,nrefs,extra in specs:
  p=S/path;m=load(p);rows=m[key];refs=m[refkey]if refkey else []
  if role=='baselines':refs=[{**r,'path':str((p.parent/r['path']).resolve().relative_to(S.resolve()))}for r in refs]
  assert len(rows)==n and len(refs)==nrefs,(role,len(rows),len(refs))
  for r in rows+refs:
   assert pin(S/r['path'])=={k:r[k]for k in ['path','bytes','sha256']},r['path'];assert (S/r['path']).stat().st_size<40000000;checks+=1
  actual={str(q.relative_to(S))for q in p.parent.rglob('*')if q.is_file()and q!=p}|set(extra)
  assert actual=={r['path']for r in rows},role
  seals.append(dict(role=role,manifest=pin(p),owned=n,exact_external_original_refs=nrefs))
 a=load(D/'coordinator-priority-acceptance.json');c=load(D/'turnout/priority-set.json');assert pin(D/'turnout/priority-set.json')==a['frozen_contract'];assert len(c)==31
 assert (a['source_candidate_denominator'],a['top15_votes'],a['full_native_source_groups'],a['all_source_authorities'],a['priority_source_authorities'])==(5592368,29572,10062,108,97)
 assert len(a['ordered_priority_keys'])==5540 and len(a['ordered_remainder_keys'])==4522 and len(a['ordered_full_keys'])==10062
 assert a['ordered_full_keys']==a['ordered_priority_keys']+a['ordered_remainder_keys']
 assert not any(a[k]for k in ['current_geography_approved','current_November_returns_admitted','current_choice_or_reporting_IDs_approved','legal_native_80_robustness_approved','live_cadence_or_exact_remainder_approved','collector_or_probability_approval'])
 reviews=['coordinator-turnout-final-review.json','coordinator-baseline-final-review.json','coordinator-first-pair-math-review.json','coordinator-county-original-review.json','coordinator-acceptance-validation.json','coordinator-maps-final-review.json','coordinator-maps-visual-review.json','coordinator-official-final-review.json','coordinator-official-visual-legal-review.json','coordinator-official-current-recheck/review.json']
 for name in reviews:assert load(D/name)['status'].startswith('pass'),name
 official=load(D/'coordinator-official-final-review.json');maps=load(D/'coordinator-maps-final-review.json');math=load(D/'coordinator-first-pair-math-review.json')
 for v in [official,maps]:assert v['priority']==5540 and v['remainder']==4522
 assert math['complete_state_scenarios']==99 and math['checks']==1388406
 syntax=links=0
 for p in S.rglob('*'):
  if not p.is_file():continue
  assert p.stat().st_size<40000000,p
  assert not any(v in p.parts for v in ['__pycache__','node_modules','.venv','venv','.pytest_cache']),p
  if p.suffix=='.py':ast.parse(p.read_bytes(),filename=str(p));syntax+=1
 for p in S.rglob('*.md'):
  for target in re.findall(r'\[[^\]\n]*\]\(([^\n)]+)\)',p.read_text()):
   target=target.split(' "')[0].strip('<>');u=urllib.parse.urlsplit(target)
   if u.scheme or u.netloc or not u.path:continue
   dest=(p.parent/urllib.parse.unquote(u.path)).resolve();assert dest.exists()or(not check and dest in [manifest.resolve(),validation.resolve()]),(p,target);links+=1
 result=dict(status='pass_complete_four_question_historical_research_with_explicit_source_limits',actual_question_workers_finished=4,question_seals=seals,exact_owned_original_hash_checks=checks,independent_reviews=[pin(D/name)for name in reviews],historical_acceptance=pin(D/'coordinator-priority-acceptance.json'),frozen_contract=pin(D/'turnout/priority-set.json'),root_fields=31,complete_companions=116,recursive_source_objects=554096,all_original12field_records=146370,all_original_field_positions=1756440,full2024_source_presentations=11535,source_native_groups=10062,priority=5540,remainder=4522,source_authorities=108,priority_parents=97,printed_known_denominator=5592368,top15=29572,preceding5539=4473789,priority_votes=4474312,crossing_votes=523,crossing_literal='StClair88/O FALLON 3',unavailable_named_pools=4,absent_Kennedy_cells=15,pair_zero_preferences_unknown=745,generic_records=57411,state_additional_named_records=40942,unallocated_scope_gap=16469,unallocated_ballot_gap=2470,county_sensitivity_only=17,independent_math_checks=math['checks'],state_scenarios=99,county_targets=8262,native_targets=90558,authority_targets=972,independent_official_checks=official['checks'],independent_maps_checks=maps['checks'],current_directory_authorities=108,local_request_authorities=103,current_setup_or_primary_samples=77,official_receipt_files=902,official_complete_entities=881,map_receipts=342,actual_state_linked_map_originals=75,map_original_PDFs=71,PDF_pages_full_metadata_text_parsed=118,worker_PDF_pages_actually_rendered_and_viewed=7,worker_affine_previews_viewed=4,coordinator_additional_map_pages_viewed=2,Census2020_native_features=10084,Census2020_counties=102,Census2020_exact_XY_positions=1664969,no_browser_claim=True,source_current_leaf_matches=0,Python_AST_files=syntax,local_markdown_links=links,all_producer_bytes_unchanged=True,cache_dependency_directories_absent=True,strict_per_stored_object_limit=40000000,current_geography_returns_liveIDs_cadence_exact_remainder_probability_approved=False,whole_manifest_excludes_only='data/coordinator-asset-manifest.json',validation_has_no_reverse_manifest_pin=True,qualification='Printed-known source historical dispatch only. Generic/eligible native writein allocation and legal80 robustness unproved; null pools/cells, county-city overlap and all discrepancies remain. Current incomplete zero November templates and primary products are not returns. Maps are acquired shared-parent/historical context with no current legal source-label join. Full signed/later roster, exhaustive later docket, current IDs, actual cadence, outstanding pools and calibration remain external qualifications.')
 b=(json.dumps(result,indent=2,ensure_ascii=False)+'\n').encode()
 if check:assert validation.read_bytes()==b
 else:validation.write_bytes(b)
 rows=[pin(p)for p in sorted(S.rglob('*'))if p.is_file()and p!=manifest]
 result=dict(schema='IL-coordinator-whole-state-assets-v1',assets=rows,excludes_only='data/coordinator-asset-manifest.json',total_files=len(rows),total_bytes=sum(r['bytes']for r in rows),maximum_stored_bytes=max(r['bytes']for r in rows),all_producer_bytes_unchanged=True,validation_has_no_reverse_manifest_pin=True)
 b=(json.dumps(result,indent=2,ensure_ascii=False)+'\n').encode()
 if check:assert manifest.read_bytes()==b
 else:manifest.write_bytes(b)
 print(json.dumps(dict(validation=pin(validation),manifest=pin(manifest),files=len(rows),total_bytes=result['total_bytes'],maximum=result['maximum_stored_bytes'])))
if __name__=='__main__':main('--check'in sys.argv)
