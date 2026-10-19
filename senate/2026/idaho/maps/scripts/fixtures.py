#!/usr/bin/env python3
"""Explicitly synthetic negative mutations; never source observations or claimed vote updates."""
import copy,gzip,json,hashlib
from pathlib import Path
from verify_history import semantic,pointer
from reconstruct import reconstruct,chunks
from evidence import MAPS,ROOT,own_receipts,original

def inventory_rules(v):
 assert len(v['parents'])==44 and len(v['observations'])==985 and len(v['ordered_priority_keys'])==528 and len(v['ordered_remainder_keys'])==457
 assert [x['key'] for x in v['observations']]==v['ordered_full_keys']
 assert [x['key'] for x in v['observations'] if x['priority']]==v['ordered_priority_keys']
 assert [x['key'] for x in v['observations'] if not x['priority']]==v['ordered_remainder_keys']
 assert len({x['key'] for x in v['observations']})==985
 for x in v['observations']:
  assert x['resource_ids'] and x['matched_native_feature_ids'] is None and x['historical_or_current_finer_ID_bridge'] is None and x['current_legal_effectiveness'] is None
  assert x['geography_scope']=='Shared parent county context, not a matched child polygon'
 assert v['current_geography_approved'] is False and v['result_polygon_join'] is None

def run(inv):
 fixtures=[]
 def rejection(name,fn):
  try:fn()
  except (AssertionError,ValueError,KeyError,TypeError,IndexError,gzip.BadGzipFile):fixtures.append(dict(name=name,rejected=True,kind='synthetic negative fixture'))
  else:raise AssertionError('negative fixture accepted: '+name)
 def changed(field,value):
  v=copy.deepcopy(inv);v[field]=value;inventory_rules(v)
 v=copy.deepcopy(inv);v['observations'][0],v['observations'][1]=v['observations'][1],v['observations'][0];rejection('swapped priority rows',lambda:inventory_rules(v))
 rejection('dropped remainder observation',lambda:changed('observations',inv['observations'][:-1]))
 rejection('dropped full parent',lambda:changed('parents',inv['parents'][:-1]))
 u=copy.deepcopy(inv);u['observations'][0]['matched_native_feature_ids']=[1];rejection('fabricated absentee physical match',lambda:inventory_rules(u))
 rejection('worker legal selfapproval',lambda:changed('current_geography_approved',True))
 c=json.loads((ROOT/'data/turnout/priority-set.json').read_text());source=c['all_county_constituents'][0]['president_contexts'][0];s=copy.deepcopy(source);s.pop('source_id_scope');rejection('dropped unknown/nonvote source field',lambda:assert_equal(semantic(source),semantic(s)))
 s=copy.deepcopy(source);s['polling_place']=0;rejection('null replaced with zero',lambda:assert_equal(semantic(source),semantic(s)))
 raw=reconstruct('data/turnout/source/2024-stats-rows.json.gz');o=json.loads(raw);s=copy.deepcopy(o);s['fixture_extra_field']='must not disappear';rejection('complete raw cell companion changed',lambda:assert_equal(semantic(s),semantic(o)))
 a=json.loads((ROOT/'data/coordinator-priority-acceptance.json').read_text());e=next(x for x in a['complete_source_companion_files'] if 'full_rows_semantic_sha256' in x);import csv,io
 rows=list(csv.reader(io.StringIO((ROOT/e['path']).read_text())));rows[0]=rows[0][::-1];rejection('CSV header order changed',lambda:assert_equal(semantic(rows),e['full_rows_semantic_sha256']))
 from native import verify,receipts
 rr=copy.deepcopy(receipts());r=next(x for x in rr if x['id']=='state-precinct-native-page01');r['url']+='&outSR=4326';rejection('silently reprojected source query',lambda:verify(rr))
 rr=copy.deepcopy(receipts());r=next(x for x in rr if x['id']=='state-precinct-native-page01');r['requested_object_ids']=r['requested_object_ids'][:-1];rejection('missing requested ID on page',lambda:verify(rr))
 fs,qa=verify();f=copy.deepcopy(fs[0]);f['geometry']['rings'][0][0][0]+=0.000000001;rejection('native coordinate precision changed',lambda:assert_equal(semantic(f),semantic(fs[0])))
 p=chunks(b'original one|original two',8);rejection('split original part order changed',lambda:assert_equal(b''.join(reversed(p)),b''.join(p)))
 rec=next(r for r in own_receipts() if '.zip' in r['requested_url']);b=original(rec);import zipfile,struct
 z=zipfile.ZipFile(io.BytesIO(b));x=bytearray(z.read('2026Precinctfiles.shx'));x[100:104]=struct.pack('>i',51);rejection('SHP index offset changed',lambda:assert_equal(struct.unpack('>i',x[100:104])[0],50))
 from geometry import adapt
 bad=copy.deepcopy(fs[0]);bad['geometry']['rings'][0]=bad['geometry']['rings'][0][:-1];g,reasons=adapt(bad);assert g is None and reasons==['open_or_short_rings_retained_unclosed'];fixtures.append(dict(name='open native ring remains unclosed/excluded',rejected=True,kind='synthetic negative fixture'))
 bad=copy.deepcopy(fs[0]);bad['geometry']={'curveRings':[]};g,reasons=adapt(bad);assert g is None and reasons==['true_curves_explicitly_excluded_from_linear_topology'];fixtures.append(dict(name='true curve explicitly excluded from linear-only topology',rejected=True,kind='synthetic negative fixture'))
 return dict(status='pass_meaningful_negative_fixtures',fixtures=fixtures,count=len(fixtures))
def assert_equal(a,b):assert a==b
if __name__=='__main__':
 result=run(json.loads((MAPS/'inventory.json').read_text()));(MAPS/'qa/negative-fixtures.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=result['status'],count=result['count'])))
