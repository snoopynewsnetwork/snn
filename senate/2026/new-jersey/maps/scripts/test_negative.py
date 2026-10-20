from acquire import *
from native_checks import *
from native_preview import geometry_diagnostics
import copy,io,zipfile,struct,shapefile
import audit_shp

def run():
 tests=[]
 def negative(name,fun):
  try:fun()
  except (AssertionError,KeyError,zipfile.BadZipFile,ValueError,struct.error,IndexError) as e:tests.append({'name':name,'status':'rejected_expected_corruption','error_type':type(e).__name__});return
  raise AssertionError('failed to reject: '+name)
 name='state-election-service';m=json.loads(content(name+'-layer-pre'));o=json.loads(content(name+'-batch-0000'));r=json.loads((BASE/'receipts'/f'{name}-batch-0000.json').read_bytes());p=r['query'];ids=check_params(p);assert check_batch(m,o,ids)==[f['attributes']['OBJECTID'] for f in o['features']]
 for key,value in [('outSR','4326'),('outCRS','EPSG:4326'),('geometryPrecision','6'),('quantizationParameters','{}'),('maxAllowableOffset','1'),('returnTrueCurves','false'),('returnZ','false'),('returnM','false'),('outFields','OBJECTID')]:
  bad=copy.deepcopy(p);bad[key]=value;negative('reject_native_transform_or_projection_'+key,lambda bad=bad:check_params(bad))
 bad=copy.deepcopy(p);bad['objectIds']=','.join(map(str,range(51)));negative('reject_batch_over50',lambda:check_params(bad))
 for label,change in [('missing',lambda b:b['features'].pop()),('duplicate',lambda b:b['features'].append(copy.deepcopy(b['features'][0]))),('unexpected',lambda b:b['features'][0]['attributes'].__setitem__('OBJECTID',999999999)),('selected_attribute_projection',lambda b:b['features'][0]['attributes'].pop('COUNTY')),('transfer_limit',lambda b:b.__setitem__('exceededTransferLimit',True)),('HTTP200_JSON_error',lambda b:b.__setitem__('error',{'code':400,'message':'not genuine data'})),('wrong_native_CRS',lambda b:b['spatialReference'].__setitem__('wkid',4326))]:
  bad=copy.deepcopy(o);change(bad);negative('reject_'+label,lambda bad=bad:check_batch(m,bad,ids))
 for name in ['state-election-service','burlington-election-service']:
  meta=json.loads(content(name+'-meta-pre'));layer=json.loads(content(name+'-layer-pre'));count=json.loads(content(name+'-count-pre'))['count'];allids=json.loads(content(name+'-ids-pre'))['objectIds'];bad=copy.deepcopy(layer);bad['name']='mutated'
  negative(name+'_changed_full_metadata',lambda:check_snapshot(meta,meta,layer,bad,count,count,allids,allids))
  for batch in json.loads((BASE/'qa'/f'{name}-native-contract.json').read_bytes())['batches']:
   rr=json.loads((BASE/'receipts'/f"{batch['receipt']}.json").read_bytes());requested=check_params(rr['query']);assert requested==batch['requested_ids'];check_batch(layer,json.loads(content(batch['receipt'])),requested)
 # Preserve invalid/curve/empty/null objects exactly. Diagnostics never call a polygon constructor.
 examples=[None,{'rings':[]},{'rings':[[[0,0],[1,0],[1,1]]]},{'curveRings':[[[0,0],{'c':[[1,1],[0,1]]}]]},{'rings':[[],[[0,0],[0,0],[1,1],[0,0]]]}]
 for x in examples:
  before=copy.deepcopy(x);geometry_diagnostics(x);assert x==before
 tests.append({'name':'null_empty_unclosed_curve_orphanlike_parts_unchanged','status':'pass'})
 # Byte-corruption/offset/schema/constructor fixtures use a complete small hand-assembled
 # ZIP with one explicitly unclosed ring; no polygon writer/repair is used.
 def fixture():
  fields=[('STATEFP20','C',2),('COUNTYFP20','C',3)];pts=[(0.,0.),(1.,0.),(1.,1.)];bb=(0.,0.,1.,1.);geom=struct.pack('<i4d2ii',5,*bb,1,3,0)+b''.join(struct.pack('<2d',*p) for p in pts)
  def header(size):return struct.pack('>7i',9994,0,0,0,0,0,size//2)+struct.pack('<2i8d',1000,5,*bb,0.,0.,0.,0.)
  shp=header(108+len(geom))+struct.pack('>2i',1,len(geom)//2)+geom;shx=header(108)+struct.pack('>2i',50,len(geom)//2);dbf=bytearray(32);dbf[0]=3;struct.pack_into('<IHH',dbf,4,1,97,6)
  for nm,tp,sz in fields:
   f=bytearray(32);f[:len(nm)]=nm.encode();f[11]=ord(tp);f[16]=sz;dbf+=f
  dbf+=b'\r 34001\x1a';return {'shp':shp,'shx':shx,'dbf':bytes(dbf)}
 f=fixture();rd=shapefile.Reader(shp=io.BytesIO(f['shp']),shx=io.BytesIO(f['shx']),dbf=io.BytesIO(f['dbf']));s=rd.shape(0);assert len(s.points)==3 and s.points[0]!=s.points[-1]
 tests.append({'name':'inspected_reader_points_parts_path_does_not_close_actual_unclosed_fixture','status':'pass','points':3})
 def mini_audit(f):
  off,ln=struct.unpack_from('>2i',f['shx'],100);assert off==50;assert ln*2+108==len(f['shp']);assert struct.unpack_from('<I',f['dbf'],4)[0]==1
  rdr=shapefile.Reader(shp=io.BytesIO(f['shp']),shx=io.BytesIO(f['shx']),dbf=io.BytesIO(f['dbf']));pts=rdr.shape(0).points;assert b''.join(struct.pack('<2d',*p) for p in pts)==f['shp'][156:]
 bad=copy.deepcopy(f);buf=bytearray(bad['shx']);struct.pack_into('>i',buf,100,51);bad['shx']=bytes(buf);negative('SHP_SHX_offset_corruption',lambda:mini_audit(bad))
 bad=copy.deepcopy(f);buf=bytearray(bad['dbf']);struct.pack_into('<I',buf,4,2);bad['dbf']=bytes(buf);negative('DBF_row_count_corruption',lambda:mini_audit(bad))
 # Any adapter that silently closes would fail the exact original IEEE byte comparison.
 badpoints=[list(p) for p in s.points]+[list(s.points[0])];negative('auto_closing_adapter_detected',lambda:assert_equal(b''.join(struct.pack('<2d',*p) for p in badpoints),f['shp'][156:]))
 # EntireZIP CRC verification, not only selected members.
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w',zipfile.ZIP_STORED) as z:z.writestr('first',b'abcd');z.writestr('unselected-companion',b'efgh')
 zz=bytearray(b.getvalue());start=zz.index(b'efgh');zz[start]=ord('z')
 def crc():
  with zipfile.ZipFile(io.BytesIO(zz)) as z:
   for member in z.infolist():z.read(member.filename)
 negative('CRC_failure_in_unselected_companion',crc)
 out={'status':'pass','fixtures':tests,'fixture_count':len(tests),'native_real_batches_checked':sum(len(json.loads((BASE/'qa'/f'{n}-native-contract.json').read_bytes())['batches']) for n in ['state-election-service','burlington-election-service']),'no_source_mutation':True};write(BASE/'qa/negative-fixtures.json',out);print({'fixtures':len(tests),'status':'pass'})
def assert_equal(a,b):assert a==b
if __name__=='__main__':run()
