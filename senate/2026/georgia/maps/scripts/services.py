#!/usr/bin/env python3
"""Capture full native ArcGIS feature batches with count and pre/post identity checks."""
import concurrent.futures, json, sys, urllib.parse
from acquire import ROOT, capture, entity, dump

def fetch(spec):
    name=spec['id'];url=spec['url'].rstrip('/');parent=spec.get('parent')
    out={**spec,'batches':[],'status':'incomplete','query_scope':'1=1; full layer, no output CRS, precision, clipping or simplification'}
    def get(suffix,endpoint='',**params):
        r=capture(name+'-'+suffix,url+endpoint+'?'+urllib.parse.urlencode({'f':'json',**params}),parent)
        if r.get('status')!=200:raise ValueError('HTTP '+str(r.get('status')))
        d=json.loads(entity(r))
        if 'error' in d:raise ValueError(str(d['error']))
        return d
    try:
        meta=get('metadata');out['metadata_id']=name+'-metadata'
        oid=meta.get('objectIdField') or next(x['name'] for x in meta['fields'] if x['type']=='esriFieldTypeOID')
        out['oid_field']=oid
        out['advertised_count']=get('count','/query',where='1=1',returnCountOnly='true')['count']
        before=get('ids-before','/query',where='1=1',returnIdsOnly='true');ids=before['objectIds'] or []
        assert len(ids)==len(set(ids))==out['advertised_count']
        seen=[]
        for i in range(0,len(ids),100):
            q=get('batch-'+str(i//100),'/query',where='1=1',objectIds=','.join(map(str,sorted(ids)[i:i+100])),outFields='*',returnGeometry='true',returnZ='true',returnM='true',returnTrueCurves='true')
            assert not q.get('exceededTransferLimit',False)
            rows=q.get('features',[]);got=[x['attributes'][oid] for x in rows]
            assert sorted(got)==sorted(ids)[i:i+100]
            seen+=got;out['batches'].append(name+'-batch-'+str(i//100))
        after=get('ids-after','/query',where='1=1',returnIdsOnly='true')
        out['pre_post_ids_equal']=sorted(ids)==sorted(after['objectIds'] or [])
        out['captured_count']=len(seen);assert out['pre_post_ids_equal'] and len(seen)==len(set(seen))==out['advertised_count']
        post=get('metadata-after');out['metadata_editingInfo_before']=meta.get('editingInfo');out['metadata_editingInfo_after']=post.get('editingInfo')
        out['metadata_editingInfo_equal']=meta.get('editingInfo')==post.get('editingInfo')
        out['geometry_key_count']=sum('geometry' in f for b in out['batches'] for f in json.loads(entity(b)).get('features',[]))
        out['status']='complete' if out['geometry_key_count']==out['captured_count'] else 'complete_ids_geometry_unavailable'
    except Exception as e:out['error']=str(e)
    dump(ROOT/'services'/f'{name}.json',out)
    print(json.dumps({k:out.get(k) for k in ['id','status','advertised_count','captured_count','error']}),flush=True)
    return out

if __name__=='__main__':
    specs=json.loads(open(sys.argv[1]).read())
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:list(ex.map(fetch,specs))
