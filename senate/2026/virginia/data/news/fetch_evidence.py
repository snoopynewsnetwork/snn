#!/usr/bin/env python3
"""Bounded public research captures, with exact source metadata and compressed bytes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import datetime,gzip,hashlib,json,requests,subprocess,tempfile
ROOT=Path(__file__).resolve().parent
URLS={'vpm-home': 'https://www.vpm.org/', 'wtop-home': 'https://wtop.com/', 'wavy-home': 'https://www.wavy.com/', 'nbc12-home': 'https://www.12onyourside.com/', 'wsls-home': 'https://www.wsls.com/', 'elect-results': 'https://www.elections.virginia.gov/results/', 'nyt-elections': 'https://www.nytimes.com/section/politics/elections', 'wtop-primary-report': 'https://wtop.com/virginia-election/2026/08/virginia-primary-results-set-the-stage-for-pivotal-midterm-elections/', 'whsv-results': 'https://www.whsv.com/politics/election-results/', 'wtop-primary-results': 'https://wtop.com/virginia-election/2026/08/aug-4-live-results-virginia-primary-election-2026/', 'elect-november-linked': 'https://enr.elections.virginia.gov/results/public/virginia/elections/2026-November-General', 'wtop-primary-ap': 'https://interactives.apelections.org/election-results/customers/layouts/organization-layouts/published/52020/31145.html', 'elect-history-index': 'https://www.elections.virginia.gov/resultsreports/election-results/', 'elect-original-results-directory': 'https://apps.elections.virginia.gov/SBE_CSV/ELECTIONS/ELECTIONRESULTS/', 'elect-2024-senate-historical': 'https://historical.elections.virginia.gov/contest/161257', 'elect-2024-original-document': 'https://historical.elections.virginia.gov/elections/get_source_documentation/168073', 'elect-2024-senate-linked-csv': 'https://va2.elstats.civera.com/api/download_contest/161257_table.csv?split_party=false', 'elect-2020-senate-historical': 'https://historical.elections.virginia.gov/contest/144564', 'elect-2020-senate-linked-csv': 'https://va2.elstats.civera.com/api/download_contest/144564_table.csv?split_party=false'}
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
