#!/usr/bin/env python3
"""Acquire only explicit public primary URLs; immutable retained sources reused by hash.
Run python acquire.py. Existing captures are verified, never silently refetched.
Original entity bytes are gzip stored (mtime=0); receipt records HTTP decoding.
"""
import datetime,gzip,hashlib,json,sys
from pathlib import Path
import requests
D=Path(__file__).resolve().parent;S=D/'source';S.mkdir(exist_ok=True)
URLS={
'enr-2022-observed-history-link':'https://electionresults.sd.gov/Default.aspx?eid=471',
'enr-2020-observed-history-link':'https://electionresults.sd.gov/?eid=422',
'returns-2024-archive':'https://sdsos.gov/elections-voting/assets/Archive/2024%20Assets/Post-Election-Audit-General/ElectionReturns2024.pdf',
'returns-2022-archive':'https://sdsos.gov/elections-voting/assets/Archive/Prior%20to%202026/Election%20Returns%202022.pdf',
'returns-2020-archive':'https://sdsos.gov/elections-voting/assets/Archive/Prior%20to%202026/ElectionReturns2020web.pdf',
'census-counties2020':'https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt',
'official-returns-index':'https://sdsos.gov/elections-voting/election-resources/election-history/official-election-returns.aspx',
'returns-2024':'https://sdsos.gov/elections-voting/assets/2024%20Assets/Post-Election-Audit-General/ElectionReturns2024.pdf',
'returns-2022':'https://sdsos.gov/elections-voting/assets/Election%20Returns%202022.pdf',
'returns-2020':'https://sdsos.gov/elections-voting/assets/ElectionReturns2020web.pdf',
'2026-offices':'https://www.sdsos.gov/elections-voting/upcoming-elections/general-information/2026%20Election%20Information/2026-offices-to-be-filled.aspx',
'2024-pres-ballot':'https://www.sdsos.gov/elections-voting/upcoming-elections/general-information/2024/2024-Presidential-Ballot-Access.aspx',
'2026-candidates':'https://vip.sdsos.gov/candidatelist.aspx?eid=774',
'2024-terminology':'https://electionresults.sd.gov/ElectionTerminology.aspx?eid=684',
'census-sd-counties':'https://api.census.gov/data/2020/dec/pl?get=NAME&for=county:*&in=state:46',
}
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 for key,url in URLS.items():
  receipt=S/(key+'.receipt.json');asset=S/(key+'.body.gz')
  if receipt.exists():
   a=json.loads(receipt.read_text())
   if 'error' in a:
    (S/(key+'.failed-request.json')).write_text(receipt.read_text());receipt.unlink()
   else:
    z=asset.read_bytes();assert sha(z)==a['stored_sha256'] and sha(gzip.decompress(z))==a['raw_sha256'];print(key,'verified retained');continue
  at=datetime.datetime.now(datetime.timezone.utc).isoformat()
  try:
   r=requests.get(url,timeout=45);raw=r.content;z=gzip.compress(raw,mtime=0);assert len(z)<40000000;asset.write_bytes(z)
   a={'id':key,'requested_url':url,'request_method':'GET','final_url':r.url,'retrieved_at_utc':at,'http_status':r.status_code,'headers':dict(r.headers),'redirects':[{'url':h.url,'status':h.status_code,'location':h.headers.get('Location')}for h in r.history],'entity_decoding':'requests HTTP transfer/content decoding; raw hash is complete decoded HTTP entity bytes','raw_bytes':len(raw),'raw_sha256':sha(raw),'stored_bytes':len(z),'stored_sha256':sha(z),'asset':asset.name}
  except requests.RequestException as e:a={'id':key,'requested_url':url,'retrieved_at_utc':at,'error':repr(e)}
  receipt.write_text(json.dumps(a,indent=2)+'\n');print(key,a.get('http_status'),a.get('raw_bytes'),flush=True)
if __name__=='__main__':main()
