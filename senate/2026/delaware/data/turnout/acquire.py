#!/usr/bin/env python3
"""Bounded original acquisition. HTTP header blocks preserve every redirect.
Usage: python3 acquire.py ID URL [PARENT_URL]. No guessed election URLs.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import sys,subprocess,hashlib,json,gzip,datetime
D=Path(__file__).resolve().parent/'source'
def acquire(sid,url,parent=None):
    D.mkdir(parents=True,exist_ok=True)
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    body=D/(sid+'.download'); headers=D/(sid+'.headers.txt')
    r=subprocess.run(['curl','--silent','--show-error','--location','--max-redirs','8','--max-time','55','--compressed','--dump-header',str(headers),'--output',str(body),'--write-out','%{json}',url],capture_output=True,text=True)
    try:info=json.loads(r.stdout)
    except ValueError:info={'curl_output':r.stdout}
    b=body.read_bytes() if body.exists() else b''
    z=gzip.compress(b,mtime=0); stored=D/(sid+'.body.gz');stored.write_bytes(z)
    if body.exists():body.unlink()
    out={'id':sid,'parent_url':parent,'requested_url':url,'retrieved_at_utc':started,'completed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'curl_exit':r.returncode,'stderr':r.stderr,'http':info,'headers_path':headers.name,'raw_sha256':hashlib.sha256(b).hexdigest(),'raw_bytes':len(b),'stored_sha256':hashlib.sha256(z).hexdigest(),'stored_bytes':len(z),'body_path':stored.name,'body_semantics':'complete HTTP content-decoded entity; gzip mtime=0; decompress restores exact entity bytes'}
    assert len(z)<40000000
    news=D.parent.parent/'news'
    for a in json.loads((news/'manifest.json').read_text()):
        if a.get('raw_sha256')==out['raw_sha256'] and b:
            stored.unlink();out['body_path']='../../news/'+a['asset'];out['stored_sha256']=a['stored_sha256'];out['stored_bytes']=(news/a['asset']).stat().st_size;out['reused_original_id']=a['id'];break
    (D/(sid+'.receipt.json')).write_text(json.dumps(out,indent=2)+'\n')
    print(sid,info.get('http_code'),len(b),out['raw_sha256'])
    return out
if __name__=='__main__':
    if sys.argv[1]=='--jobs':
        for job in json.loads(Path(sys.argv[2]).read_text()):acquire(*job)
    else:acquire(*sys.argv[1:])
