"""One bounded current observation; prior 35-receipt source ledger unchanged."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import csv,gzip,hashlib,io,json,re
import requests
N=Path(__file__).resolve().parent;S=N.parent.parent;O=N/'coordinator-oct19-recheck'
URLS={'dakota-results':'https://www.dakotanewsnow.com/politics/election-results/','kelo-home':'https://www.keloland.com/','newscenter1-home':'https://www.newscenter1.tv/','nyt-elections':'https://www.nytimes.com/section/politics/elections','sos-media':'https://electionresults.sd.gov/ResultsMedia.aspx','sos-linked-statewide-CSV':'https://electionresults.sd.gov/resultsCSV.aspx?text=All&type=SWR&map=CTY'}
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 O.mkdir(exist_ok=True);original_ledger=(N/'manifest.json').read_bytes();old=json.loads(original_ledger);mf=O/'acquisition.json'
 if mf.exists():rows=json.loads(mf.read_bytes())
 else:
  bodies={r['raw_sha256']:r for r in old if'asset'in r}
  def fetch(item):
   key,url=item;r=dict(id=key,requested_url=url,method='GET',retrieved_at_utc=datetime.now(timezone.utc).isoformat())
   try:
    a=requests.get(url,timeout=35);b=a.content;r.update(status=a.status_code,final_url=a.url,headers=dict(a.headers),redirects=[dict(url=h.url,status=h.status_code,headers=dict(h.headers))for h in a.history],raw_bytes=len(b),raw_sha256=sha(b),body_representation='Complete requests decoded HTTP entity bytes; original wire encoding/length remain in headers');r['_body']=b
   except requests.RequestException as e:r.update(status=0,error=repr(e),final_url=None)
   return r
  rows=list(ThreadPoolExecutor(max_workers=4).map(fetch,URLS.items()))
  for r in rows:
   if'_body'not in r:continue
   b=r.pop('_body')
   if r['raw_sha256']in bodies:
    prior=bodies[r['raw_sha256']];p=N/prior['asset'];z=p.read_bytes();assert gzip.decompress(z)==b and sha(z)==prior['stored_sha256'];r['exact_original_reuse_id']=prior['id']
   else:
    p=O/(r['id']+'.body.gz');assert not p.exists();z=gzip.compress(b,mtime=0);p.write_bytes(z)
   assert len(z)<40_000_000;r.update(asset_path=str(p.relative_to(S)),stored_bytes=len(z),stored_sha256=sha(z))
  mf.write_text(json.dumps(rows,indent=2)+'\n')
 observations=[]
 for r in rows:
  f=dict(id=r['id'],HTTP_status=r['status'],retrieved_at_utc=r['retrieved_at_utc'],current_November_counts_admitted=False)
  if'asset_path'in r:
   z=(S/r['asset_path']).read_bytes();b=gzip.decompress(z);assert sha(z)==r['stored_sha256']and sha(b)==r['raw_sha256']and len(b)==r['raw_bytes'];text=b.decode('utf-8-sig',errors='replace')
   f.update(raw_bytes=len(b),raw_sha256=sha(b))
   if r['id']=='dakota-results':
    decoder=json.JSONDecoder();parsed={}
    for key in ['selectedElection','globalSettings','electionData']:
     items=[]
     for m in re.finditer('"'+key+'"'+r'\s*:\s*',text):
      try:x,end=decoder.raw_decode(text[m.end():]);items.append(x)
      except json.JSONDecodeError:continue
     parsed[key]=items
    p=O/'dakota-complete-embedded-selected-objects.json.gz';raw=(json.dumps(parsed,indent=2)+'\n').encode();z=gzip.compress(raw,mtime=0)
    if p.exists():assert p.read_bytes()==z
    else:p.write_bytes(z)
    f.update(selectedElection_objects=parsed['selectedElection'],displayTestData_literals=sorted(set(re.findall(r'"displayTestData"\s*:\s*(true|false)',text))),complete_parsed_embedded_objects=dict(path=str(p.relative_to(S)),bytes=len(z),sha256=sha(z)))
   if r['id']=='sos-media':f.update(testing_in_progress_present='Testing In Progress'in text,November_date_present='November 3, 2026'in text,publisher_clock_literal_matches=re.findall(r'.{0,45}(?:Last Updated|Updated on|Updated:|updated).{0,100}',text,re.I)[:12])
   if r['id']=='sos-linked-statewide-CSV':
    rawrows=list(csv.reader(io.StringIO(text)));senate=[v for v in rawrows if any('U.S. Senate'in c or 'United States Senator'in c for c in v)];f.update(raw_CSV_rows=len(rawrows),literal_header=rawrows[0]if rawrows else None,complete_Senate_rows=senate,source_generation_clock_is_vote_update=False)
  observations.append(f)
 assert (N/'manifest.json').read_bytes()==original_ledger
 result=dict(status='bounded_current_source_recheck_not_genuine_count_admission',old35_receipts_unchanged=True,old_ledger_bytes=len(original_ledger),old_ledger_sha256=sha(original_ledger),new_observations=len(rows),observations=observations,qualification='Independent six-source October19 GET observations; complete bodies/errors retained separately from the old source ledger. Raw HTTP status, setup/test flags and generated clocks are not vote updates, completed contest identity, legal ballot eligibility or a measured live cadence. Newsroom and official overlapping data are never added.')
 p=O/'review.json';b=(json.dumps(result,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
 print(json.dumps(dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b),statuses={r['id']:r['status']for r in rows})))
if __name__=='__main__':main()
