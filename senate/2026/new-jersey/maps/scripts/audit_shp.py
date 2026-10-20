"""Independent byte-struct audit; never a geo-interface/ring/hole adapter."""
from acquire import *
import zipfile,io,struct,binascii,shapefile,inspect,collections,math

def bits(x):return struct.pack('<d',x)
def run():
 raw=content('census-vtd-zip');z=zipfile.ZipFile(io.BytesIO(raw));members=[]
 assert z.testzip() is None
 for m in z.infolist():
  b=z.read(m.filename);assert len(b)==m.file_size and binascii.crc32(b)&0xffffffff==m.CRC
  members.append({'name':m.filename,'bytes':len(b),'crc32':f'{m.CRC:08x}','sha256':sha(b),'compress_type':m.compress_type,'flag_bits':m.flag_bits,'zip_datetime':m.date_time})
 stem='tl_2020_34_vtd20';shp=z.read(stem+'.shp');shx=z.read(stem+'.shx');dbf=z.read(stem+'.dbf');cpg=z.read(stem+'.cpg').decode();prj=z.read(stem+'.prj').decode()
 def hdr(b):
  assert struct.unpack_from('>i',b)[0]==9994 and struct.unpack_from('>i',b,24)[0]*2==len(b)
  return {'file_code':9994,'file_words':len(b)//2,'version':struct.unpack_from('<i',b,28)[0],'shape_type':struct.unpack_from('<i',b,32)[0],'bbox_XY_Z_M':struct.unpack_from('<8d',b,36)}
 h=hdr(shp);hx=hdr(shx);assert h['bbox_XY_Z_M']==hx['bbox_XY_Z_M'];n=struct.unpack_from('<I',dbf,4)[0];hlen,rlen=struct.unpack_from('<HH',dbf,8);assert (len(shx)-100)//8==n
 fields=[];pos=32
 while dbf[pos]!=13:
  b=dbf[pos:pos+32];fields.append({'name':b[:11].split(b'\0')[0].decode('ascii'),'type':chr(b[11]),'size':b[16],'decimal':b[17],'descriptor_hex':b.hex()});pos+=32
 assert hlen==pos+1 and 1+sum(x['size'] for x in fields)==rlen and len(dbf)>=hlen+n*rlen
 # Inspect actual installed reader/constructor call path. from_byte_stream supplies points+parts,
 # never lines=, so its optional auto-closing branch is NOT used. Empty/orphan records bypass it.
 inspected=[]
 for name,obj in [('Shape_init',shapefile.Shape.__init__),('Polygon_from_byte_stream',shapefile.Polygon.from_byte_stream),('ShpReader_shape',shapefile.ShpReader._shape),('DbfReader_record',shapefile.DbfReader.record),('Reader_shape',shapefile.Reader.shape)]:
  s=inspect.getsource(obj);(BASE/'qa'/f'inspected-{name}.py.txt').write_text(s);inspected.append({'function':name,'source_sha256':sha(s.encode())})
 reader=shapefile.Reader(shp=io.BytesIO(shp),shx=io.BytesIO(shx),dbf=io.BytesIO(dbf),encoding=cpg)
 assert [(f.name,str(f.field_type),f.size,f.decimal) for f in reader.fields[1:]]==[(f['name'],f['type'],f['size'],f['decimal']) for f in fields]
 off=100;rows=[];audits=[];counts=collections.Counter();xyhash=hashlib.sha256();parsedhash=hashlib.sha256()
 for i in range(n):
  idxoff,idxlen=struct.unpack_from('>2i',shx,100+8*i);recno,words=struct.unpack_from('>2i',shp,off);assert idxoff*2==off and idxlen==words and recno==i+1
  b=shp[off+8:off+8+words*2];assert len(b)==words*2;typ=struct.unpack_from('<i',b)[0];counts['shape_type_'+str(typ)]+=1
  row=dbf[hlen+i*rlen:hlen+(i+1)*rlen];assert len(row)==rlen;vals=[];rp=1;rawfields=[]
  for f in fields:
   cell=row[rp:rp+f['size']];rp+=f['size'];rawfields.append(cell.hex())
   if f['type']=='C':v=cell.decode(cpg).strip().rstrip('\0')
   elif f['type']=='N':v=int(cell.strip()) if cell.strip() and f['decimal']==0 else float(cell.strip()) if cell.strip() else None
   else:raise AssertionError(('unhandled actual field type',f))
   vals.append(v)
  parsedrow=reader.record(i)
  assert (list(parsedrow)==vals if row[:1]==b' ' else parsedrow is None)
  geom={'shape_type':typ};diagnostic={'index':i,'SHP_record_number':recno,'SHP_offset_bytes':off,'SHX_offset_words':idxoff,'content_words':words,'DBF_deletion_flag_hex':row[:1].hex(),'raw_shape_sha256':sha(b),'raw_dbf_row_sha256':sha(row)}
  if typ==5:
   bbox=struct.unpack_from('<4d',b,4);np,nxy=struct.unpack_from('<2i',b,36);parts=list(struct.unpack_from('<'+str(np)+'i',b,44));xybytes=b[44+4*np:44+4*np+16*nxy];assert len(xybytes)==16*nxy
   pts=[list(v) for v in struct.iter_unpack('<2d',xybytes)];assert len(b)==44+4*np+16*nxy
   geom.update(bbox=list(bbox),parts=parts,points=pts)
   safe=bool(parts) and bool(pts) and parts[0]==0 and parts==sorted(parts) and parts[-1]<len(pts)
   if safe:
    shape=reader.shape(i);assert shape.shapeType==typ and list(shape.parts)==parts
    assert b''.join(bits(v) for v in shape.bbox)==b[4:36]
    parsedxy=b''.join(struct.pack('<2d',*p) for p in shape.points);assert parsedxy==xybytes
    xyhash.update(xybytes);parsedhash.update(parsedxy);counts['every_XY_IEEE754_values_compared']+=2*nxy
    # JSON representation round-trips the exact floats, including signed zeros.
    assert b''.join(struct.pack('<2d',*p) for p in json.loads(json.dumps(pts)))==xybytes
    counts['constructor_compared_records']+=1
   else:diagnostic['constructor_bypassed']='empty/orphan parts preserved independently; reader may infer a part'
   ringinfo=[]
   for j,k in enumerate(parts):
    end=parts[j+1] if j+1<len(parts) else len(pts);ring=pts[k:end];closed=bool(ring) and ring[0]==ring[-1];area=sum(a[0]*bb[1]-bb[0]*a[1] for a,bb in zip(ring,ring[1:]))/2 if closed else None
    ringinfo.append({'start':k,'end_exclusive':end,'points':len(ring),'explicitly_closed':closed,'signed_shoelace_native_degrees_squared':area,'adjacent_duplicate_points':sum(a==bb for a,bb in zip(ring,ring[1:]))})
    counts['rings']+=1;counts['unclosed_rings']+=not closed;counts['short_rings']+=len(ring)<4
   diagnostic['parts']=ringinfo;diagnostic['coordinate_bbox_matches_record']=list(bbox)==[min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)] if pts else None
   counts['points']+=nxy
  elif typ==0:counts['null_shapes_preserved']+=1
  else:geom['raw_shape_hex']=b.hex();diagnostic['constructor_bypassed']='unhandled native shape type preserved unchanged in original/hex'
  attrs=dict(zip([f['name'] for f in fields],vals));rows.append({'index':i,'attributes':attrs,'raw_dbf_cells_hex':rawfields,'deletion_flag_hex':row[:1].hex(),'geometry':geom});audits.append(diagnostic);off+=8+len(b)
 assert off==len(shp);assert xyhash.hexdigest()==parsedhash.hexdigest();counts['records']=n
 (BASE/'derived/census-vtd-native.jsonl.gz').write_bytes(gzip.compress(b''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()+b'\n' for r in rows),mtime=0))
 (BASE/'qa/census-vtd-every-record.json.gz').write_bytes(gzip.compress(json.dumps(audits,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
 out={'status':'pass_complete_ZIP_and_independent_binary_audit','ZIP_raw_sha256':sha(raw),'members':members,'SHP_header':h,'SHX_header':hx,'DBF_header_hex':dbf[:hlen].hex(),'DBF_schema':fields,'DBF_trailing_bytes_hex':dbf[hlen+n*rlen:].hex(),'cpg':cpg,'prj':prj,'counts':dict(counts),'all_XY_bytes_sha256':xyhash.hexdigest(),'installed_constructor_XY_bytes_sha256':parsedhash.hexdigest(),'installed_pyshp_version':shapefile.__version__,'installed_module_sha256':sha(Path(shapefile.__file__).read_bytes()),'inspected_functions':inspected,'constructor_path':'Polygon.from_byte_stream -> points and explicit parts; never lines= or geo-interface; unsafe empty/orphan bypass preserves original','ring_or_hole_reinterpretation':False,'topology_scope':'linear closure/part/order/bbox/duplicate diagnostics only; geographic native degrees; no operative outline, no legal gaps/overlaps/slivers certification','county_counts':dict(collections.Counter(r['attributes']['COUNTYFP20'] for r in rows))}
 write(BASE/'qa/census-vtd-audit.json',out);print(out['counts'])
if __name__=='__main__':run()
