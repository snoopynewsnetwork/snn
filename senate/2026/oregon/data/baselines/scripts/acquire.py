"""Bounded refresh of observed primary authority URLs; retains all response hops/errors."""
import datetime,gzip,hashlib,json,sys
from pathlib import Path
import requests
R=Path(__file__).resolve().parents[1]/'source/current';R.mkdir(exist_ok=True)
URLS={
 'sos-history':'https://sos.oregon.gov/elections/pages/historical-data.aspx',
 'sos-current-election':'https://sos.oregon.gov/elections/Pages/current-election.aspx',
 'sos-filings':'https://sos.oregon.gov/elections/pages/candidate-filings-local-measures.aspx',
 'sos-native-2024-literal':'https://records.sos.state.or.us/ORSOSCMSearch/Search/SearchMain.aspx?arch=0&op1=AND&page=1&q1=2024+General+Election+Precinct+Level+Results&size=25&t1=notes',
 'lane-access':'https://www.lanecounty.org/government/county_departments/county_administration/general_county_administration/operations/county_clerk/elections/historical_election_details',
 'ors254':'https://www.oregonlegislature.gov/bills_laws/ors/ors254.html'}
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 tag=sys.argv[1] if len(sys.argv)>1 else 'refresh'
 for key,url in URLS.items():
  if (R/f'{tag}-{key}.receipt.json').exists():
   print(key,'existing immutable receipt; use a new tag for a new observation');continue
  now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
  r={'requested_url':url,'started_utc':now(),'method':'GET','parent':'independently observed official navigation or official search result','hops':[]}
  try:
   response=requests.get(url,timeout=35)
   for n,s in enumerate([*response.history,response]):
    body=s.content;stored=gzip.compress(body,mtime=0);f=R/f'{tag}-{key}-hop{n}.gz';f.write_bytes(stored)
    r['hops'].append({'url':s.url,'status':s.status_code,'headers':dict(s.headers),'raw_bytes':len(body),'raw_sha256':sha(body),'stored_bytes':len(stored),'stored_sha256':sha(stored),'asset':f.name})
   r['final_url']=response.url
  except Exception as e:r['error']=str(e)
  r['finished_utc']=now();(R/f'{tag}-{key}.receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(key,r.get('error') or r['hops'][-1]['status'],flush=True)
if __name__=='__main__':main()
