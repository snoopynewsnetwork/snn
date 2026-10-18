#!/usr/bin/env python3
"""Pin shared original bytes read-only; acquire bounded additional primary evidence.

Default makes/validates a pinned inventory. --fetch downloads the listed current
authority pages, preserving HTTP entity bytes and all redirect response headers.
Never overwrites a retained response; --replay ID fetches an exact recorded URL
under a new UTC-suffixed ID. External dependencies are not stored in this tree.
"""
import argparse, datetime, gzip, hashlib, json, subprocess, tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
STATE=HERE.parent.parent
def sha(b): return hashlib.sha256(b).hexdigest()
def dump(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')

def pin():
    dest=HERE/'source/references.json'
    if dest.exists():
        refs=json.loads(dest.read_text())
    else:
        refs=[]
        for m in json.loads((STATE/'data/news/manifest.json').read_text()):
            refs.append(dict(id=m['id'],path='data/news/'+m['asset'],stored_sha256=m['stored_sha256'],
                original_sha256=m['raw_sha256'],original_bytes=m['bytes'],metadata=m,
                parent_chain='See retained news manifest, actual CDX captures and source Link rel=original headers; missing redirect-hop metadata remains unknown.'))
        for f in sorted((STATE/'data/turnout/source').glob('*.json')):
            m=json.loads(f.read_text())
            if not isinstance(m,dict) or 'body_path' not in m: continue
            refs.append(dict(id=m['id'],path='data/turnout/source/'+m['body_path'],
                stored_sha256=m['stored_sha256'],original_sha256=m['original_sha256'],
                original_bytes=m['original_bytes'],metadata_path=str(f.relative_to(STATE)),
                metadata=m,parent_chain=m.get('parent_source_id','not supplied')))
        dump(dest,refs)
    assert len({r['id'] for r in refs})==len(refs)
    for r in refs:
        b=(STATE/r['path']).read_bytes(); assert sha(b)==r['stored_sha256'],r['id']
        raw=gzip.decompress(b)
        assert sha(raw)==r['original_sha256'] and len(raw)==r['original_bytes'],r['id']
    return refs

URLS={
 'current-sample-ballots':'https://www.sos.nh.gov/elections/sample-ballots',
 'current-election-details':'https://www.sos.nh.gov/2026-election-details',
 'current-running-office':'https://www.sos.nh.gov/elections/running-office',
 'current-2024-results':'https://www.sos.nh.gov/2024-general-election-results',
 'current-2022-results':'https://www.sos.nh.gov/elections/2022-election-results/2022-general-election-results',
 'current-2020-results':'https://www.sos.nh.gov/elections/2020-election-results/2020-general-election-results',
 'rsa-659-81':'https://gc.nh.gov/rsa/html/LXIII/659/659-81.htm',
 'rsa-659-chapter':'https://gc.nh.gov/rsa/html/LXIII/659/659-mrg.htm',
 'farmington-clerk':'https://www.farmington.nh.us/1206/Town-Clerk-Tax-Collector',
 'farmington-general-sample-ballot':'https://www.farmington.nh.us/DocumentCenter/View/3121',
 'cdx-2024-pres-write-in':'https://web.archive.org/cdx/search/cdx?url=www.sos.nh.gov/*2024*write*&output=json&filter=statuscode:200&collapse=urlkey&filter=mimetype:application/vnd.ms-excel&limit=1000',
}
def fetch(sid,url):
    meta=HERE/'source'/(sid+'.json')
    if meta.exists(): return
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)
        r=subprocess.run(['curl','-L','--max-time','45','--connect-timeout','15','-sS',
            '-H','Accept-Encoding: identity','-D',str(p/'headers'),'-o',str(p/'body'),
            '-w','%{http_code}\n%{url_effective}\n%{num_redirects}',url],capture_output=True,text=True)
        body=(p/'body').read_bytes() if (p/'body').exists() else b''
        headers=(p/'headers').read_bytes() if (p/'headers').exists() else b''
    stored=gzip.compress(body,mtime=0); bp=HERE/'source'/(sid+'.body.gz');bp.write_bytes(stored)
    hp=HERE/'source'/(sid+'.headers.txt');hp.write_bytes(headers)
    out=r.stdout.splitlines()
    dump(meta,dict(id=sid,requested_url=url,final_url=out[1] if len(out)>1 else None,
        status=int(out[0]) if out and out[0].isdigit() else None,
        redirect_count=int(out[2]) if len(out)>2 and out[2].isdigit() else None,
        retrieved_utc=start,curl_exit=r.returncode,error=r.stderr,body_path=bp.name,
        stored_bytes=len(stored),stored_sha256=sha(stored),original_bytes=len(body),
        original_sha256=sha(body),headers_path=hp.name,headers_sha256=sha(headers),
        encoding='gzip of exact HTTP response entity, Accept-Encoding identity',
        source_clocks='Complete headers retained; capture/election/retrieval/Last-Modified clocks distinct.'))

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--fetch',action='store_true');a.add_argument('--replay');args=a.parse_args()
    refs=pin()
    if args.fetch:
        for sid,u in URLS.items(): fetch(sid,u)
    if args.replay:
        r=next(x for x in refs if x['id']==args.replay);m=r['metadata']
        fetch(args.replay+'-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'),m.get('requested_url',m.get('url')))
    print(json.dumps(dict(pinned_shared_originals=len(refs),all_hashes_verified=True)))
