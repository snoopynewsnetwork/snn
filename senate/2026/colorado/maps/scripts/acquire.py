"""Bounded one-shot public acquisition; every response retained, including failures."""
import concurrent.futures,datetime,gzip,hashlib,json,pathlib,re,sys,urllib.parse
import requests
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def fetch(job):
 key,url,purpose,parent=job
 assert re.fullmatch(r'[a-z0-9-]+',key),key
 assert not (ROOT/'raw'/f'{key}.receipt.json').exists(),('immutable acquisition ID already exists',key)
 start=datetime.datetime.now(datetime.timezone.utc).isoformat()
 rec=dict(id=key,url=url,purpose=purpose,parent=parent,method='GET',retrieved_utc=start,source_clock=None,source_status='as published; geometry vintage requires separate evidence')
 try:
  r=requests.get(url,timeout=(15,55),headers={'User-Agent':'Colorado precinct map research/1.0','Accept-Encoding':'identity'})
  b=r.content;rec.update(status=r.status_code,final_url=r.url,headers=dict(r.headers),redirects=[dict(url=h.url,status=h.status_code,headers=dict(h.headers)) for h in r.history])
 except Exception as e:
  b=str(e).encode();rec.update(status=None,error=repr(e),headers={},redirects=[])
 packed=gzip.compress(b,mtime=0);parts=[]
 for i in range(0,len(packed),39000000):
  p=ROOT/'raw'/f'{key}.{i//39000000:03d}.gzpart';p.write_bytes(packed[i:i+39000000]);parts.append(dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=sha(p.read_bytes())))
 rec.update(raw_bytes=len(b),raw_sha256=sha(b),storage='concatenate ordered gzip parts then decompress; original response entity bytes',parts=parts)
 (ROOT/'raw'/f'{key}.receipt.json').write_text(json.dumps(rec,indent=2)+'\n')
 return rec
def body(key):
 r=json.loads((ROOT/'raw'/f'{key}.receipt.json').read_text());return gzip.decompress(b''.join((ROOT/x['path']).read_bytes() for x in r['parts']))
if __name__=='__main__':
 jobs=json.loads(pathlib.Path(sys.argv[1]).read_text())
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
  for r in pool.map(fetch,jobs):print(r['id'],r['status'],r['raw_bytes'],r.get('error',''))
