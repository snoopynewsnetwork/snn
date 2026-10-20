"""Bounded explicit public research requests; no polling, IDs, or URL constructors guessed."""
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urljoin,urldefrag
from concurrent.futures import ThreadPoolExecutor
import requests,json,gzip,hashlib,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def store(b):
 z=gzip.compress(b,mtime=0);h=sha(b);p=HERE/'bodies'/f'{h}.gz';p.parent.mkdir(exist_ok=True)
 if len(z)>=40000000:
  parts=[]
  for i in range(0,len(b),20000000):parts.append(store(b[i:i+20000000]))
  return {'raw_bytes':len(b),'raw_sha256':h,'ordered_exact_entity_parts':parts}
 if not p.exists():p.write_bytes(z)
 return {'raw_bytes':len(b),'raw_sha256':h,'stored_bytes':len(z),'stored_sha256':sha(z),'asset':str(p.relative_to(HERE))}
def fetch(job):
 rid=job['id'];out=HERE/'requests'/f'{rid}.json';out.parent.mkdir(exist_ok=True)
 if out.exists():return json.loads(out.read_bytes())
 result={'id':rid,'purpose':job.get('purpose'),'parent':job.get('parent'),'literal_href':job.get('literal_href',job['url']),'requested_url':job['url'],'query':job.get('query'),'request_body':None,'started_utc':now(),'hops':[],'admission':'research_only_not_admitted_November_counts'}
 url=job['url'];session=requests.Session()
 try:
  for i in range(8):
   started=now();r=session.get(url,params=job.get('query') if i==0 else None,allow_redirects=False,timeout=(12,35),headers={'User-Agent':'NJOfficialResultsResearch/1.0 (bounded public-source inspection)'})
   hop={'started_utc':started,'finished_utc':now(),'method':r.request.method,'actual_requested_url':r.request.url,'request_headers':dict(r.request.headers),'request_body':r.request.body,'response_url':r.url,'status':r.status_code,'reason':r.reason,'headers':dict(r.headers),'header_fields':[(k,r.raw.headers.getlist(k)) for k in r.raw.headers],**store(r.content)};result['hops'].append(hop)
   if r.is_redirect:
    url=urljoin(r.url,r.headers['Location']);continue
   break
  else:result['error']='bounded eight-hop redirect limit'
  result.update(final_url=r.url,status=r.status_code)
 except Exception as e:result['error']=repr(e)
 result['finished_utc']=now();out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');return result
def main():
 jobs=json.loads(Path(sys.argv[1]).read_bytes())
 with ThreadPoolExecutor(max_workers=4) as pool:
  for r in pool.map(fetch,jobs):print(r['id'],r.get('status'),r.get('error'),r.get('final_url'),flush=True)
if __name__=='__main__':main()
