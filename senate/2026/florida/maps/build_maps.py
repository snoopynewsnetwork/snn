#!/usr/bin/env python3
"""Offline preservation, native geometry diagnostics and static map previews.
Raw snapshots are never repaired, rounded, or overwritten by this build.
"""
import sys
sys.dont_write_bytecode=True
import collections,datetime,gzip,hashlib,html,io,json,math,pathlib,struct,xml.etree.ElementTree as ET,zipfile
import shapefile,shapely
from shapely.geometry import Polygon,MultiPolygon,shape
from shapely.validation import explain_validity
from shapely.strtree import STRtree
from pyproj import CRS
from PIL import Image,ImageDraw,ImageFont
from acquire import ROOT,body
STATE=ROOT.parent
PIN='0c056e0ebfdb393d4fcb59676805122d8442f444200b9edaf7f4c979c5e9a173'
sha=lambda b:hashlib.sha256(b).hexdigest()
def canonical(o):return json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def dump(name,o):
 p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def json_gzip(name,o):
 p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(gzip.compress(canonical(o),mtime=0))
def relative_pin(p):
 b=p.read_bytes();return {'path':str(p.relative_to(STATE)), 'bytes':len(b),'sha256':sha(b)}
def equal(a,b):
 assert type(a)==type(b)
 if isinstance(a,dict):
  assert list(a)==list(b)
  return 1+sum(equal(a[k],b[k]) for k in a)
 if isinstance(a,list):assert len(a)==len(b);return 1+sum(equal(x,y) for x,y in zip(a,b))
 assert a==b;return 1

