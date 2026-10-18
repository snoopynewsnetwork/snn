"""Independent public acquisition. Never writes outside this assignment.

Run without arguments for eight historical queries; --pages for authority pages.
Exact shared bodies are referenced by SHA256 rather than duplicated. Requests
are copied byte-for-byte from the observed official application's read queries.
"""
from pathlib import Path
import argparse, datetime, gzip, hashlib, json, requests

BASE = Path(__file__).resolve().parent
SRC = BASE / 'source'
DATA = BASE.parent
SRC.mkdir(parents=True, exist_ok=True)
def sha(b): return hashlib.sha256(b).hexdigest()
def writej(p,x): p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')

def capture(sid,url,parent,request=None,shared=None,session=None,content_type='application/json'):
    dest=SRC/(sid+'.meta.json')
    if dest.exists(): return json.loads(dest.read_text())
    headers={'User-Agent':'SC historical partisanship research; public read-only acquisition'}
    if request is not None:
        headers.update({'Content-Type':content_type})
        if content_type=='application/json': headers['X-Elstats-Tenant']='sc'
        (SRC/(sid+'.request.json')).write_bytes(request)
    m={'id':sid,'requested_url':url,'parent_source':parent,'method':'POST' if request else 'GET',
       'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'request_headers':headers}
    if request is not None: m.update(request_file=sid+'.request.json',request_sha256=sha(request))
    try:
        r=(session or requests).request(m['method'],url,data=request,headers=headers,timeout=40)
        b=r.content
        m.update(final_url=r.url,http_status=r.status_code,response_headers=dict(r.headers),
                 redirects=[{'url':h.url,'status':h.status_code,'location':h.headers.get('Location')} for h in r.history],
                 original_bytes=len(b),original_sha256=sha(b),body_encoding='complete decoded HTTP entity; lossless gzip')
        if shared and shared.exists() and sha(gzip.decompress(shared.read_bytes()) if shared.suffix=='.gz' else shared.read_bytes())==sha(b):
            import os
            m.update(body_path=os.path.relpath(shared,SRC),storage='read-only shared exact-byte reference')
            stored=shared.read_bytes()
        else:
            stored=gzip.compress(b,mtime=0)
            assert len(stored)<40000000
            (SRC/(sid+'.body.gz')).write_bytes(stored)
            m.update(body_path=sid+'.body.gz',storage='owned lossless gzip')
        m.update(stored_bytes=len(stored),stored_sha256=sha(stored))
    except requests.RequestException as e: m['transport_error']=str(e)
    writej(dest,m)
    print(sid,m.get('http_status'),m.get('original_sha256'),flush=True)
    return m

PAGES={
 'authority-results':('https://scvotes.gov/elections-statistics/election-results/','common brief official authority'),
 'authority-database':('https://scvotes.gov/elections-statistics/election-database/','authority-results'),
 'authority-candidates':('https://scvotes.gov/candidates/','scvotes official navigation'),
 'candidate-select':('https://vrems.scvotes.sc.gov/Candidate/SelectElection','authority-candidates Candidate Tracking System'),
 'code-13':('https://www.scstatehouse.gov/code/t07c013.php','official legislature Title7'),
 'code-17':('https://www.scstatehouse.gov/code/t07c017.php','official legislature Title7'),
 'code-19':('https://www.scstatehouse.gov/code/t07c019.php','official legislature Title7'),
 'cherokee-2026-dates':('https://cherokeecountysc.gov/voter-registration-election-board/2026-election-dates/','official county 2026 schedule'),
 'general-prep':('https://scvotes.gov/voters/2026prep/','authority-results navigation'),
 'senate-class2':('https://www.senate.gov/senators/Class_II.htm','state README primary seat roster'),
 'senate-class3':('https://www.senate.gov/senators/Class_III.htm','US Senate official class roster'),
}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--pages',action='store_true');args=ap.parse_args()
    if args.pages:
        for sid,(url,parent) in PAGES.items(): capture(sid,url,parent)
    else:
        for label in ['2024-pres','2020-senate','2022-senate','2022-governor']:
            for mode in ['combined','methods']:
                old=DATA/'history-api'/('history-'+label+'-granular-'+mode)
                capture(label+'-'+mode,'https://electionhistory.scvotes.gov/api/graphql_pr',
                        f'official database observed /contest/ route; request/fragments in ../history-api and ../news/manifest.json; {old.name}',
                        old.with_suffix('.request.json').read_bytes(),old.with_suffix('.body.gz'))
