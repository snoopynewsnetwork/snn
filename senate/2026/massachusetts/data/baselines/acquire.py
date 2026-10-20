#!/usr/bin/env python3
"""Bounded original HTTP acquisition. Default verifies pinned bodies, --fetch captures new observations."""
import argparse,datetime,gzip,hashlib,json
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parent
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--fetch',action='store_true');ap.add_argument('--folder',default='http-network');a=ap.parse_args()
    jobs=json.loads((ROOT/'source/requested-sources.json').read_text()); folder=ROOT/'source'/a.folder;folder.mkdir(exist_ok=True)
    for job in jobs:
        receipt=folder/(job['id']+'.receipt.json')
        if receipt.exists():
            r=json.loads(receipt.read_text())
            if r.get('status') is None: continue
            z=(ROOT/r['stored_path']).read_bytes();b=gzip.decompress(z)
            assert hashlib.sha256(z).hexdigest()==r['stored_sha256'] and hashlib.sha256(b).hexdigest()==r['raw_sha256'];continue
        if not a.fetch: raise ValueError('Missing observation; explicitly --fetch: '+job['id'])
        now=datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:
            response=requests.get(job['url'],timeout=25);body=response.content
            asset=folder/(job['id']+'.body.gz');z=gzip.compress(body,mtime=0);assert len(z)<40_000_000;asset.write_bytes(z)
            record=dict(job,retrieved_at_utc=now,status=response.status_code,final_url=response.url,redirects=[dict(url=x.url,status=x.status_code,headers=dict(x.headers)) for x in response.history],headers=dict(response.headers),raw_bytes=len(body),raw_sha256=hashlib.sha256(body).hexdigest(),stored_path=str(asset.relative_to(ROOT)),stored_bytes=len(z),stored_sha256=hashlib.sha256(z).hexdigest(),publisher_clock=None,source_status='HTTP observation only; content must be inspected')
        except requests.RequestException as e: record=dict(job,retrieved_at_utc=now,error=str(e),status=None)
        receipt.write_text(json.dumps(record,indent=2)+'\n');print(job['id'],record['status'],flush=True)
if __name__=='__main__':main()
