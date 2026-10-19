#!/usr/bin/env python3
"""Bounded public research captures, with exact source metadata and compressed bytes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import datetime,gzip,hashlib,json,requests,subprocess,tempfile
ROOT=Path(__file__).resolve().parent
URLS={'denver7-results': 'https://www.denver7.com/electionresults2026', 'cpr-home': 'https://www.cpr.org/', '9news-home': 'https://www.9news.com/', 'kktv-home': 'https://www.kktv.com/', 'nyt-elections': 'https://www.nytimes.com/section/politics/elections', 'kktv-results': 'https://www.kktv.com/politics/election-results/', 'sos-results': 'https://www.sos.state.co.us/pubs/elections/resultsData.html', 'cpr-primary-report': 'https://www.cpr.org/podcast-episode/colorado-primaries-phil-weiser-melat-kiros-wildfire-updates/', 'sun-primary-results': 'https://coloradosun.com/colorado-election-results-2026/', 'sun-primary-ap': 'https://interactives.apelections.org/election-results/customers/layouts/organization-layouts/published/113508/30468.html', 'sos-archive': 'https://www.sos.state.co.us/pubs/elections/Results/Archives.html', 'sos-2024-abstract': 'https://www.coloradosos.gov/pubs/elections/Results/2024/2024BiennialAbstract.pdf', 'sos-2024-native-turnout': 'https://www.sos.state.co.us/pubs/elections/Results/2024/2024GeneralPrecinctVoterTurnout.xlsx', 'sos-2022-abstract-index': 'https://www.sos.state.co.us/pubs/elections/Results/Abstract/2022/index.html', 'sos-2020-abstract-index': 'https://www.sos.state.co.us/pubs/elections/Results/Abstract/2020/index.html'}
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
