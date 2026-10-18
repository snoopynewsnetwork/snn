#!/usr/bin/env python3
"""Offline scope/identity/conservation/full-resolution/provenance/link validator."""
import argparse,pathlib,json,gzip,hashlib,csv,io,zipfile,struct,math,subprocess,sys,collections,re,urllib.parse,os
from html.parser import HTMLParser
from acquire import ROOT,body,sha
import shapefile,fitz,pyproj
P=argparse.ArgumentParser();P.add_argument('--check-manifest',action='store_true');a=P.parse_args();STATE=ROOT.parent
C=json.loads((STATE/'data/turnout/priority-set.json').read_text());cb=(STATE/'data/turnout/priority-set.json').read_bytes();assert sha(cb)=='11c042966c67a50e496ad6f839afd8e3c8b28afe6e2761c6cda1aa51f7ce90fc'and len(cb)==3653481
accepted=json.loads((STATE/'data/coordinator-priority-acceptance.json').read_text());assert accepted['accepted']and accepted['ordered_priority_keys']==C['ordered_priority_keys'];assert (STATE/'data/coordinator-priority-keys.txt').read_text().splitlines()==C['ordered_priority_keys']
for ref in json.loads((ROOT/'source/shared-originals.json').read_text()):
 b=(STATE/ref['path']).read_bytes();assert len(b)==ref['bytes']and sha(b)==ref['sha256'],ref['path']
inv=json.loads((ROOT/'inventory.json').read_text())['units'];pri=json.loads((ROOT/'priority.json').read_text());assert len(inv)==320 and [r['geography_key']for r in inv]==C['full_ordered_keys'];assert len(pri['units'])==143 and pri['units']==inv[:143];assert pri['ordered_priority_keys']==C['ordered_priority_keys'];assert [r['source_unit']for r in inv]==C['all_units'];assert len({r['geography_key']for r in inv})==320
assert len({r['source_unit']['municipal_parent_label']for r in inv[:143]})==98;assert sum(r['source_unit']['ward']is not None for r in inv)==73;assert len({r['source_unit']['municipal_parent_label']for r in inv if r['source_unit']['ward']is not None})==12
assert sum(r['source_unit']['reported_candidate_write_in_votes']for r in inv)==826189;assert sum(r['source_unit']['reported_candidate_write_in_votes']for r in inv[:15])==185659;assert sum(r['source_unit']['reported_candidate_write_in_votes']for r in inv[:143])==662624;assert 5*660378<4*826189<=5*662624
assert sum(r['scope']=='no_polygon_unknown_administrative_scope'for r in inv)==25
for r in inv:
 assert r['source_unit']['source_native_id']is None and r['current_results_source_id']is None and r['current_november_2026_approved']is False
 if r['scope']=='no_polygon_unknown_administrative_scope':assert r['municipal_reference']is None and r['preview']is None
 if r['priority_rank']:
  assert (ROOT/r['preview']).exists()and r['primary_assets']
  if r['source_unit']['ward']is not None:assert r['scope']=='actual_ward_reference'and not r['preview'].startswith('previews/m-')
berlin=[r for r in inv if r['source_unit']['municipal_parent_label']=='Berlin'];assert len(berlin)==1 and berlin[0]['source_unit']['ward']is None
# Exact source-scoped objects; each raw field/null/type/locator is preserved without a cross-year join.
source_rows={};native_fields=0
for fam in C['source_native_coverage']:
 b=(ROOT/'compatibility'/fam['path']).read_bytes();assert sha(b)==fam['sha256']and b==(STATE/'data/turnout'/fam['path']).read_bytes();rows=[json.loads(x)for x in gzip.decompress(b).splitlines()];assert len(rows)==320
 assert len({(x['source_id'],x['county'],x['native_label'])for x in rows})==320
 for r,c in zip(rows,fam['constituents']):
  assert r['source_native_id']is None;assert r['source_locator']==c['locator'];assert r['native_label']==c['native_label'];assert set(r['fields'])==set(r['raw_fields']);native_fields+=len(r['fields'])
 source_rows[fam['source_id']]=rows
