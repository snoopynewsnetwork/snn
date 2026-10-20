"""Coordinator full-state integrity, source-preservation and link seal.
--check is strictly read-only; producer programs are never imported/executed.
"""
from pathlib import Path
import ast,hashlib,json,re,sys,urllib.parse
S=Path(__file__).resolve().parents[1];D=S/'data'
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def load(p):return json.loads(p.read_bytes())
def main(check=False):
 manifest=D/'coordinator-asset-manifest.json';validation=D/'coordinator-validation.json';seals=[];nchecks=0
 specifications=[('turnout','data/turnout/asset-manifest.json','owned',202,'shared_originals',12,['turnout.md','data/county-turnout.csv']),('baselines','data/baselines/asset-manifest.json','assets',139,None,12,['county-partisanship.md','data/county-baselines.csv']),('official','data/results-sources/manifest.json','owned',410,None,0,['official-results.md','data/official-results-sources.csv']),('maps','maps/asset-manifest.json','owned',408,'external_complete_references',382,['precinct-maps.md'])]
 for role,relative,key,count,refkey,nrefs,extra in specifications:
  p=S/relative;m=load(p);rows=m[key];refs=m[refkey]if refkey else []
  if role=='baselines':
   own=[];refs=[]
   for e in rows:
    actual=(p.parent/e['path']).resolve();ne={**e,'path':str(actual.relative_to(S.resolve()))}
    (own if ne['path'].startswith('data/baselines/')or ne['path']in extra else refs).append(ne)
   rows=own
  assert len(rows)==count and len(refs)==nrefs,(role,len(rows),len(refs))
  for r in rows+refs:
   q=S/r['path'];assert pin(q)=={k:r[k]for k in ['path','bytes','sha256']};assert q.stat().st_size<40000000;nchecks+=1
  actual={str(f.relative_to(S))for f in p.parent.rglob('*')if f.is_file()and f!=p}|set(extra);assert actual=={r['path']for r in rows},role
  seals.append(dict(role=role,manifest=pin(p),owned=count,complete_original_references=nrefs))
 acceptance=load(D/'coordinator-priority-acceptance.json');contract=D/'turnout/priority-set.json';c=load(contract);assert pin(contract)==acceptance['frozen_contract']
 assert len(c['full_order'])==530 and len(c['ordered_priority_keys'])==311 and len(c['ordered_remainder_keys'])==219 and len(c['county_native_hierarchy'])==3
 assert (c['total'],c['top15_votes'],c['priority_votes'],c['preceding_votes'],c['remainder_votes'])==(500606,35875,400539,399708,100067)
 assert c['crossing_key']=='ElectionDistrict0807'and c['crossing_votes']==831 and c['formal_coordinator_acceptance']is False and c['current_geography_approved']is False
 reviews=['coordinator-native-original-review.json','coordinator-structure-original-review.json','coordinator-first-pair-target-review.json','coordinator-first-pair-seal-review.json','coordinator-second-wave-review.json','coordinator-current-law-visual-review.json','coordinator-cache-cleanup-review.json','coordinator-final-command-review.json']
 for name in reviews:assert load(D/name)['status'].startswith('pass')
 syntax=links=0
 for p in S.rglob('*'):
  if not p.is_file():continue
  assert p.stat().st_size<40000000,p;assert not any(v in p.parts for v in ['__pycache__','node_modules','.venv','venv','.pytest_cache']),p
  if p.suffix=='.py':ast.parse(p.read_bytes(),filename=str(p));syntax+=1
 for p in S.rglob('*.md'):
  for target in re.findall(r'\[[^\]\n]*\]\(([^\n)]+)\)',p.read_text()):
   target=target.split(' "')[0].strip('<>');u=urllib.parse.urlsplit(target)
   if u.scheme or u.netloc or not u.path:continue
   dest=(p.parent/urllib.parse.unquote(u.path)).resolve();assert dest.exists()or(not check and dest in [manifest.resolve(),validation.resolve()]),(p,target);links+=1
 result=dict(status='pass_complete_four_question_historical_research_with_explicit_source_limits',actual_question_workers_finished=4,question_manifests=seals,exact_question_owned_and_original_hash_checks=nchecks,independent_reviews=[pin(D/name)for name in reviews],historical_acceptance=pin(D/'coordinator-priority-acceptance.json'),complete_frozen_contract=pin(contract),complete_root_fields=42,complete_companion_bodies=42,complete_recursive_objects=16388,primary_reported_Senate_votes=500606,source_native=530,priority=311,parents=3,remainder=219,top15=35875,before310=399708,priority_votes=400539,original_source_tables=2674,original_candidate_rows=10699,all_year_native_union=1495,structure=537,sample_index_identities=533,first_pair_math_checks=146238,scenario_count=80,unit_targets=8650,second_wave_independent_checks=213504,current_primary_CSV_rows=829,current_CSV_electiondate_values=12,current_CSV_USSenate_rows=17,current_primary_USSenate_rows=6,November2026_CSV_rows=0,native_map_features=531,native_map_rings=533,native_map_positions=169245,Census2020_VTDs=412,acquired_distinct_map_PDFs=34,automatically_rendered_map_pages=200,worker_actually_viewed_PDF_pages=11,worker_actually_viewed_geographic_previews=4,no_browser_render_claim=True,local_markdown_links=links,Python_AST_files=syntax,strict_per_stored_object_limit=40000000,cache_dependency_directories_absent=True,all_producer_bytes_unchanged=True,current_geography_November_returns_collector_forecast_probability_approved=False,whole_manifest_excludes_only='data/coordinator-asset-manifest.json',validation_has_no_reverse_manifest_pin=True,qualification='Complete historical source/scenario/reference research. Separate write-ins336/18/1215 remain unallocated to EDs,2020 early methods staynull and0218/3117/4117 president-only parents remain unknown. Different source participation stocks and administrative/map inventories remain nonadditive. Primary mixed-election CSV is not genuineNovemberreturns. All map resources are shared-parent/historical references with zero approved leaf crosswalk. Code/effective-date and court holdings are bounded; signed/later roster, exhaustive docket, Senate tie remedy, current IDs, measured cadence, exact outstanding pool and calibration remain external qualifications.')
 b=(json.dumps(result,indent=2,ensure_ascii=False)+'\n').encode()
 if check:assert validation.read_bytes()==b
 else:validation.write_bytes(b)
 entries=[pin(p)for p in sorted(S.rglob('*'))if p.is_file()and p!=manifest]
 result=dict(schema='DE-coordinator-whole-state-assets-v1',assets=entries,excludes_only='data/coordinator-asset-manifest.json',total_files=len(entries),total_bytes=sum(r['bytes']for r in entries),maximum_stored_bytes=max(r['bytes']for r in entries),all_producer_bytes_unchanged=True,validation_has_no_reverse_manifest_pin=True)
 b=(json.dumps(result,indent=2,ensure_ascii=False)+'\n').encode()
 if check:assert manifest.read_bytes()==b
 else:manifest.write_bytes(b)
 print(json.dumps(dict(validation=pin(validation),manifest=pin(manifest),files=len(entries),total_bytes=result['total_bytes'],maximum=result['maximum_stored_bytes'])))
if __name__=='__main__':main('--check'in sys.argv)
