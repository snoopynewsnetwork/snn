#!/usr/bin/env python3
"""Preserve a full, unsimplified public ArcGIS layer using count + ID-bounded batches."""
import argparse,json,urllib.parse
from acquire import ROOT,fetch,body

def query(key,url,params,parent):
 request=url+('?' if '?' not in url else '&')+urllib.parse.urlencode(params)
 r=fetch(key,request,parent,'ArcGIS public query; native CRS, all attributes; no precision/generalization options')
 if r['status']!=200:raise RuntimeError(r)
 d=json.loads(body(key))
 if 'error' in d:raise RuntimeError(d)
 return d

def acquire_layer(key,url,parent=None):
 meta=query(key+'-layer',url,{'f':'pjson'},parent)
 assert meta.get('geometryType')=='esriGeometryPolygon',meta.get('geometryType')
 ids=query(key+'-ids-pre',url+'/query',{'f':'json','where':'1=1','returnIdsOnly':'true'},key+'-layer')
 count=query(key+'-count',url+'/query',{'f':'json','where':'1=1','returnCountOnly':'true'},key+'-layer')['count']
 oid=ids['objectIdFieldName'];original_ids=ids['objectIds'];assert len(original_ids)==count and len(set(original_ids))==count
 batch_size=min(50,meta.get('maxRecordCount',50));batches=[]
 for i in range(0,len(original_ids),batch_size):
  subset=sorted(original_ids)[i:i+batch_size];bid=key+f'-batch-{i//batch_size:04d}'
  d=query(bid,url+'/query',{'f':'json','objectIds':','.join(map(str,subset)),'outFields':'*','returnGeometry':'true','returnZ':'true','returnM':'true','returnTrueCurves':'true'},key+'-layer')
  got=[f['attributes'][oid] for f in d['features']]
  assert set(got)==set(subset) and len(got)==len(subset),(bid,len(got),len(subset))
  assert not d.get('exceededTransferLimit',False),bid
  batches.append({'source_id':bid,'requested_ids':subset,'returned_ids':got,'feature_count':len(got),'exceededTransferLimit':d.get('exceededTransferLimit')})
 ids2=query(key+'-ids-post',url+'/query',{'f':'json','where':'1=1','returnIdsOnly':'true','returnGeometry':'false'},key+'-layer')
 meta2=query(key+'-layer-post',url,{'f':'json'},key+'-layer')
 assert set(ids2['objectIds'])==set(original_ids)
 result={'key':key,'layer_url':url,'parent_source_id':parent,'layer_source_id':key+'-layer','object_id_field':oid,'source_count':count,'ids_pre_source_id':key+'-ids-pre','ids_post_source_id':key+'-ids-post','ids_pre_post_equal':True,'batches':batches,'spatial_reference':meta.get('extent',{}).get('spatialReference'),'hasZ':meta.get('hasZ'),'hasM':meta.get('hasM'),'supportsTrueCurve':meta.get('supportsTrueCurve'),'pre_editingInfo':meta.get('editingInfo'),'post_editingInfo':meta2.get('editingInfo'),'native_export_limit':'Exact server-returned native-CRS JSON with requested Z/M/true curves. Not a database backup or legal approval; unversioned upstream geometry could change while IDs remain stable. No maxAllowableOffset, outSR, quantizationParameters, geometryPrecision, or simplification.'}
 (ROOT/f'{key}.acquisition.json').write_text(json.dumps(result,indent=2)+'\n');print(key,count,len(batches),result['spatial_reference'])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('key');p.add_argument('url');p.add_argument('--parent');a=p.parse_args();acquire_layer(a.key,a.url,a.parent)
