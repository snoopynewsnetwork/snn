#!/usr/bin/env python3
"""Bounded read-only evidence acquisition; explicit observed URLs, no crawler/collector.
Run: python3 acquire.py jobs.json. Existing receipts are immutable. Complete
response entity bytes (HTTP content decoding applied by requests) are losslessly
gzipped/split, with full headers and redirects. Does not interpret HTTP200 as data.
"""
import sys,json,gzip,hashlib,datetime,pathlib,requests,concurrent.futures
ROOT=pathlib.Path(__file__).resolve().parent
LIMIT=32_000_000
def sha(b):return hashlib.sha256(b).hexdigest()
def fetch(j):
 id=j['id']; dest=ROOT/'raw'/f'{id}.receipt.json'
 if dest.exists():return json.loads(dest.read_text())
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();body=b'';r=None;err=None
 try:
  r=requests.request(j.get('method','GET'),j['url'],data=j.get('form'),timeout=(15,75),headers={'User-Agent':'Public election research (bounded read-only)','Accept-Encoding':'gzip, deflate'},allow_redirects=True);body=r.content
 except Exception as e:err=repr(e);body=(err+'\n').encode()
 z=gzip.compress(body,mtime=0);parts=[]
 for i in range(0,len(z),LIMIT):
  p=ROOT/'raw'/f'{id}.body.gz.part{i//LIMIT+1:02d}';b=z[i:i+LIMIT];p.write_bytes(b);parts.append({'path':str(p.relative_to(ROOT)), 'bytes':len(b),'sha256':sha(b)})
 o={**j,'method':j.get('method','GET'),'retrieved_utc':start,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':r.status_code if r is not None else None,'final_url':r.url if r is not None else None,'headers':dict(r.headers) if r is not None else {},'redirects':[{'url':h.url,'status':h.status_code,'headers':dict(h.headers)} for h in r.history] if r is not None else [],'error':err,'body_kind':'complete_response_entity' if r is not None else 'complete_local_exception','raw_bytes':len(body),'raw_sha256':sha(body),'compression':'gzip ordered parts','stored_parts':parts,'source_clock':None,'source_timezone':None,'clock_note':'Unparsed at acquisition; see schema-inspection.json. HTTP Date is not vote-update time.'}
 dest.write_text(json.dumps(o,indent=2)+'\n');print(id,o['status'],len(body),flush=True);return o
if __name__=='__main__':
 jobs=json.load(open(sys.argv[1]));assert len(jobs)<=100
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:list(ex.map(fetch,jobs))
