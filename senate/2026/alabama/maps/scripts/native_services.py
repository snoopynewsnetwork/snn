"""Download native ArcGIS layers from observed webmap/layer/query anchors."""
from acquire import fetch
from html_tools import entity,links,ROOT
from urllib.parse import urlencode
import json
INPUTS=['source/2026-10-20T202957761770+0000-d0495b8904f0.receipt.json','source/2026-10-20T203001168540+0000-0037da786e0d.receipt.json']
def get(url,parent):
 p,r=fetch(url,parent);assert r['status']==200,(p,r['status']);_,b=entity(p);return p,json.loads(b)
out=[]
for initial in INPUTS:
 r,_=entity(initial);layer=r['requested_url'];aa=links(initial);service=next(a for a in aa if a['url'].endswith('FeatureServer'));query=next(a for a in aa if a['text']=='Query')
 qp,qr=fetch(query['url'],{'receipt':initial,'anchor':query});assert qr['status']==200
 row={'initial_layer_html':initial,'query_form':qp,'layer_url':layer,'service_anchor':service,'query_anchor':query,'pre':{},'post':{},'pages':[],'current_geography_approved':False,'result_label_join':None}
 def observe(stage):
  sp,s=get(service['url']+'?f=json',{'receipt':initial,'anchor':service,'operation':'full service '+stage});lp,l=get(layer+'?f=json',{'receipt':initial,'operation':'full layer '+stage})
  cp,c=get(query['url']+'?'+urlencode({'f':'json','where':'1=1','returnCountOnly':'true'}),{'receipt':qp,'operation':'count '+stage})
  ip,i=get(query['url']+'?'+urlencode({'f':'json','where':'1=1','returnIdsOnly':'true'}),{'receipt':qp,'operation':'ALL IDs '+stage})
  assert len(i['objectIds'])==len(set(i['objectIds']))==c['count'];row[stage]={'service':sp,'layer':lp,'count':cp,'all_ids':ip,'ordered_ids':i['objectIds'],'object_id_field':i['objectIdFieldName']};return s,l,c,i
 s,l,c,i=observe('pre');ids=i['objectIds'];field=i['objectIdFieldName'];received=[]
 for start in range(0,len(ids),50):
  batch=ids[start:start+50];params={'f':'json','objectIds':','.join(map(str,batch)),'outFields':'*','returnGeometry':'true','returnZ':'true','returnM':'true','returnTrueCurves':'true'}
  p,d=get(query['url']+'?'+urlencode(params),{'receipt':qp,'operation':'disjoint native all-fields geometry page','requested_ids':batch})
  assert not d.get('exceededTransferLimit')
  rid=[f['attributes'][field] for f in d['features']];assert len(rid)==len(set(rid))==len(batch) and set(rid)==set(batch)
  assert not (set(received)&set(rid));received+=rid
  assert set(d['fields'][j]['name'] for j in range(len(d['fields'])))==set(f['name'] for f in l['fields'])
  for f in d['features']:assert set(f['attributes'])==set(x['name'] for x in l['fields'])
  row['pages'].append({'receipt':p,'requested_ids':batch,'returned_ids':rid,'count':len(rid),'spatial_reference':d.get('spatialReference'),'all_fields':True,'all_native_coordinates':True,'z_m_truecurves_requested':True})
 s2,l2,c2,i2=observe('post');assert set(received)==set(ids)==set(i2['objectIds']) and c==c2
 row['observed_changes']={'service':s!=s2,'layer':l!=l2,'ordered_ids':ids!=i2['objectIds']};row['count']=len(ids);row['metadata_geometry_type']=l['geometryType'];row['native_spatial_reference']=l.get('extent',{}).get('spatialReference');row['qualified_vintage']='2026 in source item/layer title and service filename; effective/adopted and November compatibility unverified'
 out.append(row);print(layer,len(ids),row['observed_changes'],flush=True)
(ROOT/'native-service-captures.json').write_text(json.dumps(out,indent=2)+'\n')
