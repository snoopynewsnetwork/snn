from acquire import *
import urllib.parse
SERVICE='https://services2.arcgis.com/S8zZg9pg23JUEexQ/ArcGIS/rest/services/BND_Voting_Precincts_2022/FeatureServer'
def get(name,url,parent):
 r=fetch(name,url,parent);assert last(r).get('status')==200 and not last(r).get('challenge_observed'),name
 x=json.loads(read(r));assert 'error' not in x,(name,x);return x
def query(name,layer,params,parent):return get(name,layer+'/query?'+urllib.parse.urlencode(dict(f='json',**params)),parent)
def run():
 import sys
 global SERVICE
 prefix='rigis'
 if len(sys.argv)>1:
  assert sys.argv[1]=='sos'
  SERVICE='https://services3.arcgis.com/KZcv0G0UvX0bPG3L/arcgis/rest/services/PRECINCTS_RI_VITDS_2022_Final/FeatureServer';prefix='sos'
 def getp(name,url,parent):return get(name.replace('rigis',prefix),url,parent.replace('rigis',prefix))
 def queryp(name,layer,params,parent):return query(name.replace('rigis',prefix),layer,params,parent.replace('rigis',prefix))
 service=getp('rigis-service-pre',SERVICE+'?f=pjson','search:literal-service-URL')
 layer_id=service['layers'][0]['id'];L=SERVICE+'/'+str(layer_id)
 meta=getp('rigis-layer-pre',L+'?f=pjson','rigis-service-pre')
 item=service['serviceItemId']
 getp('rigis-service-item','https://www.arcgis.com/sharing/rest/content/items/'+item+'?f=pjson','rigis-service-pre')
 ids=queryp('rigis-ids-pre',L,dict(where='1=1',returnIdsOnly='true'),'rigis-layer-pre')
 count=queryp('rigis-count-pre',L,dict(where='1=1',returnCountOnly='true'),'rigis-layer-pre')
 ordered=sorted(ids['objectIds']);assert len(ordered)==len(set(ordered))==count['count']
 batches=[]
 for i,start in enumerate(range(0,len(ordered),50)):
  selected=ordered[start:start+50];name=f'rigis-features-{i:03}'
  x=queryp(name,L,dict(objectIds=','.join(map(str,selected)),outFields='*',returnGeometry='true',returnZ='true',returnM='true',returnTrueCurves='true'),'rigis-ids-pre')
  field=ids['objectIdFieldName'];returned=[f['attributes'][field] for f in x['features']]
  assert set(returned)==set(selected) and len(returned)==len(selected) and not x.get('exceededTransferLimit',False)
  batches.append(dict(request=name.replace('rigis',prefix),requested_ids=selected,returned_ids=returned))
 getp('rigis-service-post',SERVICE+'?f=pjson','rigis-service-pre')
 getp('rigis-layer-post',L+'?f=pjson','rigis-layer-pre')
 queryp('rigis-ids-post',L,dict(where='1=1',returnIdsOnly='true'),'rigis-layer-pre')
 queryp('rigis-count-post',L,dict(where='1=1',returnCountOnly='true'),'rigis-layer-pre')
 dump(M/('source/'+prefix+'-native-batches.json'),dict(service_url=SERVICE,layer_url=L,batches=batches,object_count=len(ordered),provenance=('Literal service URL from sos-webmap-data operationalLayers[1]' if prefix=='sos' else 'Literal full service URL found through public search; matches Secretary-linked RIGIS dataset title/credits. No thumbnail suffix removal or guessed item ID. Service itemID and layer ID resolved from complete service metadata.'),native_crs=meta.get('extent',{}).get('spatialReference'),requested_transformation=False))
 print('complete native features',len(ordered),flush=True)
if __name__=='__main__':run()
