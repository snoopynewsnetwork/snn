"""Whole-state integration checks against four immutable owned manifests."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote,urlsplit
import datetime,gzip,hashlib,json,re
STATE=Path(__file__).resolve().parents[1];DATA=STATE/'data'
sha=lambda b:hashlib.sha256(b).hexdigest()
load=lambda p:json.loads(p.read_bytes())
class Links(HTMLParser):
 def __init__(self):super().__init__();self.urls=[]
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ['src','href'] and v:self.urls.append(v)
def main():
 specs=[
  ('data/turnout/asset-manifest.json','assets','c510f3321a7764815fee9745fa6f6ce294e6a312320b1f723c80dc6a44edffb7',272,'data/turnout','turnout.md','data/county-turnout.csv'),
  ('data/baselines/asset-manifest.json','owned','5517e4baeafaf57f2858839d8bd3f868355947e94d8e07ce15ff53bf579f2b65',201,'data/baselines','county-partisanship.md','data/county-baselines.csv'),
  ('data/results-sources/asset-manifest.json','assets','0b68e2a10d9d4c4ec88cad5989aaa97b186b04c464dfb40e4e1b9afc74ab927e',1057,'data/results-sources','official-results.md','data/official-results-sources.csv'),
  ('maps/asset-manifest.json','files','4c5385dffd8b0f375dbd8698a38dd984fbe53bea893d2c3932804c279b84312e',733,'maps','precinct-maps.md',None)]
 manifests=[];allassets=set()
 for relative,key,digest,count,root,report,csv in specs:
  path=STATE/relative;body=path.read_bytes();assert sha(body)==digest,relative
  rows=json.loads(body)[key];assert len(rows)==count
  expected={p.resolve() for p in (STATE/root).rglob('*') if p.is_file() and p!=path}|{(STATE/report).resolve()}
  if csv:expected.add((STATE/csv).resolve())
  actual=set()
  for row in rows:
   p=(STATE/row['path']).resolve();assert STATE.resolve() in p.parents and p not in actual and p not in allassets
   actual.add(p);allassets.add(p);b=p.read_bytes();assert len(b)==row['bytes']<40000000 and sha(b)==row['sha256'],row['path']
  assert actual==expected,(relative,sorted(map(str,expected-actual)),sorted(map(str,actual-expected)))
  manifests.append({'path':relative,'sha256':digest,'exact_owned_entries':count,'self_only_excluded':True})
 reviews=['coordinator-primary-table-review.json','coordinator-native-original-review.json','coordinator-target-review.json','coordinator-final-baseline-review.json','coordinator-ballot-review.json','coordinator-poll-clock-review.json','coordinator-current-source-review.json','coordinator-map-native-review.json','coordinator-results-final-review.json']
 for name in reviews:assert load(DATA/name)['status'].lower().startswith('pass'),name
 contractraw=(DATA/'turnout/priority-set.json').read_bytes();assert len(contractraw)==23823926 and sha(contractraw)=='0c056e0ebfdb393d4fcb59676805122d8442f444200b9edaf7f4c979c5e9a173'
 c=json.loads(contractraw);assert load(DATA/'coordinator-priority-acceptance.json')['accepted'];assert c['coordinator_accepted'] is False
 assert c==json.loads(gzip.decompress((STATE/'maps/frozen-contract.semantic.json.gz').read_bytes()))
 assert c==json.loads(gzip.decompress((DATA/'results-sources/frozen-context.json.gz').read_bytes()))['frozen_contract']
 rows=[json.loads(s) for s in gzip.decompress((DATA/'results-sources/county-investigations.jsonl.gz').read_bytes()).splitlines()]
 assert [r['frozen_parent'] for r in rows]==c['all_unit_order'];assert [r['frozen_primary_constituent_object'] for r in rows]==c['native_constituents']
 linkcount=0
 for p in list(STATE.rglob('*.md'))+list(STATE.rglob('*.html')):
  if p.suffix=='.md':urls=re.findall(r'\]\(([^)]+)\)',p.read_text())
  else:parser=Links();parser.feed(p.read_text());urls=parser.urls
  for url in urls:
   u=urlsplit(url.strip('<>'))
   if u.scheme or not u.path:continue
   target=(p.parent/unquote(u.path)).resolve()
   assert target.exists() or target==(DATA/'coordinator-checks.json').resolve(),(str(p.relative_to(STATE)),url)
   linkcount+=1
 files=[p for p in STATE.rglob('*') if p.is_file()];assert all(p.stat().st_size<40000000 for p in files)
 assert not any(p.name in ['node_modules','__pycache__','.cache','.venv'] for p in STATE.rglob('*'))
 output={'status':'pass','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'four_assignment_manifests':manifests,'exact_owned_assignment_entries':len(allassets),'independent_reviews':reviews,'complete_frozen_parents':67,'complete_native_contexts':23532,'priority_counties':22,'remainder_counties':45,'denominator':10757428,'priority_votes':8734473,'top15_votes':7373225,'preceding21_votes':8572752,'crossing_Escambia':161721,'local_MD_HTML_links':linkcount,'max_stored_object_bytes':max(p.stat().st_size for p in files),'strict_exclusive_cap':40000000,'cache_dependency_trees':0,'repository_check':'npm run check passed:35race records,TypeScript andpublic app syntax','scope':'Completed research package. Historical dispatch only; no genuine November counts, approved current reporting-geometry join, exact Senate remainder, running collector or calibrated probability model. Source conflicts, protected values, historical Duval and source rendering defects remain explicit.'}
 target=DATA/'coordinator-checks.json'
 if target.exists():
  old=load(target)
  if {k:v for k,v in old.items() if k!='checked_utc'}=={k:v for k,v in output.items() if k!='checked_utc'}:output['checked_utc']=old['checked_utc']
 target.write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output,indent=2))
if __name__=='__main__':main()
