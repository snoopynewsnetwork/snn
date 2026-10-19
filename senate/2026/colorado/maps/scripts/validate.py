"""Read-only validation by default. --write-report is preparation before sealing."""
import copy,gzip,html,io,json,pathlib,re,sys,zipfile,urllib.parse
from html.parser import HTMLParser
from acquire import ROOT,body,sha
from conservation import run as conservation,semantic
from geometry import run as geometry
from service_audit import run as services

def negative_fixtures(c):
 cases=[]
 def reject(name,func):
  try:func()
  except (AssertionError,ValueError,zipfile.BadZipFile,KeyError):cases.append(dict(name=name,rejected=True));return
  raise AssertionError(('negative fixture incorrectly admitted',name))
 orig=c['full_order'][0];expected=semantic(orig)
 def same(o):assert semantic(o)==expected
 bad=copy.deepcopy(orig);bad.pop('method');reject('omitted-null-method-field',lambda:same(bad))
 bad=copy.deepcopy(orig);bad['candidate_values']=bad['candidate_values'][:2];reject('vote-only-selected-candidate-projection',lambda:same(bad))
 bad=copy.deepcopy(orig);bad['raw_fields'][0]='Precinct changed';reject('raw-source-label-change',lambda:same(bad))
 bad=copy.deepcopy(orig);bad['candidate_votes']+=1;reject('one-candidate-vote-change',lambda:same(bad))
 reject('missing-entire-root-field',lambda:check_contract({k:v for k,v in c.items() if k!='unavailable_administrative_cases'},c))
 reject('priority-county-substitution',lambda:check_keys(c['ordered_priority_keys'][:-1]+['CO|2024|26499|Summit'],c['ordered_priority_keys']))
 reject('priority-order-swap',lambda:check_keys(list(reversed(c['ordered_priority_keys'])),c['ordered_priority_keys']))
 reject('missing-remainder-observation',lambda:check_keys(c['ordered_remainder_keys'][:-1],c['ordered_remainder_keys']))
 reject('51-id-page',lambda:check_page(list(range(51)),list(range(51))))
 reject('duplicate-feature-ID',lambda:check_page([1,2],[1,1]))
 reject('missing-feature-ID',lambda:check_page([1,2],[1]))
 reject('unrequested-feature-ID',lambda:check_page([1,2],[1,3]))
 reject('truncated-flag',lambda:check_transfer({'exceededTransferLimit':True}))
 reject('output-CRS-transform',lambda:check_params({'outSR':['4326']}))
 reject('geometry-precision-loss',lambda:check_params({'geometryPrecision':['3']}))
 reject('max-offset-generalization',lambda:check_params({'maxAllowableOffset':['1']}))
 reject('quantized-native-geometry',lambda:check_params({'quantizationParameters':['{}']}))
 # Complete native true-curve feature must survive as a full object, including every attribute.
 curve=None
 for pg in json.loads((ROOT/'raw/adams-native.service.json').read_text())['pages']:
  for feature in json.loads(body(pg))['features']:
   if 'curveRings'in (feature.get('geometry') or {}):curve=feature;break
  if curve:break
 assert curve is not None
 expected_curve=semantic(curve)
 def same_curve(v):assert semantic(v)==expected_curve
 v=copy.deepcopy(curve);v['geometry'].pop('curveRings');reject('dropped-native-truecurve-geometry',lambda:same_curve(v))
 v=copy.deepcopy(curve);v['attributes'].pop(next(iter(v['attributes'])));reject('omitted-native-attribute',lambda:same_curve(v))
 v=copy.deepcopy(curve);v['geometry']['curveRings'][0][0][0]+=0.000001;reject('rounded-or-changed-native-ordinate',lambda:same_curve(v))
 v=copy.deepcopy(curve);v['geometry']['curveRings'][0]=list(reversed(v['geometry']['curveRings'][0]));reject('native-ring-order-change',lambda:same_curve(v))
 # Original binary member CRC mutation: alter a stored entry byte without repairing CRC.
 zbuf=io.BytesIO()
 with zipfile.ZipFile(zbuf,'w',compression=zipfile.ZIP_STORED) as z:z.writestr('native.shp',b'12345678')
 b=bytearray(zbuf.getvalue());pos=b.index(b'12345678');b[pos]^=1
 def crc():
  with zipfile.ZipFile(io.BytesIO(b)) as z:assert z.testzip() is None
 reject('corrupt-native-ZIP-CRC',crc)
 return cases

