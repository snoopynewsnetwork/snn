"""Whole-owned seal: only the manifest itself is excluded. No reverse cycle."""
from acquire import *
import sys,json,re,urllib.parse
S=M.parent
MAN=M/'asset-manifest.json'
def assets():return sorted([S/'precinct-maps.md']+[p for p in M.rglob('*')if p.is_file()and p!=MAN])
def row(p):
 b=p.read_bytes();assert len(b)<40000000;return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))
def verify():
 mf=json.loads(MAN.read_bytes());want=[row(p)for p in assets()];assert mf['owned_assets']==want;assert mf['excludes_only']=='maps/asset-manifest.json';assert json.loads((M/'validation.json').read_bytes())['status']=='pass';assert json.loads((M/'replay.json').read_bytes())['status']=='pass'
 for r in mf['readonly_inputs']:
  b=(S/r['path']).read_bytes();assert len(b)==r['bytes']and sha(b)==r['sha256']
 for p in [S/'precinct-maps.md',M/'README.md',M/'SCHEMA.md',M/'index.html']:
  text=p.read_text()
  links=re.findall(r'\]\(([^)]+)\)',text)if p.suffix=='.md'else re.findall(r'(?:href|src)="([^"]+)"',text)
  for link in links:
   if not link.startswith(('http:','https:','#','mailto:')):assert (p.parent/urllib.parse.unquote(link.split('#')[0])).exists(),(p,link)
 print(json.dumps(dict(status='pass',owned_assets=len(want),excludes_only=mf['excludes_only'],manifest_bytes=MAN.stat().st_size,manifest_sha256=sha(MAN.read_bytes()),maximum_owned_bytes=max(x['bytes']for x in want),owned_total_bytes=sum(x['bytes']for x in want),readonly_inputs=len(mf['readonly_inputs']))))
if '--verify'in sys.argv:verify()
else:
 validation=json.loads((M/'validation.json').read_bytes());assert validation['status']=='pass'
 dump(M/'final-seal.json',dict(status='sealed_bounded_historical_maps_research',authority_path='data/coordinator-priority-acceptance.json',pins=[row(p)for p in [S/'precinct-maps.md',M/'validation.json',M/'replay.json',M/'reconstruction.json',M/'SCHEMA.md',M/'visual-review.json']],current_legal_result_geometry_approval=False,coordinator_acceptance_or_publication=False,exclusion_policy='only maps/asset-manifest.json; validation/final-seal included; no reverse manifest digest',owned_research_complete=True))
 dump(MAN,dict(schema='MA-maps-complete-owned-seal-v1',authority_path='data/coordinator-priority-acceptance.json',excludes_only='maps/asset-manifest.json',owned_assets=[row(p)for p in assets()],readonly_inputs=json.loads((M/'readonly-inputs.json').read_bytes())))
 verify()
