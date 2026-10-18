#!/usr/bin/env python3
"""Query actual Wayback CDX, then fetch only returned exact captures.
Archive evidence remains date-scoped, never current official approval.
"""
import concurrent.futures,json,re
from urllib.parse import urlencode
from acquire import ROOT,acquire,dump
from inspect_html import decode_body,inspect
parents=['barrington','brentwood','enfield','henniker','hillsborough','hopkinton','kingston','lee','milton','north-hampton','northfield','nottingham','ossipee','rochester','sunapee','wakefield','walpole','weare','exeter']
def one(name):
    candidates=list((ROOT/'source').glob('municipal-'+name+'-alternate*.json'))
    if not candidates:candidates=[ROOT/'source'/('municipal-'+name+'-home.json')]
    src=json.loads(candidates[0].read_text());url=src['requested_url']
    query='https://web.archive.org/cdx/search/cdx?'+urlencode({'url':url,'output':'json','filter':'statuscode:200','from':'20260101','to':'20261018','fl':'timestamp,original,statuscode,mimetype,digest','collapse':'digest','limit':'-1'})
    sid='archive-discovery-'+name;m=acquire(sid,query,src['source_id']);inspect(sid)
    captures=[];error=None
    try:
        rows=json.loads(decode_body(m));keys=rows[0] if rows else []
        captures=[dict(zip(keys,row)) for row in rows[1:]]
    except Exception as e:error=str(e)
    rec={'municipality_slug':name,'query_source_id':sid,'requested_original':url,'captures':captures,'parse_error':error,'scope':'Archive capture is historical primary publication evidence; not a fresh source response.'}
    if captures:
        c=captures[-1];u='https://web.archive.org/web/'+c['timestamp']+'id_/'+c['original'];a=acquire('municipal-'+name+'-archive1',u,sid);inspect(a['source_id']);rec['selected_capture']=c;rec['archive_source_id']=a['source_id']
    dump(ROOT/'derived'/('archive-'+name+'.json'),rec)
    return {'name':name,'captures':len(captures),'status':m['http_status'],'parse_error':error}
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        for r in ex.map(one,parents):print(json.dumps(r),flush=True)
