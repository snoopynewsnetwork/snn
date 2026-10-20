#!/usr/bin/env python3
"""Bounded public research captures, with exact source metadata and compressed bytes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import datetime,gzip,hashlib,json,requests,subprocess,tempfile
ROOT=Path(__file__).resolve().parent
URLS={'reflector-home': 'https://alabamareflector.com/', 'wbbrc-home': 'https://www.wbrc.com/', 'wsfa-home': 'https://www.wsfa.com/', 'waff-home': 'https://www.waff.com/', 'wkra-home': 'https://www.wkrg.com/', 'sos-primary-release': 'https://www.sos.alabama.gov/newsroom/secretary-state-wes-allen-announces-unofficial-primary-election-results-are-available', 'nyt-elections': 'https://www.nytimes.com/section/politics/elections', 'wsfa-results': 'https://www.wsfa.com/politics/election-results', 'wbrc-results': 'https://www.wbrc.com/politics/election-results/', 'sos-election-information': 'https://www.sos.alabama.gov/alabama-votes/voter/election-information', 'sos-2022-canvass-parent': 'https://www.sos.alabama.gov/node/3228', 'sos-2022-canvass-original': 'https://www.sos.alabama.gov/sites/default/files/election-data/2022-11/Final%20Canvass%20of%20Results%20%28canvassed%20by%20state%20canvassing%20board%2011-28-2022%29.pdf', 'sos-2024-results-index': 'https://www.sos.alabama.gov/alabama-votes/voter/election-information/2024', 'sos-2020-results-index': 'https://www.sos.alabama.gov/alabama-votes/voter/election-information/2020', 'sos-2024-canvass-original': 'https://www.sos.alabama.gov/sites/default/files/election-2024/State%20Certification%20of%202024%20General%20Election.pdf', 'sos-2020-canvass-original': 'https://www.sos.alabama.gov/sites/default/files/election-2020/Final%20Canvass%20of%20Results-Merged.pdf', 'sos-2020-ballots-original': 'https://www.sos.alabama.gov/sites/default/files/election-2020/2020_General_Total_Ballots_Cast_Report.pdf'}
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
