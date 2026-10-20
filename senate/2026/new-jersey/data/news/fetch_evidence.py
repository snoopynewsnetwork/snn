#!/usr/bin/env python3
"""Bounded public research captures, with exact source metadata and compressed bytes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import datetime,gzip,hashlib,json,requests,subprocess,tempfile
ROOT=Path(__file__).resolve().parent
URLS={'njspotlight-home': 'https://www.njspotlightnews.org/', 'njspotlight-primary-report': 'https://www.njspotlightnews.org/2026/06/nj-primary-one-u-s-senate-seat-all-12-in-house-top-the-ballot/', 'nj-election-info': 'https://nj.gov/state/elections/election-information-2026.shtml', 'nj-election-night': 'https://www.nj.gov/state/elections/election-night-results.shtml', 'nbc10-home': 'https://www.nbcphiladelphia.com/', 'news12-home': 'https://newjersey.news12.com/', 'nyt-elections': 'https://www.nytimes.com/section/politics/elections', 'news12-primary': 'https://newjersey.news12.com/vote-2026-new-jersey-primaries', 'fox29-results': 'https://www.fox29.com/election-results', 'news12-primary-embed': 'https://elections.news12.com/elections_v2/2026/index.jsp?region=NJ&category=U.S.%20House&sub_category=7th%20District%20Democratic%20Primary', 'news12-primary-code': 'https://elections.news12.com/elections_v2/2026/js/elections.js?clear=3', 'news12-primary-categories': 'https://elections.news12.com/elections_v2/2026/include/categories.jsp?region=NJ', 'news12-primary-category-list': 'https://elections.news12.com/elections_v2/2026/include/categories.jsp?region=NJ&type=category&title=', 'news12-primary-linked-house-list': 'https://elections.news12.com/elections_v2/2026/include/categories.jsp?region=NJ&type=sub_category&title=U.S.%20House', 'news12-senate-general-list': 'https://elections.news12.com/elections_v2/2026/include/categories.jsp?region=NJ&type=sub_category&title=U.S.+Senate+Class+II+General+New+Jersey+state+', 'news12-senate-general-data': 'https://elections.news12.com/elections_v2/2026/include/races.jsp?RaceID=13&region=NJ', 'sos-2022-index': 'https://www.nj.gov/state/elections/election-information-2022.shtml', 'sos-current-results': 'https://nj.gov/state/elections/election-results.shtml', 'sos-2024-index': 'https://nj.gov/state/elections/election-information-2024.shtml', 'sos-2024-senate-county': 'https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-results-us-senate.pdf', 'sos-2020-index': 'https://nj.gov/state/elections/election-information-2020.shtml', 'sos-2024-president-county': 'https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-results-president.pdf', 'sos-2024-turnout': 'https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-voter-turnout.pdf', 'sos-2020-senate-county': 'https://nj.gov/state/elections/assets/pdf/election-results/2020/2020-official-general-results-us-senate.pdf', 'sos-2022-turnout': 'https://nj.gov/state/elections/assets/pdf/election-results/2022/2022-official-general-voter-turnout.pdf', 'sos-2018-index': 'https://nj.gov/state/elections/election-information-2018.shtml', 'sos-2018-senate-county': 'https://nj.gov/state/elections/assets/pdf/election-results/2018/2018-official-general-election-results-us-senate.pdf'}
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
