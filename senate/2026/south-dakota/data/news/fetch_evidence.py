#!/usr/bin/env python3
"""Bounded public research captures, with exact source metadata and compressed bytes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import datetime,gzip,hashlib,json,requests,subprocess,tempfile
ROOT=Path(__file__).resolve().parent
URLS={'sos-results-media': 'https://electionresults.sd.gov/ResultsMedia.aspx', 'kelo-home': 'https://www.keloland.com/', 'dakota-home': 'https://www.dakotanewsnow.com/', 'newscenter1-home': 'https://www.newscenter1.tv/', 'nyt-elections': 'https://www.nytimes.com/section/politics/elections', 'dakota-results': 'https://www.dakotanewsnow.com/politics/election-results/', 'sos-statewide-export': 'https://electionresults.sd.gov/resultsCSV.aspx?text=All&type=SWR&map=CTY', 'sos-election-history': 'https://sdsos.gov/elections-voting/election-resources/election-history/default.aspx', 'sos-2024-history': 'https://sdsos.gov/elections-voting/election-resources/election-history/2024_Election_History.aspx', 'sos-2024-general-canvass': 'https://sdsos.gov/elections-voting/assets/Archive/2024%20Assets/Recount-Canvass-and-Canvass-Docs-General/2024GeneralElectionCanvassWithCert.pdf', 'sos-2024-general-county-aurora-clark': 'https://sdsos.gov/elections-voting/assets/Archive/2024%20Assets/Recount-Canvass-and-Canvass-Docs-General/Aurora-Clark.pdf', 'sos-2022-history': 'https://sdsos.gov/elections-voting/election-resources/election-history/2022_Election_History.aspx', 'sos-2024-county-clay-faulk': 'https://sdsos.gov/elections-voting/assets/Archive/2024%20Assets/Recount-Canvass-and-Canvass-Docs-General/Clay-Faulk.pdf', 'sos-2024-county-grant-lyman': 'https://sdsos.gov/elections-voting/assets/Archive/2024%20Assets/Recount-Canvass-and-Canvass-Docs-General/Grant-Lyman.pdf', 'sos-2024-county-marshall-ziebach': 'https://sdsos.gov/elections-voting/assets/Archive/2024%20Assets/Recount-Canvass-and-Canvass-Docs-General/Marshall-Ziebach.pdf', 'sos-2022-general-canvass': 'https://sdsos.gov/elections-voting/assets/Archive/2022%20Assets/2022Generalcanvassreport.pdf', 'sos-2022-precinct-canvass': 'https://sdsos.gov/elections-voting/assets/Archive/2022%20Assets/2022PrecintCanvass.pdf', 'sos-2022-general-recount': 'https://sdsos.gov/elections-voting/assets/Archive/2022%20Assets/2022GeneralStateCanvassRecountReport.pdf', 'sos-2020-history': 'https://sdsos.gov/elections-voting/election-resources/election-history/2020_Election_History.aspx', 'sos-2020-history-retry': 'https://sdsos.gov/elections-voting/election-resources/election-history/2020_Election_History.aspx', 'sos-2020-general-canvass': 'https://sdsos.gov/elections-voting/assets/Archive/2020%20Assests/2020GeneralStateCanvassFinal%26Certificate.pdf', 'sos-2020-general-county-canvass': 'https://sdsos.gov/elections-voting/assets/Archive/2020%20Assests/2020GeneralCountyCanvassFinal.pdf', 'sos-general-candidate-list': 'https://vip.sdsos.gov/candidatelist.aspx?eid=774', 'sos-bengs-validation': 'https://sdsos.gov/about-the-office/assets/Press%20Releases/BengsValidationPressRelease.pdf'}
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
