#!/usr/bin/env python3
"""Native ArcGIS extraction; unchanged response bytes remain canonical."""
import json,sys,urllib.parse
from acquire import fetch,body,ROOT,savejson

def acquire(key,url):
    def get(suffix,params):
        r=fetch(key+'-'+suffix,url+('?' if suffix in ['pre','post'] else '/query?')+urllib.parse.urlencode(params),key)
        assert r['status']==200,r
        d=json.loads(body(r));assert 'error' not in d,(key,suffix,d)
        return d
    pre=get('pre',{'f':'pjson'})
    c=get('count-pre',{'f':'json','where':'1=1','returnCountOnly':'true'})['count']
    ids=get('ids-pre',{'f':'json','where':'1=1','returnIdsOnly':'true'})['objectIds']
    assert len(ids)==len(set(ids))==c
    oid=pre.get('objectIdField') or next(f['name'] for f in pre['fields'] if f['type']=='esriFieldTypeOID');got=[];batches=[]
    for n in range(0,len(ids),50):
        want=sorted(ids)[n:n+50]
        d=get('batch-%03d'%(n//50),dict(f='json',objectIds=','.join(map(str,want)),outFields='*',returnGeometry='true',returnZ='true',returnM='true',returnTrueCurves='true'))
        assert not d.get('exceededTransferLimit'),d
        actual=[f['attributes'][oid] for f in d['features']]
        assert sorted(actual)==want and len(actual)==len(set(actual))
        assert all(set(f['attributes'])=={x['name'] for x in pre['fields'] if x['type']!='esriFieldTypeGeometry'} for f in d['features'])
        got+=actual;batches.append(dict(id=key+'-batch-%03d'%(n//50),count=len(actual),null_geometry=[f['attributes'][oid] for f in d['features'] if f.get('geometry') is None]))
    postids=get('ids-post',{'f':'json','where':'1=1','returnIdsOnly':'true'})['objectIds']
    postcount=get('count-post',{'f':'json','where':'1=1','returnCountOnly':'true'})['count']
    post=get('post',{'f':'pjson'})
    savejson(ROOT/'source'/f'{key}.service-proof.json',dict(source_url=url,count=c,all_ids=ids,batches=batches,all_ids_exact=sorted(got)==sorted(ids)==sorted(postids),post_count=postcount,metadata_equal=pre==post,editingInfo_pre=pre.get('editingInfo'),editingInfo_post=post.get('editingInfo'),edit_clock_unavailable=not bool(pre.get('editingInfo')),native_spatial_reference=pre.get('sourceSpatialReference',pre.get('extent',{}).get('spatialReference')),hasZ=pre.get('hasZ'),hasM=pre.get('hasM'),supportsTrueCurve=pre.get('advancedQueryCapabilities',{}).get('supportsTrueCurve'),qualification='No outSR, precision, offset or quantization requested. Full native server JSON retained; source geodatabase fidelity/server default precision cannot be independently proven. Stable IDs and metadata do not rule out unclocked concurrent coordinate edits.'))
    print(key,'COMPLETE',c,flush=True)

if __name__=='__main__':acquire(*sys.argv[1:])