assert len(source_rows)==23 and native_fields==34880
subprocess.run([sys.executable,str(ROOT/'audit_native.py'),'--check-only'],check=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},stdout=subprocess.DEVNULL)
# Compare all stable peer CSV observations by source/vintage + county + literal identity only.
turn=list(csv.DictReader((STATE/'data/county-turnout.csv').open()));assert len(turn)==320 and [r['geography_key']for r in turn]==C['full_ordered_keys']
for r,u in zip(turn,C['all_units']):assert r['native_label']==u['native_label']and int(r['reported_candidate_write_in_votes'])==u['reported_candidate_write_in_votes']
base=list(csv.DictReader((STATE/'data/county-baselines.csv').open()));assert len(base)==960;basechecks=0
for r in base:
 native=[x for x in source_rows[r['source_id']]if x['county']==r['county']and x['native_label']==r['native_label']];assert len(native)==1,(r['source_id'],r['native_label']);n=native[0];assert json.loads(r['raw_fields_json'])==n['raw_fields']
 for k,v in n['fields'].items():assert (None if r[k]==''else int(r[k]))==v;basechecks+=1
# All original and stored captures, including complete split reconstruction and blocked bodies.
metas={p.name[:-10]:json.loads(p.read_text())for p in (ROOT/'source').glob('*.meta.json')};objects=set()
for id,m in metas.items():
 if m.get('parent'):assert m['parent']in metas,(id,m['parent'])
 if m.get('status')is None:continue
 assert 'response_headers'in m and 'redirects'in m and 'requested_utc'in m and 'completed_utc'in m
 full=body(id);assert len(full)==m['original_bytes']and sha(full)==m['original_sha256']
 assert [x['order']for x in m['objects']]==list(range(len(m['objects'])))
 for x in m['objects']:
  b=(ROOT/x['path']).read_bytes();assert sha(b)==x['sha256']and len(b)==x['bytes']<40000000;d=gzip.decompress(b)if x['encoding']=='gzip'else b;assert len(d)==x['decoded_bytes']and sha(d)==x['decoded_sha256'];objects.add(x['path'])
# Native ZIP record counts, CRC, attributes, complete points/parts and SHX offsets; no derived repair.
z=zipfile.ZipFile(io.BytesIO(body('granit-pbp')));assert z.testzip()is None;zc=json.loads((ROOT/'derived/zip-controls.json').read_text());assert len(z.infolist())==len(zc['members'])==16
for x in zc['members']:assert sha(z.read(x['member']))==x['sha256']and f"{z.getinfo(x['member']).CRC:08x}"==x['crc32']
for stem,count in [('pbp',259),('pba',773)]:
 r=shapefile.Reader(shp=io.BytesIO(z.read(stem+'.shp')),shx=io.BytesIO(z.read(stem+'.shx')),dbf=io.BytesIO(z.read(stem+'.dbf')));native=json.loads(gzip.decompress((ROOT/f'derived/granit-archive-{stem}-native.json.gz').read_bytes()));assert len(native)==len(r)==count
 for i,x in enumerate(native):s=r.shape(i);assert x['attributes']==r.record(i).as_dict()and x['points']==[list(p)for p in s.points]and x['parts']==list(s.parts)and x['bbox']==list(s.bbox);assert x['z']is None and x['m']is None
# Re-audit native ArcGIS ID sets, counts, full fields, no truncation/generalization and geometries.
services=[]
for f in sorted((ROOT/'derived').glob('*-service-audit.json')):
 d=json.loads(f.read_text());id=d['id'];before=json.loads(body(id+'-ids-pre'));after=json.loads(body(id+'-ids-post'));ids=sorted(before['objectIds']);assert ids==sorted(after['objectIds'])==d['pre_ids']==d['post_ids'];assert len(ids)==d['count_pre']==d['count_post']==json.loads(body(id+'-count-pre'))['count']==json.loads(body(id+'-count-post'))['count'];allids=[];vertices=0
 layer=json.loads(body(id+'-layer'));fieldnames={x['name']for x in layer['fields']}
 for batch in d['batches']:
  m=metas[batch['id']];q=urllib.parse.parse_qs(urllib.parse.urlparse(m['requested_url']).query)
  assert not any(k in q for k in ['geometryPrecision','maxAllowableOffset','quantizationParameters','outSR']);assert q['outFields']==['*']and q['returnTrueCurves']==['true']and q['returnZ']==['true']and q['returnM']==['true'];assert len(batch['requested_ids'])<=100
  b=json.loads(body(batch['id']));assert not b.get('exceededTransferLimit',False)
  got=[x['attributes'][d['object_id_field']]for x in b['features']];assert sorted(got)==batch['requested_ids'];allids+=got
  for feat in b['features']:
   assert set(feat['attributes'])==fieldnames;g=feat['geometry'];assert g
   for ring in g.get('rings',[]):
    assert ring[0]==ring[-1]and len(ring)>=4
    for p in ring:assert all(math.isfinite(x)for x in p)
    vertices+=len(ring)
 assert sorted(allids)==ids and len(allids)==len(set(allids));services.append({'dataset':id,'features':len(ids),'native_vertices':vertices,'hasZ':layer.get('hasZ'),'hasM':layer.get('hasM'),'curve_features':d['features_with_curveRings'],'native_crs':d['native_crs']})
