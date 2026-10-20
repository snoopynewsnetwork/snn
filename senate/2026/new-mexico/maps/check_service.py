"""Offline complete native service validation and unfiltered metadata differences."""
from common import *
import collections,math
from audit_shapefile import topology

def differences(a,b,p=''):
 if type(a)!=type(b):return [{'pointer':p,'before':a,'after':b}]
 if isinstance(a,dict):
  out=[]
  for k in sorted(set(a)|set(b)):
   q=p+'/'+k.replace('~','~0').replace('/','~1')
   if k not in a or k not in b:out.append({'pointer':q,'before_present':k in a,'after_present':k in b,'before':a.get(k),'after':b.get(k)})
   else:out.extend(differences(a[k],b[k],q))
  return out
 if isinstance(a,list):
  if a==b:return []
  if len(a)!=len(b):return [{'pointer':p,'before':a,'after':b}]
  return [r for i,(x,y)in enumerate(zip(a,b))for r in differences(x,y,p+'/'+str(i))]
 return []if a==b else[{'pointer':p,'before':a,'after':b}]

def run():
 cfg=json.loads((M/'service-batches.json').read_bytes());pre=json.loads(original('precinct-layer-pre'));post=json.loads(original('precinct-layer-post'));oid=cfg['objectIdField'];allids=json.loads(original('precinct-ids-pre'))['objectIds'];after=json.loads(original('precinct-ids-post'))['objectIds'];assert len(allids)==len(after)==len(set(allids))==len(set(after))and set(allids)==set(after)
 assert len(allids)==json.loads(original('precinct-count-pre'))['count']==json.loads(original('precinct-count-post'))['count']
 fields={x['name']for x in pre['fields']if x['type']!='esriFieldTypeGeometry'};got=[];counts=collections.Counter();defects=[];curves=[];empty=[];allattrs=[];xycount=0
 for i,batch in enumerate(cfg['batches']):
  r=json.loads((S/batch['receipt']['path']).read_bytes());o=json.loads(body(r['body']));features=o['features'];ids=[x['attributes'][oid]for x in features];assert len(batch['requested_IDs'])<=50 and set(ids)==set(batch['requested_IDs'])and len(ids)==len(set(ids))==batch['count']and not o.get('exceededTransferLimit')
  params=urllib.parse.parse_qs(urllib.parse.urlsplit(r['requested_url']).query)
  assert params['outFields']==['*']and params['returnZ']==params['returnM']==params['returnTrueCurves']==['true']
  assert not set(params)&{'outSR','geometryPrecision','quantizationParameters','maxAllowableOffset','resultOffset','resultRecordCount'}
  assert o['spatialReference']['wkid']==pre['extent']['spatialReference']['wkid'];got+=ids
  for f in features:
   a=f['attributes'];fid=a[oid];assert set(a)==fields,(fid,set(a)^fields);counts[a['STATE']+a['COUNTY_FIP']]+=1;g=f.get('geometry');allattrs.append({'objectID':fid,'all_attributes':a,'batch_receipt':batch['receipt']})
   if not g or not any(g.get(k)for k in ['rings','curveRings']):empty.append(fid);continue
   if 'curveRings'in g:curves.append(fid);continue
   rings=g['rings'];points=[p for ring in rings for p in ring];parts=[];n=0
   for ring in rings:parts.append(n);n+=len(ring)
   diag,_=topology({'points':points,'parts':parts});diag['native_units']='meters EPSG26913';diag.pop('area_native_square_degrees',None);diag['signed_ring_areas_native_square_meters']=diag.pop('signed_ring_areas_native',[])
   xycount+=len(points)
   if diag.get('valid')is False or diag.get('open_rings')or diag.get('orphan_hole_indices')or diag.get('short_rings'):defects.append({'objectID':fid,'all_attributes':a,'diagnostic':diag})
 assert len(got)==len(set(got))==len(allids)and set(got)==set(allids)
 service_diff=differences(json.loads(original('political-service-pre')),json.loads(original('political-service-post')));layer_diff=differences(pre,post)
 out=dict(status='pass_complete_native_snapshot',count=len(got),batches=len(cfg['batches']),maximum_batch=max(b['count']for b in cfg['batches']),pre_post_count_equal=True,pre_post_IDsets_equal=True,pre_post_order_equal=allids==after,service_metadata_differences=service_diff,layer_metadata_differences=layer_diff,service_extent_changes=[d for d in service_diff if 'Extent'in d['pointer']],metadata_equality_claim=not service_diff and not layer_diff,CRS=pre['extent']['spatialReference'],native_units='meters',hasZ=pre.get('hasZ'),hasM=pre.get('hasM'),truecurve_features=curves,empty_geometry_IDs=empty,linear_geometry_defects=defects,county_counts=dict(counts),XY_pairs_diagnosed=xycount,geometry_repaired=False,gap_overlap_sliver_certification=None,independent_same_vintage_legal_outline=None,all_attributes=allattrs)
 write(M/'service-validation.json',out);print({k:v for k,v in out.items()if k not in ['all_attributes','linear_geometry_defects']})
if __name__=='__main__':run()