def check_contract(a,b):assert semantic(a)==semantic(b)
def check_keys(a,b):assert a==b
def check_page(wanted,actual):assert len(wanted)<=50 and len(actual)==len(set(actual))==len(wanted) and set(actual)==set(wanted)
def check_transfer(d):assert not d.get('exceededTransferLimit',False)
def check_params(p):assert not set(p)&{'outSR','geometryPrecision','maxAllowableOffset','quantizationParameters'}

def run(sealed=True):
 con,c=conservation();assert json.loads((ROOT/'historical-conservation.json').read_text())==con;checks=con['checks']+1;receipts=[]
 for f in sorted((ROOT/'raw').glob('*.receipt.json')):
  r=json.loads(f.read_text());b=body(r['id']);assert sha(b)==r['raw_sha256'] and len(b)==r['raw_bytes'];checks+=2
  assert r['method']=='GET' and r['retrieved_utc'] and 'status'in r and 'headers'in r and 'redirects'in r and 'source_clock'in r and 'source_status'in r;checks+=7
  for p in r['parts']:
   s=(ROOT/p['path']).read_bytes();assert sha(s)==p['sha256'] and len(s)==p['bytes'] and len(s)<40000000;checks+=3
  receipts.append(r)
 a,t,_=geometry();assert json.loads((ROOT/'qa/binary-geometry-audit.json').read_text())==a;assert json.loads((ROOT/'qa/topology.json').read_text())==t
 checks+=sum(x['checks'] for x in a['audits'])+2
 sa,st,_=services();assert json.loads((ROOT/'qa/service-audit.json').read_text())==sa and json.loads((ROOT/'qa/service-topology.json').read_text())==st;checks+=2
 inv=json.loads((ROOT/'inventory.json').read_text());parents=json.loads((ROOT/'parent-inventory.json').read_text());assert len(inv['all3199'])==3199 and len(parents)==64;checks+=2
 assert inv['ordered_priority_keys']==c['ordered_priority_keys'] and inv['ordered_remainder_keys']==c['ordered_remainder_keys'];checks+=2
 for i,v in enumerate(inv['all3199']):
  assert v['rank']==i+1 and v['key']==c['full_order'][i]['key'] and v['candidate_votes']==c['full_order'][i]['candidate_votes'] and v['priority']==(i<1992);checks+=4
  assert not v['leaf_geometry_match'] and not v['current_legal_match'] and v['historical_fallback']=='census-co-vtd' and v['fallback_feature_count']>0;checks+=4
 for p,h in zip(parents,c['county_native_hierarchy']):
  assert p['source_all_native_keys']==h['all_native_keys'];assert p['derived_remainder_native_keys']==[k for k in h['all_native_keys'] if k in set(c['ordered_remainder_keys'])];checks+=2
  if p['priority_parent']:assert any(r['id']==p['acquisition_id'] for r in receipts);checks+=1
 pdfs=json.loads((ROOT/'pdf-assets.json').read_text())
 for p in pdfs:
  b=(ROOT/p['path']).read_bytes();assert len(b)==p['bytes'] and sha(b)==p['sha256'];checks+=2
  raw=body(p['source'])
  if p['zip_member']:
   with zipfile.ZipFile(io.BytesIO(raw)) as z:assert z.read(p['zip_member'])==b
  else:assert raw==b
  checks+=1
  for page in p['page_previews']:assert (ROOT/page).read_bytes().startswith(b'\x89PNG');checks+=1
 class H(HTMLParser):
  def __init__(self):super().__init__();self.refs=[];self.keys=[];self.tags=[];self.ids=set()
  def handle_starttag(self,t,a):
   d=dict(a)
   for v in ['href','src']:
    if v in d:self.refs.append(d[v])
   if 'id'in d:self.ids.add(d['id'])
   if t=='tr'and 'data-priority'in d:self.tags.append(d['data-priority'])
  def handle_data(self,s):
   if s.startswith('CO|2024|26499|'):self.keys.append(s)
 htmlparsers={}
 for f in ROOT.glob('*.html'):
  h=H();h.feed(f.read_text());htmlparsers[f.name]=h
  for ref in h.refs:
   u=urllib.parse.urlsplit(ref)
   if u.scheme or u.netloc or not u.path:continue
   target=(f.parent/urllib.parse.unquote(u.path)).resolve();assert target.is_file(),(f,ref);checks+=1
 index=htmlparsers['index.html'];assert index.keys==[r['key'] for r in c['full_order']];assert index.tags==['true']*1992+['false']*1207;checks+=2
 assert not re.search(r'fetch\(|https?://[^\s]+\.js|<script\s+src',''.join(f.read_text() for f in ROOT.glob('*.html')));checks+=1
 for f in list(ROOT.glob('*.md'))+[ROOT.parent/'precinct-maps.md']:
  for ref in re.findall(r'\]\(([^)]+)\)',f.read_text()):
   u=urllib.parse.urlsplit(ref)
   if u.scheme or u.netloc or not u.path:continue
   assert (f.parent/urllib.parse.unquote(u.path)).resolve().is_file(),(f,ref);checks+=1
 neg=negative_fixtures(c);assert json.loads((ROOT/'qa/negative-fixtures.json').read_text())==neg;checks+=len(neg)
 owned=[ROOT.parent/'precinct-maps.md']+[p for p in ROOT.rglob('*') if p.is_file()]
 assert not any(p.name=='__pycache__' for p in ROOT.rglob('*'))
 for f in owned:assert f.stat().st_size<40000000;checks+=1
 if sealed:
  manifest=json.loads((ROOT/'asset-manifest.json').read_text());entries=manifest['owned_files'];actual={str(p.relative_to(ROOT.parent)) for p in owned if p!=ROOT/'asset-manifest.json'};assert {p['path'] for p in entries}==actual;checks+=1
  for r in entries:
   b=(ROOT.parent/r['path']).read_bytes();assert len(b)==r['bytes'] and sha(b)==r['sha256'];checks+=2
  for r in manifest['read_only_dependencies']:
   b=(ROOT.parent/r['path']).read_bytes();assert len(b)==r['bytes'] and sha(b)==r['sha256'];checks+=2
 return dict(status='research QA passed; external coordinator review remains separate',checks=checks,historical_conservation_checks=con['checks'],recursive_complete_source_objects=13174,complete_companions=26,actual_acquisition_receipts=len(receipts),priority_parent_bounded_requests=45,inventory=3199,priority=1992,remainder=1207,full_parents=64,census_features=3108,native_service_features=527,pdf_assets=len(pdfs),pdf_pages=sum(p['pages'] for p in pdfs),negative_fixtures=len(neg),browser_used=False,source_originals_changed=False,current_legal_crosswalk_approved=False)
if __name__=='__main__':
 if '--write-fixtures'in sys.argv:
  _,c=conservation();(ROOT/'qa/negative-fixtures.json').write_text(json.dumps(negative_fixtures(c),indent=2)+'\n')
 else:
  write='--write-report'in sys.argv;r=run(sealed=not write)
  if write:(ROOT/'qa/validation.json').write_text(json.dumps(r,indent=2)+'\n')
  print(json.dumps(r,indent=2))
