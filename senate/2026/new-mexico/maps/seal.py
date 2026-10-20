"""Acyclic self-only-excluded owned manifest and separate read-only seal audit."""
from common import *

def owned():return sorted([p for p in M.rglob('*')if p.is_file()]+[S/'precinct-maps.md'])
def seal():
 proofnames=['validation.json','replay-proof.json','historical-source-checks.json','dom-tests.json','negative-fixtures.json','service-validation.json','native-audit-index.json','pdf-render-inventory.json','visual-scope.json','geographic-diagnostics.json']
 write(M/'final-seal.json',{'status':'complete_bounded_geographic_source_research_pending_coordinator_review','authority_path':'data/coordinator-source-research-acceptance.json','scope':{'source_observations':2201,'county_parents':33,'administrative':33,'masked':20,'SHP_2024_features':2169,'SHP_2026_features':2177,'native_service_features':2177,'native_batches':44,'PDFs':60,'PDF_pages':194},'proofs':[pin(M/n)for n in proofnames],'report':pin(S/'precinct-maps.md'),'certified_priority':None,'ordered_priority_keys':[],'current_legal_reporting_leaf_join':None,'private_spatial_allocation':False,'coordinator_acceptance_or_publication_claim':False,'reverse_current_manifest_pin':None,'external_qualifications':['current legal geometry/leaf/reporting/municipal/ballotstyle/site dictionaries','later law/dockets/eligible write-in/ballot scope','November live feeds/cadence/eligible remaining votes'],'browser_render_observed':False})
 ps=[p for p in owned()if p!=M/'asset-manifest.json'];assert all(p.stat().st_size<40000000 for p in ps)
 write(M/'asset-manifest.json',{'schema':'nm-maps-owned-seal-v1','status':'sealed_for_coordinator_review','authority_path':'data/coordinator-source-research-acceptance.json','self_only_exclusion':'maps/asset-manifest.json','owned_files':[pin(p)for p in ps],'immutable_external_references':pin(M/'immutable-inputs.json'),'current_geography_approved':False,'certified_native_priority':None,'source_allocation':False})
 print('Sealed',len(ps),'owned files; manifest excludes only itself')
def audit():
 p=M/'asset-manifest.json';a=json.loads(p.read_bytes());assert a['status']=='sealed_for_coordinator_review';expected={r['path']:r for r in a['owned_files']};actual={str(q.relative_to(S)):q for q in owned()if q!=p};assert set(expected)==set(actual),(set(expected)^set(actual))
 for path,q in actual.items():assert pin(q)==expected[path]and q.stat().st_size<40000000,path
 ext=json.loads((M/'immutable-inputs.json').read_bytes())
 for r in ext['complete_body_pins']:assert pin(S/r['path'])==r
 for snap in ext['immutable_historical_snapshot_body_resolvers']:
  for r in snap['complete_records']:
   z=(S/r['immutable_stored_body']['path']).read_bytes();assert pin(S/r['immutable_stored_body']['path'])==r['immutable_stored_body'];b=gzip.decompress(z)if r['storage']=='lossless_gzip_body'else z;assert len(b)==r['original_bytes']and sha(b)==r['original_sha256']
 for r in ext['complete_original_entity_references']:
  z=(S/r['path']).read_bytes();b=gzip.decompress(z)if r['path'].endswith('.gz')else z;assert sha(b)==r['raw_sha256']
 for q in (M/'receipts').rglob('*.json'):
  r=json.loads(q.read_bytes())
  for event in r['requests']:
   if event.get('body'):body(event['body'])
  if r.get('body'):body(r['body'])
 for ref in json.loads((M/'final-seal.json').read_bytes())['proofs']:assert pin(S/ref['path'])==ref
 mh=sha(p.read_bytes()).encode()
 for name in ['validation.json','final-seal.json']:assert mh not in (M/name).read_bytes(),'reverse manifest hash'
 # Final actual relative report links (no planned/provisional target exemptions).
 import re
 for url in re.findall(r'\]\(([^)]+)\)',(S/'precinct-maps.md').read_text()):
  if not url.startswith(('http:','https:')):assert (S/url).is_file(),url
 authority_hash=sha((S/'data/coordinator-source-research-acceptance.json').read_bytes()).encode()
 for q in owned():assert authority_hash not in q.read_bytes()
 print(json.dumps({'status':'pass_final_read_only_seal_audit','owned_files_including_manifest':len(actual)+1,'owned_bytes_including_manifest':sum(q.stat().st_size for q in owned()),'maximum_owned_file_bytes':max(q.stat().st_size for q in owned()),'immutable_body_pins':len(ext['complete_body_pins']),'historical_virtual_bodies':196,'manifest':pin(p),'final_seal':pin(M/'final-seal.json'),'current_legal_leaf_approval':False,'self_acceptance':False},indent=2))
if __name__=='__main__':
 import sys
 audit()if '--audit'in sys.argv else seal()
