#!/usr/bin/env python3
"""Meaningful offline conservation, bytes, service ID, geometry, bounds and link checks."""
import collections,datetime,gzip,hashlib,json,math,pathlib,re,sys,urllib.parse,xml.etree.ElementTree as ET,zipfile,io
from html.parser import HTMLParser
from acquire import ROOT,MAN,read
from geometry import load_records,as_crs
from pyproj import Transformer
from PIL import Image
BASE=ROOT.parent
checks=[]
def check(name,condition,detail=None):
 checks.append({'check':name,'pass':bool(condition),'detail':detail})
 if not condition:raise AssertionError((name,detail))
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 pin=json.loads((ROOT/'readonly-pins.json').read_text())
 for p in pin['files']:
  b=(ROOT/p['path']).read_bytes();check('read-only input hash '+p['path'],len(b)==p['bytes'] and sha(b)==p['sha256'])
 shared=0
 for ref in pin['full_shared_source_metadata']:
  r=ref['source_object']
  if 'stored_path'in r:p=BASE/r['stored_path']
  else:p=BASE/'data/turnout'/r['path']
  b=p.read_bytes();check('shared original stored '+r.get('id',r.get('source_id','')),len(b)==r['stored_bytes'] and sha(b)==r['stored_sha256'])
  original=gzip.decompress(b) if b.startswith(b'\x1f\x8b') else b
  if 'original_sha256'in r:check('shared original reconstructed '+r.get('id',r.get('source_id','')),sha(original)==r['original_sha256'] and len(original)==r['original_bytes'])
  elif 'raw_sha256'in r:check('shared raw original '+r.get('id',''),sha(original)==r['raw_sha256'] and len(original)==r.get('raw_bytes',r.get('bytes')))
  shared+=1
 contract=json.loads((BASE/'data/turnout/priority-set.json').read_text());accept=json.loads((BASE/'data/coordinator-priority-acceptance.json').read_text())
 check('external coordinator accepted exact contract',accept['accepted'] and accept['contract_sha256']==sha((BASE/'data/turnout/priority-set.json').read_bytes()))
 keys=(BASE/'data/coordinator-priority-keys.txt').read_text().splitlines();check('exact ordered23 keys',keys==contract['ordered_priority_keys'] and len(keys)==23)
 check('priority arithmetic',contract['denominator']==1327591 and contract['top15_votes']==970376 and contract['minimum80']['minimum80_votes']==1067659 and contract['minimum80']['preceding_votes']==1057110)
 inv=json.loads((ROOT/'inventory.json').read_text());cs=inv['counties'];check('inventory exact105 county order',[x['county_key'] for x in cs]==contract['full_all_unit_order'] and len(cs)==105)
 check('inventory exact23 priority',[x['county_key'] for x in cs if x['priority']]==keys)
 fam=collections.Counter();unknown=collections.Counter();unitkeys=[];groups=0
 for source,c in zip(contract['all_geography_coverage'],cs):
  obj=json.loads(gzip.decompress((ROOT/c['native_context']).read_bytes()));check('complete native county source-object conservation '+c['county_fips'],obj==source)
  check('unapproved all current county crosswalks '+c['county_fips'],not c['november_2026_boundary_approval'])
  for f in obj['source_native_families']:
   groups+=1;fam[f['source_id']]+=len(f['constituents']);unknown[f['source_id']]+=sum(u['named_candidate_total'] is None for u in f['constituents']);unitkeys += [u['unit_key'] for u in f['constituents']]
 check('all525 native county-family groups',groups==525)
 expected=[4567,4566,4535,3867,4496];check('all22031 native identities unique and five overlapping counts',list(fam.values())==expected and len(unitkeys)==len(set(unitkeys))==22031)
 check('unknown units retained not zero',list(unknown.values())==[0,13,12,19,31])
 records={x['id']:x for x in json.loads(MAN.read_text())};nraw=0
 for key,r in records.items():
  if not r.get('storage'):check('connection failure retained '+key,r.get('status') is None and bool(r.get('error')));continue
  s=r['storage'];parts=[]
  for part in s['ordered_parts']:
   b=(ROOT/part['path']).read_bytes();check('stored original part '+key,len(b)==part['bytes'] and len(b)<40000000 and sha(b)==part['sha256']);parts.append(b)
  b=b''.join(parts);check('stored stream '+key,len(b)==s['stored_bytes'] and sha(b)==s['stored_sha256'])
  b=gzip.decompress(b) if s['encoding']=='gzip' else b;check('original entity reconstruct '+key,len(b)==r['original_bytes'] and sha(b)==r['original_sha256']);nraw+=1
  check('requested final UTC headers redirects retained '+key,bool(r['requested_url']) and bool(r.get('final_url')) and bool(r['retrieved_utc']) and isinstance(r.get('headers'),dict) and isinstance(r.get('redirects'),list))
 services=json.loads((ROOT/'services.json').read_text());data,archives=load_records(records,services)
 for s in services:
  key=s['id'];j=lambda suffix:json.loads(read(records[key+suffix]))
  pre=j('-ids-before');post=j('-ids-after');before=j('-count-before')['count'];after=j('-count-after')['count'];oid=s['oid_field'];ids=[]
  for page in s['pages']:
   r=records[page];pj=json.loads(read(r));ids += [x['attributes'][oid] for x in pj['features']]
   q=urllib.parse.parse_qs(urllib.parse.urlsplit(r['requested_url']).query)
   check('bounded all native geometry query '+page,len(q['objectIds'][0].split(','))<=100 and q.get('outFields')==['*'] and q.get('returnZ')==['true'] and q.get('returnM')==['true'] and q.get('returnTrueCurves')==['true'] and not any(x in q for x in ['outSR','geometryPrecision','quantizationParameters','geometry']))
   check('no transfer limit/quantization '+page,not pj.get('exceededTransferLimit',False) and 'transform'not in pj)
  check('service count all IDs pre/post '+key,before==after==s['count']==len(ids)==len(set(ids)) and sorted(ids)==sorted(pre['objectIds'])==sorted(post['objectIds']))
  check('service schema stable pre/post '+key,j('-layer').get('fields')==j('-layer-after').get('fields') and j('-layer').get('editingInfo')==j('-layer-after').get('editingInfo'))
  d=json.loads(gzip.decompress((ROOT/'extracts'/f'{key}-geometry.json.gz').read_bytes()));check('all service attributes retained '+key,[x['attributes'] for x in d['attributes']]==[x['attributes'] for x in data[key]['features']])
  check('actual XY finite '+key,not d['nonfinite'])
  if d['extent']:
   crs=as_crs(data[key]['spatial_reference']);t=Transformer.from_crs(crs,'EPSG:4326',always_xy=True);x0,y0,x1,y1=d['extent'];corners=[t.transform(x,y) for x in [x0,x1] for y in [y0,y1]]
   check('broad Kansas geographic bounds '+key,all(-103<x<-93 and 36<y<41 for x,y in corners),{'longitude_latitude_corners':corners,'policy':'coarse scope check, not approved boundary overlay'})
   extent=j('-extent').get('extent')
   check('full extent original query exists '+key,extent is not None)
   if extent:
    e=[extent[k] for k in ['xmin','ymin','xmax','ymax']];tol=1e-5
    check('native vertices within full advertised extent '+key,x0>=e[0]-tol and y0>=e[1]-tol and x1<=e[2]+tol and y1<=e[3]+tol,{'actual_nonlinearized_XY_bounds':d['extent'],'full_query_bounds':e,'tolerance_native_units':tol,'curves':'Four Shawnee curve objects retained separately; query bounds include all objects'})
 state=data['klrd-2022']['features'];countyids=collections.defaultdict(list)
 for f in state:countyids[f['attributes']['CO_CODE']].append(f['attributes']['FID'])
 check('complete statewide4749 map units105 exact county FIPS',len(state)==4749 and set(countyids)=={c['county_fips'] for c in cs})
 for c in cs:check('state reference all county IDs '+c['county_fips'],sorted(c['state_2022_feature_ids'])==sorted(countyids[c['county_fips']]))
 check('state reference no null or empty polygons',all(f.get('geometry',{}).get('rings') for f in state))
 check('Wyandotte geometry absence retained',all(not f.get('geometry') for f in data['wyandotte']['features']) and len(data['wyandotte']['features'])==153)
 curveids=[f['attributes']['OBJECTID'] for f in data['shawnee']['features'] if 'curveRings'in (f.get('geometry')or{})];check('Shawnee all four native curve objects retained',sorted(curveids)==[2120,2176,2199,2211])
 check('SHP ZIP CRC and record offsets/counts',all(l['shp_records']==l['shx_records']==l['dbf_records'] and l['shx_offsets_match_shp'] for v in archives.values() for l in v['layers']))
 class Parser(HTMLParser):
  def __init__(self):super().__init__();self.urls=[];self.cards=[];self.rows=0
  def handle_starttag(self,t,attrs):
   d=dict(attrs)
   if t=='article' and d.get('data-county-key'):self.cards.append(d['data-county-key'])
   if t=='tr' and 'data-search'in d:self.rows+=1
   for k in ['href','src']:
    if d.get(k):self.urls.append(d[k])
 parsed=Parser();parsed.feed((ROOT/'index.html').read_text());check('offline HTML exact ordered23 cards',parsed.cards==keys);check('offline HTML all105 inventory rows',parsed.rows==105)
 for u in parsed.urls:
  p=urllib.parse.urlsplit(u)
  check('offline index no external library/resource',not p.scheme and not p.netloc,u)
  if p.path:check('offline index relative asset '+p.path,(ROOT/urllib.parse.unquote(p.path)).exists())
 for p in list((ROOT/'previews').glob('*.png'))+list((ROOT/'previews').glob('*.jpg')):
  with Image.open(p) as img:img.verify()
 check('all105 complete state SVG previews',len(list((ROOT/'previews').glob('klrd2022-*.svg')))==105)
 for p in (ROOT/'previews').glob('*.svg'):ET.parse(p)
 for p in [ROOT/'SCHEMA.md',ROOT/'visual-review.md',BASE/'precinct-maps.md']:
  for u in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   parsedurl=urllib.parse.urlsplit(u)
   if parsedurl.scheme or u.startswith('#'):continue
   check('Markdown relative link '+str(p.name)+':'+u,(p.parent/urllib.parse.unquote(parsedurl.path)).exists())
 manifest=json.loads((ROOT/'asset-manifest.json').read_text());listed=set()
 for a in manifest['assets']:
  p=ROOT/a['path'];b=p.read_bytes();listed.add(p.resolve());check('owned frozen asset '+a['path'],len(b)==a['bytes'] and len(b)<40000000 and sha(b)==a['sha256'])
 excluded={'asset-manifest.json','validation.json','FROZEN.json'}
 actual={p.resolve() for p in ROOT.rglob('*') if p.is_file() and p.name not in excluded}|{(BASE/'precinct-maps.md').resolve()}
 check('owned manifest covers whole allowed output tree',actual==listed,{'unlisted':[str(p) for p in actual-listed],'missing':[str(p) for p in listed-actual]})
 check('no dependency/cache tree',not any(p.name in ['__pycache__','node_modules','.venv','venv'] for p in ROOT.rglob('*') if p.is_dir()))
 frozen=json.loads((ROOT/'FROZEN.json').read_text())
 for a in frozen['pins']:check('final freeze '+a['path'],sha((ROOT/a['path']).read_bytes())==a['sha256'])
 result={'status':'pass','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks_passed':len(checks),'checks':checks,'counties':105,'priority_counties':23,'native_identities':22031,'county_family_groups':525,'five_family_counts':dict(fam),'unknown_count_units':dict(unknown),'read_only_files':len(pin['files']),'full_shared_source_objects_checked':shared,'acquired_entity_records':nraw,'service_sources':len(services),'state_native_reference_polygons':4749,'originals_unrepaired':True,'november_boundary_approved':False,'map_result_crosswalk_approved':False,'collection_or_forecast_implemented':False,'owned_files':len(manifest['assets'])}
 (ROOT/'validation.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print('PASS',len(checks),'checks;',len(manifest['assets']),'owned assets;',len(pin['files']),'read-only inputs;',shared,'shared source objects')
if __name__=='__main__':
 try:main()
 except Exception as e:
  (ROOT/'validation.json').write_text(json.dumps({'status':'fail','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'error':repr(e),'checks':checks},indent=2)+'\n');raise
