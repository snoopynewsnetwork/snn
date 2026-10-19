"""Explicit public URL acquisition, full response bytes and redirect receipts.

Usage: python acquire.py ID URL [ID URL ...]. Stores only in owned source/.
Original shared news assets are read-only; use their exact-hash references.
"""
from pathlib import Path
import datetime, gzip, hashlib, json, sys
import requests

DEST=Path(__file__).resolve().parent/'source'
def fetch(sid,url):
    stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    r=requests.get(url,timeout=120)
    raw=r.content; stored=gzip.compress(raw,mtime=0)
    assert len(stored)<40_000_000, 'Must split losslessly before retaining oversized artifact'
    p=DEST/(sid+'.body.gz');p.write_bytes(stored)
    receipt={'id':sid,'url':url,'requested_url':url,'final_url':r.url,'retrieved_at_utc':stamp,
      'status':r.status_code,'headers':dict(r.headers),
      'redirects':[{'url':v.url,'status':v.status_code,'headers':dict(v.headers)}for v in r.history],
      'raw_bytes':len(raw),'raw_sha256':hashlib.sha256(raw).hexdigest(),
      'stored_bytes':len(stored),'stored_sha256':hashlib.sha256(stored).hexdigest(),
      'asset':p.name,'transport_decoding':'requests response.content; HTTP Content-Encoding decoded by requests, content bytes otherwise unchanged'}
    (DEST/(sid+'.receipt.json')).write_text(json.dumps(receipt,indent=2)+'\n')
    print(sid,r.status_code,len(raw),receipt['raw_sha256'])
if __name__=='__main__':
    assert len(sys.argv)%2==1
    DEST.mkdir(parents=True,exist_ok=True)
    for i in range(1,len(sys.argv),2):fetch(sys.argv[i],sys.argv[i+1])
