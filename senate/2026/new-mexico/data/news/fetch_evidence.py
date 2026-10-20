#!/usr/bin/env python3
"""Bounded public research captures, with exact source metadata and compressed bytes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import datetime,gzip,hashlib,json,requests,subprocess,tempfile
ROOT=Path(__file__).resolve().parent
URLS={'source-nm-primary': 'https://sourcenm.com/2026/06/03/incumbents-mostly-win-in-contested-new-mexico-legislative-races/', 'kob-home': 'https://www.kob.com/', 'koat-home': 'https://www.koat.com/', 'krqe-home': 'https://www.krqe.com/', 'sos-2026-results': 'https://www.sos.nm.gov/voting-and-elections/election-results/2026-election-results/', 'sos-history': 'https://electionstats.sos.nm.gov/', 'nyt-elections': 'https://www.nytimes.com/section/politics/elections', 'kvia-full-results': 'https://kvia.com/full-election-results/', 'sos-primary': 'https://electionresults.sos.nm.gov/default.aspx?eid=2911', 'sos-2024-archive': 'https://www.sos.nm.gov/sos-archive/election-results-archive/2024-election-results/', 'sos-2022-archive': 'https://www.sos.nm.gov/sos-archive/election-results-archive/2022-election-results/', 'sos-2020-archive': 'https://www.sos.nm.gov/sos-archive/election-results-archive/2020-election-results/', 'sos-2024-general': 'https://electionresults.sos.nm.gov/Default.aspx?eid=2882', 'sos-2022-general': 'https://electionresults.sos.nm.gov/?eid=2838', 'sos-2020-general': 'https://electionresults.sos.nm.gov/Default.aspx?eid=2782', 'sos-2024-media-exports': 'https://electionresults.sos.nm.gov/ResultsMedia.aspx?eid=2882', 'sos-2024-federal': 'https://electionresults.sos.nm.gov/resultsSW.aspx?type=FED&map=CTY&eid=2882', 'sos-2024-federal-csv': 'https://electionresults.sos.nm.gov/resultsCSV.aspx?text=All&type=FED&map=CTY&eid=2882', 'sos-2022-media-exports': 'https://electionresults.sos.nm.gov/ResultsMedia.aspx?eid=2838', 'sos-2020-media-exports': 'https://electionresults.sos.nm.gov/ResultsMedia.aspx?eid=2782', 'sos-2020-federal-csv': 'https://electionresults.sos.nm.gov/resultsCSV.aspx?text=All&type=FED&map=CTY&eid=2782', 'sos-2022-statewide-csv': 'https://electionresults.sos.nm.gov/resultsCSV.aspx?text=All&type=SW&map=CTY&eid=2838', 'elstats-2024-primary-source-discovery': 'https://electionstats.sos.nm.gov/contest/15074', 'elstats-2024-senate': 'https://electionstats.sos.nm.gov/contest/14873', 'elstats-2024-senate-linked-csv': 'https://nm.elstats.civera.com/api/download_contest/14873_table.csv?split_party=false', 'elstats-2024-canvass-document': 'https://electionstats.sos.nm.gov/document/799?page=1', 'elstats-2024-state-canvass-original': 'https://nm.elstats2.civera.com/eng/files/serve/799'}
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
