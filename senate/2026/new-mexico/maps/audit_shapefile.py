"""Independent native binary reader compared against installed PyShp, no GIS writes."""
from common import *
import struct,zipfile,io,zlib,shapefile,collections,math,html,inspect
from shapely.geometry import Polygon,Point,MultiPolygon
from shapely.validation import explain_validity
import shapely

def unpack(fmt,b,off=0):return struct.unpack_from(fmt,b,off)
def dbf_native(b):
 n,header,recsize=unpack('<IHH',b,4);fields=[]
 for off in range(32,header-1,32):
  raw=b[off:off+32];name=raw[:11].split(b'\0')[0].decode('ascii');fields.append({'name':name,'type':chr(raw[11]),'length':raw[16],'decimals':raw[17],'descriptor_hex':raw.hex()})
 assert b[header-1]==13 and 1+sum(x['length']for x in fields)==recsize
 rows=[]
 for i in range(n):
  raw=b[header+i*recsize:header+(i+1)*recsize];assert len(raw)==recsize;cells=[];pos=1;values=[]
  for f in fields:
   cell=raw[pos:pos+f['length']];pos+=f['length'];text=cell.decode('utf-8');literal=text.strip()
   if f['type']=='C':v=text.strip().rstrip('\x00')
   elif f['type']in ('N','F'):v=None if not literal or literal.startswith('*')else float(literal)if f['decimals']else int(literal)
   else:raise AssertionError(f)
   cells.append({'raw_hex':cell.hex(),'literal':text,'value':v});values.append(v)
  rows.append({'deletion_flag_hex':raw[:1].hex(),'cells':cells,'values':values})
 return fields,rows,{'header_bytes':header,'record_bytes':recsize,'record_count':n,'complete_header_hex':b[:header].hex(),'trailer_hex':b[header+n*recsize:].hex()}

def native_shapes(shp,shx):
 assert unpack('>i',shp)[0]==9994 and unpack('>i',shp,24)[0]*2==len(shp)
 assert unpack('>i',shx,24)[0]*2==len(shx);assert shp[:24]==shx[:24]and shp[28:100]==shx[28:100]
 assert unpack('<ii',shp,28)==(1000,5)
 rows=[];off=100
 while off<len(shp):
  number,words=unpack('>ii',shp,off);content=shp[off+8:off+8+words*2];kind=unpack('<i',content)[0];assert kind==5
  bbox=unpack('<4d',content,4);np,nv=unpack('<ii',content,36);parts=list(unpack('<'+str(np)+'i',content,44));start=44+4*np
  xy=content[start:start+nv*16];assert len(content)==start+nv*16;points=list(struct.iter_unpack('<dd',xy))
  index=unpack('>ii',shx,100+8*len(rows));assert index==(off//2,words);assert number==len(rows)+1
  rows.append({'record_number':number,'offset_bytes':off,'content_words':words,'bbox':bbox,'bbox_hex':content[4:36].hex(),'parts':parts,'point_count':nv,'xy_bytes_sha256':sha(xy),'record_content_sha256':sha(content),'shape_type':kind,'points':points})
  off+=8+words*2
 assert off==len(shp)and len(shx)==100+8*len(rows);return rows

def topology(r):
 points=r['points'];parts=r['parts']+[len(points)];rings=[points[a:b]for a,b in zip(parts,parts[1:])];openrings=[i for i,x in enumerate(rings)if not x or x[0]!=x[-1]]
 short=[i for i,x in enumerate(rings)if len(x)<4];nonfinite=any(not math.isfinite(v)for p in points for v in p)
 out={'ring_count':len(rings),'open_rings':openrings,'short_rings':short,'nonfinite':nonfinite,'linear_only':True,'native_units':'degrees','geometry_repair':False}
 if openrings or short or nonfinite:return dict(out,topology_status='skipped_native_ring_defect'),rings
 signed=[sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(ring,ring[1:]))/2 for ring in rings]
 shells=[(i,Polygon(ring))for i,ring in enumerate(rings)if signed[i]<0];holes=[i for i,a in enumerate(signed)if a>=0];assigned=collections.defaultdict(list);orphan=[]
 for i in holes:
  containers=[(abs(p.area),j)for j,p in shells if p.covers(Point(rings[i][0]))]
  if containers:assigned[min(containers)[1]].append(rings[i])
  else:orphan.append(i)
 out.update(signed_ring_areas_native=signed,orphan_hole_indices=orphan,shell_count=len(shells))
 if orphan:return dict(out,topology_status='skipped_orphan_holes_no_reinterpretation'),rings
 ps=[Polygon(rings[j],assigned[j])for j,p in shells];g=MultiPolygon(ps)if len(ps)>1 else ps[0]if ps else Polygon()
 out.update(topology_status='diagnostic_only',empty=g.is_empty,valid=g.is_valid,reason=explain_validity(g),area_native_square_degrees=g.area)
 return out,rings

def preview(year,bycounty):
 out=[]
 for county,features in bycounty.items():
  pts=[p for r,rings in features for p in r['points']];xmin=min(p[0]for p in pts);xmax=max(p[0]for p in pts);ymin=min(p[1]for p in pts);ymax=max(p[1]for p in pts);cx=math.cos(math.radians((ymin+ymax)/2));w=(xmax-xmin)*cx;h=ymax-ymin;scale=min(1100/max(w,1e-20),780/max(h,1e-20))
  paths=[]
  for r,rings in features:
   ds=[]
   for ring in rings:
    if not ring:continue
    ds.append('M'+' L'.join(f'{(x-xmin)*cx*scale+40:.2f},{(ymax-y)*scale+70:.2f}'for x,y in ring)+(' Z'if ring[0]==ring[-1]else''))
   paths.append('<path d="'+' '.join(ds)+'"><title>'+html.escape(str(r['record_number']))+'</title></path>')
  p=M/'previews'/year/(county+'.svg');p.parent.mkdir(parents=True,exist_ok=True);p.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900"><rect width="1200" height="900" fill="#f7f7f2"/><text x="40" y="30" font-family="sans-serif" font-size="22">'+html.escape(year+' RGIS county '+county+' • '+str(len(features))+' native features')+'</text><text x="40" y="55" font-family="sans-serif" font-size="14">Geographic preview; no historical-result/current/legal identity established</text><g fill="#d6e7ed" fill-rule="evenodd" stroke="#24546b" stroke-width="0.5">'+''.join(paths)+'</g></svg>')
  out.append({'county_fips':county,'count':len(features),'preview':pin(p)})
 return out