def frozen():
 p=STATE/'data/turnout/priority-set.json';b=p.read_bytes();assert len(b)==23823926 and sha(b)==PIN;d=json.loads(b)
 # Preserve complete semantic object including all original order, flags/nulls and source/admin objects.
 raw=json.dumps(d,ensure_ascii=False,separators=(',',':')).encode();(ROOT/'frozen-contract.semantic.json.gz').write_bytes(gzip.compress(raw,mtime=0));copy=json.loads(gzip.decompress((ROOT/'frozen-contract.semantic.json.gz').read_bytes()));nodes=equal(d,copy)
 assert d['coordinator_accepted'] is False
 a=json.load(open(STATE/'data/coordinator-priority-acceptance.json'));assert a['accepted'] and a['contract']['sha256']==PIN
 order=d['all_unit_order'];assert len(order)==67 and len({x['key'] for x in order})==67 and len(d['ordered_priority_keys'])==22
 assert [x['key'] for x in order[:22]]==d['ordered_priority_keys']==a['ordered_priority_keys']
 votes=[x['votes'] for x in order];assert votes==sorted(votes,reverse=True)
 assert sum(votes)==10757428 and sum(votes[:15])==7373225 and sum(votes[:21])==8572752 and sum(votes[:22])==8734473 and sum(votes[22:])==2022955
 assert sum(votes[:21])<8605943<=sum(votes[:22]) and votes[21]==161721
 pointers={};frozen_units={}
 for i,g in enumerate(d['native_constituents']):
  assert len(g['units'])==g['constituent_count']
  lists=[('2024_senate',g['units'],f'/native_constituents/{i}/units')]+[(c,o['units'],f'/native_constituents/{i}/other_contexts/{c}/units') for c,o in g['other_contexts'].items()]
  for c,units,ptr in lists:
   for j,u in enumerate(units):assert u['native_key'] not in pointers;pointers[u['native_key']]=ptr+'/'+str(j);frozen_units[u['native_key']]=u
 assert len(pointers)==23532
 native_path=STATE/'data/turnout/extracts/native-units.jsonl.gz';units=[json.loads(s) for s in gzip.decompress(native_path.read_bytes()).splitlines()];assert len(units)==23532
 out=io.BytesIO();counts=collections.Counter();county_contexts=collections.Counter();unknowns=collections.Counter()
 for n,line in enumerate(units,1):
  key=line['native_key'];u=frozen_units[key];counts[line['context']]+=1;county_contexts[(line['parent_key'],line['context'])]+=1
  for k in ['source_id','source_member','election_number','precinct_id','polling_location','contest_code','precinct_id_available','source_label_method_hint_only','administrative_case']:assert u[k]==line[k],(key,k)
  assert [r['source_row_1based'] for r in line['candidate_category_rows']]==u.get('source_rows_1based',[r['source_row_1based'] for r in line['candidate_category_rows']])
  unknowns['blank_id']+=not line['precinct_id_available'];unknowns['label_method_hint_only']+=line['source_label_method_hint_only']
  diag={'source_record':line,'source_native_record_sha256':sha(canonical(line)),'canonical_source_line_1based':n,'frozen_constituent_json_pointer':pointers[key],'frozen_constituent_sha256':sha(canonical(u)),'physical_geometry_match':None,'geometry_allocation_status':'unallocated: native submitted identity semantics and election-specific crosswalk not established','method_assignment':None,'lexical_candidates':[],'legal_named_writein_allocation':None}
  out.write(canonical(diag)+b'\n')
 assert set(pointers)=={u['native_key'] for u in units};assert dict(counts)=={'2024_president':5712,'2024_senate':5710,'2022_senate':6013,'2020_president':6097}
 (ROOT/'identity-diagnostics.jsonl.gz').write_bytes(gzip.compress(out.getvalue(),mtime=0))
 refs=[p,STATE/'data/coordinator-priority-acceptance.json',native_path,STATE/'data/turnout/asset-manifest.json',STATE/'data/baselines/asset-manifest.json',STATE/'data/turnout/source/shared-source-references.json',STATE/'data/coordinator-native-original-review.json',STATE/'data/coordinator-target-review.json',STATE/'data/coordinator-primary-table-review.json',STATE/'data/coordinator-poll-clock-review.json']
 refs += sorted((STATE/'data/turnout/source').glob('supervisor-*.receipt.json'))+sorted((STATE/'data/turnout/source').glob('supervisor-*.body.gz'))
 for name,pin in [('turnout','c510f3321a7764815fee9745fa6f6ce294e6a312320b1f723c80dc6a44edffb7'),('baselines','5517e4baeafaf57f2858839d8bd3f868355947e94d8e07ce15ff53bf579f2b65')]:assert sha((STATE/f'data/{name}/asset-manifest.json').read_bytes())==pin
 dump('frozen-reference.json',{'canonical_contract':relative_pin(p),'semantic_copy':'frozen-contract.semantic.json.gz','recursive_object_equality':True,'recursive_nodes_compared':nodes,'all_source_and_administrative_objects_preserved':True,'external_historical_authority':relative_pin(STATE/'data/coordinator-priority-acceptance.json'),'internal_false_flag_retained':True,'references':[relative_pin(x) for x in refs],'identity_source':relative_pin(native_path),'native_counts':dict(counts),'native_identity_diagnostics':'identity-diagnostics.jsonl.gz','all_unallocated':23532,'unknowns':dict(unknowns),'no_raw_original_duplication':'Historical ZIPs stay at exact immutable shared-source references; verify_native_originals.py rereads them in place.'})
 return d,county_contexts

NS={'k':'http://www.opengis.net/kml/2.2'}
def zipcheck(key):
 z=zipfile.ZipFile(io.BytesIO(body(key)));assert z.testzip() is None
 return z,[{'name':x.filename,'bytes':x.file_size,'compressed_bytes':x.compress_size,'CRC32':f'{x.CRC:08x}','header_offset':x.header_offset,'sha256':sha(z.read(x))} for x in z.infolist()]
