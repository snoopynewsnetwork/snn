"""Offline read-only geometry diagnostics and preview extraction; originals never changed."""
import collections,gzip,hashlib,io,json,math,struct,zipfile
import shapefile,shapely
from shapely.geometry import Polygon,MultiPolygon
from shapely.validation import explain_validity
from shapely.strtree import STRtree
from pyproj import CRS,Transformer
from acquire import ROOT,read

def load_records(records,services):
 out={};archives={}
 for s in services:
  features=[];sr=None
  for key in s['pages']:
   j=json.loads(read(records[key]));features+=j['features'];sr=j.get('spatialReference',sr)
  out[s['id']]={'features':features,'spatial_reference':sr or s['native_crs'],'source_type':'Esri JSON','metadata':s}
 for key in ['johnson-shp','sedgwick-shp','leavenworth-shp']:
  if key not in records:continue
  b=read(records[key])
  if not b.startswith(b'PK'):continue
  z=zipfile.ZipFile(io.BytesIO(b));assert z.testzip() is None
  members=[{'name':x.filename,'uncompressed_bytes':x.file_size,'compressed_bytes':x.compress_size,'crc32':f'{x.CRC:08x}','sha256':hashlib.sha256(z.read(x.filename)).hexdigest()} for x in z.infolist()]
  archives[key]={'members':members,'zip_crc':'all members pass','layers':[]}
  for shp in [x for x in z.namelist() if x.lower().endswith('.shp')]:
   stem=shp[:-4];match=lambda ext:next(x for x in z.namelist() if x.lower()==(stem+ext).lower())
   bb={ext:z.read(match(ext)) for ext in ['.shp','.shx','.dbf']}
   reader=shapefile.Reader(shp=io.BytesIO(bb['.shp']),shx=io.BytesIO(bb['.shx']),dbf=io.BytesIO(bb['.dbf']))
   rawcount=0;pos=100;offsets=[]
   while pos<len(bb['.shp']):
    num,words=struct.unpack('>ii',bb['.shp'][pos:pos+8]);offsets.append((pos//2,words));pos+=8+words*2;rawcount+=1
   shxcount=(len(bb['.shx'])-100)//8;dbfcount=struct.unpack('<I',bb['.dbf'][4:8])[0]
   idx=[struct.unpack('>ii',bb['.shx'][p:p+8]) for p in range(100,len(bb['.shx']),8)]
   assert rawcount==shxcount==dbfcount==len(reader) and offsets==idx and pos==len(bb['.shp'])
   prj=z.read(match('.prj')).decode('utf8','replace')
   rows=[];zvals=[];mvals=[];types=collections.Counter()
   for n,record in enumerate(reader.iterShapeRecords()):
    shape=record.shape;types[shape.shapeType]+=1;attrs=record.record.as_dict()
    ends=list(shape.parts)+[len(shape.points)]
    rings=[[[float(v) for v in xy] for xy in shape.points[a:b]] for a,b in zip(ends,ends[1:])]
    geom=None if shape.shapeType==0 else {'rings':rings}
    # Native Z/M values remain byte-for-byte in SHP; diagnostics retain their ranges and null/sentinel counts.
    zz=list(getattr(shape,'z',[]));mm=list(getattr(shape,'m',[]));zvals+=zz;mvals+=mm
    rows.append({'attributes':dict(_record_index=n,**attrs),'geometry':geom,'diagnostic_z':zz,'diagnostic_m':mm})
   def numbers(v):
    f=[x for x in v if x is not None and math.isfinite(x)];return {'values':len(v),'null':sum(x is None for x in v),'nonfinite':sum(x is not None and not math.isfinite(x) for x in v),'range':[min(f),max(f)] if f else None,'shapefile_no_data_sentinel':sum(x is not None and x < -1e38 for x in v)}
   dbf_header_len=struct.unpack('<H',bb['.dbf'][8:10])[0];dbf_record_len=struct.unpack('<H',bb['.dbf'][10:12])[0]
   deleted=[n for n in range(dbfcount) if bb['.dbf'][dbf_header_len+n*dbf_record_len:dbf_header_len+n*dbf_record_len+1]==b'*']
   info={'deleted_dbf_record_indices':deleted,'parsed_feature_records':len(rows),'stem':stem,'shp_records':rawcount,'shx_records':shxcount,'dbf_records':dbfcount,'shx_offsets_match_shp':True,'shape_types':dict(types),'fields':[list(x) for x in reader.fields],'crs_wkt':prj,'header_bbox':list(reader.bbox),'z':numbers(zvals),'m':numbers(mvals)}
   archives[key]['layers'].append(info)
   out[key]={'features':rows,'spatial_reference':{'wkt':prj},'source_type':'SHP native record diagnostic','metadata':info}
 return out,archives

def as_crs(sr):
 if 'wkt'in sr:return CRS.from_wkt(sr['wkt'])
 code=sr.get('latestWkid',sr.get('wkid'))
 try:return CRS.from_epsg(code)
 except:return CRS.from_user_input('ESRI:'+str(code))

def diagnostic(data):
 rows=data['features'];sr=data['spatial_reference'];crs=as_crs(sr)
 units=crs.axis_info[0].unit_name if crs.axis_info else 'unknown'
 result={'features':len(rows),'native_spatial_reference':sr,'interpreted_crs_wkt':crs.to_wkt(),'axis_info':[{'name':a.name,'direction':a.direction,'unit':a.unit_name,'conversion_factor':a.unit_conversion_factor} for a in crs.axis_info],'preview_axis_policy':'source x/y fitted to image; geographic XY uses longitude then latitude, no EPSG axis-order rewrite','area_units':units+' squared; Cartesian diagnostic, not geodesic area','null_geometry':[],'missing_geometry':[],'explicit_null_geometry':[],'empty_geometry':[],'nonfinite':[],'invalid':[],'curve_geometry':[],'orphan_holes':[],'vertices':0,'rings':0,'z_coordinate_positions':0,'m_coordinate_positions':0,'extent':None,'valid_pair_overlap':[],'overlap_skipped_invalid_or_missing':0,'attributes':[]}
 geoms=[];idents=[];bbox=[math.inf,math.inf,-math.inf,-math.inf]
 for n,f in enumerate(rows):
  attr=f['attributes'];ident=attr.get('OBJECTID',attr.get('objectid',attr.get('FID',attr.get('_record_index',n))))
  result['attributes'].append({'row':n,'id':ident,'attributes':attr})
  g=f.get('geometry')
  if g is None:
   result['null_geometry'].append(ident)
   result['missing_geometry' if 'geometry' not in f else 'explicit_null_geometry'].append(ident)
   continue
  if not g:result['empty_geometry'].append(ident);continue
  if 'curveRings'in g:result['curve_geometry'].append(ident);continue
  rings=g.get('rings',[]);result['rings']+=len(rings)
  bad=False
  for ring in rings:
   for xy in ring:
    result['vertices']+=1
    if len(xy)>=3:result['z_coordinate_positions']+=1
    if len(xy)>=4:result['m_coordinate_positions']+=1
    if not all(isinstance(v,(int,float)) and math.isfinite(v) for v in xy[:2]):bad=True;continue
    bbox=[min(bbox[0],xy[0]),min(bbox[1],xy[1]),max(bbox[2],xy[0]),max(bbox[3],xy[1])]
  if bad:result['nonfinite'].append(ident);continue
  try:
   # GEOS validity and intersections are explicitly XY-only derivatives.
   # Z/M (including null M) stay untouched in native original pages.
   planar_rings=[[[xy[0],xy[1]] for xy in ring] for ring in rings]
   shell=[];holes=[]
   for ring in planar_rings:
    area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ring,ring[1:]))/2
    if area<=0:shell.append((ring,[]))
    else:holes.append(ring)
   if not shell and holes:
    result['orphan_holes'].append({'id':ident,'reason':'No clockwise shell; diagnostic treats rings as shells without changing originals'});shell=[(x,[]) for x in holes];holes=[]
   for hole in holes:
    candidates=[i for i,(s,h) in enumerate(shell) if Polygon(s).covers(Polygon(hole).representative_point())]
    if not candidates:
     result['orphan_holes'].append({'id':ident,'reason':'Counterclockwise ring outside shell'});shell.append((hole,[]))
    else:shell[min(candidates,key=lambda i:Polygon(shell[i][0]).area)][1].append(hole)
   polys=[Polygon(s,h) for s,h in shell];geom=polys[0] if len(polys)==1 else MultiPolygon(polys)
   if not geom.is_valid:result['invalid'].append({'id':ident,'reason':explain_validity(geom)})
   elif geom.is_empty:result['empty_geometry'].append(ident)
   else:geoms.append(geom);idents.append(ident)
  except Exception as e:result['invalid'].append({'id':ident,'reason':str(e)})
 if math.isfinite(bbox[0]):result['extent']=bbox
 result['overlap_skipped_invalid_or_missing']=len(rows)-len(geoms)
 if geoms:
  tree=STRtree(geoms)
  for i,g in enumerate(geoms):
   for jj in tree.query(g):
    j=int(jj)
    if j<=i:continue
    area=g.intersection(geoms[j]).area
    if area>0:result['valid_pair_overlap'].append({'id_a':idents[i],'id_b':idents[j],'intersection_area':area})
 result['planar_diagnostic_policy']='GEOS operates on XY-only copies; no original Z/M or geometry is modified. True curves are enumerated and excluded from GEOS, never silently linearized.'
 result['overlap_policy']='Every positive Cartesian intersection area between valid polygons, no tolerance cutoff; touching edges area0 not overlap. Invalid/null/curve geometries excluded from overlap calculation; no buffer/snap/make_valid/repair.'
 result['software']={'shapely':shapely.__version__,'GEOS':shapely.geos_version_string,'pyshp':shapefile.__version__}
 return result
