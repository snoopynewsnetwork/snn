from acquire import *
from concurrent.futures import ThreadPoolExecutor

def snapshot(name):
 layerpage=json.loads((BASE/'receipts'/f'{name}-layer-page.json').read_bytes());layer=layerpage['final_url'];service=json.loads((BASE/'receipts'/f'{name}.json').read_bytes())['final_url'];query=json.loads((BASE/'receipts'/f'{name}-query-form.json').read_bytes())['final_url']
 meta=json.loads(content(name+'-layer-pre'));oid=next(f['name'] for f in meta['fields'] if f['type']=='esriFieldTypeOID')
 for phase in ['pre']:
  fetch(name+'-count-'+phase,query,name+'-query-form',params={'f':'json','where':'1=1','returnCountOnly':'true'})
  fetch(name+'-ids-'+phase,query,name+'-query-form',params={'f':'json','where':'1=1','returnIdsOnly':'true'})
 count=json.loads(content(name+'-count-pre'))['count'];idsobj=json.loads(content(name+'-ids-pre'));ids=idsobj['objectIds'];assert len(ids)==len(set(ids))==count
 ordered=sorted(ids);chunks=[ordered[i:i+50] for i in range(0,len(ordered),50)]
 def batch(v):
  i,ids=v;return fetch(name+f'-batch-{i:04d}',query,name+'-ids-pre',params={'f':'json','objectIds':','.join(map(str,ids)),'outFields':'*','returnGeometry':'true','returnZ':'true','returnM':'true','returnTrueCurves':'true'})
 with ThreadPoolExecutor(max_workers=5) as e:list(e.map(batch,enumerate(chunks)))
 for suffix,url,params in [('meta-post',service,{'f':'pjson'}),('layer-post',layer,{'f':'pjson'}),('count-post',query,{'f':'json','where':'1=1','returnCountOnly':'true'}),('ids-post',query,{'f':'json','where':'1=1','returnIdsOnly':'true'})]:fetch(name+'-'+suffix,url,name+' complete native batches; post snapshot',params=params)
 assert json.loads(content(name+'-meta-pre'))==json.loads(content(name+'-meta-post'))
 assert meta==json.loads(content(name+'-layer-post'))
 assert json.loads(content(name+'-count-post'))['count']==count
 assert set(json.loads(content(name+'-ids-post'))['objectIds'])==set(ids)
 got=[];checks=[]
 for i,expected in enumerate(chunks):
  id=name+f'-batch-{i:04d}';o=json.loads(content(id));assert 'error' not in o and not o.get('exceededTransferLimit',False),id
  actual=[f['attributes'][oid] for f in o['features']];assert len(actual)==len(set(actual)) and set(actual)==set(expected),(id,actual,expected);got+=actual
  assert o.get('spatialReference')==meta['extent']['spatialReference'] or o.get('spatialReference',{}).get('wkid')==meta['extent']['spatialReference']['wkid']
  checks.append({'receipt':id,'requested_ids':expected,'returned_ids_in_native_order':actual,'requested_minus_returned':sorted(set(expected)-set(actual)),'returned_minus_requested':sorted(set(actual)-set(expected)),'raw_body_sha256':sha(content(id)),'all_attributes_and_native_geometry':True})
 assert len(got)==len(set(got))==count and set(got)==set(ids)
 out={'name':name,'complete_count':count,'object_id_field':oid,'native_spatial_reference':meta['extent']['spatialReference'],'hasZ_metadata':meta.get('hasZ'),'hasM_metadata':meta.get('hasM'),'complete_pre_post_metadata_equal':True,'complete_pre_post_counts_equal':True,'complete_pre_post_IDsets_equal':True,'maximum_requested_batch':50,'all_ordered_pre_ids':ids,'all_ordered_returned_ids':got,'batches':checks,'prohibited_transform_parameters_present':False,'current_2026_legal_or_source_row_crosswalk':False}
 write(BASE/'qa'/f'{name}-native-contract.json',out);return out
if __name__=='__main__':
 for n in ['state-election-service','burlington-election-service']:print(snapshot(n)['complete_count'])