def shp_source(key,county=None):
 z,members=zipcheck(key);name=[x.filename[:-4] for x in z.infolist() if x.filename.lower().endswith('.shp')];assert len(name)==1;name=name[0]
 shp=z.read(name+'.shp');shx=z.read(name+'.shx');dbf=z.read(name+'.dbf');assert struct.unpack('>i',shp[24:28])[0]*2==len(shp);assert struct.unpack('>i',shx[24:28])[0]*2==len(shx)
 count=(len(shx)-100)//8;assert (len(shx)-100)%8==0;dbfcount=struct.unpack('<I',dbf[4:8])[0];assert dbfcount==count
 hlen,rlen=struct.unpack('<HH',dbf[8:12]);deleted=[];offsets=[]
 for i in range(count):
  offset,length=struct.unpack('>ii',shx[100+8*i:108+8*i]);recordnum,reclen=struct.unpack('>ii',shp[2*offset:2*offset+8]);assert recordnum==i+1 and length==reclen;assert 2*offset+8+2*length<=len(shp);offsets.append({'record_1based':i+1,'byte_offset':offset*2,'content_bytes':length*2})
  if dbf[hlen+i*rlen:hlen+i*rlen+1]!=b' ':deleted.append(i+1)
 enc=z.read(name+'.cpg').decode().strip() if name+'.cpg' in z.namelist() else 'utf-8';enc='utf-8' if enc=='UTF-8' else enc
 r=shapefile.Reader(shp=io.BytesIO(shp),shx=io.BytesIO(shx),dbf=io.BytesIO(dbf),encoding=enc);features=[]
 for i in range(count):
  rec=r.record(i);attrs=rec.as_dict() if rec is not None else None;s=r.shape(i);rings=[list(s.points[a:b]) for a,b in zip(s.parts,list(s.parts)[1:]+[len(s.points)])]
  if county is None or attrs.get('COUNTYFP20')==county:features.append({'source_locator':{'archive':key,'member':name+'.shp','record_1based':i+1},'attributes':attrs,'rings':rings,'geometry_type_code':s.shapeType,'z':getattr(s,'z',None),'m':getattr(s,'m',None)})
 return features,{'archive_members':members,'SHP_SHX_DBF_record_count':count,'SHX_all_offsets_verified':True,'record_offsets':offsets,'DBF_deleted_records_1based':deleted,'DBF_encoding':enc,'prj':z.read(name+'.prj').decode(),'native_shape_type':r.shapeType,'filter':county,'unfiltered_original_retained':True}

def kml_source(key,selected_folder):
 z,members=zipcheck(key);features=[];folders=[];root=ET.fromstring(z.read('doc.kml'))
 for fi,f in enumerate(root.findall('.//k:Folder',NS)):
  name=f.findtext('k:name',namespaces=NS);pms=f.findall('k:Placemark',NS);folders.append({'folder':name,'placemarks':len(pms),'polygon_parts':len(f.findall('.//k:Polygon',NS)),'points':len(f.findall('.//k:Point',NS))})
  for pi,pm in enumerate(pms):
   if name!=selected_folder:continue
   rings=[]
   for poly in pm.findall('.//k:Polygon',NS):
    for coords in poly.findall('.//k:coordinates',NS):rings.append([[float(x) for x in word.split(',')] for word in (coords.text or '').split()])
   attrs={'id':pm.get('id'),'name':pm.findtext('k:name',namespaces=NS),'description':pm.findtext('k:description',namespaces=NS),'extended_data':[ET.tostring(e,encoding='unicode') for e in pm.findall('k:ExtendedData',NS)]}
   features.append({'source_locator':{'archive':key,'member':'doc.kml','folder_index_0based':fi,'folder_name':name,'placemark_index_0based':pi},'attributes':attrs,'rings':rings,'kml_polygon_parts':len(pm.findall('.//k:Polygon',NS))})
 assert features
 return features,{'archive_members':members,'folders':folders,'selected_folder':selected_folder,'coordinate_convention':'KML longitude,latitude,altitude; altitudeMode retained in original XML. Geometry diagnostics use XY only; no native ordinates discarded from original.'}

