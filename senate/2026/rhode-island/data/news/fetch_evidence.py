#!/usr/bin/env python3
"""Bounded public research captures, with exact source metadata and compressed bytes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import datetime,gzip,hashlib,json,requests,subprocess,tempfile
ROOT=Path(__file__).resolve().parent
URLS={'journal-primary-results': 'https://election.providencejournal.com/', 'wpri-home': 'https://www.wpri.com/', 'turnto10-home': 'https://turnto10.com/', 'publics-radio-home': 'https://thepublicsradio.org/', 'state-results': 'https://electionresults.ri.gov/', 'state-primary': 'https://electionresults.ri.gov/results/public/rhodeisland/elections/RI2026StatewidePrimary', 'nyt-elections': 'https://www.nytimes.com/section/politics/elections', 'journal-election-config': 'https://election.providencejournal.com/js/election-config.js', 'journal-election-code': 'https://election.providencejournal.com/js/election.js', 'journal-statewide-primary': 'https://election.providencejournal.com/data-fetch/get-election-results.php?locale=statewide', 'boe-history': 'https://elections.ri.gov/elections/previous-election-results', 'boe-publications': 'https://elections.ri.gov/elections/publications', 'boe-2024-summary': 'https://elections.ri.gov/sites/g/files/xkgbur756/files/2024-12/Gen24SummaryReport.pdf', 'ri-2024-general-old-authority': 'https://www.ri.gov/election/results/2024/general_election/', 'ri-2024-data-index': 'https://www.ri.gov/election/results/2024/general_election/data/', 'ri-2024-senate': 'https://www.ri.gov/election/results/2024/general_election/races/2.html', 'ri-2024-original-data-zip': 'https://www.ri.gov/election/results/2024/general_election/data/rigen2024.zip', 'ri-2024-layout-zip': 'https://www.ri.gov/election/results/2024/general_election/data/rigen2024l.zip', 'ri-2022-description': 'https://www.ri.gov/election/results/20220819_data_description.pdf'}
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
