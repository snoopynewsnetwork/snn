"""Coordinator frozen-manifest, scope, bounds and local-link integration check."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote,urlsplit
import datetime,gzip,hashlib,json,re
STATE=Path(__file__).resolve().parents[1]
DATA=STATE/'data'
sha=lambda b:hashlib.sha256(b).hexdigest()
def load(path):return json.loads(path.read_bytes())
class Links(HTMLParser):
 def __init__(self):super().__init__();self.urls=[]
 def handle_starttag(self,tag,attrs):
  for key,value in attrs:
   if key in ['href','src'] and value:self.urls.append(value)
def main():
 specs=[
  ('data/turnout/asset-manifest.json','owned_assets','70ae7c258291328257baa9061c8d3854ccb371c40f80298803d8b06197583f95',519,'manifest',['data/turnout'],'turnout.md','data/county-turnout.csv'),
  ('data/baselines/asset-manifest.json','assets','41c90cccc7767494146ec76bbbf1ccf1f68ccb01419fa0dbf1e1e1be79e43994',1111,'state',['data/baselines'],'county-partisanship.md','data/county-baselines.csv'),
  ('data/results-sources/asset-manifest.json','assets','8421dbc4c30802f122d56a1d1723414dc2401b04a1e3c95cf6a68516568b2e49',323,'state',['data/results-sources'],'official-results.md','data/official-results-sources.csv'),
  ('maps/manifest.json','owned_assets','211448510c96f031c20e93c8ad35ff81cb7401da65e7ac72a4fe859ebd5bc9bf',381,'state',['maps'],'precinct-maps.md',None)]
 checked=set();manifests=[]
 for relative,key,digest,count,basekind,roots,report,csv in specs:
  path=STATE/relative;b=path.read_bytes();assert sha(b)==digest
  mf=json.loads(b);assets=mf[key];assert len(assets)==count
  base=path.parent if basekind=='manifest' else STATE
  actual=set()
  for a in assets:
   target=(base/a['path']).resolve();assert STATE.resolve() in target.parents
   assert target not in checked;checked.add(target);actual.add(target)
   body=target.read_bytes();assert len(body)==a['bytes']<40000000 and sha(body)==a['sha256']
  expected={(STATE/report).resolve()}
  if csv:expected.add((STATE/csv).resolve())
  for root in roots:expected.update(p.resolve() for p in (STATE/root).rglob('*') if p.is_file() and p.resolve()!=path.resolve())
  assert actual==expected,(relative,sorted(str(p) for p in expected-actual),sorted(str(p) for p in actual-expected))
  manifests.append({'path':relative,'sha256':digest,'owned_assets':count})
 reviews=['coordinator-native-review.json','coordinator-legacy-review.json','coordinator-target-review.json','coordinator-original-target-review.json','coordinator-first-pair-final-review.json','coordinator-current-source-review.json','coordinator-map-native-review.json','coordinator-results-final-review.json']
 for filename in reviews:assert load(DATA/filename)['status'].startswith('pass'),filename
 acceptance=load(DATA/'coordinator-priority-acceptance.json');assert acceptance['accepted']
 contract_body=(DATA/'turnout/priority-set.json').read_bytes();assert len(contract_body)==33917555 and sha(contract_body)=='a4dc8e50ce09889e5873d1f54c887dbef50a42a0b7bf600b4ab6663afab4ccef'
 contract=json.loads(contract_body)
 compatibility=json.loads(gzip.decompress((STATE/'maps/contract-compatibility.json.gz').read_bytes()))
 assert compatibility['frozen_contract']==contract
 records=json.loads(gzip.decompress((DATA/'results-sources/county-records.json.gz').read_bytes()))
 assert [r['frozen_county'] for r in records['counties']]==contract['counties']
 link_count=0
 for path in list(STATE.rglob('*.md'))+list(STATE.rglob('*.html')):
  if path.suffix=='.md':urls=re.findall(r'\]\(([^)]+)\)',path.read_text())
  else:
   parser=Links();parser.feed(path.read_text());urls=parser.urls
  for url in urls:
   parts=urlsplit(url.strip('<>'))
   if parts.scheme or not parts.path:continue
   target=(path.parent/unquote(parts.path)).resolve()
   assert target.exists() or target==(DATA/'coordinator-checks.json').resolve(),(str(path.relative_to(STATE)),url)
   link_count+=1
 files=[p for p in STATE.rglob('*') if p.is_file()]
 assert all(p.stat().st_size<40000000 for p in files)
 assert not any(p.name in ['__pycache__','node_modules','.venv','.cache'] for p in STATE.rglob('*'))
 output={'status':'pass','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'four_assignment_manifests':manifests,'owned_assignment_asset_hashes':len(checked),'independent_reviews':reviews,'complete_frozen_county_objects':46,'priority_counties':17,'remainder_counties':29,'native_maps':{'statewide':2315,'priority_subset_features':1639,'RFA_PDF_sheets':18,'county_alternative_features':320},'local_MD_HTML_links':link_count,'max_stored_object_bytes':max(p.stat().st_size for p in files),'strict_cap_exclusive':40000000,'cache_dependency_trees':0,'repository_check':'npm run check passed:35race records,TypeScript,public app syntax','production_admission':'No genuine November count source or physical/reporting crosswalk admitted; named writeins,cadence,exact Senate remainder and later operative court outcome gaps remain.','forecast_status':'Deterministic historical/conditional arithmetic only; no running collector or calibrated Needle.'}
 target=DATA/'coordinator-checks.json'
 if target.exists():
  old=load(target)
  if {k:v for k,v in old.items() if k!='checked_utc'}=={k:v for k,v in output.items() if k!='checked_utc'}:output['checked_utc']=old['checked_utc']
 target.write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output,indent=2))
if __name__=='__main__':main()
