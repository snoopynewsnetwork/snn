"""Independent ZIP/DBF/SHP/SHX parser; comparison with installed PyShp, without repairs."""
from common import *
from acquire import body_of
import zipfile,struct,zlib,math,shapefile,sys,collections

def bits(x):return struct.pack('<d',x)
def field_value(raw,t,dec):
 s=raw.decode('utf-8').strip().strip('\0')
 if t=='C':return raw.decode('utf-8').replace('\x00','').strip()
 if t in ['N','F']:
  if not s or '*' in s:return None
  return float(s) if dec or t=='F' else int(s.split('.')[0])
 if t=='L':return None if s in ['?',''] else s.upper() in ['Y','T','1']
 if t=='D':
  import datetime
  return datetime.date(int(s[:4]),int(s[4:6]),int(s[6:])) if s and s!='00000000' else None
 raise ValueError('Unsupported field type '+t)

def audit_zip(key,b):
 z=zipfile.ZipFile(io.BytesIO(b));members=[];data={}
 for info in z.infolist():
  raw=z.read(info.filename);assert len(raw)==info.file_size and zlib.crc32(raw)&0xffffffff==info.CRC
  data[info.filename]=raw;members.append({'name':info.filename,'bytes':len(raw),'sha256':sha(raw),'crc32':f'{info.CRC:08x}','crc_pass':True,'compressed_bytes':info.compress_size,'date_time':list(info.date_time)})
 out={'request':'maps/requests/'+key+'.json','zip_sha256':sha(b),'members':members,'pyshp_version':shapefile.__version__,'constructor_inspected':'maps/history/pyshp-constructor.txt','layers':[],'source_repair':False}
 for name,shp in data.items():
  if not name.lower().endswith('.shp'):continue
  stem=name[:-4];shx=data[stem+'.shx'];dbf=data[stem+'.dbf'];prj=data.get(stem+'.prj');cpg=data.get(stem+'.cpg');encoding=(cpg.decode().strip() if cpg else 'utf-8');encoding='utf-8' if encoding in ['UTF-8','65001'] else encoding
  rd=shapefile.Reader(shp=io.BytesIO(shp),shx=io.BytesIO(shx),dbf=io.BytesIO(dbf),encoding=encoding)
  for source in [shp,shx]:assert struct.unpack_from('>i',source,0)[0]==9994 and struct.unpack_from('>i',source,24)[0]*2==len(source) and struct.unpack_from('<i',source,28)[0]==1000
  assert shp[:100]==shx[:24]+shp[24:28]+shx[28:100]
  assert b''.join(map(bits,rd.bbox))==shp[36:68]
  n,hlen,rlen=struct.unpack_from('<IHH',dbf,4);assert (hlen-33)%32==0 and dbf[hlen-1]==13 and len(dbf)>=hlen+n*rlen
  schema=[]
  for o in range(32,hlen-1,32):
   raw=dbf[o:o+32];schema.append({'name':raw[:11].split(b'\0')[0].decode(encoding),'type':chr(raw[11]),'width':raw[16],'decimals':raw[17],'descriptor_sha256':sha(raw)})
  assert sum(f['width'] for f in schema)+1==rlen and len(rd.fields)-1==len(schema)
  for ours,theirs in zip(schema,rd.fields[1:]):assert [ours['name'],ours['type'],ours['width'],ours['decimals']]==list(theirs)
  cells=0;records=[];deleted=0
  for i in range(n):
   raw=dbf[hlen+i*rlen:hlen+(i+1)*rlen];flag=raw[0:1];assert flag in [b' ',b'*'];offset=1;row=[];observed=rd.record(i)
   for j,f in enumerate(schema):
    vraw=raw[offset:offset+f['width']];offset+=f['width'];value=field_value(vraw,f['type'],f['decimals']);row.append({'column':j,'raw_sha256':sha(vraw),'value':str(value) if hasattr(value,'isoformat') else value});cells+=1
    if flag==b' ':
     if isinstance(value,float):assert bits(value)==bits(observed[j])
     else:assert value==observed[j],(key,i,f['name'],value,observed[j])
   if flag==b'*':deleted+=1;assert observed is None
   records.append({'record':i,'offset':hlen+i*rlen,'deletion_marker':flag.decode(),'sha256':sha(raw),'cells':row})
  assert len(shx)>=100 and (len(shx)-100)%8==0;index_count=(len(shx)-100)//8;assert index_count==n==len(rd)
  pos=100;shapes=[];xy=0;parts_count=0;stream=hashlib.sha256();adapter_stream=hashlib.sha256();open_rings=0;short_rings=0
  for i in range(n):
   offset,words=struct.unpack_from('>ii',shx,100+8*i);assert offset*2==pos
   num,length=struct.unpack_from('>ii',shp,pos);assert num==i+1 and length==words
   rec=shp[pos+8:pos+8+length*2];assert len(rec)==length*2;typ=struct.unpack_from('<i',rec)[0];obj=rd.shape(i);assert obj.shapeType==typ
   partlist=[];points=[];box=None;np=0;nr=0
   if typ in [3,5,13,15,23,25]:
    box=list(struct.unpack_from('<4d',rec,4));nr,np=struct.unpack_from('<ii',rec,36);partlist=list(struct.unpack_from('<'+'i'*nr,rec,44));start=44+4*nr;assert start+16*np<=len(rec);assert partlist==list(obj.parts)
    assert not partlist or (partlist[0]==0 and partlist==sorted(partlist) and partlist[-1]<=np)
    assert b''.join(map(bits,obj.bbox))==rec[4:36]
    for j in range(np):
     raw=rec[start+16*j:start+16*(j+1)];p=list(struct.unpack('<2d',raw));points.append(p);observed=b''.join(map(bits,obj.points[j][:2]));assert raw==observed;stream.update(raw);xy+=2
    ends=partlist[1:]+[np]
    for st,en in zip(partlist,ends):
     ring=points[st:en];open_rings+=bool(ring and ring[0]!=ring[-1]);short_rings+=len(ring)<4
    if points:
     adapter=shapefile.Shape(shapeType=typ,points=points,parts=partlist,bbox=box)
     assert list(adapter.parts)==partlist and len(adapter.points)==np
     for orig,adapt in zip(points,adapter.points):assert b''.join(map(bits,orig))==b''.join(map(bits,adapt));adapter_stream.update(b''.join(map(bits,adapt)))
    # Preserve all trailing Z/M bytes; compare every stored ordinate when represented by PyShp.
    cursor=start+16*np
    for lane,required in [('z',typ in [13,15]),('m',typ in [13,15,23,25])]:
     if not required:continue
     if lane=='m' and cursor==len(rec):continue
     assert cursor+16+8*np<=len(rec);values=struct.unpack_from('<'+'d'*np,rec,cursor+16);actual=getattr(obj,lane)
     for v,w in zip(values,actual):assert (w is None and v < -1e38) or bits(v)==bits(w)
     cursor+=16+8*np
    assert cursor==len(rec)
   elif typ==0:assert len(rec)==4 and not obj.points
   else:raise ValueError('Unimplemented actual shape type '+str(typ))
   shapes.append({'record':i,'record_number':num,'shp_offset':pos,'shx_offset_words':offset,'content_words':words,'shape_type':typ,'parts':partlist,'positions':np,'bbox':box,'record_sha256':sha(rec)})
   parts_count+=nr;pos+=8+length*2
  assert pos==len(shp) and stream.digest()==adapter_stream.digest()
  layer={'stem':stem,'records':n,'dbf_schema':schema,'dbf_header_bytes':hlen,'dbf_record_bytes':rlen,'dbf_cells_checked':cells,'dbf_deleted_records':deleted,'dbf_trailer_hex':dbf[hlen+n*rlen:].hex(),'dbf_records':records,'shp_shx_records':shapes,'xy_IEEE754_values_checked':xy,'raw_xy_stream_sha256':stream.hexdigest(),'adapter_xy_stream_sha256':adapter_stream.hexdigest(),'parts_checked':parts_count,'open_rings_preserved':open_rings,'short_rings_preserved':short_rings,'prj':prj.decode('utf-8','replace') if prj else None,'cpg':cpg.decode('utf-8','replace') if cpg else None,'geometry_source':{'request':out['request'],'member':name},'null_empty_repair':False,'orphan_hole_reinterpretation':False}
  out['layers'].append(layer)
 return out

def main():
 results=[]
 for p in sorted((M/'requests').glob('*.json')):
  r=load(str(p.relative_to(S)));b=body_of(r)
  if b[:4]!=b'PK\x03\x04':continue
  a=audit_zip(r['key'],b);save('maps/qa/binary-'+r['key']+'.json.gz',a);results.append({'request':a['request'],'audit':'maps/qa/binary-'+r['key']+'.json.gz','layers':[{k:l[k] for k in ['stem','records','dbf_cells_checked','xy_IEEE754_values_checked','open_rings_preserved','short_rings_preserved','prj']} for l in a['layers']]})
 save('maps/qa/binary-summary.json',results);print(json.dumps(results))
if __name__=='__main__':main()
