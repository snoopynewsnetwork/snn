#!/usr/bin/env python3
"""Bounded public research captures, with exact source metadata and compressed bytes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import datetime,gzip,hashlib,json,requests,subprocess,tempfile
ROOT=Path(__file__).resolve().parent
URLS={'wbez-home': 'https://www.wbez.org/', 'wttw-home': 'https://news.wttw.com/', 'wcia-home': 'https://www.wcia.com/', 'wglt-home': 'https://www.wglt.org/', 'state-results': 'https://www.elections.il.gov/electionoperations/votetotalsearch.aspx', 'nyt-elections': 'https://www.nytimes.com/section/politics/elections', 'wglt-election2026': 'https://www.wglt.org/election-2026', 'wbez-primary-report': 'https://www.wbez.org/government-politics/elections/2026/03/17/biss-fine-abughazaleh-shakowsky-congress-house-illinois-9th-district', 'suntimes-primary-liveblog': 'https://chicago.suntimes.com/live/election-day-illinois-primaries-2026-results-analysis', 'suntimes-senate-primary': 'https://chicago.suntimes.com/elections/2026/03/17/us-senate-illinois-primary-results', 'sos-2024-county-totals': 'https://www.elections.il.gov/electionoperations/ElectionVoteTotalsCounty.aspx?ID=9huvqbsiUWA%3D', 'sos-2024-president-csv': 'https://www.elections.il.gov/Downloads/ElectionOperations/ElectionResults/ByOffice/66/66-120-PRESIDENT%20AND%20VICE%20PRESIDENT-2024GE.csv'}
def fetch(item):
 key,url=item;row={'id':key,'url':url,'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  r=requests.get(url,timeout=35);path=ROOT/(key+'.html.gz');path.write_bytes(gzip.compress(r.content,mtime=0))
  row.update(status=r.status_code,final_url=r.url,raw_sha256=hashlib.sha256(r.content).hexdigest(),asset=path.name,stored_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=len(r.content),headers=dict(r.headers))
 except requests.exceptions.SSLError as e:
  row['requests_error']=str(e)
  with tempfile.TemporaryDirectory() as t:
   body=Path(t)/'body';hdr=Path(t)/'headers'
   c=subprocess.run(['curl','--silent','--show-error','--location','--max-time','35','--dump-header',str(hdr),'--output',str(body),'--write-out','%{http_code}\\n%{url_effective}',url],capture_output=True,text=True)
   row['transport']='system curl with default certificate verification'
   if c.returncode==0:
    code,final=c.stdout.split('\\n',1) if '\\n' in c.stdout else c.stdout.split('\n',1)
    raw=body.read_bytes();path=ROOT/(key+'.html.gz');path.write_bytes(gzip.compress(raw,mtime=0))
    row.update(status=int(code),final_url=final,raw_sha256=hashlib.sha256(raw).hexdigest(),asset=path.name,stored_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=len(raw),raw_headers=hdr.read_text())
   else:row['error']=c.stderr
 except requests.RequestException as e:row['error']=str(e)
 return row
if __name__=='__main__':
 rows=list(ThreadPoolExecutor(max_workers=4).map(fetch,URLS.items()));(ROOT/'manifest.json').write_text(json.dumps(rows,indent=2)+'\n')
 for r in rows:print(r['id'],r.get('status',r.get('error')))
