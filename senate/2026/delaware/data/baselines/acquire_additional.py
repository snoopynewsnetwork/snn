#!/usr/bin/env python3
from pathlib import Path
from urllib.parse import urljoin
import requests,gzip,json,hashlib,datetime,re,html
P=Path(__file__).resolve().parent

def main():
 parent='https://elections.delaware.gov/candidates/regtotals.html';t=gzip.decompress((P/'source/current/registration.gz').read_bytes()).decode();links=re.findall(r'href=["\']([^"\']+)["\']',t);rows=[]
 targets=[(f'participation-{y}',f'agprpt_{y}.txt') for y in [2020,2022,2024]]+[(f'registration-archive-{y}',f'regtotals{y}.html') for y in [2020,2022,2024]]+[('registration-definitions','RegistrationTotalsPageInformation.pdf')]
 for sid,frag in targets:
  href=next(html.unescape(x) for x in links if frag in x);url=urljoin(parent,href);now=datetime.datetime.now(datetime.timezone.utc).isoformat();r=requests.get(url,timeout=60,headers={'Accept-Encoding':'identity'});b=r.content;z=gzip.compress(b,mtime=0);path=P/'source/current'/(sid+'.gz');path.write_bytes(z);rows.append(dict(id=sid,requested_url=url,final_url=r.url,parent=parent,discovered_href=href,retrieved_utc=now,status=r.status_code,response_headers=dict(r.headers),redirect_chain=[dict(url=x.url,status=x.status_code,headers=dict(x.headers)) for x in r.history],asset='source/current/'+path.name,raw_sha256=hashlib.sha256(b).hexdigest(),stored_sha256=hashlib.sha256(z).hexdigest(),raw_bytes=len(b),stored_bytes=len(z)))
  (P/'source/additional-acquisition.json').write_text(json.dumps(rows,indent=2)+'\n')
 print([(x['id'],x['status'],x['raw_bytes']) for x in rows])
if __name__=='__main__':main()
