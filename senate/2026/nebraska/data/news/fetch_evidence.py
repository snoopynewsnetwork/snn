#!/usr/bin/env python3
"""Bounded public research captures, with exact source metadata and compressed bytes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import datetime,gzip,hashlib,json,requests,subprocess,tempfile
ROOT=Path(__file__).resolve().parent
URLS={'wowt-politics': 'https://www.wowt.com/politics/', '1011-home': 'https://www.1011now.com/', 'ketv-home': 'https://www.ketv.com/', 'knop-home': 'https://www.knopnews2.com/', 'nyt-elections': 'https://www.nytimes.com/section/politics/elections', 'wowt-results': 'https://www.wowt.com/politics/election-results/', 'wowt-nebraska': 'https://www.wowt.com/nebraska-election-results/', '1011-results': 'https://www.1011now.com/politics/election-results/', 'knop-results': 'https://www.knopnews2.com/politics/election-results/', 'ketv-primary': 'https://www.ketv.com/article/nebraska-primary-election-results-2026/71151712', 'sos-enr': 'https://electionresults.nebraska.gov/', 'county-results': 'https://countyelectionresults.nebraska.gov/default.aspx', 'ketv-senate-primary-ap': 'https://interactives.apelections.org/election-results/customers/layouts/organization-layouts/published/58700/28086.html', 'ketv-local-primary-embed': 'https://ehub.htvapps.com/ketv/wp-json/election-hub/v1/iframe-embed/460', 'sos-previous-elections': 'https://sos.nebraska.gov/previous-elections', 'sos-2024-canvass': 'https://sos.nebraska.gov/sites/default/files/doc/elections/2024/2024%20General%20Canvass%20Book.pdf', 'sos-2022-canvass': 'https://sos.nebraska.gov/sites/default/files/doc/elections/2022/2022%20General%20Canvass%20Book.pdf', 'sos-2020-canvass': 'https://sos.nebraska.gov/sites/default/files/doc/elections/2020/2020-General-Canvass-Book.pdf', 'sos-enr-linked-bundle': 'https://neresultswebservice.azurewebsites.us/Scripts/script.bundle.js', 'sos-enr-observed-candidates': 'https://neresultswebservice.azurewebsites.us/ResultsAjax.svc/GetCandidates?ElectionType=General&ElectionID=0', 'sos-enr-statewide': 'https://electionresults.nebraska.gov/resultsSW.aspx?type=SW&map=CTY', 'sos-2026-election-parent': 'https://sos.nebraska.gov/elections', 'sos-final-general-candidate-pdf': 'https://sos.nebraska.gov/sites/default/files/doc/elections/2026/Final_Statewide_General_Candidate_Filing_List_9.11.26.pdf'}
def fetch(item):
 key,url=item;row={'id':key,'url':url,'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  r=requests.get(url,timeout=35);path=ROOT/(key+'.html.gz');path.write_bytes(gzip.compress(r.content,mtime=0))
  row.update(status=r.status_code,final_url=r.url,redirects=[{'url':h.url,'status':h.status_code,'location':h.headers.get('Location')} for h in r.history],raw_sha256=hashlib.sha256(r.content).hexdigest(),asset=path.name,stored_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=len(r.content),headers=dict(r.headers))
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