def run():
 inspection=inspect.getsource(shapefile.Shape.__init__);(M/'pyshp-constructor-inspection.txt').write_text('Installed PyShp '+shapefile.__version__+'\n\n'+inspection+'\n'+inspect.getsource(shapefile.Writer.poly))
 pts=[[0.,0.],[0.,1.],[1.,1.],[1.,0.]];assert len(shapefile.Shape(shapeType=5,points=pts,parts=[0]).points)==4;assert len(shapefile.Shape(shapeType=5,lines=[pts]).points)==5
 outputs=[]
 for year in ['2024','2026']:
  name='rgis-'+year+'-zip';raw=original(name);z=zipfile.ZipFile(io.BytesIO(raw));members=[]
  for m in z.infolist():
   b=z.read(m.filename);assert zlib.crc32(b)&0xffffffff==m.CRC
   members.append({'name':m.filename,'CRC32':m.CRC,'uncompressed_bytes':len(b),'compressed_bytes':m.compress_size,'sha256':sha(b),'zip_info':{'date_time':m.date_time,'compress_type':m.compress_type,'flag_bits':m.flag_bits,'external_attr':m.external_attr,'extra_hex':m.extra.hex(),'comment_hex':m.comment.hex()}})
  names={Path(x.filename).suffix:x.filename for x in z.infolist()if not x.is_dir()};bs={ext:z.read(names[ext])for ext in ['.shp','.shx','.dbf']};fields,dbf,header=dbf_native(bs['.dbf']);shapes=native_shapes(bs['.shp'],bs['.shx'])
  reader=shapefile.Reader(shp=io.BytesIO(bs['.shp']),shx=io.BytesIO(bs['.shx']),dbf=io.BytesIO(bs['.dbf']));assert len(reader)==len(dbf)==len(shapes)
  for f,g in zip(fields,reader.fields[1:]):assert (f['name'],f['type'],f['length'],f['decimals'])==(g.name,str(g.field_type),g.size,g.decimal)
  records=[];bycounty=collections.defaultdict(list);xycount=0
  for i,(r,d)in enumerate(zip(shapes,dbf)):
   shp=reader.shape(i);assert list(shp.parts)==r['parts']and len(shp.points)==r['point_count'];assert b''.join(struct.pack('<dd',*p)for p in shp.points)==b''.join(struct.pack('<dd',*p)for p in r['points']);assert struct.pack('<4d',*shp.bbox).hex()==r['bbox_hex'];assert list(reader.record(i))==d['values']
   # Raw points/parts adapter tested to avoid lines= auto-closure. No __geo_interface__ hole rewrite.
   adapted=shapefile.Shape(shapeType=5,points=r['points'],parts=r['parts'],bbox=r['bbox']);assert list(adapted.parts)==r['parts']and adapted.points==r['points']
   diag,rings=topology(r);attrs=dict(zip([f['name']for f in fields],d['values']));county=attrs['STATE']+attrs['COUNTY_FIP'];bycounty[county].append((r,rings));xycount+=r['point_count']
   records.append({**{k:v for k,v in r.items()if k!='points'},'dbf':d,'all_attributes':attrs,'diagnostics':diag})
  result={'year':year,'original_receipt':pin(M/'receipts'/(name+'.json')),'members':members,'zip_comment_hex':z.comment.hex(),'schema':fields,'DBF':header,'SHP_header_hex':bs['.shp'][:100].hex(),'SHX_header_hex':bs['.shx'][:100].hex(),'native_CRS_WKT':z.read(names['.prj']).decode(),'records':records,'feature_count':len(shapes),'XY_pairs_compared_bitwise':xycount,'pyshp_version':shapefile.__version__,'independent_binary_reader':True,'constructor_open_ring_points_parts_preserved':True,'constructor_lines_autocloses':True,'Z_M':'not present in native Polygon type5','current_legal_join_approved':False,'same_vintage_independent_legal_outline':None,'gap_overlap_sliver_certification':None,'county_previews':preview(year,bycounty),'shapely_version':shapely.__version__}
  p=M/f'native-audit-{year}.json.gz';b=json.dumps(result,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode();p.write_bytes(gzip.compress(b,mtime=0));outputs.append({'year':year,'audit':pin(p),'feature_count':len(shapes),'counties':len(bycounty),'XY_pairs':xycount,'invalid':[r['record_number']for r in records if r['diagnostics'].get('valid')is False],'empty':[r['record_number']for r in records if r['diagnostics'].get('empty')],'open_ring_records':[r['record_number']for r in records if r['diagnostics']['open_rings']],'orphan_hole_records':[r['record_number']for r in records if r['diagnostics'].get('orphan_hole_indices')],'previews':result['county_previews'],'native_CRS':result['native_CRS_WKT']})
  print(year,len(shapes),xycount,'invalid',len(outputs[-1]['invalid']),flush=True)
 write(M/'native-audit-index.json',outputs)
if __name__=='__main__':run()
