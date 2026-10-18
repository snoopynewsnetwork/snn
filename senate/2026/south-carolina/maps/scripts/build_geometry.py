#!/usr/bin/env python3
"""Offline, read-only native geometry audit and exact ordered-byte county subsets.
Requires Shapely 2.x. No repair, buffer, snapping, dissolve or allocation.
"""
import sys
sys.dont_write_bytecode=True
from acquire import *
import re,math,collections,html
import shapely
from shapely.geometry import Polygon,MultiPolygon,Point
from shapely.strtree import STRtree
from shapely.validation import explain_validity

def dump(path,obj):
 b=(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode();p=ROOT/path;p.write_bytes(gzip.compress(b,mtime=0) if str(p).endswith('.gz') else b)
def slices(name):
 b=body(name);s=b.decode();d=json.loads(s);m=re.search(r'"features"\s*:\s*\[',s);pos=m.end();dec=json.JSONDecoder();out=[]
 while True:
  while s[pos].isspace() or s[pos]==',':pos+=1
  if s[pos]==']':break
  a=pos;f,pos=dec.raw_decode(s,pos);aa=len(s[:a].encode());bb=len(s[:pos].encode());raw=b[aa:bb];assert json.loads(raw)==f;out.append((f,{'capture':name,'json_pointer':f'/features/{len(out)}','byte_start_inclusive':aa,'byte_end_exclusive':bb,'feature_original_bytes':bb-aa,'feature_sha256':sha(raw)},raw))
 assert [f for f,_,_ in out]==d['features'];return d,out

def signed(r):return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(r,r[1:]))/2

def geometry(f):
 g=f.get('geometry');diag={'missing':g is None,'empty':False,'curves':bool(g and 'curveRings' in g)}
 if not g:return None,diag
 if 'rings' not in g:diag['unsupported_for_GEOS']='true curves kept native, GEOS audit not linearized';return None,diag
 rr=g['rings'];diag.update(rings=len(rr),positions=sum(map(len,rr)),coordinate_dimensions=dict(collections.Counter(str(len(p)) for r in rr for p in r)),unclosed_rings=[i for i,r in enumerate(rr) if r and r[0]!=r[-1]],short_rings=[i for i,r in enumerate(rr) if len(r)<4],nonfinite_positions=[(i,j) for i,r in enumerate(rr) for j,p in enumerate(r) if not all(math.isfinite(v) for v in p)],consecutive_duplicate_positions=sum(a==b for r in rr for a,b in zip(r,r[1:])))
 areas=[signed(r) for r in rr];diag['signed_ring_areas_sq_international_feet']=areas;diag['native_signed_ring_area_absolute_sum']=abs(sum(areas));shells=[r for r,a in zip(rr,areas) if a<0];holes=[r for r,a in zip(rr,areas) if a>=0];diag['clockwise_shell_count']=len(shells);diag['counterclockwise_or_zero_count']=len(holes)
 if not rr:diag['empty']=True;return None,diag
 if not shells:diag['unsupported_for_GEOS']='no clockwise exterior; raw winding preserved';return None,diag
 try:
  shellpolys=[Polygon(r) for r in shells];assigned=[[] for _ in shells];orphan=[]
  for r in holes:
   matches=[i for i,p in enumerate(shellpolys) if p.covers(Point(r[0][:2]))]
   if not matches:orphan.append(r)
   else:assigned[min(matches,key=lambda i:shellpolys[i].area)].append(r)
  diag['orphan_holes']=len(orphan)
  if orphan:diag['unsupported_for_GEOS']='unassigned holes; no repair or orientation reversal';return None,diag
  pp=[Polygon(r,hh) for r,hh in zip(shells,assigned)];geom=pp[0] if len(pp)==1 else MultiPolygon(pp);diag.update(valid=bool(geom.is_valid),validity_reason=explain_validity(geom),empty=bool(geom.is_empty),native_area_sq_international_feet=geom.area,native_length_international_feet=geom.length,bounds=list(geom.bounds));return geom,diag
 except Exception as e:diag['GEOS_error']=str(e);return None,diag

