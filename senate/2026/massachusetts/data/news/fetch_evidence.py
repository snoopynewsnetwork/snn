#!/usr/bin/env python3
"""Bounded public research captures, with exact source metadata and compressed bytes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import datetime,gzip,hashlib,json,requests,subprocess,tempfile
ROOT=Path(__file__).resolve().parent
URLS={'wbur-election': 'https://www.wbur.org/news/tag/massachusetts-2026-election', 'wbur-primary-analysis': 'https://www.wbur.org/news/2026/09/02/primary-election-results-massachusetts', 'wgbh-primary': 'https://www.wgbh.org/news/local/2026-09-02/gbh-daily-incumbent-sweep', 'wwlp-home': 'https://www.wwlp.com/', 'state-elections': 'https://www.sec.state.ma.us/divisions/elections/elections-and-voting.htm', 'nyt-elections': 'https://www.nytimes.com/section/politics/elections', 'wgbh-primary-results': 'https://www.wgbh.org/news/politics/2026-09-01/live-results-of-the-2026-massachusetts-primary-elections', 'wgbh-senate-primary-ap': 'https://interactives.apelections.org/election-results/customers/layouts/organization-layouts/published/60951/32341.html', 'nepm-primary-results': 'https://www.nepm.org/2026-09-01/live-wmass-2026-primary-election-results', 'westernmass-results': 'https://www.westernmassnews.com/politics/election-results/', 'westernmass-embed': 'https://webpubcontent.gray.tv/wggb/xml/WMNelections.html', 'nepm-primary-ap': 'https://interactives.apelections.org/election-results/customers/layouts/organization-layouts/published/79545/32390.html', 'sos-pd43-root': 'https://electionstats.state.ma.us/index.php', 'sos-2024-senate-view': 'https://electionstats.state.ma.us/elections/view/165304/', 'sos-2024-senate-municipal-csv': 'https://electionstats.state.ma.us/elections/download/165304/precincts_include:0/', 'sos-2024-senate-precinct-csv': 'https://electionstats.state.ma.us/elections/download/165304/precincts_include:1/'}
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
