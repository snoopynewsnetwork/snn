#!/usr/bin/env python3
"""Native ArcGIS all-ID acquisition; no outSR/precision/generalization."""
import json,urllib.parse
from acquire import fetch,body,ROOT

def query(id,url,params,parent):
 m=fetch(id,url+'/query?'+urllib.parse.urlencode(params),parent)
 assert m['status']==200,(id,m)
 d=json.loads(body(id));assert 'error'not in d,(id,d);return d

def acquire(id,url,parent):
 fetch(id+'-layer',url+'?f=pjson',parent);d=json.loads(body(id+'-layer'));assert 'error'not in d
 c=query(id+'-count-pre',url,{'f':'json','where':'1=1','returnCountOnly':'true'},id+'-layer')
 pre=query(id+'-ids-pre',url,{'f':'json','where':'1=1','returnIdsOnly':'true'},id+'-layer');ids=sorted(pre['objectIds']);assert len(set(ids))==len(ids)==c['count']
 of=pre['objectIdFieldName'];allids=[];batches=[];features=[]
 for i in range(0,len(ids),100):
  bid=f'{id}-batch-{i//100:03d}';want=ids[i:i+100]
  x=query(bid,url,{'f':'json','objectIds':','.join(map(str,want)),'outFields':'*','returnGeometry':'true','returnZ':'true','returnM':'true','returnTrueCurves':'true','returnExceededLimitFeatures':'true'},id+'-ids-pre')
  got=[f['attributes'][of] for f in x['features']];assert sorted(got)==want and not x.get('exceededTransferLimit',False),(bid,want,got)
  features+=x['features'];allids+=got;batches.append({'id':bid,'requested_ids':want,'returned_ids':got,'exceededTransferLimit':x.get('exceededTransferLimit','absent'),'spatialReference':x.get('spatialReference')})
 post=query(id+'-ids-post',url,{'f':'json','where':'1=1','returnIdsOnly':'true'},id+'-layer');cp=query(id+'-count-post',url,{'f':'json','where':'1=1','returnCountOnly':'true'},id+'-layer');fetch(id+'-layer-post',url+'?f=pjson',id+'-layer')
 assert ids==sorted(post['objectIds'])==sorted(allids) and c['count']==cp['count']
 out={'id':id,'url':url,'native_crs':d.get('extent',{}).get('spatialReference'),'metadata_hasZ':d.get('hasZ'),'metadata_hasM':d.get('hasM'),'object_id_field':of,'count_pre':c['count'],'count_post':cp['count'],'pre_ids':ids,'post_ids':sorted(post['objectIds']),'batches':batches,'native_full_features':True,'no_precision_or_generalization_parameters':True,'true_curve_request':True,'features_with_curveRings':sum('curveRings'in f.get('geometry',{}) for f in features),'features_with_z_arrays':sum('z'in f.get('geometry',{}) for f in features),'features_with_m_arrays':sum('m'in f.get('geometry',{}) for f in features)}
 (ROOT/'derived'/f'{id}-service-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(id,'audited',len(ids),flush=True)

if __name__=='__main__':
 acquire('granit-live','https://nhgeodata.unh.edu/hosting/rest/services/Hosted/GV_BaseLayers/FeatureServer/8','granit-item')
 for id,url,item in [('keene-wards','https://services2.arcgis.com/QKs1u1Zs6RQO4G4r/arcgis/rest/services/WARDS_2022/FeatureServer/0','a503697bba4248b292d1332e8ca3797e'),('keene-polling','https://services2.arcgis.com/QKs1u1Zs6RQO4G4r/arcgis/rest/services/Wards15/FeatureServer/0','fa3e7692773e47c7b4eff18ef266cace')]:
  fetch(id+'-item','https://www.arcgis.com/sharing/rest/content/items/'+item+'?f=pjson','keene-webmap-data');acquire(id,url,'keene-webmap-data')
