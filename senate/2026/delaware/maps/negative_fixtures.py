"""Meaningful corrupted-data and source-defect tests; synthetic only."""
from common import *
import copy,io,struct,zipfile,zlib
from audit_geometry import diagnostics
import shapefile

def batch_check(wanted,got,attributes,fields,query):
 assert len(wanted)<=50 and len(wanted)==len(set(wanted))
 assert len(got)==len(set(got))==len(wanted) and set(got)==set(wanted)
 assert all(set(a)==set(fields) for a in attributes)
 assert not set(query)&{'outSR','geometryPrecision','quantizationParameters','maxAllowableOffset','resultOffset','resultRecordCount'}
def fixture_test():
 tests=[]
 def rejects(name,fn):
  try:fn()
  except (AssertionError,zipfile.BadZipFile,zlib.error,ValueError):tests.append(dict(name=name,status='rejected'));return
  raise AssertionError('negative fixture accepted: '+name)
 base=dict(wanted=[1,2],got=[1,2],attributes=[{'id':1,'null_field':None},{'id':2,'null_field':None}],fields=['id','null_field'],query={'outFields':'*'})
 batch_check(**base)
 for name,changes in [('same-count-wrong-ID',{'got':[1,3]}),('duplicate-ID',{'got':[1,1]}),('truncated-page',{'got':[1]}),('over-50-ID-page',{'wanted':list(range(51))}),('lost-null-attribute',{'attributes':[{'id':1},{'id':2,'null_field':None}]}),('server-reprojection',{'query':{'outSR':'4326'}}),('server-quantization',{'query':{'quantizationParameters':'{}'}}),('server-generalization',{'query':{'maxAllowableOffset':'10'}})]:
  x=copy.deepcopy(base);x.update(changes);rejects(name,lambda x=x:batch_check(**x))
 contract=read(S/read(M/'source/frozen-references.json.gz')['contract']['path']);order=contract['ordered_priority_keys'];altered=order[:];altered[0],altered[1]=altered[1],altered[0]
 rejects('priority-order-mutated',lambda:assert_equal(altered,order))
 complete={'candidate':'A','votes':1,'party':None,'raw_fields':{'Machine':'1'},'position':52};projection={'candidate':'A','votes':1}
 rejects('vote-only-projection',lambda:assert_equal(semantic(complete),semantic(projection)))
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w',compression=zipfile.ZIP_STORED)as z:z.writestr(zipfile.ZipInfo('full-member.bin',date_time=(2000,1,1,0,0,0)),b'not-an-election-source')
 damaged=bytearray(b.getvalue());name_len,extra_len=struct.unpack_from('<HH',damaged,26);damaged[30+name_len+extra_len]^=1
 rejects('member-CRC-corruption',lambda:zipfile.ZipFile(io.BytesIO(damaged)).read('full-member.bin'))
 # Constructor preservation: open lines and polygon rings remain exactly open with points/parts.
 points=[[0.,0.],[1.,0.],[1.,1.]]
 line=shapefile.Shape(shapeType=3,points=copy.deepcopy(points),parts=[0]);poly=shapefile.Shape(shapeType=5,points=copy.deepcopy(points),parts=[0]);assert line.points==poly.points==points
 tests.append(dict(name='open-lines-and-rings-not-auto-closed',status='preserved'))
 cases=[dict(attributes={'OBJECTID':1},geometry=None),dict(attributes={'OBJECTID':2},geometry={}),dict(attributes={'OBJECTID':3},geometry={'curveRings':[[[0,0],{'c':[[2,0],[1,1]]}]]}),dict(attributes={'OBJECTID':4},geometry={'rings':[[[0,0],[1,0],[1,1],[0,1],[0,0]]]}),dict(attributes={'OBJECTID':5},geometry={'rings':[[[0,0],[1,1],[0,1],[1,0],[0,0]]]}),dict(attributes={'OBJECTID':6},geometry={'rings':[points]})]
 before=semantic(cases);d=diagnostics(cases);assert semantic(cases)==before
 assert d['features'][0]['null_geometry'] and d['features'][1]['empty_geometry'] and d['features'][2]['curve_rings'];assert d['features'][3]['orphan_positive_rings']==[0];assert not d['features'][4]['rings'][0]['ring_valid'];assert not d['features'][5]['rings'][0]['closed']
 tests.append(dict(name='null-empty-truecurve-orphan-invalid-open-source-defects-retained',status='preserved'))
 return dict(status='pass',synthetic_only=True,tests=tests,source_defect_fixtures=cases,diagnostic_observations=d,corrupt_zip_fixture_hex=damaged.hex())
def assert_equal(a,b):assert a==b
if __name__=='__main__':
 result=fixture_test();write('qa/negative-fixtures.json',result);print('PASS',len(result['tests']),'negative/preservation fixtures')
