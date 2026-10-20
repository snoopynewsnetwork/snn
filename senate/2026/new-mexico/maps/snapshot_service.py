"""Full native all-ID capture, <=50 IDs per request. No offset/output CRS controls."""
from common import *
import concurrent.futures

def run():
 service=json.loads((M/'receipts/political-service-pre.json').read_bytes())['requested_url'].split('?')[0]
 data=json.loads(original('political-service-pre'));layer=next(x for x in data['layers']if x['name']=='Voting Precinct');url=service+'/'+str(layer['id'])
 pre=fetch('precinct-layer-pre',url+'?f=pjson','political-service-pre',layer,timeout=100)
 meta=json.loads(body(pre['body']));oid=meta.get('objectIdField')or next(x['name']for x in meta['fields']if x['type']=='esriFieldTypeOID')
 def query(name,params,basis):return fetch(name,url+'/query?'+urllib.parse.urlencode(dict(f='json',**params)),'precinct-layer-pre',basis,timeout=100)
 count=query('precinct-count-pre',dict(where='1=1',returnCountOnly='true'),'complete native layer pre count')
 ids=query('precinct-ids-pre',dict(where='1=1',returnIdsOnly='true'),'complete native layer pre allIDs')
 allids=json.loads(body(ids['body']))['objectIds'];assert len(allids)==len(set(allids))==json.loads(body(count['body']))['count']
 jobs=[allids[i:i+50]for i in range(0,len(allids),50)]
 def batch(ij):
  i,wanted=ij;params=dict(objectIds=','.join(map(str,wanted)),outFields='*',returnGeometry='true',returnZ='true',returnM='true',returnTrueCurves='true')
  r=query(f'precinct-native-{i+1:04d}',params,{'requested_exact_IDs':wanted,'all_attributes':True,'native_CRS':True,'XY_Z_M_truecurves':True})
  o=json.loads(body(r['body']));features=o['features'];got=[x['attributes'][oid]for x in features]
  assert len(got)==len(set(got))==len(wanted)and set(got)==set(wanted)and not o.get('exceededTransferLimit'),(i,wanted,got)
  print('batch',i+1,len(got),r['body']['raw_bytes'],flush=True)
  return {'receipt':pin(M/'receipts'/(r['id']+'.json')),'requested_IDs':wanted,'returned_IDs':got,'count':len(got),'spatialReference':o.get('spatialReference'),'hasZ':o.get('hasZ'),'hasM':o.get('hasM'),'geometryType':o.get('geometryType'),'exceededTransferLimit':o.get('exceededTransferLimit')}
 with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:batches=list(pool.map(batch,enumerate(jobs)))
 query('precinct-count-post',dict(where='1=1',returnCountOnly='true'),'complete native layer post count')
 query('precinct-ids-post',dict(where='1=1',returnIdsOnly='true'),'complete native layer post allIDs')
 fetch('precinct-layer-post',url+'?f=pjson','precinct-layer-pre','full native layer post metadata')
 fetch('political-service-post',service+'?f=pjson','political-service-pre','full native service post metadata including fullExtent')
 write(M/'service-batches.json',dict(service_url=service,layer_url=url,objectIdField=oid,full_count=len(allids),batches=batches,max_requested_IDs=50,offset_paging=False,geometry_modifying_parameters=False))
if __name__=='__main__':run()
