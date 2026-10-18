#!/usr/bin/env python3
"""Offline audits all ID batches, transfer flags and native format controls.
Server attribute differences are observational and preserved; geometry source is original GPKG.
"""
import sys
sys.dont_write_bytecode=True
import json,sqlite3,collections,gzip,hashlib,re
from pathlib import Path
from acquire import ROOT,read,sha

def raw(k):return read(json.loads((ROOT/'evidence'/f'{k}.request.json').read_text()))
def doc(k):return json.loads(raw(k))
def save(p,d): (ROOT/p).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
summary={};differences=[]
for key,native,table in [('current','current','bdry_votingdistricts'),('results','results','general_election_results_by_precinct_2024'),('results2022','results','general_election_results_by_precinct_2022')]:
 c=sqlite3.connect(':memory:');c.deserialize(raw(native+'-gpkg'));fields=[x[1] for x in c.execute('pragma table_info('+table+')')];rr=c.execute('select * from '+table).fetchall();byid={dict(zip(fields,r))['VTDID']:dict(zip(fields,r)) for r in rr};pre=doc(key+'-ids-pre');post=doc(key+'-ids-post');ids=pre['objectIds'];assert len(ids)==len(set(ids));assert sorted(ids)==sorted(post['objectIds']);nativeoids=sorted(r[0] for r in rr);batches=[];allrows=[]
 for p in sorted((ROOT/'evidence').glob(key+'-attributes-*.request.json')):
  m=json.loads(p.read_text());d=json.loads(read(m));requested=[int(v) for v in m['params']['objectIds'].split(',')];got=[r['attributes'][pre['objectIdFieldName']] for r in d['features']]
  assert sorted(requested)==sorted(got);assert d.get('exceededTransferLimit') is not True;assert 'error' not in d
  batches.append({'request_path':str(p.relative_to(ROOT)),'requested_ids':requested,'received_ids':got,'exceededTransferLimit_present':'exceededTransferLimit' in d,'exceededTransferLimit':d.get('exceededTransferLimit'),'f':'json','returnGeometry':False,'geometry_source':'native original GPKG; no geometry fetched in attribute batches'})
  allrows.extend(r['attributes'] for r in d['features'])
 gotids=[r[pre['objectIdFieldName']] for r in allrows];assert sorted(gotids)==sorted(ids)==nativeoids
 matched=0;fieldmap={f.lower():f for f in fields if f!='Shape'};fieldmap['shape__area']='Shape_Area';fieldmap['shape__length']='Shape_Length'
 for r in allrows:
  native_r=byid[r['vtdid']]
  for f,v in r.items():
   target=fieldmap.get(f.lower())
   if target is None:differences.append({'layer':key,'VTDID':r['vtdid'],'server_field':f,'native_field':None,'server':v,'reason':'unmapped source field'})
   elif native_r[target]!=v: differences.append({'layer':key,'VTDID':r['vtdid'],'server_field':f,'native_field':target,'server':v,'native':native_r[target]})
   else:matched+=1
 summary[key]={'pre_count':doc(key+'-count-pre')['count'],'post_count':doc(key+'-count-post')['count'],'native_count':len(rr),'pre_ids':ids,'post_ids':post['objectIds'],'native_object_ids':nativeoids,'all_ids_equal':True,'duplicates':len(gotids)-len(set(gotids)),'batches':batches,'attribute_equal_fields':matched,'native_vs_service_attribute_differences':sum(d['layer']==key for d in differences),'scope':'Controls bracket attribute batch acquisition, not the earlier native GPKG download. Equal IDs/counts do not prove transactional coherence or unchanged geometry.'}
 assert summary[key]['pre_count']==summary[key]['post_count']==len(rr)
wc=doc('waconia-native');layer=doc('waconia-layer');pre=doc('waconia-ids-pre');post=doc('waconia-ids-post');oids=[f['attributes'][layer['objectIdField']] for f in wc['features']];assert sorted(oids)==sorted(pre['objectIds'])==sorted(post['objectIds']);assert not wc.get('exceededTransferLimit',False)
summary['waconia']={'feature_count':len(oids),'native_CRS':wc['spatialReference'],'native_units':layer['geometryProperties']['units'],'hasZ':layer['hasZ'],'hasM':layer['hasM'],'raw_geometry_keys':[list(f['geometry']) for f in wc['features']],'linear_rings_vertex_count':sum(len(r) for f in wc['features'] for r in f['geometry'].get('rings',[])),'curveRings_present':any('curveRings' in f['geometry'] for f in wc['features']),'pre_ids':pre['objectIds'],'post_ids':post['objectIds'],'acquired_ids':oids,'all_ids_equal':True,'exceededTransferLimit':wc.get('exceededTransferLimit'),'schema_request':'evidence/waconia-layer.request.json','original_request':'evidence/waconia-native.request.json','native_precision':'All response entity bytes retained, no outSR/geometryPrecision/maxAllowableOffset/quantization requested. No inference about hidden server storage precision.','editingInfo':layer['editingInfo']}
curve_counts=collections.Counter()
for f in wc['features']:
 for ring in f['geometry'].get('curveRings',[]):
  for segment in ring:
   if isinstance(segment,dict):curve_counts.update(segment.keys())
summary['waconia']['native_curve_segment_types']=dict(curve_counts)
summary['waconia']['native_curve_topology']='Not evaluated by GEOS; no flattening of original curveRings. Linearized preview topology is derivative only.'
linear=doc('waconia-preview-linearized');assert sorted(f['attributes'][layer['objectIdField']] for f in linear['features'])==sorted(oids)
assert [f['attributes'] for f in linear['features']]==[f['attributes'] for f in wc['features']]
summary['waconia']['linearized_preview']={'request':'evidence/waconia-preview-linearized.request.json','vertex_positions':sum(len(r) for f in linear['features'] for r in f['geometry'].get('rings',[])),'scope':'server returnTrueCurves=false separate derivative; densification tolerance unknown; original curveRings retained'}
save('service-audit.json',summary);save('service-attribute-differences.json',differences)
print('ID/count/batch controls PASS', {k:(v.get('native_count',v.get('feature_count')),v.get('native_vs_service_attribute_differences')) for k,v in summary.items()})
