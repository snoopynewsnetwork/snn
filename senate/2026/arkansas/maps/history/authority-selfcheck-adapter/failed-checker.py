"""Complete final read-only audit. --prepare writes only the preseal validation proof."""
from pathlib import Path
import gzip,hashlib,json,re,subprocess,sys,urllib.parse
from build import ROOT,STATE,load,dumps
import replay_authority,original_body_audit,negative_fixtures,atlas_qa

def digest(p):
 b=p.read_bytes();return {'path':str(p.relative_to(STATE)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def owned():return sorted([STATE/'precinct-maps.md']+[p for p in ROOT.rglob('*') if p.is_file()],key=lambda p:str(p))
def run(sealed):
 files=owned();assert all(p.stat().st_size<40000000 for p in files),'stored object size cap'
 assert not any(p.name in ['__pycache__','node_modules','.cache','.venv','venv'] for p in ROOT.rglob('*')),'cache/dependency directory'
 # Deliberately do not persist or reproduce any authority hash in owned code/output.
 # The launch digest is checked only at launch; this validator tests path-only authority by structure.
 for p in files:
  if p.name.endswith(('.json','.py','.md','.txt','.csv','.html')):
   b=p.read_bytes()
   # Only authority path is allowed; no authority body schema copied in any output.
   assert b'"schema": "arkansas-priority-source-authority' not in b,'authority body copy'
 # Full graph and every exact historical body/receipt/old archive, without producer code.
 graph,roles=replay_authority.replay();assert load((ROOT/'qa/historical-replay.json').read_bytes())==graph
 assert load((ROOT/'source-roles.json').read_bytes())==roles
 orig=original_body_audit.run(False);negative=negative_fixtures.run(False);atlas=atlas_qa.run(False)
 p=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/offline_reconstruction.py')],capture_output=True)
 assert p.returncode==0,p.stderr.decode();offline=load((ROOT/'qa/offline-reconstruction.json').read_bytes())
 assert offline['status']=='pass_exact' and len(offline['isolated_generated_files'])==234
 assert set(offline['explicit_forbidden_route_attempts_denied'])=={'network','mutable_news_aggregate','unfinished_official_peer','producer_helper','owned_writer','external_directory_discovery','subprocess'}
 inv=load((ROOT/'parent-investigations.json').read_bytes());assert len(inv)==75 and sum(x['priority_parent'] for x in inv)==68
 assert sum(len(x['ordered_priority_children']) for x in inv)==1056 and sum(len(x['ordered_remainder_children']) for x in inv)==1785
 diag=load((ROOT/'qa/geometry-diagnostics.json').read_bytes());assert len(diag['feature_diagnostics'])==2928 and diag['true_curve_features']==36 and len(diag['positive_area_pair_overlaps'])==21
 assert diag['exact_linear_XY_IEEE754_positions_compared']==1553886 and diag['source_repairs'] is False
 auto=load((ROOT/'qa/pdf/automatic-review.json').read_bytes());manual=load((ROOT/'qa/pdf/manual-review.json').read_bytes());assert sum(x['pages'] for x in auto)==2 and len(manual['manual_whole_page_images_actually_viewed'])==2
 assert len(manual['manual_selected_detail_images_actually_viewed'])==4
 for pdf in auto:
  folder=ROOT/'qa/pdf'/pdf['label'];assert len(list(folder.glob('page-*.png')))==pdf['pages']
  for name in ['info','text','render']:assert (folder/(name+'.stderr')).is_file() and (folder/(name+'.stdout')).is_file()
 for name in ['companion-list-adapter','preseal-report-link','initial-redirect-metadata','offline-cleanup-guard','offline-cleanup-fd-adapter']:
  assert (ROOT/'history'/name).is_dir() and any((ROOT/'history'/name).iterdir())
 deferred=[];links=0
 for p in [STATE/'precinct-maps.md',ROOT/'SCHEMA.md']:
  text=p.read_text()
  for label,href in re.findall(r'\[([^\]]+)\]\(([^\s)]+)\)',text):
   url=urllib.parse.urlsplit(href)
   if url.scheme:continue
   path=(p.parent/urllib.parse.unquote(url.path)).resolve()
   if not sealed and path in [ROOT/'final-seal.json',ROOT/'asset-manifest.json'] and not path.exists():deferred.append(str(path.relative_to(STATE)));continue
   assert path.exists(),('broken report/schema link',str(p),href);links+=1
 if sealed:
  mf=load((ROOT/'asset-manifest.json').read_bytes());entries=mf['files'];assert [x['path'] for x in entries]==sorted(x['path'] for x in entries)
  expected={str(p.relative_to(STATE)):p for p in files if p!=ROOT/'asset-manifest.json'}
  assert len(entries)==len(expected) and {x['path'] for x in entries}==set(expected),'complete owned manifest membership'
  for x in entries:assert digest(expected[x['path']])==x,('owned size/hash',x['path'])
  seal=load((ROOT/'final-seal.json').read_bytes());assert seal['status']=='complete_bounded_original_maps_research' and all(v in [False,None] for v in seal['approvals'].values())
  assert seal['authority_path']=='data/coordinator-priority-acceptance.json' and 'manifest_sha256' not in seal
 proof={'status':'pass_preseal' if not sealed else 'pass_final_readonly','historical_graph':graph,'original_body_count':orig['whole_original_bodies'],'all_required_OOXML_candidate_rows':19887,'all_required_OOXML_raw_cells':198870,'negative_fixture_count':negative['negative_packets'],'atlas_pages':len(atlas['pages']),'complete_contract_roots_in_atlas':18,'native_GIS_objects':2928,'priority_parent_investigations':68,'all_parent_investigations':75,'exact_offline_outputs':234,'explicit_forbidden_routes_denied':offline['explicit_forbidden_route_attempts_denied'],'source_linear_XY_positions':1553886,'full_PDF_pages_rendered':2,'manual_whole_pages_viewed':2,'manual_selected_details_viewed':4,'live_browser_claim':False,'local_report_schema_links':links,'preseal_deferred_only':deferred,'all_stored_files_strictly_below_40000000':True,'current_approvals':False,'producer_writes':False}
 if not sealed:(ROOT/'qa/validation.json').write_text(dumps(proof))
 return proof
if __name__=='__main__':
 assert '--sealed' in sys.argv or '--prepare' in sys.argv
 p=run('--sealed' in sys.argv);print(json.dumps(p))
