"""Bounded public GETs of observed links only. Each job names its parent evidence.
Usage: python -B acquire.py source/jobs-NN.json. Existing receipts never replaced.
Network is explicit; offline build/QA does not call this script.
"""
from common import *
import sys,datetime,requests,urllib.parse
def acquire(job):
 ident=job['id'];out=MAPS/'raw'/f'{ident}.receipt.json'
 if out.exists():
  e=json.loads(out.read_bytes());assert e['url']==job['url'],'ID collision; existing original not replaced';return e
 assert job.get('parent_id') and job.get('literal_href'),job
 assert urllib.parse.urlsplit(job['url']).scheme in ['http','https']
 e=dict(job,method='GET',retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_clock=None,source_timezone=None,clock_note='Map/document snapshot; HTTP Date and Last-Modified are not election-effective dates or vote-update clocks.')
 try:
  r=requests.get(job['url'],timeout=(15,60),headers={'User-Agent':'SD-public-map-research/1.0','Accept-Encoding':'gzip, deflate'})
  b=r.content;e.update(status=r.status_code,final_url=r.url,headers=dict(r.headers),redirects=[dict(url=x.url,status=x.status_code,headers=dict(x.headers)) for x in r.history],error=None)
 except requests.RequestException as exc:
  b=str(exc).encode();e.update(status=None,final_url=None,headers={},redirects=[],error=repr(exc))
 e.update(completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),raw_bytes=len(b),raw_sha256=sha(b),body_representation='Complete decoded HTTP response entity; transport errors store complete exception text, not an invented HTTP body.' if e['status'] is None else 'Complete requests-decoded HTTP entity; wire content encoding/length retained in headers.')
 z=gzip.compress(b,mtime=0);parts=[]
 for i in range(0,len(z),32000000):
  p=MAPS/'raw'/f'{ident}.body.gz.part{i//32000000+1:02d}';p.write_bytes(z[i:i+32000000]);parts.append(pin(p))
 e['stored_objects']=parts;dump(f'raw/{ident}.receipt.json',e)
 print(ident,e['status'],len(b),flush=True);return e
if __name__=='__main__':
 jobs=load(sys.argv[1]);assert len(jobs)<=80
 for j in jobs:acquire(j)
