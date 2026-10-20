#!/usr/bin/env python3
"""Bounded public acquisition, exact response entities and redirect headers.

Usage: acquire.py KEY URL [PARENT_KEY]. Does not guess resource identifiers.
Requests returns the decoded HTTP entity (Content-Encoding removal, if any);
that exact entity is preserved as deterministic gzip. Redirects are separate.
"""
from pathlib import Path
import datetime, gzip, hashlib, json, sys
import requests

OUT=Path(__file__).resolve().parents[1]
ROOT=OUT/'source'/'acquired'
ROOT.mkdir(exist_ok=True)

def acquire(key,url,parent=None):
    path=ROOT/(key+'.receipt.json')
    if path.exists():
        return json.loads(path.read_text())
    session=requests.Session()
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    result={'key':key,'requested_url':url,'parent_key':parent,'started_utc':start,
            'purpose':'bounded original-source recovery; historical scope only',
            'response_entities':[]}
    try:
        response=session.get(url,timeout=(20,90),headers={'User-Agent':'OregonElectionResearch/1.0 public historical source audit'})
        for i,r in enumerate([*response.history,response]):
            b=r.content
            z=gzip.compress(b,mtime=0)
            name=f'{key}.hop{i}.gz'
            assert len(z)<40000000, 'Use ordered byteparts for large originals'
            (ROOT/name).write_bytes(z)
            result['response_entities'].append(dict(url=r.url,status=r.status_code,
                headers=dict(r.headers),raw_bytes=len(b),raw_sha256=hashlib.sha256(b).hexdigest(),
                asset=name,stored_bytes=len(z),stored_sha256=hashlib.sha256(z).hexdigest()))
        result['final_url']=response.url
    except Exception as e:
        result['error']=repr(e)
    result['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    path.write_text(json.dumps(result,indent=2)+'\n')
    print(key,[(x['status'],x['raw_bytes'])for x in result['response_entities']],result.get('error',''),flush=True)
    return result

if __name__=='__main__':
    acquire(*sys.argv[1:])
