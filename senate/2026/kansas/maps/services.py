#!/usr/bin/env python3
"""Acquire complete native Esri JSON geometry by bounded object-ID batches.
No output reprojection/precision/quantization/envelope filter, no repair.
Native Z/M/true curves requested; full layer/root metadata and IDs saved.
"""
import json,urllib.parse
from acquire import fetch,ROOT
FILE=ROOT/'services.json'
def capture(key,url,parent):
 r,b=fetch(key,url,parent,'Native service metadata / completeness evidence')
 if r.get('status')!=200:raise ValueError((key,r))
 j=json.loads(b)
 if 'error' in j:raise ValueError((key,j))
 return j

def collect(key,url,parent,county):
 entries=json.loads(FILE.read_text()) if FILE.exists() else []
 if any(x['id']==key for x in entries):return
 meta=capture(key+'-layer',url+'?f=json',parent)
 print(key,meta.get('name'),meta.get('geometryType'),[x['name'] for x in meta.get('fields',[])],flush=True)
 if meta.get('geometryType')!='esriGeometryPolygon':raise ValueError('Not precinct polygon')
 root=url.rsplit('/',1)[0];capture(key+'-root',root+'?f=json',key+'-layer')
 def query(tag,pars):return capture(key+'-'+tag,url+'/query?'+urllib.parse.urlencode(dict(f='json',where='1=1',**pars)),key+'-layer')
 count=query('count-before',{'returnCountOnly':'true'})['count']
 pre=query('ids-before',{'returnIdsOnly':'true'});ids=sorted(pre['objectIds']);oid=pre['objectIdFieldName']
 assert count==len(ids)==len(set(ids))
 size=min(100,meta.get('maxRecordCount',100));pages=[];got=[]
 for n,pos in enumerate(range(0,len(ids),size)):
  wanted=ids[pos:pos+size]
  tag=f'features-{n:03}'
  page=query(tag,{'objectIds':','.join(map(str,wanted)),'outFields':'*','returnGeometry':'true','returnZ':'true','returnM':'true','returnTrueCurves':'true'})
  assert not page.get('exceededTransferLimit',False),(key,n,'transfer limit')
  assert 'transform' not in page,(key,'quantized transform')
  found=[x['attributes'][oid] for x in page['features']]
  assert sorted(found)==wanted,(key,n,'ID mismatch')
  got+=found;pages.append(key+'-'+tag)
 post=query('ids-after',{'returnIdsOnly':'true'});after=query('count-after',{'returnCountOnly':'true'})
 assert sorted(post['objectIds'])==ids and after['count']==count and sorted(got)==ids
 capture(key+'-layer-after',url+'?f=json',parent)
 rec={'id':key,'county':county,'service_url':url,'authority_parent':parent,'layer_name':meta.get('name'),'geometry_type':meta['geometryType'],'native_crs':meta.get('sourceSpatialReference',meta.get('extent',{}).get('spatialReference')),'count':count,'oid_field':oid,'pages':pages,'id_checks':'count before=ID before=exact batched ID union=ID after=count after; no transfer flags','hasZ':meta.get('hasZ'),'hasM':meta.get('hasM'),'supportsTrueCurve':meta.get('advancedQueryCapabilities',{}).get('supportsTrueCurve'),'requested':['returnZ=true','returnM=true','returnTrueCurves=true','outFields=*','no outSR/precision/quantization/clip'],'scope':'County publication precinct reference snapshot; November2026 legal approval not established'}
 entries.append(rec);FILE.write_text(json.dumps(entries,indent=2)+'\n')
 print(key,'COMPLETE',count,flush=True)
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('id');p.add_argument('url');p.add_argument('parent');p.add_argument('county');a=p.parse_args();collect(a.id,a.url,a.parent,a.county)
