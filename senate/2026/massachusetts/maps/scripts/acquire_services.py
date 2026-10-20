from acquire import *
import json

def J(key,url,parent,params=None):
 b,r=fetch(key,url,parent=parent,literal_href=url,params=params or {'f':'pjson'});assert r['status']==200,(key,r);o=json.loads(b);assert 'error'not in o,(key,o);return o

def service(prefix,url,parent):
 meta=J(prefix+'-service-pre',url,parent)
 for layer in meta['layers']:
  lu=url+'/'+str(layer['id']);key=prefix+'-layer'+str(layer['id']);lm=J(key+'-pre',lu,prefix+'-service-pre');oid=lm['objectIdField'];q=lu+'/query'
  c=J(key+'-count-pre',q,key+'-pre',{'f':'json','where':'1=1','returnCountOnly':'true'})['count'];ids=J(key+'-ids-pre',q,key+'-pre',{'f':'json','where':'1=1','returnIdsOnly':'true'})['objectIds'];assert len(ids)==len(set(ids))==c
  batches=[];seen=[]
  for i in range(0,len(ids),50):
   want=ids[i:i+50];bn=key+'-batch%04d'%(i//50);o=J(bn,q,key+'-ids-pre',{'f':'json','objectIds':','.join(map(str,want)),'outFields':'*','returnGeometry':'true','returnZ':'true','returnM':'true','returnTrueCurves':'true'})
   got=[x['attributes'][oid]for x in o['features']];assert len(got)==len(want)and set(got)==set(want)and not o.get('exceededTransferLimit'),(bn,want,got)
   seen.extend(got);batches.append(dict(receipt='receipts/'+bn+'.json',requested_ids=want,returned_ids=got,requested_count=len(want),returned_count=len(got)))
  lm2=J(key+'-post',lu,key+'-pre');c2=J(key+'-count-post',q,key+'-pre',{'f':'json','where':'1=1','returnCountOnly':'true'})['count'];ids2=J(key+'-ids-post',q,key+'-pre',{'f':'json','where':'1=1','returnIdsOnly':'true'})['objectIds'];meta2=J(prefix+'-service-post',url,parent)
  assert c==c2==len(seen)and set(ids)==set(ids2)==set(seen)and len(seen)==len(set(seen));assert lm==lm2
  differences={k:dict(pre=meta.get(k),post=meta2.get(k))for k in meta.keys()|meta2.keys()if meta.get(k)!=meta2.get(k)}
  dump(M/(key+'-acquisition.json'),dict(service=url,layer=lu,object_id_field=oid,count=c,ids=ids,batches=batches,pre_post_layer_metadata_equal=lm==lm2,pre_post_service_metadata_equal=meta==meta2,service_metadata_differences=differences,pre_post_ids_equal=True,pre_post_count_equal=True,native_spatial_reference=lm.get('extent',{}).get('spatialReference'),outCRS=None,rounding=None,quantization=None,generalization=None,repair=None))
if __name__=='__main__':
 x=json.loads(load(M/'receipts/wards-item.json')[0]);service('wards',x['url'],'receipts/wards-item.json')
 search=json.loads(load(M/'receipts/subprecinct-search.json')[0]);x=next(x for x in search['results']if x['title']=='Subprecincts 2022 (Feature Service)')
 J('subprecinct-item','https://www.arcgis.com/sharing/rest/content/items/'+x['id'],'receipts/subprecinct-search.json');service('subprecinct',x['url'],'receipts/subprecinct-search.json')
