#!/usr/bin/env python3
"""Original public downloads; preserve all bytes, redirects and failed transport evidence."""
from pathlib import Path
import datetime,gzip,hashlib,json,subprocess,tempfile,requests
ROOT=Path(__file__).resolve().parents[1]/'source'
URLS={
 'lincoln-elections':'https://www.lincolncountysd.gov/159/Elections',
 'lincoln-2026-publication-ballot':'https://www.lincolncountysd.gov/DocumentCenter/View/1989/Sample-Ballot-2026-PDF',
 'sos-2026-information':'https://www.sdsos.gov/elections-voting/upcoming-elections/general-information/2026%20Election%20Information/default.aspx',
 'sos-2026-precinct-manual':'https://sdsos.gov/elections-voting/assets/2026%20Documents/2026PrecinctManual.pdf',
 'statutes-chapter12-20':'https://sdlegislature.gov/Statutes/12-20',
 'current-senate-status':'https://vip.sdsos.gov/candidatelist.aspx?eid=774',
 'minnehaha-home':'https://www.minnehahacounty.gov/',
 'minnehaha-elections':'https://www.minnehahacounty.gov/dept/au/electionInfo/electionInfo.php',
 'senate-classII':'https://www.senate.gov/senators/Class_II.htm',
 'senate-classIII':'https://www.senate.gov/senators/Class_III.htm',
 'census-county-name-change':'https://www.census.gov/programs-surveys/geography/technical-documentation/county-changes.2010.html',
 'sos-2025-election-code':'https://sdsos.gov/elections-voting/assets/2025%20Documents/2025%20Election%20Code.pdf',
 'lincoln-ballot-alternate-host':'https://lincolncountysd.gov/DocumentCenter/View/1989/Sample-Ballot-2026-PDF',
 'lincoln-ballot-resource-route':'https://www.lincolncountysd.gov/DocumentCenter/View/1989',
 'lincoln-ballot-download-query':'https://www.lincolncountysd.gov/DocumentCenter/View/1989/Sample-Ballot-2026-PDF?download=1',
}
def sha(b):return hashlib.sha256(b).hexdigest()
def fetch(key,url):
 a=dict(id=key,requested_url=url,method='GET',retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),parent='lincoln-elections'if key=='lincoln-2026-publication-ballot'else None)
 try:
  r=requests.get(url,timeout=45);raw=r.content
  a.update(status=r.status_code,final_url=r.url,headers=dict(r.headers),redirects=[dict(status=h.status_code,url=h.url,headers=dict(h.headers))for h in r.history],transport='requests default TLS')
 except requests.exceptions.RequestException as e:
  a['requests_failure']=str(e)
  with tempfile.TemporaryDirectory()as d:
   d=Path(d);r=subprocess.run(['curl','--silent','--show-error','--location','--max-time','45','--dump-header',str(d/'headers'),'--output',str(d/'body'),'--write-out','%{http_code}\n%{url_effective}',url],capture_output=True,text=True)
   a.update(curl_exit=r.returncode,curl_stderr=r.stderr,transport='curl default TLS',raw_response_headers=(d/'headers').read_text()if(d/'headers').exists()else None)
   if r.returncode:
    (ROOT/(key+'.receipt.json')).write_text(json.dumps(a,indent=2)+'\n');return
   code,final=r.stdout.split('\n',1);raw=(d/'body').read_bytes();a.update(status=int(code),final_url=final)
 z=gzip.compress(raw,mtime=0);assert len(z)<40000000
 asset=key+'.body.gz';(ROOT/asset).write_bytes(z)
 a.update(asset=asset,raw_bytes=len(raw),raw_sha256=sha(raw),stored_bytes=len(z),stored_sha256=sha(z),entity_definition='complete HTTP response entity after transfer/content decoding; gzip is local lossless storage')
 (ROOT/(key+'.receipt.json')).write_text(json.dumps(a,indent=2)+'\n');print(key,a['status'],len(raw))
if __name__=='__main__':
 for k,u in URLS.items():fetch(k,u)
