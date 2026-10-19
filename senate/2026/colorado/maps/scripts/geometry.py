"""Exact native binary audit; source bytes never repaired or rewritten."""
import collections,gzip,hashlib,io,json,pathlib,struct,zipfile,warnings
import shapefile
from acquire import ROOT,body,sha

def constructor_probe():
 points=[(0.,0.),(2.,0.),(0.,2.)];parts=[0]
 a=shapefile.Shape(shapeType=5,points=points,parts=parts)
 b=shapefile.Shape(shapeType=5,lines=[points])
 result=dict(version=shapefile.__version__,points_parts_preserved=list(a.points)==points and list(a.parts)==parts,lines_autocloses=len(b.points)==4 and b.points[0]==b.points[-1],tested_input=points,points_parts_result=list(a.points),lines_result=list(b.points),adapter='points/parts only; never lines')
 assert result['points_parts_preserved'] and result['lines_autocloses'];return json.loads(json.dumps(result))

def zip_shapes(key):
 z=zipfile.ZipFile(io.BytesIO(body(key)));assert z.testzip() is None
 for n in z.namelist():
  if n.lower().endswith('.shp'):
   prefix=n[:-4];files={x.rsplit('.',1)[-1].lower():z.read(x) for x in z.namelist() if x[:-4]==prefix}
   if 'shx'in files and 'dbf'in files:yield n,files

