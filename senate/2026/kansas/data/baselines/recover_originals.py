"""Recover a missing referenced original by exact hash, without changing shared paths.

Existing originals are verified and reused. A missing original is downloaded only
to this worker's source/recovered directory. A changed response is retained as a
disagreement, never silently substituted into a pinned baseline.
"""
import datetime,gzip,hashlib,json,urllib.request,urllib.error
from pathlib import Path
H=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    refs=json.loads((H/'source/references.json').read_text()); root=H.parents[1];records=[]
    for r in refs:
        p=root/r['stored_path']
        if p.exists():
            stored=p.read_bytes();assert sha(stored)==r['stored_sha256'];assert sha(gzip.decompress(stored))==r['raw_sha256'];continue
        out=H/'source/recovered';out.mkdir(exist_ok=True)
        m=dict(id=r['id'],requested_url=r['requested_url'],retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),expected_original_sha256=r['raw_sha256']); redirects=[]
        class Redirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self,req,fp,code,msg,headers,newurl):
                redirects.append(dict(from_url=req.full_url,status=code,to_url=newurl,headers=dict(headers)))
                return super().redirect_request(req,fp,code,msg,headers,newurl)
        try:
            req=urllib.request.Request(r['requested_url'],headers={'User-Agent':'Kansas historical election source recovery','Accept-Encoding':'identity'})
            try:resp=urllib.request.build_opener(Redirect()).open(req,timeout=30)
            except urllib.error.HTTPError as e:resp=e
            body=resp.read();raw=gzip.decompress(body) if resp.headers.get('Content-Encoding','').lower()=='gzip' else body
            compressed=gzip.compress(raw,mtime=0);assert len(compressed)<40000000
            name=r['id']+'-'+sha(raw)+'.gz';(out/name).write_bytes(compressed)
            m.update(status=resp.status,final_url=resp.geturl(),headers=dict(resp.headers),redirects=redirects,response_body_sha256=sha(body),response_body_bytes=len(body),raw_sha256=sha(raw),raw_bytes=len(raw),stored_sha256=sha(compressed),stored_bytes=len(compressed),path='source/recovered/'+name,hash_matches_pinned_original=sha(raw)==r['raw_sha256'])
        except Exception as e:m['error']=repr(e)
        records.append(m)
    if records:(H/'source/recovery.json').write_text(json.dumps(records,indent=2)+'\n')
    print(json.dumps(dict(recovered_or_attempted=len(records),existing_references_verified=len(refs)-len(records),note='Recovered objects never replace shared originals or the pinned manifest; review recovery.json explicitly.')))
if __name__=='__main__':main()
