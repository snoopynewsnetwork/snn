#!/usr/bin/env python3
"""Bounded public research captures, with exact source metadata and compressed bytes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import datetime,gzip,hashlib,json,requests,subprocess,tempfile
ROOT=Path(__file__).resolve().parent
URLS={'sos-results': 'https://voteidaho.gov/election-results/', 'sos-data': 'https://voteidaho.gov/data-and-dashboards/', 'ktvb-home': 'https://www.ktvb.com/', 'kifi-home': 'https://localnews8.com/', 'boisestate-primary': 'https://www.boisestatepublicradio.org/politics-government/2026-06-10/idaho-primary-election-results-certified', 'nyt-elections': 'https://www.nytimes.com/section/politics/elections', 'ktvb-nov-guide': 'https://www.ktvb.com/article/news/politics/voter-guide/2026-idaho-general-election-voter-guide-candidates-races-polling-place-results/277-6cc81b3c-0fb3-4e25-9291-28cb727279d3', 'kifi-results': 'https://localnews8.com/politics/election-results/', 'kxly-home': 'https://www.kxly.com/', 'kmvt-results': 'https://www.kmvt.com/politics/election-results/', 'sos-2024-canvass': 'https://archive.sos.idaho.gov/elections/data/results/2024/2024_general_canvass.pdf', 'sos-2024-all-races-xlsx': 'https://archive.sos.idaho.gov/elections/data/results/2024/raw_races_general.xlsx', 'sos-2024-turnout-xlsx': 'https://archive.sos.idaho.gov/elections/data/results/2024/raw_stats_general.xlsx', 'sos-2022-general-canvass-zip': 'https://archive.sos.idaho.gov/elections/data/results/2022/2022_General_Canvass.zip', 'sos-2020-general-canvass-zip': 'https://archive.sos.idaho.gov/elections/data/results/2020/2020_General_Canvass.zip', 'sos-2020-general-abstracts-zip': 'https://archive.sos.idaho.gov/elections/data/results/2020/2020_General_Abstracts.zip'}
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
