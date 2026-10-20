#!/usr/bin/env python3
"""Bounded public research captures, with exact source metadata and compressed bytes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import datetime,gzip,hashlib,json,requests,subprocess,tempfile
ROOT=Path(__file__).resolve().parent
URLS={'opb-election2026': 'https://www.opb.org/tag/election-2026/', 'opb-primary-recap': 'https://www.opb.org/article/2026/05/20/oregon-primary-election-recap-first-look/', 'kgw-home': 'https://www.kgw.com/', 'kptv-home': 'https://www.kptv.com/', 'ktvz-home': 'https://ktvz.com/', 'kezi-home': 'https://www.kezi.com/', 'sos-calendar': 'https://sos.oregon.gov/elections/Documents/current-elections-calendar.pdf', 'sos-results': 'https://results.oregonvotes.gov/', 'nyt-elections': 'https://www.nytimes.com/section/politics/elections', 'kptv-results': 'https://www.kptv.com/politics/election-results', 'ktvz-results': 'https://ktvz.com/election/election-results/', 'ktvz-results-embed': 'https://ktvz.com/wp-admin/admin-ajax.php?action=npg_embed&mode=full', 'sos-history': 'https://sos.oregon.gov/elections/pages/historical-data.aspx', 'sos-2024-abstract': 'https://sos.oregon.gov/elections/Documents/results/november-general-2024-results.pdf', 'sos-2024-abstract-record': 'https://records.sos.state.or.us/ORSOSWebDrawer/Recordhtml/11125187', 'sos-2022-abstract-record': 'https://records.sos.state.or.us/ORSOSWebDrawer/Recordhtml/11125222', 'sos-2020-abstract-record': 'https://records.sos.state.or.us/ORSOSWebDrawer/Recordhtml/7888043', 'sos-2024-precinct-index': 'https://records.sos.state.or.us/ORSOSCMSearch/Search/SearchMain.aspx?t1=notes&q1=2024+General+Election+Precinct+Level+Results&op1=AND&arch=0&page=1&size=25', 'sos-2024-abstract-original': 'https://records.sos.state.or.us/ORSOSCMSearch/Search/DocumentStream.ashx?uri=11125187', 'sos-2022-abstract-original': 'https://records.sos.state.or.us/ORSOSCMSearch/Search/DocumentStream.ashx?uri=11125222', 'sos-2020-abstract-original': 'https://records.sos.state.or.us/ORSOSCMSearch/Search/DocumentStream.ashx?uri=7888043', 'sos-results-webpart-code': 'https://sos.oregon.gov/elections/_layouts/15/OID.SharePoint.StarterTemplate/scripts/data-tables-web-part.js', 'sos-sharepoint-public-client': 'https://orcdn.govstatus.site/Application/CDN/Enterprise/scripts/sharepoint/oregon-sharepoint.js?v=10062026', 'sos-2024-abstract-cdx': 'https://web.archive.org/cdx/search/cdx?url=sos.oregon.gov%2Felections%2FDocuments%2Fresults%2Fnovember-general-2024-results.pdf&output=json&filter=statuscode:200&filter=mimetype:application/pdf&collapse=digest', 'sos-2024-results-archived-20241212': 'https://web.archive.org/web/20241212212240id_/https://sos.oregon.gov/elections/Documents/results/november-general-2024-results.pdf', 'sos-2024-results-archived-20250118': 'https://web.archive.org/web/20250118103853id_/https://sos.oregon.gov/elections/Documents/results/november-general-2024-results.pdf'}
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
