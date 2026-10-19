#!/usr/bin/env python3
"""Cassia ZIP: independent binary SHP/SHX/DBF checks, original bytes unchanged."""
import gzip,hashlib,io,json,struct,zipfile
from pathlib import Path
import shapefile
from pyproj import CRS
MAPS=Path(__file__).resolve().parents[1];ROOT=MAPS.parent

def verify():
 r=next(json.loads(p.read_text()) for p in (MAPS/'source').glob('additional-16031*.receipt.json') if '.zip' in json.loads(p.read_text())['requested_url']);b=gzip.decompress((ROOT/r['stored_path']).read_bytes());z=zipfile.ZipFile(io.BytesIO(b));assert z.testzip() is None
 members=[]
 for info in z.infolist():
  bb=z.read(info);members.append(dict(name=info.filename,bytes=len(bb),CRC32=info.CRC,sha256=hashlib.sha256(bb).hexdigest()))
 assert set(z.namelist())=={'2026Precinctfiles.'+e for e in ['sbn','sbx','shp','shp.xml','shx','cpg','dbf','prj']}
 shp=z.read('2026Precinctfiles.shp');shx=z.read('2026Precinctfiles.shx');dbf=z.read('2026Precinctfiles.dbf')
 assert struct.unpack('>i',shp[:4])[0]==9994 and struct.unpack('>i',shp[24:28])[0]*2==len(shp)
 assert struct.unpack('>i',shx[24:28])[0]*2==len(shx) and shp[28:100]==shx[28:100]
 assert struct.unpack('<ii',shp[28:36])==(1000,5)
 # Test the installed constructor before any adapter: points/parts preserves open rings;
 # lines closes them automatically and must never be used for an original-ring adapter.
 sample=[[0.,0.],[2.,0.],[0.,1.]]
 direct=shapefile.Shape(shapeType=5,points=sample,parts=[0]);assert list(map(list,direct.points))==sample and list(direct.parts)==[0]
 auto=shapefile.Shape(shapeType=5,lines=[sample]);assert len(auto.points)==4 and list(auto.points[0])==list(auto.points[-1])
 reader=shapefile.Reader(shp=io.BytesIO(shp),shx=io.BytesIO(shx),dbf=io.BytesIO(dbf),encoding='utf-8')
 count=struct.unpack('<I',dbf[4:8])[0];hlen,rlen=struct.unpack('<HH',dbf[8:12]);assert count==len(reader)
 fields=[]
 for start in range(32,hlen-1,32):
  f=dbf[start:start+32];fields.append(dict(name=f[:11].split(b'\0')[0].decode(),type=chr(f[11]),length=f[16],decimals=f[17],raw_descriptor_hex=f.hex()))
 records=[];native_features=[];all_xy=[];xyhash=hashlib.sha256();total=0
 nindex=(len(shx)-100)//8;assert nindex==count
 for i in range(count):
  offset,words=struct.unpack('>ii',shx[100+i*8:108+i*8]);offset*=2;recno,reclen=struct.unpack('>ii',shp[offset:offset+8]);assert recno==i+1 and reclen==words
  data=shp[offset+8:offset+8+words*2];typ=struct.unpack('<i',data[:4])[0];assert typ==5
  bbox=struct.unpack('<4d',data[4:36]);np,npts=struct.unpack('<ii',data[36:44]);parts=list(struct.unpack('<'+'i'*np,data[44:44+np*4]));start=44+np*4
  assert len(data)==start+npts*16;coords=list(struct.iter_unpack('<dd',data[start:]));total+=npts;all_xy+=coords
  assert parts[0]==0 and parts==sorted(set(parts)) and parts[-1]<npts
  assert list(bbox)==[min(p[0] for p in coords),min(p[1] for p in coords),max(p[0] for p in coords),max(p[1] for p in coords)]
  if i+1<count:assert struct.unpack('>i',shx[108+i*8:112+i*8])[0]*2==offset+8+len(data)
  sh=reader.shape(i);assert list(sh.parts)==parts and list(sh.bbox)==list(bbox) and list(map(tuple,sh.points))==coords
  xyhash.update(data[start:]);adapter=shapefile.Shape(shapeType=typ,points=coords,parts=parts,bbox=bbox)
  assert list(map(tuple,adapter.points))==coords and list(adapter.parts)==parts
  rows=dbf[hlen+i*rlen:hlen+(i+1)*rlen];assert len(rows)==rlen and rows[0:1]==b' '
  attrs=reader.record(i).as_dict();positions=[];pos=1
  for f in fields:
   raw=rows[pos:pos+f['length']];assert f['type']=='C' and raw.decode('utf-8').strip()==attrs[f['name']];positions.append(dict(field=f['name'],raw_hex=raw.hex(),value=attrs[f['name']]));pos+=f['length']
  assert pos==rlen
  native_features.append(dict(attributes=dict(OBJECTID=recno,COUNTY='Cassia',PCNCT_NME=attrs['District']),geometry=dict(rings=[[list(p) for p in coords[a:b]] for a,b in zip(parts,parts[1:]+[npts])])) )
  records.append(dict(record_number=recno,index_offset_bytes=offset,index_content_words=words,shape_type=typ,bbox=list(bbox),parts=parts,positions=npts,raw_XY_double_sha256=hashlib.sha256(data[start:]).hexdigest(),attributes=attrs,complete_dbf_record_hex=rows.hex(),raw_field_values=positions,open_rings=sum(coords[a]!=coords[b-1] for a,b in zip(parts,parts[1:]+[npts]))))
 assert list(struct.unpack('<4d',shp[36:68]))==[min(p[0] for p in all_xy),min(p[1] for p in all_xy),max(p[0] for p in all_xy),max(p[1] for p in all_xy)]
 from geometry import diagnose
 topology=diagnose(native_features);topology.update(native_crs='Exact original Cassia PRJ retained below',native_area_units='US survey feet squared')
 prj=z.read('2026Precinctfiles.prj').decode();crs=CRS.from_wkt(prj)
 return dict(status='pass_complete_Cassia_original_ZIP_binary_verification',receipt=r['id'],original=r['stored_path'],zip_sha256=hashlib.sha256(b).hexdigest(),members=members,dbf_fields=fields,record_count=count,shp_shx_equal_count=nindex,global_bbox=list(struct.unpack('<4d',shp[36:68])),XY_positions=total,all_original_XY_double_sha256=xyhash.hexdigest(),crs_wkt=prj,crs_name=crs.name,axis_units=[a.unit_name for a in crs.axis_info],native_area_unit='US survey feet squared; distinct from state-layer metres squared',pyshp_version=shapefile.__version__,constructor_test=dict(points_parts_preserve_three_position_open_ring=True,lines_auto_closes_to_four_positions=True,adapter_uses='points and parts only'),records=records,legal_or_historical_crosswalk=None,topology=topology)
if __name__=='__main__':
 q=verify();(MAPS/'qa/cassia-shapefile.json').write_text(json.dumps(q,indent=2,ensure_ascii=False)+'\n');print(json.dumps({k:q[k] for k in ['status','record_count','XY_positions','constructor_test']}))
