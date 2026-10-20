#!/usr/bin/env python3
from pathlib import Path
from urllib.parse import urljoin
import requests,gzip,json,hashlib,datetime,re,html
P=Path(__file__).resolve().parent

def main():
 rows=[]
 for year in [2020,2022,2024]:
  sid=f'registration-archive-{year}';base=f'https://elections.delaware.gov/voter/registrationtotals/regtotals{year}.html';t=gzip.decompress((P/f'source/current/{sid}.gz').read_bytes()).decode('utf-8-sig');links=re.findall(r'href=["\']([^"\']+)["\']',t)
  wanted=[x for x in links if str(year)+'1101' in x and (x.endswith('.csv') or year==2020 and x.endswith('.html'))]
  for i,href in enumerate(wanted):
   url=urljoin(base,html.unescape(href));now=datetime.datetime.now(datetime.timezone.utc).isoformat();r=requests.get(url,timeout=60,headers={'Accept-Encoding':'identity'});b=r.content;z=gzip.compress(b,mtime=0);name=f'november-registration-{year}-{i}';path=P/'source/current'/(name+'.gz');path.write_bytes(z);rows.append(dict(id=name,requested_url=url,final_url=r.url,parent=base,discovered_href=href,retrieved_utc=now,status=r.status_code,response_headers=dict(r.headers),redirect_chain=[dict(url=x.url,status=x.status_code,headers=dict(x.headers)) for x in r.history],asset='source/current/'+path.name,raw_sha256=hashlib.sha256(b).hexdigest(),stored_sha256=hashlib.sha256(z).hexdigest(),raw_bytes=len(b),stored_bytes=len(z)))
   (P/'source/registration-acquisition.json').write_text(json.dumps(rows,indent=2)+'\n')
 print([(r['id'],r['status'],r['raw_bytes']) for r in rows])
if __name__=='__main__':main()
