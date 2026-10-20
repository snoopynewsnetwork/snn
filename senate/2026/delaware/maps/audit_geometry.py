"""Independent exact native and ZIP/DBF/SHP/SHX audits. No geometry repair.
Native ring orientation and containment used only for qualified diagnostics.
"""
from common import *
import base64,collections,inspect,io,math,struct,zipfile,zlib
import shapefile,shapely
from shapely.geometry import Polygon,MultiPolygon
from shapely.validation import explain_validity

def signed(r):return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(r,r[1:]))/2

def diagnostics(features):
 results=[];geoms=[]
 for f in features:
  a=f['attributes'];g=f.get('geometry');r=dict(id=a.get('OBJECTID'),null_geometry=g is None,empty_geometry=g=={},curve_rings='curveRings'in(g or {}),rings=[])
  if not g or 'rings'not in g:r['qualification']='Native absent/empty/curve representation retained, no linear conversion';results.append(r);continue
  shells=[];holes=[]
  for i,ring in enumerate(g['rings']):
   area=signed(ring);obs=dict(index=i,positions=len(ring),closed=bool(ring) and ring[0]==ring[-1],signed_native_area=area,finite=all(math.isfinite(v) for p in ring for v in p),coordinate_dimensions=sorted(set(map(len,ring))))
   p=Polygon(ring) if len(ring)>=4 and obs['closed'] else None
   obs['ring_valid']=p.is_valid if p is not None else False;obs['reason']=explain_validity(p) if p is not None else 'unclosed/too short; not auto-closed'
   r['rings'].append(obs)
   if p is not None:(shells if area<0 else holes).append((i,p,ring))
  assigned={i:[] for i,p,v in shells};orphan=[]
  for i,p,v in holes:
   containers=[(q.area,j) for j,q,w in shells if q.contains(p)]
   if containers:assigned[min(containers)[1]].append(v)
   else:orphan.append(i)
  r['orphan_positive_rings']=orphan
  if not orphan and shells:
   ps=[Polygon(v,assigned[i]) for i,p,v in shells];geom=ps[0] if len(ps)==1 else MultiPolygon(ps)
   r.update(valid=geom.is_valid,reason=explain_validity(geom),area_native_square_units=geom.area)
   geoms.append((a.get('OBJECTID'),geom))
  results.append(r)
 overlaps=[];touches=0
 for j,(i,g) in enumerate(geoms):
  if not g.is_valid:continue
  for k,h in geoms[j+1:]:
   if not h.is_valid:continue
   if g.intersects(h):
    x=g.intersection(h)
    if x.area>0:overlaps.append(dict(a=i,b=k,area_native_square_units=x.area))
    else:touches+=1
 return dict(shapely_version=shapely.__version__,native_units='EPSG3857 coordinate metres; area square projected metres, not ground geodesic area',ring_convention='Esri clockwise shells; positive rings are holes only if actually contained by a negative ring, orphan holes retained as defects without reinterpretation',features=results,positive_area_pair_intersections=overlaps,touching_pairs=touches,legal_boundary_coverage_certified=False,qualification='No same-vintage legal state/ED outline acquired. Intersections are numerical diagnostics only; no legal gaps/slivers/overlaps certified. Null/empty/invalid/curve native originals remain untouched.')

