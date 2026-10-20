"""Native all-attribute geometry snapshots, exact ID-set pages <=50, full pre/post metadata."""
from common import *
from acquire import fetch,body_of
import urllib.parse,concurrent.futures,sys

def data(key,url,parent):
 r=fetch(key,url,parent,'native service snapshot; all attributes, XY/Z/M/true curves, no output CRS or geometry reduction')
 b=body_of(r)
 if not b:raise ValueError(r['error'])
 x=json.loads(b)
 if 'error' in x:raise ValueError(str(x['error']))
 return x

def diff(a,b,p=''):
 if type(a)!=type(b):return [p]
 if isinstance(a,dict):
  out=[]
  for k in sorted(a.keys()|b.keys()):out+=diff(a[k],b[k],p+'/'+k) if k in a and k in b else [p+'/'+k]
  return out
 if isinstance(a,list):
  if len(a)!=len(b):return [p]
  return [q for i,(x,y) in enumerate(zip(a,b)) for q in diff(x,y,p+'/'+str(i))]
 return [] if a==b else [p]

def capture(plan):
 k=plan['key'];layer=plan['url'].rstrip('/');service=layer.rsplit('/',1)[0];out={**plan,'complete':False,'error':None,'pages':[],'snapshot_atomic':False}
 def snap(stage):
  obj={}
  for typ,url in [('service',service+'?f=pjson'),('layer',layer+'?f=pjson'),('count',layer+'/query?f=json&where=1%3D1&returnCountOnly=true'),('ids',layer+'/query?f=json&where=1%3D1&returnIdsOnly=true')]:
   key=k+'-'+stage+'-'+typ;obj[typ]=data(key,url,plan['parent']);out[stage+'_'+typ]='maps/requests/'+key+'.json'
  ids=obj['ids']['objectIds'];assert isinstance(ids,list) and len(ids)==len(set(ids))==obj['count']['count'];return obj
 try:
  pre=snap('pre');ids=pre['ids']['objectIds'];oid=pre['ids']['objectIdFieldName'];out['object_id_field']=oid;out['native_crs']=pre['layer'].get('extent',{}).get('spatialReference',pre['service'].get('spatialReference'));out['hasZ']=pre['layer'].get('hasZ');out['hasM']=pre['layer'].get('hasM');returned=[];out['attribute_key_sets']=[]
  for i in range(0,len(ids),50):
   wanted=ids[i:i+50];q={'f':'json','objectIds':','.join(map(str,wanted)),'outFields':'*','returnGeometry':'true','returnZ':'true','returnM':'true','returnTrueCurves':'true'};key=k+'-page-'+str(i//50).zfill(4);x=data(key,layer+'/query?'+urllib.parse.urlencode(q),plan['parent']);got=[v['attributes'][oid] for v in x['features']];assert len(got)==len(set(got)) and set(got)==set(wanted) and not x.get('exceededTransferLimit',False)
   expected={f['name'] for f in pre['layer']['fields'] if f['type']!='esriFieldTypeGeometry'}
   for f in x['features']:assert expected<=set(f['attributes']),('missing attributes',expected-set(f['attributes']))
   out['pages'].append({'request':'maps/requests/'+key+'.json','requested_ids':wanted,'returned_ids':got,'complete_attributes':True,'source_crs':x.get('spatialReference'),'hasZ':x.get('hasZ'),'hasM':x.get('hasM')});returned+=got
  post=snap('post');assert len(returned)==len(set(returned))==len(ids) and set(returned)==set(ids)
  out['pre_post_changes']={typ:diff(pre[typ],post[typ]) for typ in pre};out['ids_and_count_stable']=set(ids)==set(post['ids']['objectIds']) and pre['count']==post['count'];out['feature_count']=len(returned);out['complete']=True
 except Exception as e:out['error']=type(e).__name__+': '+str(e)
 save('maps/native/'+k+'.json',out);print(json.dumps({'key':k,'complete':out['complete'],'features':out.get('feature_count'),'changes':out.get('pre_post_changes'),'error':out['error']}),flush=True)
 return out
if __name__=='__main__':
 plans=load(sys.argv[1])
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:list(ex.map(capture,plans))