def preview(county,features):
 rr=[r for f in features for r in (f.get('geometry') or {}).get('rings',[])];pts=[p for r in rr for p in r];x0=min(p[0] for p in pts);x1=max(p[0] for p in pts);y0=min(p[1] for p in pts);y1=max(p[1] for p in pts);scale=min(1080/(x1-x0),870/(y1-y0));paths=[];labels=[]
 for f in features:
  g=f.get('geometry') or {};d=' '.join('M'+' L'.join(f'{(p[0]-x0)*scale+35:.2f},{(y1-p[1])*scale+70:.2f}' for p in r)+' Z' for r in g.get('rings',[]));a=f['attributes'];paths.append(f'<path d="{d}"><title>{html.escape(str(a.get("PCode"))+" "+str(a.get("PName")))}</title></path>')
 title=html.escape(county['name']);s=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1150 1010"><rect width="1150" height="1010" fill="#f8fafc"/><text x="35" y="35" font-family="sans-serif" font-size="25">{title} — RFA native publication preview</text><g fill="#dce9ed" stroke="#243b53" stroke-width=".45" fill-rule="evenodd">{''.join(paths)}</g><text x="35" y="975" font-family="sans-serif" font-size="16">{len(features)} features · source EPSG:6570 · display coordinates rounded only in this SVG</text><text x="35" y="999" font-family="sans-serif" font-size="14">Research preview; current publication is not November reporting/physical approval. No vote allocation.</text></svg>''';(ROOT/'derived'/f'{county["county_fips"]}-preview.svg').write_text(s)

