"""Independent byte-level SHP/SHX/DBF audit BEFORE any geometry adapter."""
import struct,io,zipfile,json,gzip,hashlib,shapefile,sys,math
from pathlib import Path
from html_tools import ROOT,entity
from collections import Counter
from datetime import date

def sha(b):return hashlib.sha256(b).hexdigest()
def js(v):return json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
def audit_zip(raw):
 z=zipfile.ZipFile(io.BytesIO(raw));members=[]
 for info in z.infolist():
  b=z.read(info);assert len(b)==info.file_size and ( __import__('zlib').crc32(b)&0xffffffff)==info.CRC
  members.append({'name':info.filename,'bytes':len(b),'sha256':sha(b),'crc32':info.CRC,'zip_date_time':list(info.date_time),'compressed_bytes':info.compress_size})
 shpnames=[n for n in z.namelist() if n.lower().endswith('.shp')];datasets=[];stats=Counter()
 for sn in shpnames:
  stem=sn[:-4];names={ext:next((n for n in z.namelist() if n.lower()==(stem+ext).lower()),None) for ext in ['.shp','.shx','.dbf','.prj','.cpg','.shp.xml']}
  assert all(names[e] for e in ['.shp','.shx','.dbf','.prj'])
  sp=z.read(sn);sx=z.read(names['.shx']);db=z.read(names['.dbf']);cp=z.read(names['.cpg']) if names['.cpg'] else b'UTF-8'
  assert struct.unpack_from('>i',sp,0)[0]==9994 and struct.unpack_from('>i',sp,24)[0]*2==len(sp)
  assert struct.unpack_from('>i',sx,24)[0]*2==len(sx) and sp[:24]==sx[:24] and sp[28:100]==sx[28:100]
  assert struct.unpack_from('<i',sp,28)[0]==1000
  typ=struct.unpack_from('<i',sp,32)[0];assert typ in [0,5],('unimplemented source shape type retained, not adapted',typ)
  nr,hlen,rlen=struct.unpack_from('<IHH',db,4);fields=[];at=32
  while db[at]!=13:
   desc=db[at:at+32];nm=desc[:11].split(b'\0',1)[0].decode('ascii');ft=chr(desc[11]);width=desc[16];dec=desc[17]
   fields.append({'name':nm,'type':ft,'width':width,'decimal':dec,'descriptor_hex':desc.hex()});at+=32
  assert at+1==hlen and 1+sum(f['width'] for f in fields)==rlen
  assert len(db) in [hlen+nr*rlen,hlen+nr*rlen+1]
  if len(db)>hlen+nr*rlen:assert db[-1]==26
  reader=shapefile.Reader(shp=io.BytesIO(sp),shx=io.BytesIO(sx),dbf=io.BytesIO(db),cpg=io.BytesIO(cp))
  assert len(reader)==nr==(len(sx)-100)//8
  assert struct.pack('<4d',*reader.bbox)==sp[36:68]
  assert [[f.name,str(f.field_type),f.size,f.decimal] for f in reader.fields[1:]]==[[f['name'],f['type'],f['width'],f['decimal']] for f in fields]
  out=[];off=100
  for i in range(nr):
   offset,words=struct.unpack_from('>2i',sx,100+i*8);rn,rw=struct.unpack_from('>2i',sp,off)
   assert offset*2==off and rw==words and rn==i+1
   record=sp[off+8:off+8+2*words];st=struct.unpack_from('<i',record)[0];assert st in [0,5]
   sh=reader.shape(i);points=[];parts=[];bbox=None
   if st==5:
    bbox=list(struct.unpack_from('<4d',record,4));nparts,npts=struct.unpack_from('<2i',record,36)
    parts=list(struct.unpack_from('<'+str(nparts)+'i',record,44));ptstart=44+4*nparts;ptbytes=record[ptstart:ptstart+16*npts]
    assert len(record)==ptstart+16*npts and parts[0]==0 and sorted(parts)==parts and all(0<=x<npts for x in parts)
    points=[list(struct.unpack_from('<2d',ptbytes,j*16)) for j in range(npts)]
    assert len(sh.points)==npts and list(sh.parts)==parts and struct.pack('<4d',*sh.bbox)==record[4:36]
    assert b''.join(struct.pack('<2d',*xy) for xy in sh.points)==ptbytes
    assert bbox==[min(p[0] for p in points),min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)]
    stats['xy_ieee754_values']+=2*npts;stats['parts']+=nparts
   else:assert sh.shapeType==0 and len(record)==4
   stats['shape_records']+=1
   row=db[hlen+i*rlen:hlen+(i+1)*rlen];deleted=row[0]!=32;tokens=[];values=[];pos=1
   for f in fields:
    token=row[pos:pos+f['width']];pos+=f['width'];tokens.append(token.hex());ft=f['type']
    if ft=='C':value=token.decode(cp.decode().strip()).rstrip('\x00 ').lstrip(' ')
    elif ft in ['N','F']:
     val=token.split(b'\0',1)[0].strip(b'*')
     if not val.strip():value=None
     else:value=float(val) if f['decimal'] else int(val)
    else:raise ValueError('unimplemented DBF type '+ft)
    values.append(value);stats['dbf_tokens']+=1
   rr=reader.record(i)
   if deleted:assert rr is None
   else:assert list(rr)==values,(i,list(rr),values)
   flags=[]
   for j,start in enumerate(parts):
    ring=points[start:parts[j+1] if j+1<len(parts) else len(points)]
    if ring and ring[0]!=ring[-1]:flags.append({'part':j,'unclosed':True})
    if len(ring)<4:flags.append({'part':j,'short':True})
   out.append({'record_number':rn,'source_shape_type':st,'shp_offset':off,'content_bytes':2*words,'content_sha256':sha(record),'bbox':bbox,'parts':parts,'points':points,'deletion_flag_hex':row[:1].hex(),'deleted':deleted,'field_tokens_hex':tokens,'values':values,'raw_part_diagnostics':flags})
   off+=8+2*words
  assert off==len(sp)
  datasets.append({'shp':sn,'members':names,'source_crs_wkt':z.read(names['.prj']).decode(),'cpg_literal':cp.decode(),'header_hex':sp[:100].hex(),'dbf_header_hex':db[:hlen].hex(),'fields':fields,'records':out,'source_generalization':'Native source geometry preserved; product role/vintage is supplied separately. No record/part/point repair or result-label join.'})
 return {'original_sha256':sha(raw),'original_bytes':len(raw),'members':members,'datasets':datasets,'checks':dict(stats),'reader_version':shapefile.__version__,'status':'PASS'}

def main():
 receipts=[]
 for p in sorted((ROOT/'source').glob('*.receipt.json')):
  r,b=entity(str(p.relative_to(ROOT)))
  if r['status']==200 and b.startswith(b'PK\x03\x04'):receipts.append((str(p.relative_to(ROOT)),b))
 seen={};index=[]
 for p,b in receipts:
  h=sha(b)
  if h not in seen:
   result=audit_zip(b);path=ROOT/'zip-audit'/(h+'.json.gz');path.parent.mkdir(exist_ok=True);path.write_bytes(gzip.compress(js(result),mtime=0));seen[h]=str(path.relative_to(ROOT));print(h[:12],result['checks'],flush=True)
  index.append({'receipt':p,'audit':seen[h],'original_sha256':h})
 (ROOT/'zip-audit-index.json').write_text(json.dumps(index,indent=2)+'\n')
if __name__=='__main__':main()
