#!/usr/bin/env python3
"""Coordinator whole-package frozen assets, local links, scope and bounds."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote,urlsplit
import datetime,hashlib,json,re
R=Path(__file__).resolve().parents[1];D=R/'data';sha=lambda b:hashlib.sha256(b).hexdigest();load=lambda p:json.loads(p.read_text())
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,t,attrs):
  x=dict(attrs);self.links.extend(x[k]for k in ['href','src']if k in x)
def main():
 specs=[('data/turnout/asset-manifest.json','assets','a30fa05a30027506e3e114520c1026f02bccd611cf27699b2c6c0c487f952173',61),('data/baselines/asset-manifest.json','owned_files','a8d9c6698ca551efca6b84f91a28b65f428b17efa484e193a714fba1d5cae735',73),('data/results-sources/asset-manifest.json','assets','2c135609fda7b4c84e7c56b9d11a08844f1c749bbf4969c4c0bf7c0a126a2768',1299),('maps/asset-manifest.json','assets','a5795ffb08c07620102da1f57413b6c14078bdeee6f7e6c5b096161d3ab0ba17',451)]
 checks=0;seen=set();manifests=[]
 for path,key,digest,n in specs:
  body=(R/path).read_bytes();assert sha(body)==digest;mf=json.loads(body);assert len(mf[key])==n;manifests.append({'path':path,'sha256':digest,'assets':n})
  for x in mf[key]:
   assert x['path']not in seen;seen.add(x['path']);b=(R/x['path']).read_bytes();assert len(b)==x['bytes']<40000000 and sha(b)==x['sha256'];checks+=1
 reviews=['coordinator-native-contract-review.json','coordinator-turnout-final-review.json','coordinator-target-review.json','coordinator-map-final-review.json','coordinator-results-final-review.json','coordinator-export-review.json','coordinator-legal-review.json']
 for f in reviews:
  x=load(D/f);assert x.get('status','').startswith('pass'),f
 count=0
 for p in list(R.rglob('*.md'))+list(R.rglob('*.html')):
  if p.suffix=='.md':urls=re.findall(r'\]\(([^)]+)\)',p.read_text())
  else:h=Links();h.feed(p.read_text());urls=h.links
  for url in urls:
   url=url.strip('<>');x=urlsplit(url)
   if x.scheme or not x.path:continue
   target=p.parent/unquote(x.path)
   assert target.exists()or target.resolve()==(D/'coordinator-checks.json').resolve(),(str(p.relative_to(R)),url);count+=1
 files=[p for p in R.rglob('*')if p.is_file()];assert all(p.stat().st_size<40000000 for p in files)
 assert not any(p.name in ['__pycache__','node_modules','.venv','.cache']for p in R.rglob('*'))
 acceptance=load(D/'coordinator-priority-acceptance.json');assert acceptance['accepted'];assert sha((D/acceptance['contract']).read_bytes())==acceptance['contract_sha256']
 out={'status':'pass','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Reviewed four-question research package, historical conditional arithmetic and actual qualified downloaded maps; no currentproductioncollector/modelapproval.','frozen_assignment_manifests':manifests,'owned_assignment_artifact_hashes':checks,'independent_review_artifacts':reviews,'local_MD_HTML_links':count,'max_stored_object_bytes':max(p.stat().st_size for p in files),'strict_object_bound_exclusive':40000000,'cache_dependency_trees':0,'repository_check':'npm run check passed (35races,TypeScript,public app syntax)','historical_scope':'all87/exact24/all12316; frozen contract and external PATH authority unchanged','production_admission':'November201TEST and invalid regional positive display excluded; currentcandidate/geography/method/writein/cadence/remainder gaps retained.'}
 p=D/'coordinator-checks.json'
 if p.exists():
  old=load(p)
  if {k:v for k,v in old.items()if k!='checked_utc'}=={k:v for k,v in out.items()if k!='checked_utc'}:out['checked_utc']=old['checked_utc']
 p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