def audit_zip(receipt):
 raw=body(receipt);z=zipfile.ZipFile(io.BytesIO(raw));assert z.testzip() is None
 members=[]
 for info in z.infolist():
  b=z.read(info.filename);assert len(b)==info.file_size and zlib.crc32(b)&0xffffffff==info.CRC
  members.append(dict(name=info.filename,bytes=len(b),sha256=sha(b),CRC32=f'{info.CRC:08x}',compressed_bytes=info.compress_size,header_offset=info.header_offset))
 names=z.namelist();get=lambda ext:z.read(next(n for n in names if n.endswith(ext)))
 shp,shx,dbf=get('.shp'),get('.shx'),get('.dbf');prj=get('.prj').decode()
 assert struct.unpack_from('>i',shp,24)[0]*2==len(shp);assert struct.unpack_from('>i',shx,24)[0]*2==len(shx)
 assert shp[:24]==shx[:24] and shp[28:100]==shx[28:100]
 n=struct.unpack_from('<I',dbf,4)[0];hlen,rlen=struct.unpack_from('<HH',dbf,8);assert dbf[hlen-1]==13
 descriptors=[];off=1
 for pos in range(32,hlen-1,32):
  d=dbf[pos:pos+32];name=d[:11].split(b'\x00')[0].decode('ascii');length=d[16];descriptors.append(dict(name=name,type=chr(d[11]),length=length,decimal=d[17],record_offset=off,descriptor_offset=pos,raw_descriptor_hex=d.hex()));off+=length
 assert off==rlen
 reader=shapefile.Reader(shp=io.BytesIO(shp),shx=io.BytesIO(shx),dbf=io.BytesIO(dbf));assert len(reader)==n
 records=[];p=100;totalpoints=0;totalparts=0;checks=0
 for idx in range(n):
  roffset,words=struct.unpack_from('>ii',shx,100+8*idx);assert roffset*2==p
  recno,size=struct.unpack_from('>ii',shp,p);assert recno==idx+1 and size==words
  content=shp[p+8:p+8+size*2];stype=struct.unpack_from('<i',content)[0];shape=reader.shape(idx);assert stype==shape.shapeType
  entry=dict(record=idx+1,shp_record_byte_offset=p,shx_entry_byte_offset=100+8*idx,content_bytes=len(content),content_sha256=sha(content),shape_type=stype)
  if stype!=0:
   assert stype==5,('unhandled source type retained',stype)
   bbox=struct.unpack_from('<4d',content,4);np,nv=struct.unpack_from('<2i',content,36);parts=list(struct.unpack_from('<'+'i'*np,content,44));start=44+4*np
   points=[struct.unpack_from('<2d',content,start+16*j) for j in range(nv)];assert start+16*nv==len(content)
   assert list(shape.parts)==parts and len(shape.points)==nv
   # Independent raw IEEE754 comparisons: every coordinate, each bbox double.
   for j,xy in enumerate(shape.points):assert struct.pack('<2d',*xy)==content[start+16*j:start+16*j+16];checks+=2
   assert struct.pack('<4d',*shape.bbox)==content[4:36]
   # Constructor inspected before use: points/parts bypass lines auto-closure.
   adapted=shapefile.Shape(shapeType=stype,points=points,parts=parts)
   assert list(adapted.parts)==parts and adapted.points==points
   rings=[points[a:b] for a,b in zip(parts,parts[1:]+[nv])]
   entry.update(bbox=list(bbox),bbox_raw_hex=content[4:36].hex(),parts=parts,positions=nv,xy_byte_offset_in_content=start,all_xy_raw_sha256=sha(content[start:]),ring_closed=[bool(r) and r[0]==r[-1] for r in rings],computed_bbox=[min(x for x,y in points),min(y for x,y in points),max(x for x,y in points),max(y for x,y in points)])
   totalpoints+=nv;totalparts+=np
  recordbytes=dbf[hlen+idx*rlen:hlen+(idx+1)*rlen];assert len(recordbytes)==rlen
  fields=[]
  for d in descriptors:
   field=recordbytes[d['record_offset']:d['record_offset']+d['length']];fields.append(dict(name=d['name'],raw_hex=field.hex(),raw_ascii=field.decode('ascii'),value=field.decode('ascii').strip(),byte_offset=hlen+idx*rlen+d['record_offset']));checks+=1
  decoded=reader.record(idx)
  if recordbytes[:1]==b' ':
   for d,field,v in zip(descriptors,fields,decoded):
    expected=field['value']
    if d['type']=='C':assert v==expected
    elif d['type']=='N':assert str(v)==expected
    else:raise AssertionError(('unhandled native DBF field',d))
   checks+=len(descriptors)
  entry.update(dbf_record_byte_offset=hlen+idx*rlen,dbf_delete_marker=recordbytes[:1].hex(),dbf_raw_sha256=sha(recordbytes),fields=fields,pyshp_values=list(decoded) if decoded is not None else None);records.append(entry);p+=8+size*2
 assert p==len(shp);assert 100+8*n==len(shx);assert len(dbf) in [hlen+n*rlen,hlen+n*rlen+1]
 return dict(source_id=receipt['id'],whole_zip_bytes=len(raw),whole_zip_sha256=sha(raw),members=members,all_member_crc_pass=True,prj=prj,native_crs='NAD83 geographic degrees per .prj (EPSG4269)',header_bbox=list(struct.unpack_from('<4d',shp,36)),shape_type=struct.unpack_from('<i',shp,32)[0],dbf_header_hex=dbf[:32].hex(),dbf_fields=descriptors,native_records=n,total_positions=totalpoints,total_parts=totalparts,independent_double_and_field_checks=checks,records=records,pyshp_version=shapefile.__version__,geometry_repaired=False)