def audit_shp(key,name,f):
 shp,shx,dbf=f['shp'],f['shx'],f['dbf'];r=shapefile.Reader(shp=io.BytesIO(shp),shx=io.BytesIO(shx),dbf=io.BytesIO(dbf),encoding='utf-8')
 assert struct.unpack('>i',shp[:4])[0]==9994
 assert struct.unpack('>i',shp[24:28])[0]*2==len(shp)
 assert struct.unpack('>i',shx[24:28])[0]*2==len(shx)
 assert shp[:24]==shx[:24] and shp[28:100]==shx[28:100]
 typ=struct.unpack('<i',shp[32:36])[0];bbox=list(struct.unpack('<4d',shp[36:68]));assert list(r.bbox)==bbox
 num,header,rowlen=struct.unpack('<IHH',dbf[4:12]);assert num==len(r)==(len(shx)-100)//8
 desc=[]
 for i in range(32,header-1,32):
  x=dbf[i:i+32];desc.append([x[:11].split(b'\0')[0].decode(),chr(x[11]),x[16],x[17]])
 assert [list(x) for x in r.fields[1:]]==desc
 assert len(dbf)>=header+num*rowlen
 checks=8;xy=parts_total=0;rows=[];features=[]
 for i,s in enumerate(r.iterShapes()):
  off,words=struct.unpack('>II',shx[100+i*8:108+i*8]);off*=2;length=words*2
  recnum,reclen=struct.unpack('>II',shp[off:off+8]);assert recnum==i+1 and reclen==words
  b=shp[off+8:off+8+length];t=struct.unpack('<i',b[:4])[0];assert t==s.shapeType;checks+=3
  record=dbf[header+i*rowlen:header+(i+1)*rowlen];assert len(record)==rowlen
  raw_values=[];pos=1
  for fld in desc:raw_values.append(record[pos:pos+fld[2]].hex());pos+=fld[2]
  assert pos==rowlen;checks+=1
  entry=dict(record=i+1,shp_offset_bytes=off,content_bytes=length,shx_offset_words=off//2,shape_type=t,dbf_deleted_byte=record[0],dbf_field_raw_hex=raw_values)
  if t in [5,15,25,3,13,23]:
   bb=list(struct.unpack('<4d',b[4:36]));np,npts=struct.unpack('<II',b[36:44]);partlist=list(struct.unpack('<'+'I'*np,b[44:44+4*np]));start=44+4*np
   pts=[struct.unpack('<dd',b[start+j*16:start+(j+1)*16]) for j in range(npts)]
   assert partlist==list(s.parts) and bb==list(s.bbox) and len(s.points)==npts;checks+=3
   for a,c in zip(pts,s.points):assert struct.pack('<dd',*a)==struct.pack('<dd',*c);checks+=2
   # Raw double bitstream hash includes every ordinate and source order.
   entry.update(parts=np,points=npts,bbox=bb,xy_double_sha256=sha(b[start:start+16*npts]),parts_sha256=sha(b[44:start]))
   adapter=shapefile.Shape(shapeType=t,points=pts,parts=partlist)
   assert list(adapter.points)==list(s.points) and list(adapter.parts)==list(s.parts);checks+=1
   xy+=npts;parts_total+=np
  elif t==0:entry.update(parts=0,points=0)
  else:raise AssertionError(('unsupported native type retained',key,t))
  rows.append(entry);features.append((s,r.record(i).as_dict()))
 # Every DBF value is retained as raw field bytes and interpreted attributes remain available from unmodified DBF.
 return dict(source=key,member=name,shape_type=typ,feature_count=num,bbox=bbox,fields=desc,crs_wkt=f.get('prj',b'').decode(errors='replace'),encoding_sidecar=f.get('cpg',b'').decode(errors='replace'),xy_points=xy,parts=parts_total,checks=checks,records=rows,zip_crc_verified=True,members=[dict(extension=k,bytes=len(v),sha256=sha(v)) for k,v in f.items()]),features

def topology(features,crs):
 from shapely.geometry import shape,Polygon
 from shapely.strtree import STRtree
 from shapely.validation import explain_validity
 import shapely
 valid=[];sourceindices=[];defects=[];openrings=0;orphan_holes=[];ring_diagnostics=[]
 for i,(s,attrs) in enumerate(features):
  if s.shapeType==0:defects.append(dict(index=i,issue='null shape'));continue
  for a,b in zip(list(s.parts),list(s.parts)[1:]+[len(s.points)]):
   if s.points[a]!=s.points[b-1]:openrings+=1;defects.append(dict(index=i,issue='open ring; no repair'))
  rings=[s.points[a:b] for a,b in zip(list(s.parts),list(s.parts)[1:]+[len(s.points)])]
  signed=[sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(ring,ring[1:]))/2 for ring in rings]
  outers=[Polygon(rings[j]) for j,area in enumerate(signed) if area<0 and len(rings[j])>=4]
  inner_indices=[j for j,area in enumerate(signed) if area>0]
  for j in inner_indices:
   if len(rings[j])>=4:
    hole=Polygon(rings[j])
    if not any(g.is_valid and hole.is_valid and g.covers(hole) for g in outers):orphan_holes.append(dict(source_index=i,part=j,issue='counterclockwise ring has no containing clockwise exterior; retained unchanged'))
  ring_diagnostics.append(dict(source_index=i,clockwise_exterior_parts=sum(x<0 for x in signed),counterclockwise_interior_parts=len(inner_indices),zero_signed_area_parts=[j for j,x in enumerate(signed) if x==0]))
  if any(x['source_index']==i for x in orphan_holes):defects.append(dict(index=i,issue='orphan interior ring; excluded from topology without repair'));continue
  try:
   with warnings.catch_warnings():warnings.simplefilter('ignore');g=shape(s.__geo_interface__)
   if g.is_empty or not g.is_valid:defects.append(dict(index=i,issue=explain_validity(g),empty=g.is_empty))
   else:valid.append(g);sourceindices.append(i)
  except Exception as e:defects.append(dict(index=i,issue=repr(e)))
 overlaps=[]
 if valid:
  tree=STRtree(valid)
  for i,g in enumerate(valid):
   for jj in tree.query(g):
    j=int(jj)
    if j<=i:continue
    area=g.intersection(valid[j]).area
    if area>0:overlaps.append(dict(left_source_index=sourceindices[i],right_source_index=sourceindices[j],positive_intersection_area_native_units=area))
 return dict(linear_source_index_to_complete_attributes=[dict(source_index=i,attributes=attrs) for i,(shape,attrs) in enumerate(features)],ring_diagnostics=ring_diagnostics,orphan_holes=orphan_holes,library=shapely.__version__,crs=crs,units='native CRS coordinate units squared, separate from preview pixel units',linear_only=True,true_curves_excluded=True,valid_linear_features=len(valid),open_rings=openrings,defects=defects,positive_area_overlaps=overlaps,legal_gap_sliver_overlap_certification=False,qualification='diagnostic only; invalid/null/open geometries retained and excluded from positive-area valid-feature intersection; no same-vintage legal outline acquired')

def run():
 probe=constructor_probe();audits=[];top=[];collections={}
 for key in ['census-co-vtd','county-fremont-map-1-asset-1']:
  for name,f in zip_shapes(key):
   a,features=audit_shp(key,name,f);audits.append(a);collections[key]=features
   top.append(dict(source=key,**topology(features,a['crs_wkt'])))
 return dict(constructor_probe=probe,audits=audits),top,collections
if __name__=='__main__':
 a,t,c=run();(ROOT/'qa/binary-geometry-audit.json').write_text(json.dumps(a,indent=2)+'\n');(ROOT/'qa/topology.json').write_text(json.dumps(t,indent=2)+'\n');print([(x['source'],x['feature_count'],x['xy_points']) for x in a['audits']])
