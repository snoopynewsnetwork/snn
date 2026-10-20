#!/usr/bin/env python3
"""Bounded public research captures, with exact source metadata and compressed bytes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import datetime,gzip,hashlib,json,requests,subprocess,tempfile
ROOT=Path(__file__).resolve().parent
URLS={'wboc-results': 'https://www.wboc.com/elections/election-results/', 'delaware-public-home': 'https://www.delawarepublic.org/', '6abc-primary': 'https://6abc.com/politics/elections/local/?year=2026', 'state-results': 'https://elections.delaware.gov/results/', 'state-calendar': 'https://elections.delaware.gov/public/calendar/pdfs/2026ElectionCalendar.pdf', 'nyt-elections': 'https://www.nytimes.com/section/politics/elections', 'wboc-senate-primary': 'https://www.wboc.com/elections/election-results/u-s-senate---delaware-r/race_07d6935f-ab62-4a81-84a1-e5dfd90a18bb.html', 'spotlight-primary-results': 'https://jowensspde.github.io/2026-Primary-Election-Results/public/', 'spotlight-primary-config': 'https://jowensspde.github.io/2026-Primary-Election-Results/public/config.js', 'spotlight-primary-app': 'https://jowensspde.github.io/2026-Primary-Election-Results/public/app.js', 'spotlight-primary-data': 'https://delaware-primary-results-2026.spotlightdelaware.workers.dev/api/results', 'fox29-results': 'https://www.fox29.com/election-results', 'fox29-primary-table': 'https://media.foxtv.com/wtxf/elections/2026_DE_PRIMARY.html', 'official-2022-report': 'https://elections.delaware.gov/reports/GE2022.html', 'sos-2024-general-report': 'https://elections.delaware.gov/reports/GE2024.html', 'sos-2024-csv': 'https://elections.delaware.gov/reports/GE2024.csv', 'sos-2024-valid-writeins': 'https://elections.delaware.gov/elections/resultsarchive/elect24/elect24_general/GE2024_Official_WriteInVotes_Statewide.pdf'}
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
