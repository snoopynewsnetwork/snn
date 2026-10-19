#!/usr/bin/env python3
"""Independent binary/attribute/native geometry audit; previews never replace originals."""
import base64,collections,gzip,html,inspect,io,json,math,pathlib,re,struct,zipfile,zlib
import shapefile
from shapely.geometry import Polygon,MultiPolygon,Point,LinearRing
from shapely.validation import explain_validity
from shapely.strtree import STRtree
from acquire import ROOT,STATE,sha,save_json,body
PREP='data/coordinator-map-preparation/acquisition-native-stage-v1.json'
PREP_PIN=None # pinned in source-references.json, not a mutable acquisition journal

def prep():
 rows=json.loads((STATE/PREP).read_bytes());assert len(rows)==38
 for x in rows:
  b=(STATE/x['asset_path']).read_bytes();assert len(b)==x['stored_bytes'] and sha(b)==x['stored_sha256']
  raw=gzip.decompress(b);assert len(raw)==x['raw_bytes'] and sha(raw)==x['raw_sha256']
 return rows

def raw(x):return body(x) if 'storage' in x else gzip.decompress((STATE/x['asset_path']).read_bytes())
def write_gz(p,j):
 b=gzip.compress((json.dumps(j,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode(),mtime=0);assert len(b)<40_000_000;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
def fingerprint(v):return sha(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def signed(r):return sum((b[0]-a[0])*(b[1]+a[1]) for a,b in zip(r,r[1:]))/2
# signed() positive = clockwise. Native ESRI polygon shells clockwise, holes counterclockwise.
def topology(features,unit):
 issues=[];geoms=[];ids=[];rings_total=0;positions=0;curves=0;nulls=0;empties=0;openrings=[];orphan=[]
 for f in features:
  id=f['source_position'];g=f.get('geometry')
  if g is None:nulls+=1;continue
  if 'curveRings' in g:curves+=1;continue # native curves retained; no linear approximation masquerades as original
  rings=g.get('rings',[]);rings_total+=len(rings);positions+=sum(map(len,rings))
  if not rings:empties+=1;continue
  outers=[];holes=[]
  for i,r in enumerate(rings):
   if len(r)<4 or r[0]!=r[-1]:openrings.append({'source_position':id,'ring':i,'positions':len(r),'closed_exactly':bool(r and r[0]==r[-1])});continue
   assert all(math.isfinite(v) for xy in r for v in xy[:2])
   (outers if signed(r)>0 else holes).append((i,r))
  assigned={i:[] for i,_ in outers}
  for i,r in holes:
   candidates=[(Polygon(o).area,j) for j,o in outers if Polygon(o).covers(Point(r[0][:2]))]
   if not candidates:orphan.append({'source_position':id,'ring':i});continue
   assigned[min(candidates)[1]].append(r)
  polys=[Polygon(r,assigned[i]) for i,r in outers]
  if not polys:issues.append({'source_position':id,'reason':'No validly closed clockwise shell; diagnostic geometry unavailable'});continue
  g=MultiPolygon(polys) if len(polys)>1 else polys[0]
  if not g.is_valid:issues.append({'source_position':id,'reason':explain_validity(g)})
  geoms.append(g);ids.append(id)
 overlaps=[];errors=[]
 valid=[(i,g) for i,g in enumerate(geoms) if g.is_valid and not g.is_empty];tree=STRtree([g for _,g in valid])
 for n,(i,g) in enumerate(valid):
  for m in tree.query(g,predicate='intersects'):
   if int(m)<=n:continue
   j,h=valid[int(m)]
   try:
    area=g.intersection(h).area
    if area>0:overlaps.append({'a':ids[i],'b':ids[j],'area':area,'units':unit+' squared'})
   except Exception as e:errors.append({'a':ids[i],'b':ids[j],'error':str(e)})
 return {'features':len(features),'native_rings':rings_total,'native_positions':positions,'native_coordinate_units':unit,'null_geometries':nulls,'empty_geometries':empties,'curve_geometry_not_linearized':curves,'open_or_short_rings':openrings,'orphan_counterclockwise_rings':orphan,'invalid_geometry_diagnostics':issues,'positive_area_overlaps_valid_features_only':overlaps,'intersection_errors':errors,'legal_gap_or_overlap_certification':False,'scope':'Unrepaired diagnostic construction from exact closed native rings and source winding. Invalid features excluded only from pairwise overlap diagnostics, never from stored originals/inventory. No same-vintage legal outline; no gap certification.'}

def svg(path,features,title,units):
 rings=[r for f in features for r in (f.get('geometry') or {}).get('rings',[])];pts=[xy for r in rings for xy in r]
 if not pts:return
 xmin=min(p[0] for p in pts);xmax=max(p[0] for p in pts);ymin=min(p[1] for p in pts);ymax=max(p[1] for p in pts);s=min(920/(xmax-xmin or 1),620/(ymax-ymin or 1))
 out=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="740" viewBox="0 0 1000 740">','<rect width="1000" height="740" fill="#f7f7f2"/>',f'<text x="30" y="30" font-family="sans-serif" font-size="20">{html.escape(title)}</text>',f'<text x="30" y="54" font-family="sans-serif" font-size="12">Native XY display; {html.escape(units)}. Research derivative; no crosswalk/current approval.</text>']
 for f in features:
  rr=(f.get('geometry') or {}).get('rings',[]);d=' '.join('M'+' L'.join(f'{30+(p[0]-xmin)*s:.3f},{690-(p[1]-ymin)*s:.3f}' for p in ring)+' Z' for ring in rr if ring)
  out.append(f'<path d="{d}" fill="#dee9ed" fill-rule="evenodd" stroke="#2a535d" stroke-width="0.6"><title>{html.escape(str(f.get("attributes",{})))}</title></path>')
 out.append('<text x="30" y="725" font-family="sans-serif" font-size="12">Display fits native axes independently per map; 0.001 SVG units rounding only. Original positions remain exact.</text></svg>');path.parent.mkdir(parents=True,exist_ok=True);path.write_text('\n'.join(out))

def service(rows,prefix):
 rr={x['id']:x for x in rows};get=lambda tail:json.loads(raw(rr[prefix+'-native-layer-'+tail]));meta=get('metadata');assert meta==get('metadata-post');count=get('count-pre')['count'];assert count==get('count-post')['count'];ids=get('ids-pre');assert ids==get('ids-post');idfield=ids['objectIdFieldName'];allids=ids['objectIds'];features=[];pages=[]
 for x in rows:
  if x['id'].startswith(prefix+'-native-layer-native-page-'):
   q=x['native_query_parameters'];assert q['outFields']=='*' and all(q[k]=='true' for k in ['returnGeometry','returnZ','returnM','returnTrueCurves']);assert not any(k.lower() in ['outsr','geometryprecision','quantizationparameters','maxallowableoffset'] for k in q)
   asked=x['requested_object_ids'];assert len(asked)<=50;j=json.loads(raw(x));assert not j.get('error') and not j.get('exceededTransferLimit');fs=j['features'];assert sorted(f['attributes'][idfield] for f in fs)==sorted(asked)
   pages.append({'receipt_id':x['id'],'requested_ids':asked,'returned_ids':[f['attributes'][idfield] for f in fs],'all_original_fields_present':all(set(z['name'] for z in j['fields'])==set(f['attributes']) for f in fs),'metadata_to_page_literal_field_difference':{'metadata_only':sorted(set(z['name'] for z in meta['fields'])-set(z['name'] for z in j['fields'])),'page_only':sorted(set(z['name'] for z in j['fields'])-set(z['name'] for z in meta['fields']))},'original_page_fields':list(j),'original_spatial_reference':j.get('spatialReference')})
   for f in fs:features.append({'source_position':f['attributes'][idfield],**f})
 assert len(features)==count==len(allids) and len(set(allids))==len(allids);assert sorted(f['attributes'][idfield] for f in features)==sorted(allids)
 assert all(p['all_original_fields_present'] for p in pages)
 out={'source':prefix,'metadata':meta,'features':features,'native_preservation':'All original response pages and lexical JSON numbers remain pinned; this parsed derivative preserves every attribute/ring/coordinate/curve object. IDs publication local.'}
 write_gz(ROOT/'native'/f'{prefix}.json.gz',out);unit={'douglas':'US survey feet','adams':'metres (ESRI:53004 Sphere_Mercator)','scottsbluff':'US survey feet (NAD83(2011) Nebraska EPSG6880)'}.get(prefix,'metres (Web Mercator projected)');diag=topology(features,unit);diag.update({'pre_post_metadata_exact':True,'pre_post_counts_exact':True,'pre_post_ids_exact':True,'complete_allID_membership':True,'ID_field':idfield,'allIDs':allids,'pages':pages,'native_CRS':meta['extent']['spatialReference'],'source_last_edit_metadata':meta.get('editingInfo'),'field_names':[f['name'] for f in meta['fields']],'attributes_and_geometry_fingerprint':fingerprint(features),'count_is_reporting_crosswalk':False})
 save_json(ROOT/'qa'/f'{prefix}-native.json',diag);svg(ROOT/'previews'/f'{prefix}-native.svg',features,prefix.title()+' native service - '+str(count)+' features',unit)
 return out

def census(rows):
 source=next(x for x in rows if x['id']=='census-nebraska-vtd20');b=raw(source);assert len(b)==3294509 and sha(b)=='2d22bbc8fcd115105fec245ba212dcfc134625a31287f87a5eb91c73d7a9f564';z=zipfile.ZipFile(io.BytesIO(b));assert z.testzip() is None
 members=[{'name':n.filename,'bytes':n.file_size,'compressed_bytes':n.compress_size,'CRC32':f'{n.CRC:08x}','sha256':sha(z.read(n))} for n in z.infolist()];files={pathlib.Path(n).suffix:z.read(n) for n in z.namelist()};shp=files['.shp'];shx=files['.shx'];dbf=files['.dbf'];assert struct.unpack('>i',shp[:4])[0]==9994 and len(shp)==struct.unpack('>i',shp[24:28])[0]*2
 # Understand PyShp 3.1.6: Reader positional path OR explicit keyword binary streams. Do not pass points as old positional Shape args.
 reader=shapefile.Reader(shp=io.BytesIO(shp),shx=io.BytesIO(shx),dbf=io.BytesIO(dbf),cpg=io.BytesIO(files['.cpg']));shapes=list(reader.iterShapes());records=list(reader.iterRecords());assert len(shapes)==len(records)==1402
 # Independent SHP/SHX binary parser, exact ordered IEEE754 doubles/parts/bboxes/record positions; no topology conversion.
 pos=100;binary=[];offsets=[]
 while pos<len(shp):
  recno,length=struct.unpack('>2i',shp[pos:pos+8]);content=shp[pos+8:pos+8+2*length];typ=struct.unpack('<i',content[:4])[0];assert typ==5
  bbox=list(struct.unpack('<4d',content[4:36]));nparts,npoints=struct.unpack('<2i',content[36:44]);parts=list(struct.unpack('<'+'i'*nparts,content[44:44+4*nparts]));pointdata=content[44+4*nparts:];assert len(pointdata)==16*npoints;points=[list(x) for x in struct.iter_unpack('<2d',pointdata)];binary.append({'record_number':recno,'shape_type':typ,'parts':parts,'points':points,'bbox':bbox});offsets.append((pos//2,length));pos+=8+2*length
 assert pos==len(shp);assert offsets==list(struct.iter_unpack('>2i',shx[100:]));assert len(binary)==1402
 # Independent DBF descriptor/cell parser. Original lexical bytes retained once inside ZIP.
 nrec,hlen,rlen=struct.unpack('<IHH',dbf[4:12]);fields=[];p=32
 while dbf[p]!=13:
  d=dbf[p:p+32];fields.append({'name':d[:11].split(b'\0')[0].decode(),'type':chr(d[11]),'width':d[16],'decimals':d[17]});p+=32
 assert nrec==1402 and [(f['name'],f['type'],f['width'],f['decimals']) for f in fields]==[tuple(f) for f in reader.fields[1:]]
 features=[];counts=collections.Counter();dbfcells=0
 for i,(s,record,bn) in enumerate(zip(shapes,records,binary)):
  assert [list(x) for x in s.points]==bn['points'] and list(s.parts)==bn['parts'] and list(s.bbox)==bn['bbox']
  rr=dbf[hlen+i*rlen:hlen+(i+1)*rlen];assert rr[0]==32;at=1;attrs=record.as_dict()
  for f in fields:
   cell=rr[at:at+f['width']];at+=f['width'];text=cell.decode('utf8').strip();v=(float(text) if f['decimals'] else int(text)) if f['type']=='N' and text else text;assert v==attrs[f['name']],(i,f,v,attrs[f['name']]);dbfcells+=1
  assert at==rlen
  rings=[bn['points'][start:(bn['parts'][j+1] if j+1<len(bn['parts']) else len(bn['points']))] for j,start in enumerate(bn['parts'])];features.append({'source_position':i,'attributes':attrs,'binary_shape':bn,'geometry':{'rings':rings}});counts['31'+attrs['COUNTYFP20']]+=1
 assert sum(len(f['binary_shape']['points']) for f in features)==383061 and len(counts)==93
 write_gz(ROOT/'native/census-vtd20.json.gz',{'metadata':{'members':members,'DBF_fields':fields,'native_PRJ':files['.prj'].decode(),'native_CPG':files['.cpg'].decode()},'features':features,'source_receipt_id':source['id']})
 diag=topology(features,'degrees NAD83 (EPSG:4269)');diag.update({'members':members,'DBF_fields':fields,'county_counts':dict(sorted(counts.items())),'native_PRJ':files['.prj'].decode(),'independent_DBF_cells_checked':dbfcells,'all_shape_points_parts_bboxes_and_SHX_positions_exact':True,'PyShp_version':shapefile.__version__,'PyShp_Reader_signature':re.sub(r'0x[0-9a-f]+','0xRUNTIME',str(inspect.signature(shapefile.Reader))),'PyShp_Shape_signature':re.sub(r'0x[0-9a-f]+','0xRUNTIME',str(inspect.signature(shapefile.Shape))),'attributes_and_geometry_fingerprint':fingerprint(features)})
 save_json(ROOT/'qa/census-native.json',diag)
 for fips in sorted(counts):svg(ROOT/'previews'/f'{fips}-census-vtd20.svg',[f for f in features if '31'+f['attributes']['COUNTYFP20']==fips],fips+' Census 2020 VTD fallback - '+str(counts[fips])+' features','degrees NAD83 (EPSG:4269)')
 return features

def main():
 rows=prep();refs=[{'path':PREP,'bytes':len((STATE/PREP).read_bytes()),'sha256':sha((STATE/PREP).read_bytes()),'complete_recursive_receipts':True}]
 for x in rows:refs.append({'path':x['asset_path'],'bytes':x['stored_bytes'],'sha256':x['stored_sha256'],'original_bytes':x['raw_bytes'],'original_sha256':x['raw_sha256'],'receipt_pointer':PREP+'#/'+str(rows.index(x))})
 save_json(ROOT/'source-references.json',{'schema':'NE-map-original-references-v1','immutable_preparation_only':True,'references':refs})
 for p in ['douglas','lancaster']:o=service(rows,p);print(p,len(o['features']))
 own=[json.loads(p.read_text()) for p in (ROOT/'receipts').glob('*native-layer*.json')]
 for p in ['sarpy','adams','scottsbluff']:o=service(own,p);print(p,len(o['features']))
 fs=census(rows);print('census',len(fs))
if __name__=='__main__':main()
