#!/usr/bin/env python3
"""Bounded public-source acquisition. Writes only turnout/source/acquired.

No guessed county IDs: county requests use GetElectionInfo's returned keys.
Original shared assets are reused only through immutable individual receipts.
Run with PYTHONDONTWRITEBYTECODE=1. Refreshes are explicit, never overwrite.
"""
import concurrent.futures, datetime, gzip, hashlib, json, pathlib, subprocess, tempfile
ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / 'source' / 'acquired'
OUT.mkdir(exist_ok=True)
API = 'https://enr-results-api.totalresults.com/'
def digest(b): return hashlib.sha256(b).hexdigest()
def fetch(key, url, parent=None):
    receipt = OUT / (key + '.receipt.json')
    if receipt.exists():
        r=json.loads(receipt.read_text())
        if r['http'].get('http_code')!=200:
            raise RuntimeError(f'{key}: retained failed receipt; preserve it in history before an explicit bounded retry')
        path=ROOT.parents[4]/r['shared_original_path'] if r.get('shared_original_path') else OUT/r['asset']
        b=gzip.decompress(path.read_bytes())
        assert digest(b)==r['raw_sha256']
        return b
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with tempfile.TemporaryDirectory(prefix='ar-turnout-') as tmp:
        body=pathlib.Path(tmp)/'body'; headers=pathlib.Path(tmp)/'headers'
        p=subprocess.run(['curl','--location','--max-redirs','8','--max-time','90','--retry','1','--silent','--show-error','--dump-header',str(headers),'--output',str(body),'--write-out','%{json}',url],capture_output=True)
        b=body.read_bytes() if body.exists() else b''
        meta=json.loads(p.stdout) if p.stdout else {}
        h=headers.read_text(errors='replace') if headers.exists() else ''
    pins=json.loads((ROOT/'source/original-pins.json').read_text())
    shared=next((r for r in pins if r['raw_sha256']==digest(b)),None)
    stored=gzip.compress(b,mtime=0); asset=key+'.body.gz'
    assert len(stored)<40000000
    if not shared: (OUT/asset).write_bytes(stored)
    r=dict(id=key,url=url,parent=parent,retrieved_at_utc=start,finished_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),curl_returncode=p.returncode,curl_stderr=p.stderr.decode(errors='replace'),http=meta,headers_raw=h,asset=asset,raw_sha256=digest(b),raw_bytes=len(b),stored_sha256=digest(stored),stored_bytes=len(stored))
    if shared:
        r.update(shared_original_path=shared['shared_original_path'],asset=None,stored_sha256=shared['stored_sha256'],stored_bytes=shared['stored_bytes'],original_receipt='../'+shared['id']+'.receipt.json')
    receipt.write_text(json.dumps(r,indent=2)+'\n')
    print(key,meta.get('http_code'),len(b),flush=True)
    if p.returncode or meta.get('http_code')!=200:
        raise RuntimeError(f'{key}: unsuccessful original retained; no numerical fallback')
    return b
def main():
    history='https://sos.arkansas.gov/elections/research/election-results'
    fetch('history-current',history)
    for year,eid in [(2024,'1846'),(2022,'1844'),(2020,'1841')]:
        info_url=API+'Election/GetElectionInfo?cId=arkansas&electionID='+eid
        info=json.loads(fetch(f'{year}-info',info_url,history))
        fetch(f'{year}-metadata',API+'Contest/GetContestSearchList?cid=arkansas&electionID='+eid,info_url)
        state_url=API+'Contest/GetContestResults?cId=arkansas&electionID='+eid+'&contestType=FED'
        fetch(f'{year}-federal-state',state_url,info_url)
        fetch(f'{year}-full',f'https://results.tally-enr.com/results/arkansas/{eid}/FullDataFile.json',history)
        turnout_url=API+'Turnout/GetTurnout?cId=arkansas&electionID='+eid
        fetch(f'{year}-turnout-state',turnout_url,info_url)
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            jobs=[pool.submit(fetch,f'{year}-federal-{key}',state_url+'&locationId='+key,info_url) for key in info['response']['locations']]
            for job in jobs: job.result()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            jobs=[pool.submit(fetch,f'{year}-turnout-{key}',turnout_url+'&locationId='+key,info_url) for key in info['response']['locations']]
            for job in jobs: job.result()
    for year in (2020,2022,2024):
        fetch(f'clerk-{year}',f'https://clerk.house.gov/member_info/electionInfo/{year}/statistics{year}.pdf','https://clerk.house.gov/Members/Election-Information/')
    for key,url in [('2024-xlsx-current','https://www.sos.arkansas.gov/uploads/elections/2024_General_Election_and_Nonpartisan_Judicial_Runoff_Election_Precinct_Level_Results.xlsx'),('2024-pdf-current','https://www.sos.arkansas.gov/uploads/elections/GE2024_report.pdf')]:
        fetch(key,url,history)
if __name__=='__main__': main()
