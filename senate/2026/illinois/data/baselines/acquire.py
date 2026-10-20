"""Read-only HTTP acquisition. Jobs specify actual observed links and parent chains.
Run with a jobs JSON filename; completed receipts and original decoded HTTP entity
bytes are retained even for unsuccessful responses. No source output truncation.
"""
import concurrent.futures,datetime,gzip,json,sys
from pathlib import Path
import requests
from source_io import ROOT,sha,dump,pins
def fetch(job):
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        r=requests.get(job['url'],timeout=45,verify=job.get('ca_bundle',True),headers={'User-Agent':'Mozilla/5.0 (public election research)'})
        b=r.content;z=gzip.compress(b,mtime=0)
        assert len(z)<40000000
        rel=f"source/{job['id']}-{sha(b)[:12]}.gz";(ROOT/rel).write_bytes(z)
        return {**job,'method':'GET','request_headers':dict(r.request.headers),'retrieved_at_utc':start,'finished_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':r.status_code,'final_url':r.url,'headers':dict(r.headers),'redirects':[{'url':h.url,'status':h.status_code,'headers':dict(h.headers)}for h in r.history],'path':rel,'bytes':len(b),'raw_sha256':sha(b),'stored_sha256':sha(z),'compression':'gzip','byte_scope':'Complete decoded HTTP response entity bytes; transfer/content compression handled by requests.'}
    except Exception as e:return {**job,'retrieved_at_utc':start,'error':repr(e)}
def main():
    jobs=json.loads(Path(sys.argv[1]).read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:out=list(pool.map(fetch,jobs))
    old=pins(); ids={x['id']for x in old}
    assert not any(x['id']in ids for x in out),'Use distinct receipt IDs, never overwrite source pins.'
    dump(ROOT/'source/registry.json.gz',old+out)
    for x in out:print(x['id'],x.get('status',x.get('error')),x.get('bytes'),x.get('raw_sha256'))
if __name__=='__main__':main()
