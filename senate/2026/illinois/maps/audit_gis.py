"""Independent binary SHP/SHX/DBF + PyShp all-record verification, exact native slices.
No source writing, ring closure, hole inference, reprojection or geometry repair.
"""
from common import *
from acquire import body
import io,zipfile,zlib,struct,shapefile,inspect,math
from collections import defaultdict

def bits(x):return struct.pack('<d',x)
def bitseq(values):return b''.join(bits(x) for x in values)
def require(ok,message):
 if not ok:raise AssertionError(message)
def audit_zip(raw,write=True):
 z=zipfile.ZipFile(io.BytesIO(raw));members=[];blobs={}
 for info in z.infolist():
  b=z.read(info);require(len(b)==info.file_size and zlib.crc32(b)&0xffffffff==info.CRC,info.filename)
  members.append(dict(name=info.filename,bytes=len(b),compressed_bytes=info.compress_size,crc32=f'{info.CRC:08x}',sha256=sha(b)))
  blobs[info.filename]=b
 def ext(e):return next(b for n,b in blobs.items() if n.endswith(e))
 shp,shx,dbf=ext('.shp'),ext('.shx'),ext('.dbf')
 require(struct.unpack('>i',shp[:4])[0]==9994,'SHP code')
 require(struct.unpack('>i',shp[24:28])[0]*2==len(shp),'SHP file length')
 require(struct.unpack('>i',shx[24:28])[0]*2==len(shx),'SHX file length')
 require(shp[:24]==shx[:24],'SHP/SHX header reserved fields')
 require(shp[28:100]==shx[28:100],'SHX version/type/bbox')
 version,kind=struct.unpack('<ii',shp[28:36]);require(version==1000 and kind==5,'expected census Polygon')
 header_bbox=struct.unpack('<4d',shp[36:68]);prj=ext('.prj').decode();cpg=ext('.cpg').decode().strip()
 n,hlen,rlen=struct.unpack('<IHH',dbf[4:12]);fields=[];offset=1
 for pos in range(32,hlen-1,32):
  f=dbf[pos:pos+32]
  if f[0]==13:break
  name=f[:11].split(b'\0')[0].decode('ascii');typ=chr(f[11]);size,dec=f[16:18]
  fields.append(dict(name=name,type=typ,size=size,decimal=dec,byte_offset=offset,descriptor_hex=f.hex()));offset+=size
 require(offset==rlen,'DBF field widths');require(dbf[hlen-1]==13,'DBF header terminator')
 require(len(shx)==100+8*n and len(dbf)>=hlen+rlen*n,'counts')
 reader=shapefile.Reader(shp=io.BytesIO(shp),shx=io.BytesIO(shx),dbf=io.BytesIO(dbf),encoding='utf-8')
 require(len(reader)==n,'PyShp rows')
 require([(x['name'],x['type'],x['size'],x['decimal']) for x in fields]==[tuple(f) for f in reader.fields[1:]],'all field schema')
 slices=defaultdict(list);all_records=[];point_count=part_count=0;nulls=[];empty=[];unclosed=[];ring_invalid=[]
 from shapely.geometry import LinearRing
 pos=100;global_min=[math.inf,math.inf];global_max=[-math.inf,-math.inf]
 for i in range(n):
  recnum,words=struct.unpack('>ii',shp[pos:pos+8]);content=shp[pos+8:pos+8+words*2]
  off,indexwords=struct.unpack('>ii',shx[100+i*8:108+i*8]);require(off*2==pos and words==indexwords,'every SHX offset/length')
  require(recnum==i+1,'record sequence');t=struct.unpack('<i',content[:4])[0];require(t in (0,5),'record type')
  row=dbf[hlen+i*rlen:hlen+(i+1)*rlen];require(row[0:1] in (b' ',b'*'),'deletion flag')
  literal={};attrs={}
  for f in fields:
   v=row[f['byte_offset']:f['byte_offset']+f['size']].decode('utf-8');literal[f['name']]=v
   attrs[f['name']]=v.strip() if f['type']=='C' else (int(v.strip()) if v.strip() else None)
  prec=reader.record(i)
  if row[:1]==b' ':require(list(attrs.values())==list(prec),'every DBF value')
  py=reader.shape(i);require(py.shapeType==t,'PyShp type')
  bbox=None;parts=[];xy=[]
  if t==0:nulls.append(i+1);require(len(content)==4 and not py.points,'null')
  else:
   bbox=list(struct.unpack('<4d',content[4:36]));np,npt=struct.unpack('<ii',content[36:44]);parts=list(struct.unpack('<'+'i'*np,content[44:44+4*np]));rawxy=content[44+4*np:]
   require(len(rawxy)==npt*16,'record point length')
   xy=[list(struct.unpack('<dd',rawxy[j:j+16])) for j in range(0,len(rawxy),16)]
   require(list(py.parts)==parts,'every part index')
   require(bitseq(v for pt in py.points for v in pt)==rawxy,'EVERY XY IEEE754 bit')
   require(bitseq(py.bbox)==content[4:36],'every feature bbox bit')
   require(bitseq(v for pt in json.loads(json.dumps(xy)) for v in pt)==rawxy,'JSON exact XY roundtrip')
   require(not parts or parts[0]==0,'first part');require(all(0<=v<npt for v in parts) and parts==sorted(set(parts)),'part offsets')
   # Constructor was inspected before writing this adapter. Never use lines= or __geo_interface__.
   if xy:
    adapted=shapefile.Shape(shapeType=t,points=xy,parts=parts)
    require(bitseq(v for pt in adapted.points for v in pt)==rawxy and list(adapted.parts)==parts,'adapter exact')
    xs=[p[0] for p in xy];ys=[p[1] for p in xy]
    require(bitseq([min(xs),min(ys),max(xs),max(ys)])==content[4:36],'native bbox every point')
    for j in range(2):global_min[j]=min(global_min[j],min(p[j] for p in xy));global_max[j]=max(global_max[j],max(p[j] for p in xy))
   else:empty.append(i+1)
   for j,start in enumerate(parts):
    ring=xy[start:parts[j+1] if j+1<len(parts) else len(xy)]
    if not ring or bitseq(ring[0])!=bitseq(ring[-1]):unclosed.append([i+1,j]);continue
    if len(ring)<4 or not LinearRing(ring).is_simple:ring_invalid.append([i+1,j])
   point_count+=len(xy);part_count+=len(parts)
  fips=attrs['STATEFP20']+attrs['COUNTYFP20']
  rec=dict(source_record_1based=i+1,source_record_number=recnum,source_shp_byte_offset=pos,source_content_bytes=words*2,source_content_sha256=sha(content),dbf_row_hex=row.hex(),dbf_literal_fields=literal,attributes=attrs,shapeType=t,bbox=bbox,parts=parts,points=xy,z=None,m=None,truecurves=None,source_xy_bytes_sha256=sha(bitseq(v for pt in xy for v in pt)))
  slices[fips].append(rec);all_records.append(dict(record_1based=i+1,county_fips=fips,GEOID20=attrs['GEOID20'],source_shp_byte_offset=pos,source_content_bytes=words*2,source_content_sha256=sha(content),dbf_row_sha256=sha(row),points=len(xy),parts=len(parts)))
  pos+=8+words*2
 require(pos==len(shp),'all SHP bytes consumed');require(bitseq(global_min+global_max)==shp[36:68],'global bbox')
 require(len(slices)==102 and all(len(x)>0 for x in slices.values()),'all counties')
 if write:
  dump('derived/census-record-index.json.gz',all_records)
  for fips,records in sorted(slices.items()):
   dump('derived/counties/'+fips+'.native.json.gz',dict(schema='exact-native-vtd-slice-v1',source_receipt='maps/source/census-illinois-vtd2020.receipt.json',source_county_fips=fips,source_vintage='2020 Census VTD; not 2024/2026 reporting geography',crs_wkt=prj,native_coordinate_unit='degree',geometry_representation='Original SHP point/part order; no ring ownership or closure repair; IEEE754 binary64 preserved by JSON roundtrip',fields=fields,records=records))
 out=dict(status='pass',original_members=members,records=n,points=point_count,parts=part_count,county_slices=102,county_records={k:len(v) for k,v in sorted(slices.items())},fields=fields,crs_wkt=prj,cpg=cpg,native_coordinate_unit='degree',all_crc_fields_rows_indices_bboxes_xy_bits_parts_verified=True,null_records=nulls,empty_records=empty,unclosed_rings=unclosed,non_simple_or_short_rings=ring_invalid,ring_diagnostic='All individually closed rings tested for simplicity; no shell/hole classification or whole-feature validity inference',positive_area_or_overlap_certification=None,legal_gap_sliver_overlap_certification=False,same_vintage_controlling_outline=None,pyshp_version=shapefile.__version__,adapter='points= and parts= only; no lines=, __geo_interface__, repair, rounding, simplification or CRS transform')
 return out

def main():
 current=inspect.getsource(shapefile.Shape.__init__)
 inspected=(M/'qa/installed-pyshp-constructor.txt').read_text();require(current in inspected,'constructor changed after inspection')
 r=load(M/'source/census-illinois-vtd2020.receipt.json');out=audit_zip(body(r));dump('qa/census-binary-audit.json',out);print(json.dumps({k:v for k,v in out.items() if k in ['status','records','points','parts','county_slices','null_records','empty_records','unclosed_rings','non_simple_or_short_rings']}))
if __name__=='__main__':main()