def native_sources():
 sources={}
 for p in sorted(ROOT.glob('*.acquisition.json')):
  a=json.load(open(p));features=[];schema=json.loads(body(a['layer_source_id']))
  for batch in a['batches']:
   d=json.loads(body(batch['source_id']));assert len(d['features'])==batch['feature_count'] and not d.get('exceededTransferLimit')
   for n,f in enumerate(d['features']):
    g=f.get('geometry');features.append({'source_locator':{'source_id':batch['source_id'],'feature_index_0based':n},'attributes':f['attributes'],'rings':g.get('rings',[]) if g else [],'original_geometry':g})
  assert len(features)==a['source_count'];assert len({f['attributes'][a['object_id_field']] for f in features})==a['source_count']
  assert set(json.loads(body(a['ids_pre_source_id']))['objectIds'])==set(json.loads(body(a['ids_post_source_id']))['objectIds'])
  epsg=a['spatial_reference'].get('latestWkid') or a['spatial_reference'].get('wkid');crs=CRS.from_epsg(epsg);units=crs.axis_info[0].unit_name
  sources[a['key']]={'features':features,'metadata':{'kind':'native ArcGIS service JSON','acquisition':p.name,'CRS':a['spatial_reference'],'axis_unit':units,'schema_fields':schema.get('fields'),'hasZ':a['hasZ'],'hasM':a['hasM'],'supportsTrueCurve':a.get('supportsTrueCurve'),'source_editingInfo':a['pre_editingInfo'],'dateFieldsTimeReference':schema.get('dateFieldsTimeReference'),'original_sources':[b['source_id'] for b in a['batches']]}}
 for key,folder in [('lee-kml','County Precincts'),('polk-kml','Precincts 2026'),('collier-kml','Precinct Boundaries')]:
  features,meta=kml_source(key,folder);meta.update(kind='officially linked Google My Maps KMZ export',axis_unit='degree',CRS='KML WGS84 longitude/latitude',original_sources=[key],precision_limit='Exact exported KML text retained. Upstream Google conversion precision/generalization and original county database precision not established.');sources[key]={'features':features,'metadata':meta}
 for key,county in [('hillsborough-shp-alt',None),('duval-census2020-vtd','031')]:
  features,meta=shp_source(key,county);meta.update(kind='original ZIP shapefile',axis_unit=CRS.from_wkt(meta['prj']).axis_info[0].unit_name,original_sources=[key]);sources[key]={'features':features,'metadata':meta}
 d=json.loads(body('st-lucie-geojson'));features=[]
 for n,f in enumerate(d['features']):
  g=f.get('geometry');rings=[]
  if g and g['type']=='Polygon':rings=g['coordinates']
  elif g and g['type']=='MultiPolygon':rings=[r for p in g['coordinates'] for r in p]
  features.append({'source_locator':{'source_id':'st-lucie-geojson','feature_index_0based':n},'attributes':f.get('properties'),'rings':rings,'original_geometry':g,'source_feature_id':f.get('id')})
 sources['st-lucie-geojson']={'features':features,'metadata':{'kind':'officially linked Dolphmap display GeoJSON','CRS':'GeoJSON WGS84 longitude/latitude','axis_unit':'degree','original_sources':['st-lucie-geojson'],'precision_limit':'Display asset: county native geometry precision, generalization tolerance, effective date, Z/M and upstream attribute completeness not established.'}}
 return sources

def rings_geom(rings):
 # Diagnostics use containment nesting of unmodified XY rings; never a geometry repair.
 polys=[Polygon([(p[0],p[1]) for p in r]) for r in rings]
 bad=[{'ring_index_0based':i,'reason':explain_validity(p)} for i,p in enumerate(polys) if not p.is_valid]
 if bad:return None,'invalid source rings: '+json.dumps(bad)
 depth=[]
 for i,p in enumerate(polys):depth.append(sum(q.area>p.area and q.covers(p.representative_point()) for j,q in enumerate(polys) if i!=j))
 outer=[]
 for i,p in enumerate(polys):
  if depth[i]%2:continue
  holes=[list(q.exterior.coords) for j,q in enumerate(polys) if depth[j]==depth[i]+1 and p.covers(q.representative_point())]
  outer.append(Polygon(list(p.exterior.coords),holes))
 g=outer[0] if len(outer)==1 else MultiPolygon(outer)
 return g,None