def main():
 pages=[read(p) for p in sorted((M/'source').glob('native-batch-*.receipt.json'))];features=[];batches=[]
 meta=json.loads(body(read(M/'source/native-pre-metadata.receipt.json')));ids=json.loads(body(read(M/'source/native-pre-ids.receipt.json')))
 for r in pages:
  x=json.loads(body(r));q=r['query_parameters'];assert not set(q)&{'outSR','geometryPrecision','quantizationParameters','maxAllowableOffset','generalization','resultOffset','resultRecordCount'}
  assert all(q[k]=='true' for k in ['returnGeometry','returnTrueCurves','returnZ','returnM']);assert q['outFields']=='*'
  got=[f['attributes'][meta['objectIdField']] for f in x['features']];wanted=r['requested_object_ids'];assert len(wanted)<=50 and len(got)==len(set(got))==len(wanted) and set(got)==set(wanted)
  assert not x.get('exceededTransferLimit',False)
  for f in x['features']:assert set(f['attributes'])=={v['name'] for v in meta['fields']}
  batches.append(dict(id=r['id'],requested=wanted,returned=got,spatialReference=x.get('spatialReference'),response_keys=list(x)))
  features+=x['features']
 assert len(features)==len(set(f['attributes']['OBJECTID'] for f in features))==len(ids['objectIds'])==531
 assert set(ids['objectIds'])=={f['attributes']['OBJECTID'] for f in features}
 for k in ['metadata','count','ids']:assert body(read(M/f'source/native-pre-{k}.receipt.json'))==body(read(M/f'source/native-post-{k}.receipt.json'))
 write('native-features.json.gz',dict(representation='Native Esri JSON, all attributes and geometry unmodified; not GeoJSON',spatialReference=meta['extent']['spatialReference'],features=features))
 write('qa/native-audit.json',dict(status='pass',batches=batches,native_features=len(features),attribute_schema=meta['fields'],null_attributes={k:sum(f['attributes'][k] is None for f in features) for k in features[0]['attributes']},native_ring_count=sum(len((f.get('geometry')or{}).get('rings',[])) for f in features),native_positions=sum(len(r) for f in features for r in (f.get('geometry')or{}).get('rings',[])),hasZ=meta['hasZ'],hasM=meta['hasM'],true_curve_features=sum('curveRings'in(f.get('geometry')or{}) for f in features),pre_post_exact=True,leaf_crosswalk_approved=False))
 write('qa/native-topology.json',diagnostics(features))
 for p in sorted((M/'source').glob('census-vtd-100*.receipt.json')):
  r=read(p);audit=audit_zip(r);write('qa/'+r['id']+'-audit.json.gz',audit);print(r['id'],audit['native_records'],audit['total_positions'],audit['independent_double_and_field_checks'])
 print('native',len(features))
if __name__=='__main__':main()
