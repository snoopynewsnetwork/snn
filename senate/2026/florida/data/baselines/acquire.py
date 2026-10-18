#!/usr/bin/env python3
"""Acquire exact public bodies; originals already in news stay read-only by hash."""
import argparse,datetime,gzip,hashlib,json,urllib.parse
from pathlib import Path
import urllib.request,urllib.error
ROOT=Path(__file__).resolve().parent
SOURCES={
 'dos-senate-2024':('https://results.elections.myflorida.com/DetailRpt.Asp?DATAMODE=&DIST=&ELECTIONDATE=11/5/2024&GRP=&PARTY=&RACE=USS','https://results.elections.myflorida.com/ElectionRaces.asp?ElectionDate=11/5/2024'),
 'dos-senate-2022':('https://results.elections.myflorida.com/DetailRpt.Asp?DATAMODE=&DIST=&ELECTIONDATE=11/8/2022&GRP=&PARTY=&RACE=USS','https://results.elections.myflorida.com/ElectionRaces.asp?ElectionDate=11/8/2022'),
 'dos-president-2024':('https://results.elections.myflorida.com/DetailRpt.Asp?DATAMODE=&DIST=&ELECTIONDATE=11/5/2024&GRP=&PARTY=&RACE=PRE','https://results.elections.myflorida.com/ElectionRaces.asp?ElectionDate=11/5/2024'),
 'dos-president-2020':('https://results.elections.myflorida.com/DetailRpt.Asp?DATAMODE=&DIST=&ELECTIONDATE=11/3/2020&GRP=&PARTY=&RACE=PRE','https://results.elections.myflorida.com/ElectionRaces.asp?ElectionDate=11/3/2020'),
 'election-dates':('https://dos.fl.gov/elections/for-voters/election-dates/','https://dos.fl.gov/elections/'),
 'notices':('https://dos.fl.gov/elections/for-voters/notices-of-general-election/','https://dos.fl.gov/elections/for-voters/election-dates/'),
 'offices':('https://dos.fl.gov/elections/candidates-committees/offices-up-for-election/','https://dos.fl.gov/elections/candidates-committees/'),
 'candidates-index':('https://dos.fl.gov/elections/candidates-committees/','https://dos.fl.gov/elections/'),
 'precinct-index':('https://dos.fl.gov/elections/data-statistics/elections-data/precinct-level-election-results/','https://dos.fl.gov/elections/data-statistics/elections-data/'),
 'supervisors':('https://dos.elections.myflorida.com/supervisors/','https://dos.fl.gov/elections/data-statistics/elections-data/precinct-level-election-results/'),
 'clerk-2024':('https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf','https://history.house.gov/Institution/Election-Statistics/'),
 'clerk-2022':('https://clerk.house.gov/member_info/electionInfo/2022/statistics2022.pdf','https://history.house.gov/Institution/Election-Statistics/'),
 'mail-law':('https://www.flsenate.gov/Laws/Statutes/2026/101.68','https://www.flsenate.gov/Laws/Statutes/2026'),
 'receipt-law':('https://www.flsenate.gov/Laws/Statutes/2026/101.67','https://www.flsenate.gov/Laws/Statutes/2026'),
 'overseas-law':('https://www.flsenate.gov/Laws/Statutes/2026/101.6952','https://www.flsenate.gov/Laws/Statutes/2026'),
 'provisional-law':('https://www.flsenate.gov/Laws/Statutes/2026/101.048','https://www.flsenate.gov/Laws/Statutes/2026'),
 'canvass-law':('https://www.flsenate.gov/Laws/Statutes/2026/102.141','https://www.flsenate.gov/Laws/Statutes/2026'),
 'certification-law':('https://www.flsenate.gov/Laws/Statutes/2026/102.111','https://www.flsenate.gov/Laws/Statutes/2026'),
 'returns-law':('https://www.flsenate.gov/Laws/Statutes/2026/102.112','https://www.flsenate.gov/Laws/Statutes/2026'),
 'tie-law':('https://www.flsenate.gov/Laws/Statutes/2026/100.181','https://www.flsenate.gov/Laws/Statutes/2026'),
 'polls-law':('https://www.flsenate.gov/Laws/Statutes/2026/100.011','https://www.flsenate.gov/Laws/Statutes/2026'),
 'senate-class-I':('https://www.senate.gov/senators/Class_I.htm','https://www.senate.gov/senators/'),
 'senate-class-III':('https://www.senate.gov/senators/Class_III.htm','https://www.senate.gov/senators/'),
}
def sha(b):return hashlib.sha256(b).hexdigest()
def fetch(key,url,parent):
 stamp=datetime.datetime.now(datetime.timezone.utc).isoformat(); hops=[]
 class Redirect(urllib.request.HTTPRedirectHandler):
  def redirect_request(self,req,fp,code,msg,headers,newurl):
   hops.append({'url':req.full_url,'status':code,'headers':list(headers.items()),'location':newurl})
   return super().redirect_request(req,fp,code,msg,headers,newurl)
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; public election research)','Accept-Encoding':'identity'})
 try:r=urllib.request.build_opener(Redirect()).open(req,timeout=50)
 except urllib.error.HTTPError as e:r=e
 raw=r.read(); stored=gzip.compress(raw,mtime=0)
 path=ROOT/'source'/f'{key}.body.gz'
 # Exact byte equality permits reference reuse, without duplicating statewide originals.
 refs=json.loads((ROOT/'source/external-source-references.json').read_text()) if (ROOT/'source/external-source-references.json').exists() else []
 same=next((a for a in refs if a['raw_sha256']==sha(raw) and a.get('status')==200),None)
 if same:
  path=ROOT/same['asset'];stored=path.read_bytes();assert gzip.decompress(stored)==raw
 else:path.write_bytes(stored)
 receipt={'id':key,'requested_url':url,'final_url':r.url,'parent_url':parent,'retrieved_at_utc':stamp,'status':r.code,'headers':list(r.headers.items()),'redirects':hops,'body_bytes_definition':'exact HTTP entity bytes; Accept-Encoding identity requested','raw_sha256':sha(raw),'raw_bytes':len(raw),'stored_sha256':sha(stored),'stored_bytes':len(stored),'asset':__import__('os').path.relpath(path,ROOT),'source_update_time':None,'source_timezone':None,'status_semantics':'read document; HTTP success is not certification'}
 (ROOT/'source'/f'{key}.receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(key,r.code,len(raw),sha(raw),flush=True);return receipt

def reuse_news():
 manifest=json.loads((ROOT.parent/'news/manifest.json').read_text()); wanted=['dos-2024-precinct-official-storage-alias','dos-2022-precinct-official-storage-alias','dos-2020-precinct-zip','dos-precinct-schema-official-storage-alias','nara-2024-index','nara-2024-ascertainment','dos-2024-president-archive-20261009173646','dos-2024-senate-county','dos-2024-races-index','dos-2024-precinct-zip','dos-2022-precinct-zip','electionwatch-downloads']
 refs=[]
 for key in wanted:
  row=next(a for a in manifest if a['id']==key); p=ROOT.parent/'news'/row['asset']; stored=p.read_bytes();raw=gzip.decompress(stored)
  assert sha(raw)==row['raw_sha256'] and sha(stored)==row['stored_sha256']
  refs.append({**row,'asset':'../news/'+row['asset'],'stored_bytes':len(stored),'raw_bytes':len(raw),'reuse':'read-only original reference; original metadata snapshot copied, bytes not duplicated'})
 (ROOT/'source/external-source-references.json').write_text(json.dumps(refs,indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('ids',nargs='*');p.add_argument('--refresh',action='store_true');p.add_argument('--url',help='Exact newly discovered URL; requires one new capture ID');p.add_argument('--parent',help='Actual parent authority URL');a=p.parse_args();reuse_news()
 if a.url:
  if len(a.ids)!=1:p.error('--url requires exactly one capture ID')
  if (ROOT/'source'/f'{a.ids[0]}.receipt.json').exists():p.error('Use a new capture ID; existing evidence is retained')
  fetch(a.ids[0],a.url,a.parent);raise SystemExit(0)
 for key in a.ids or SOURCES:
  if not a.refresh and (ROOT/'source'/f'{key}.receipt.json').exists():continue
  fetch(key,*SOURCES[key])
