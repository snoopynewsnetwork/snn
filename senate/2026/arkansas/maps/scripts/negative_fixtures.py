"""Full actual source packets, not projected synthetic vote fixtures. Reject all corruption."""
from pathlib import Path
import copy,gzip,json,sys
from build import ROOT,STATE,load,native,dumps

def original_packet():
 return {'contract':load((STATE/'data/turnout/priority-set.json').read_bytes()),'complete_companion':load((STATE/'data/baselines/source/candidate-metadata.json').read_bytes()),'native_page':load(native('native-page-0000')[0]),'native_receipt':native('native-page-0000')[1],'layer_metadata':load(native('precinct-layer-pre')[0]),'service_metadata':load(native('boundaries-service-pre')[0]),'all_IDs':load(native('precinct-ids-pre')[0]),'count':load(native('precinct-count-pre')[0]),'policy':{'authority_path':'data/coordinator-priority-acceptance.json','source_scope':'whole historical source objects plus actual native snapshot; not a current admission','result_polygon_join':None,'spatial_allocation':False,'county_substitute':False,'residual_allocation':False,'current_admission':False}}
def exact(v,expected,p=''):
 if type(v)!=type(expected):raise ValueError('type/null mismatch '+p)
 if isinstance(v,dict):
  if list(v)!=list(expected):raise ValueError('whole object fields/order mismatch '+p)
  for k in expected:exact(v[k],expected[k],p+'/'+str(k))
 elif isinstance(v,list):
  if len(v)!=len(expected):raise ValueError('whole array count mismatch '+p)
  for i,(a,b) in enumerate(zip(v,expected)):exact(a,b,p+'/'+str(i))
 elif v!=expected:raise ValueError('source literal/value mismatch '+p)
def check(raw,expected):exact(load(raw),expected)
def cases():
 return [
 ('truncated-whole-source',lambda p:p['contract']['full_order'].pop()),
 ('truncated-whole-companion',lambda p:p['complete_companion'].pop()),
 ('missing-native-observation',lambda p:p['contract']['full_order'].pop(10)),
 ('missing-native-field',lambda p:p['contract']['full_order'][0].pop('source_pointer')),
 ('candidate-count',lambda p:p['contract']['full_order'][0]['candidates'].__setitem__(next(iter(p['contract']['full_order'][0]['candidates'])),0)),
 ('party-normalization',lambda p:p['contract']['full_order'][0]['party_literals'].__setitem__(next(iter(p['contract']['full_order'][0]['party_literals'])),'Democrat')),
 ('method-collapse',lambda p:p['contract']['full_order'][0]['methods'].pop('Absentee')),
 ('null-to-zero',lambda p:p['contract']['full_order'][0].__setitem__('ballots_cast',0)),
 ('admin-context',lambda p:p['contract']['all75parents'][0].pop('administrative_cases')),
 ('raw-source-positions',lambda p:p['contract']['full_order'][0]['source_rows'].reverse()),
 ('source-mask',lambda p:p['contract']['full_order'][0].__setitem__('unit_type','physical precinct')),
 ('header-trimming',lambda p:p['native_receipt']['headers'].__setitem__('bytes',0)),
 ('wrong-ID',lambda p:p['native_page']['features'][0]['attributes'].__setitem__('objectid',-1)),
 ('wrong-all-ID-count',lambda p:p['all_IDs']['objectIds'].pop()),
 ('wrong-count',lambda p:p['count'].__setitem__('count',2929)),
 ('wrong-CRS',lambda p:p['native_page']['spatialReference'].__setitem__('wkid',4326)),
 ('wrong-vintage',lambda p:p['layer_metadata'].__setitem__('description','Approved for November 2026')),
 ('full-order',lambda p:p['contract']['full_order'].reverse()),
 ('priority-order',lambda p:p['contract']['ordered_priority_keys'].reverse()),
 ('remainder-order',lambda p:p['contract']['remainder_keys'].reverse()),
 ('80-percent-crossing',lambda p:p['contract']['statistics'].__setitem__('minimum80_count',1055)),
 ('parent-child-array',lambda p:p['contract']['all75parents'][0]['source_native_constituents'].pop(next(iter(p['contract']['all75parents'][0]['source_native_constituents'])))),
 ('county-substitute',lambda p:p['policy'].__setitem__('county_substitute',True)),
 ('residual-allocation',lambda p:p['policy'].__setitem__('residual_allocation',True)),
 ('spatial-allocation',lambda p:p['policy'].__setitem__('spatial_allocation',True)),
 ('result-polygon-alias',lambda p:p['policy'].__setitem__('result_polygon_join',{'numeric_label':'same polygon'})),
 ('current-admission',lambda p:p['policy'].__setitem__('current_admission',True)),
 ('native-geometry-precision',lambda p:p['native_page']['features'][1]['geometry']['rings'][0][0].__setitem__(0,0)),
 ('native-geometry-part-loss',lambda p:p['native_page']['features'][0]['geometry']['curveRings'].pop()),
 ]
def run(write=False):
 expected=original_packet();base=dumps(expected).encode();check(base,expected);root=ROOT/'qa/fixtures'
 if write:root.mkdir(parents=True,exist_ok=True)
 receipts=[]
 for name,mutate in cases():
  p=copy.deepcopy(expected);mutate(p);raw=dumps(p).encode()
  try:check(raw,expected);raise AssertionError('accepted invalid packet '+name)
  except ValueError as e:out={'case':name,'status':'rejected','error':str(e)}
  f=root/(name+'.json.gz')
  if write:f.write_bytes(gzip.compress(raw,mtime=0));(root/(name+'.result.json')).write_text(dumps(out))
  else:
   assert gzip.decompress(f.read_bytes())==raw
   assert load((root/(name+'.result.json')).read_bytes())==out
  receipts.append(out)
 # Actual parser duplicate-key and truncated-JSON failures, preserving entire input.
 for name,raw in [('duplicate-keys',b'{"context":'+base+b',"context":'+base+b'}'),('truncated-JSON',base[:-13])]:
  try:check(raw,expected);raise AssertionError('accepted invalid JSON')
  except (ValueError,json.JSONDecodeError) as e:out={'case':name,'status':'rejected','error':str(e)}
  f=root/(name+'.json.gz')
  if write:f.write_bytes(gzip.compress(raw,mtime=0));(root/(name+'.result.json')).write_text(dumps(out))
  else:assert gzip.decompress(f.read_bytes())==raw and load((root/(name+'.result.json')).read_bytes())==out
  receipts.append(out)
 proof={'status':'pass','complete_actual_packet_positive':True,'negative_packets':len(receipts),'cases':receipts,'qualification':'These fixtures reject corrupted full immutable historical/native packets before current admission; no legal or physical identity is asserted.'}
 if write:(ROOT/'qa/negative-proof.json').write_text(dumps(proof))
 else:assert load((ROOT/'qa/negative-proof.json').read_bytes())==proof
 return proof
if __name__=='__main__':
 d=run('--write' in sys.argv);print('Positive whole packet accepted;',d['negative_packets'],'actual whole negative inputs rejected.')