assert len(services)==7
# All municipal transformed downloads retain every native coordinate; finite local extent bounds.
municipals=list((ROOT/'derived/municipal').glob('*.geojson'));assert len(municipals)==468
archive_native=json.loads(gzip.decompress((ROOT/'derived/granit-archive-pbp-native.json.gz').read_bytes()))
live_native={f['attributes']['objectid_1']:f for batch in json.loads((ROOT/'derived/granit-live-service-audit.json').read_text())['batches']for f in json.loads(body(batch['id']))['features']}
municipalmatches={t['archive_geojson']:t for t in json.loads((ROOT/'derived/municipal-reference-matches.json').read_text())if t.get('archive_geojson') and (ROOT/t['archive_geojson']).exists()}
municipalmatches.update({t['live_geojson']:t for t in json.loads((ROOT/'derived/municipal-reference-matches.json').read_text())if t.get('live_geojson') and (ROOT/t['live_geojson']).exists()})
tx=pyproj.Transformer.from_crs(3437,4326,always_xy=True)
for p in municipals:
 d=json.loads(p.read_text());assert len(d['features'])==1;g=d['features'][0]['geometry'];assert g['type']in ['Polygon','MultiPolygon']
 t=municipalmatches[str(p.relative_to(ROOT))]
 if p.stem.endswith('-archive'):
  native=archive_native[t['archive_record_ids'][0]];nativepoints=native['points'];props=native['attributes']
 else:
  native=live_native[t['live_object_ids'][0]];nativepoints=[p for ring in native['geometry']['rings']for p in ring];props=native['attributes']
 assert d['features'][0]['properties']==props

 def coords(x):
  if x and isinstance(x[0],(int,float)):yield x
  else:
   for v in x:yield from coords(v)
 transformedpoints=list(coords(g['coordinates']));expectedpoints=[tx.transform(p[0],p[1])for p in nativepoints];assert len(transformedpoints)==len(expectedpoints)
 for got,want in zip(sorted(map(tuple,transformedpoints)),sorted(expectedpoints)):assert all(abs(a-b)<1e-12 for a,b in zip(got,want))
 for point in transformedpoints:assert len(point)>=2 and -73<point[0]<-70 and 42<point[1]<46 and all(math.isfinite(n)for n in point)
# PDF counts and every actual page preview; visual-review hashes prevent filename/vintage confusion.
pdfs=json.loads((ROOT/'derived/pdf-pages.json').read_text());reviews={r['id']:r for r in json.loads((ROOT/'derived/visual-review.json').read_text())['reviews']};npages=0
for d in pdfs:
 doc=fitz.open(stream=body(d['id']),filetype='pdf');assert len(doc)==d['page_count']==len(d['pages'])==reviews[d['id']]['page_count'];assert d['original_sha256']==reviews[d['id']]['original_sha256']
 for x in d['pages']:assert (ROOT/x['preview']).is_file()and (ROOT/x['preview']).read_bytes().startswith(b'\x89PNG');npages+=1
assert len(pdfs)==44 and npages==124
# All local HTML references and report/schema Markdown links; no network dependency in HTML.
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.refs=[];self.cards=[];self.inventory=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  for k in ['href','src']:
   if k in a:self.refs.append((t,k,a[k]))
  if 'data-key'in a:self.cards.append(a['data-key'])
  if 'data-inventory-key'in a:self.inventory.append(a['data-inventory-key'])