def preview(key,features,title):
 points=[p for f in features for r in f['rings'] for p in r if len(p)>1 and all(math.isfinite(v) for v in p[:2])];assert points
 xs=[p[0] for p in points];ys=[p[1] for p in points];xmin,xmax,ymin,ymax=min(xs),max(xs),min(ys),max(ys)
 curves=sum(bool(f.get('original_geometry') and 'curveRings' in f['original_geometry']) for f in features)
 if curves:title+=f' (linear preview; {curves} curved features retained separately)'
 w,h=900,720;margin=35;s=min((w-2*margin)/(xmax-xmin),(h-100)/(ymax-ymin));ox=(w-s*(xmax-xmin))/2;oy=70+(h-100-s*(ymax-ymin))/2
 paths=[];img=Image.new('RGB',(w,h),'#f6f7f9');draw=ImageDraw.Draw(img);draw.text((24,18),title,fill='#172435');draw.text((24,39),'Research preview · source coordinates retained in originals · no results join',fill='#40536b')
 for f in features:
  cmds=[]
  for r in f['rings']:
   xy=[(ox+(p[0]-xmin)*s,oy+(ymax-p[1])*s) for p in r]
   if len(xy)>1:draw.line(xy,fill='#285b7d',width=1)
   cmds.append('M'+'L'.join(f'{x:.2f},{y:.2f}' for x,y in xy)+'Z')
  if cmds:paths.append('<path d="'+' '.join(cmds)+'"/>')
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"><title>{html.escape(title)}</title><rect width="100%" height="100%" fill="#f6f7f9"/><text x="24" y="27" font-family="sans-serif" font-size="18">{html.escape(title)}</text><text x="24" y="49" font-family="sans-serif" font-size="12">Research preview; original coordinates and attributes remain in native downloads.</text><g fill="none" stroke="#285b7d" stroke-width="0.65">'+''.join(paths)+'</g></svg>'
 p=ROOT/'previews'/f'{key}.svg';p.write_text(svg);img.save(ROOT/'previews'/f'{key}.png')
 return {'SVG':str(p.relative_to(ROOT)),'PNG':f'previews/{key}.png','linear_preview_coordinate_bounds':[xmin,ymin,xmax,ymax],'linear_vertex_count':len(points),'curved_features_not_approximated':curves,'preview_feature_count':sum(bool(f['rings']) for f in features),'display_only':'All XY vertices transformed to panel. SVG positions rounded to 0.01 pixel; PNG rasterized. Native source bytes/attributes unchanged. Outline only, no inferred legal outline/basemap.'}

