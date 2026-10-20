#!/usr/bin/env python3
"""Explicit acquisition; default offline reuse of complete original newsroom bodies.
--fetch-current saves new bodies and every response/redirect header; never writes shared files.
"""
from pathlib import Path
import gzip,hashlib,json,datetime,sys,requests,re,html
from urllib.parse import urljoin
P=Path(__file__).resolve().parent; N=P.parent/'news'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 mf=json.loads((N/'manifest.json').read_text()); ids=['state-results','sos-observed-general-archive','sos-2024-general-report','sos-2024-csv','sos-2024-valid-writeins','official-2022-report','sos-observed-2022-state-csv','sos-observed-2022-writeins','sos-observed-2020-general-report','sos-observed-2020-state-csv','sos-observed-2020-writeins','state-calendar']
 rows=[]
 for sid in ids:
  a=next(r for r in mf if r['id']==sid);z=(N/a['asset']).read_bytes();b=gzip.decompress(z)
  assert sha(z)==a['stored_sha256'] and sha(b)==a['raw_sha256']
  rows.append(dict(a,shared_asset='../news/'+a['asset'],redirect_chain_scope='Historical receipt has requested/final URL only; intermediate redirects not retained',reuse='Exact stored gzip and decompressed entity verified independently; shared read-only'))
 (P/'source/shared-sources.json').write_text(json.dumps(rows,indent=2)+'\n')
 if '--fetch-current' not in sys.argv:return
 dest=P/'source/current';dest.mkdir(exist_ok=True);ledger=[]
 def fetch(sid,url,parent=None,anchor=None):
  now=datetime.datetime.now(datetime.timezone.utc).isoformat();r=requests.get(url,timeout=65,headers={'User-Agent':'Delaware historical election research; public original-source audit','Accept-Encoding':'identity'})
  b=r.content;path=dest/(sid+'.gz');path.write_bytes(gzip.compress(b,mtime=0));z=path.read_bytes()
  ledger.append(dict(id=sid,requested_url=url,final_url=r.url,retrieved_utc=now,status=r.status_code,response_headers=dict(r.headers),redirect_chain=[dict(url=x.url,status=x.status_code,headers=dict(x.headers)) for x in r.history],parent=parent,discovered_href=anchor,asset='source/current/'+path.name,raw_sha256=sha(b),stored_sha256=sha(z),raw_bytes=len(b),stored_bytes=len(z),entity_scope='Complete requests decoded HTTP entity; transfer/content transport encoding removed'))
  (P/'source/current-acquisition.json').write_text(json.dumps(ledger,indent=2)+'\n');return r.text
 results=fetch('results','https://elections.delaware.gov/results/')
 candidates=fetch('candidates','https://elections.delaware.gov/candidates/candidatelist/', 'results','/candidates/candidatelist')
 for year in [2020,2022,2024,2026]:
  for kind in ['fcddt','wcddt']:
   href=next((html.unescape(x) for x in re.findall(r'href=["\']([^"\']+)',candidates) if f'genl_{kind}_{year}.html' in x),None)
   if href:fetch(f'candidates-{kind}-{year}',urljoin('https://elections.delaware.gov/candidates/candidatelist/',href),'candidates',href)
 for sid,frag in [('primary-2026','PR2026.html'),('archive','election_archive.html')]:
  href=next(html.unescape(x) for x in re.findall(r'href=["\']([^"\']+)',results) if frag in x);fetch(sid,urljoin('https://elections.delaware.gov/results/',href),'results',href)
 fetch('locations','https://elections.delaware.gov/locations.html','results','/locations.html')
 reg=fetch('registration','https://elections.delaware.gov/candidates/regtotals.html','results','/candidates/regtotals.html')
 for year in [2020,2022,2024]:
  links=re.findall(r'href=["\']([^"\']+)',reg)
  for suffix,frag in [('statistics',f'Age'),('archive',f'{year}')]:
   found=[html.unescape(x) for x in links if str(year) in x]
   if suffix=='archive' and found:
    href=found[0];fetch(f'registration-{year}',urljoin('https://elections.delaware.gov/candidates/regtotals.html',href),'registration',href)
 # Current authoritative legal text, discovered/referenced scope is statute URLs, not guessed election IDs.
 fetch('code-chapter57','https://delcode.delaware.gov/title15/c057/index.html',None,'official law canvass/winner rules')
 fetch('code-chapter45','https://delcode.delaware.gov/title15/c045/index.html',None,'official law ballot/write-in provisions')
 print(json.dumps([{'id':r['id'],'status':r['status'],'bytes':r['raw_bytes']} for r in ledger]))
if __name__=='__main__':main()
