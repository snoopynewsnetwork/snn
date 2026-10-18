#!/usr/bin/env python3
"""Retain one complete public HTTP response. No guessed routes; inputs are observed links.
Run: python3 acquire.py ID URL [PARENT_ID]. Existing IDs are immutable.
"""
import datetime, gzip, hashlib, json, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent
SOURCE = ROOT / 'source'
LIMIT = 40_000_000
def sha(b): return hashlib.sha256(b).hexdigest()
def dump(p, x): p.write_text(json.dumps(x, ensure_ascii=False, indent=2)+'\n')
def acquire(sid, url, parent=None):
    target=SOURCE/(sid+'.json')
    if target.exists(): return json.loads(target.read_text())
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with tempfile.TemporaryDirectory(prefix='nh-official-http-') as td:
        raw=pathlib.Path(td)/'body'; headers=pathlib.Path(td)/'headers'
        cmd=['curl','--silent','--show-error','--location','--max-redirs','8',
             '--connect-timeout','10','--max-time','30','-H','Accept-Encoding: identity',
             '-A','Public election source research; bounded archival observation',
             '--dump-header',str(headers),'--output',str(raw),'--write-out','%{json}',url]
        r=subprocess.run(cmd,capture_output=True)
        b=raw.read_bytes() if raw.exists() else b''
        h=headers.read_bytes() if headers.exists() else b''
        try: info=json.loads(r.stdout)
        except Exception: info={'curl_write_out':r.stdout.decode(errors='replace')}
        # Curl failures are retained as partial/access evidence, never successful sources.
        stored=gzip.compress(b,mtime=0)
        if len(stored)>=LIMIT: raise ValueError('Response requires documented lossless splitting; not retained/truncated')
        (SOURCE/(sid+'.body.gz')).write_bytes(stored)
        (SOURCE/(sid+'.headers.txt')).write_bytes(h)
        meta={'source_id':sid,'requested_url':url,'final_url':info.get('url_effective',url),
              'parent_source_id':parent,'retrieved_utc':started,
              'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'http_status':info.get('http_code',info.get('response_code',0)),
              'curl_exit':r.returncode,'curl_error':r.stderr.decode(errors='replace'),
              'complete_response':r.returncode==0,'original_bytes':len(b),'original_sha256':sha(b),
              'stored_bytes':len(stored),'stored_sha256':sha(stored),'headers_sha256':sha(h),
              'body_path':'source/'+sid+'.body.gz','headers_path':'source/'+sid+'.headers.txt',
              'curl':info,'storage':'one local gzip layer; HTTP Content-Encoding, if any, remains original'}
        dump(target,meta)
        return meta

if __name__=='__main__':
    m=acquire(*sys.argv[1:]); print(json.dumps({k:m[k] for k in ['source_id','http_status','original_bytes','curl_exit']}))