def analyze(sources):
 results={}
 for key,src in sources.items():
  features=src['features'];details=[];geoms=[];geomidx=[];counts=collections.Counter();bounds=[]
  for i,f in enumerate(features):
   rings=f['rings'];pts=[p for r in rings for p in r];defects=[]
   curve=bool(f.get('original_geometry') and any(k in f['original_geometry'] for k in ['curveRings','curvePaths']))
   if curve:defects.append('native true curve geometry: linear-ring preview not complete')
   if not pts and not curve:defects.append('empty or absent geometry');counts['empty_geometries']+=1
   if f.get('original_geometry',{}) is None:counts['null_geometries']+=1
   if any(len(p)<2 or not all(isinstance(v,(int,float)) and math.isfinite(v) for v in p[:2]) for p in pts):defects.append('nonfinite_or_nonnumeric_XY')
   if any(len(r)<4 or r[0][:2]!=r[-1][:2] for r in rings):defects.append('unclosed_or_short_ring')
   counts['curve_geometries']+=curve;counts['vertices']+=len(pts)
   g=None;reason=None
   if not defects:
    try:
     g,reason=rings_geom(rings)
     if g is not None and not g.is_valid:reason=explain_validity(g)
     if g is not None and g.is_empty:reason='empty GEOS geometry'
    except Exception as e:reason=repr(e)
    if reason:defects.append(reason);counts['GEOS_invalid_or_uninterpretable']+=1
   if g is not None and g.is_valid and not g.is_empty:geoms.append(g);geomidx.append(i)
   if pts and not any('nonfinite' in d for d in defects):bounds.append([min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)])
   details.append({'feature_index_0based':i,'source_locator':f['source_locator'],'attributes':f['attributes'],'attributes_sha256':sha(canonical(f['attributes'])),'geometry_sha256':sha(canonical(f.get('original_geometry',{'rings':rings,'z':f.get('z'),'m':f.get('m')}))),'vertex_count':len(pts),'ordinate_dimensions':sorted({len(p) for p in pts}),'ring_count':len(rings),'defects':defects,'diagnostic_XY_area':g.area if g is not None else None})
  overlaps=[]
  if geoms:
   tree=STRtree(geoms)
   for i,g in enumerate(geoms):
    for j0 in tree.query(g):
     j=int(j0)
     if j<=i:continue
     try:area=g.intersection(geoms[j]).area
     except Exception as e:overlaps.append({'feature_a':geomidx[i],'feature_b':geomidx[j],'error':repr(e)});continue
     if area>0:overlaps.append({'feature_a':geomidx[i],'feature_b':geomidx[j],'intersection_area':area})
  counts['positive_area_overlap_pairs']=sum('intersection_area' in x for x in overlaps);counts['overlap_eligible_valid_features']=len(geoms)
  # All source field values stay visible; identifier diagnostics do not create joins.
  attrs=[f['attributes'] or {} for f in features];fields=sorted(set(k for a in attrs for k in a));field_diag={}
  for field in fields:
   values=[a.get(field) for a in attrs];freq=collections.Counter(json.dumps(v,ensure_ascii=False,sort_keys=True,default=str) for v in values)
   field_diag[field]={'null':sum(v is None for v in values),'blank_string':sum(isinstance(v,str) and not v.strip() for v in values),'distinct_values_including_null':len(freq),'duplicate_values':[{'value':json.loads(v),'features':n} for v,n in freq.items() if n>1]}
  meta=src['metadata'];meta.update(feature_count=len(features),counts=dict(counts),field_diagnostics=field_diag,geometry_interpretation='Containment depth nesting of unmodified XY rings for diagnostics only; original rings, orientation, attrs, coordinates and Z/M remain untouched. No validity repair. Source invalid rings excluded from overlap calculations and explicitly listed. Positive overlaps include arbitrarily small numerical slivers, in native axis units squared. No unseen legal county outline, completeness-of-land, or gap/adjacency certification.')
  pr=preview(key,features,key+f' · {len(features)} source features');meta['preview']=pr
  dump('geometry/'+key+'.json',{'source_metadata':meta,'all_features':details,'all_positive_area_overlap_pairs':overlaps,'exact_XY_ring_duplicate_groups':[v for v in (lambda groups:groups.values())(__import__('functools').reduce(lambda a,iv:(a.setdefault(sha(canonical(iv[1]['rings'])),[]).append(iv[0]) or a),enumerate(features),{})) if len(v)>1]});results[key]=meta
 dump('geometry-summary.json',{'shapely_version':shapely.__version__,'GEOS_version':shapely.geos_version_string,'sources':results});return results

def main():
 d,counts=frozen();sources=native_sources();summary=analyze(sources);dump('build-state.json',{'all67':67,'ordered22':d['ordered_priority_keys'],'native23532':23532,'source_layer_count':len(summary),'all_geometries_preserved':True,'no_crosswalk_or_vote_allocation':True})
 print(json.dumps({k:{'features':v['feature_count'],**v['counts']} for k,v in summary.items()},indent=2))
if __name__=='__main__':main()