linkschecked=0
for p in list(ROOT.glob('*.html'))+[STATE/'precinct-maps.md',ROOT/'source/SCHEMA.md']:
 assert p.exists(),str(p)
 if p.suffix=='.html':
  parser=Parser();parser.feed(p.read_text());refs=parser.refs
  if p.name=='index.html':assert parser.cards==C['ordered_priority_keys']and parser.inventory==C['full_ordered_keys']
  for t,k,u in refs:
   if urllib.parse.urlparse(u).scheme:assert k!='src'and t not in ['script','link'],'External dependency '+u
 else:refs=[('a','href',x)for x in re.findall(r'\]\(([^)]+)\)',p.read_text())]
 for t,k,u in refs:
  if not u or u.startswith('#')or urllib.parse.urlparse(u).scheme:continue
  local=urllib.parse.unquote(u.split('#')[0].split('?')[0]);q=(p.parent/local).resolve();assert q.exists()or q==ROOT/'validation.json',(p,u);assert q==STATE or STATE in q.parents,(p,u);linkschecked+=1
files=[p for p in ROOT.rglob('*')if p.is_file()];assert not any('__pycache__'in p.parts or p.suffix=='.pyc'for p in files),'No cache trees allowed';assert all(p.stat().st_size<40000000 for p in files)
out={'schema_version':'nh-maps-offline-validation-1','status':'pass','scope':'Research asset/integrity validation; current legal precinct/November result crosswalk unapproved','checks':['frozen acceptance, ordered143/full320/177remainder and exact source_unit objects','23x320 exact native roster bytes and objects, fresh34880 primary fields and original controls,960baseline CSV/320turnout CSV','whole-state candidate/administrative balances preserved, no rescale/null imputation','all original/stored/split streams hashes/sizes/redirect metadata and all read-only pins','ZIP16memberCRC/SHP259+773/SHX/DBF/fullpoints/parts/nativeattributes','7services allIDs/prepost counts/bounded100/transferflags/allattributes/nativeprecision/Z/M/truecurves','468wholemunicipalityfullcoordinateGeoJSONdownloads finite NHbounds','44PDFcapture/124actualpagecounts/previews/visualhashreview','local HTML ordered143cards/full320rows, no external rendering dependencies, all local relative links','strictlybelow40000000bytes; no cache/dependency trees; no peer/Git writes'], 'counts':{'priority':143,'all_source_leaves':320,'remainder':177,'explicit_priority_parents':98,'priority_whole_municipality_rows':89,'priority_ward_rows':54,'all_city_wards':73,'explicit_ward_parents':12,'administrative_no_polygon':25,'native_source_rosters':23,'native_source_objects':7360,'native_source_fields':34880,'stable_baseline_CSV_rows':960,'baseline_fields_checked':basechecks,'primary_response_captures':len(metas),'unique_original_objects':len(objects),'municipal_GeoJSONs':len(municipals),'PDF_captures':len(pdfs),'PDF_page_previews':npages,'local_links_checked':linkschecked},'services':services,'preserved_known_defects':['2022summaryheaderreversal/opposing297candidatevintages','2024Coosdetail17511/summary17510;SomersworthWard3parts1222/reported1221','ChecklistHopkintonparts296/literal3; source blanks/dashes/asterisks remain'], 'material_gaps':['No November2026 source-key/ward/precinct/method approval or crosswalk','49priorityward identities have actualPDF reference but no downloaded native wardvector;Dover6 currentvector backend500 with2012fallback','Berlin current1/3 precinct polygons unknown; historicalBerlin1row preserved','NashuaWard1andHudsonWard1polling-location conflicts; metadata clocks not effective dates','25administrativeleaves nopolygon/unknownscope;19remainderwardsonlyparentreference','Externallegalenvelope gap tests and cross-source geometry comparisons unverified; no repair']}
if a.check_manifest:
 mf=json.loads((ROOT/'asset-manifest.json').read_text());expected={str(p.relative_to(STATE))for p in files if p.name!='asset-manifest.json'}|{'precinct-maps.md'};assert {x['path']for x in mf['assets']}==expected
 for x in mf['assets']:
  b=(STATE/x['path']).read_bytes();assert len(b)==x['bytes']and sha(b)==x['sha256'],x['path']
 assert json.loads((ROOT/'validation.json').read_text())==out,'Validation output drift; regenerate and refreeze manifest'
else:(ROOT/'validation.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'status':'pass','counts':out['counts'],'manifest_verified':a.check_manifest},indent=2))