def run():
 contract=json.loads((ROOT.parent/'data/turnout/priority-set.json').read_text());allentries=[];pages=[];oid='OBJECTID'
 for p in sorted((ROOT/'raw').glob('native-page-*.request.json')):
  name=p.name.removesuffix('.request.json');d,ss=slices(name);pages.append({'capture':name,'count':len(ss),'exceededTransferLimit':d.get('exceededTransferLimit'),'has_transform':'transform' in d,'hasZ':d.get('hasZ'),'hasM':d.get('hasM'),'spatialReference':d.get('spatialReference'),'requested_object_ids':list(map(int,re.search(r'objectIds=([^&]+)',json.loads(p.read_text())['requested_url']).group(1).replace('%2C',',').split(',')))})
  assert {f['attributes'][oid] for f,_,_ in ss}==set(pages[-1]['requested_object_ids']);pages[-1]['returned_object_ids']=[f['attributes'][oid] for f,_,_ in ss];pages[-1]['requested_returned_ID_sets_equal']=True;pages[-1]['pagination']='bounded explicit object-ID batches; no resultOffset pagination, no transfer-limit truncation'
  allentries+=ss
 ids=[f[0]['attributes'][oid] for f in allentries];expected=js('native-pre-ids')['objectIds'];assert len(ids)==len(set(ids))==js('native-pre-count')['count']==2315;assert set(ids)==set(expected)==set(js('native-post-ids')['objectIds']);assert js('native-pre-count')==js('native-post-count')
 for page in pages:assert not page['exceededTransferLimit'] and not page['has_transform']
 records=[];geoms=[];geomindices=[];bycounty=collections.defaultdict(list);prefixes={c['county_fips'][-2:]:c for c in contract['counties']}
 for i,(f,loc,raw) in enumerate(allentries):
  a=f['attributes'];code=re.fullmatch(r'P-(\d\d)-.+',a['CodeMapNum']).group(1);c=prefixes[code];bycounty[c['county_fips']].append((f,loc,raw));g,diag=geometry(f);row={'OBJECTID':a['OBJECTID'],'county_fips_from_official_map_number':c['county_fips'],'complete_attributes':a,'original_locator':loc,'geometry_diagnostics':diag};records.append(row)
  if g is not None:geoms.append(g);geomindices.append(i)
 pairs=[];skipped=[];tree=STRtree(geoms);bboxpairs=0;touches=0
 for i,g in enumerate(geoms):
  for jn in tree.query(g):
   j=int(jn)
   if j<=i:continue
   bboxpairs+=1;ri=records[geomindices[i]];rj=records[geomindices[j]];pair={'a_OBJECTID':ri['OBJECTID'],'b_OBJECTID':rj['OBJECTID'],'a_county':ri['county_fips_from_official_map_number'],'b_county':rj['county_fips_from_official_map_number']}
   if not g.is_valid or not geoms[j].is_valid:skipped.append(pair|{'reason':'invalid native geometry; no repair applied'});continue
   try:
    z=g.intersection(geoms[j]);ar=z.area
    if ar>0:pairs.append(pair|{'overlap_area_sq_international_feet':ar,'intersection_type':z.geom_type})
    elif not z.is_empty:touches+=1
   except Exception as e:skipped.append(pair|{'reason':str(e)})
 countyrows=[]
 for c in contract['counties']:
  entries=bycounty[c['county_fips']];features=[f for f,_,_ in entries];codes=[f['attributes']['PCode'] for f in features];names=[f['attributes']['PName'] for f in features];row={'geography_key':c['geography_key'],'name':c['name'],'county_fips':c['county_fips'],'rank':c['rank'],'in_priority':c['in_priority'],'native_count':len(features),'native_OBJECTID_set':[f['attributes']['OBJECTID'] for f in features],'native_PCode_values':codes,'native_PName_values':names,'duplicate_nonmissing_PCode_values':[k for k,v in collections.Counter(codes).items() if v>1 and k is not None],'missing_PCode_count':sum(x is None for x in codes),'null_geometry_OBJECTIDs':[r['OBJECTID'] for r in records if r['county_fips_from_official_map_number']==c['county_fips'] and r['geometry_diagnostics']['missing']],'invalid_OBJECTIDs':[r['OBJECTID'] for r in records if r['county_fips_from_official_map_number']==c['county_fips'] and r['geometry_diagnostics'].get('valid') is False]}
  if c['in_priority']:
   # The feature slices themselves, including every original numeric lexeme, are copied unchanged.
   native={'displayFieldName':js('rfa-precinct-layer').get('displayField'),'fields':js('rfa-precinct-layer')['fields'],'geometryType':'esriGeometryPolygon','spatialReference':js('rfa-precinct-layer')['spatialReference'],'hasZ':False,'hasM':False};head=json.dumps(native,separators=(',',':')).encode();b=head[:-1]+b',"features":['+b','.join(raw for _,_,raw in entries)+b']}\n';out=ROOT/'derived'/f'{c["county_fips"]}-native.esrijson.gz';out.write_bytes(gzip.compress(b,mtime=0));assert json.loads(b)['features']==features;row.update(exact_native_subset=str(out.relative_to(ROOT)),exact_subset_original_bytes=len(b),exact_subset_original_sha256=sha(b),subset_feature_lexemes_unchanged=True,subset_feature_origins=[loc for _,loc,_ in entries],preview=f'derived/{c["county_fips"]}-preview.svg');preview(c,features)
  countyrows.append(row)
 summary={'schema':'sc-map-native-audit-v1','source':'raw/rfa-precinct-layer.body.gz','count':len(ids),'pre_post_count_equal':True,'pre_post_all_id_sets_equal':True,'downloaded_all_ids_equal':True,'complete_ID_set':sorted(ids),'pages':pages,'schema_hasZ':js('rfa-precinct-layer')['hasZ'],'schema_hasM':js('rfa-precinct-layer')['hasM'],'native_crs':js('rfa-precinct-layer')['spatialReference'],'native_units':'international feet; native areas square international feet (0.3048 m per foot)','topology_method':'ArcGIS clockwise shells, counterclockwise holes assigned to smallest covering shell. No coordinate transforms, snapping, repair, buffer or vote allocation. GEOS only on interpretable native rings. All raw geometry retained. Bbox index covers all statewide native features; invalid-pair intersection computations explicitly skipped. No external legal boundary used for gap certification.','software':{'shapely':shapely.__version__,'GEOS':shapely.geos_version_string},'features':records,'topology':{'bbox_candidate_pairs':bboxpairs,'positive_area_overlaps':pairs,'skipped_pairs':skipped,'zero_area_contact_pair_count':touches,'gap_audit':'No trusted, same-vintage legal coverage outline acquired; holes are listed per feature but inter-precinct gaps cannot be certified.'},'counties':countyrows,'archive_audit':{'applicable':False,'reason':'Native originals are unarchived Esri JSON entities losslessly gzip-compressed; gzip CRC/trailer is checked by decompression. PDFs are native PDF entities. No ZIP or geodatabase archive substituted.'}}
 dump('native-audit.json.gz',summary);dump('county-geometry-inventory.json',countyrows);print(json.dumps({'features':len(records),'invalid':sum(r['geometry_diagnostics'].get('valid') is False for r in records),'missing':sum(r['geometry_diagnostics']['missing'] for r in records),'curves':sum(r['geometry_diagnostics']['curves'] for r in records),'overlaps':len(pairs),'skipped_pairs':len(skipped),'priority_features':sum(r['native_count'] for r in countyrows if r['in_priority'])}))
if __name__=='__main__':run()
