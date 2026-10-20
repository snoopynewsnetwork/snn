"""Bounded public GET acquisition. Never overwrite retained evidence."""
from pathlib import Path
import datetime,gzip,hashlib,json,subprocess,tempfile,urllib.parse
ROOT=Path(__file__).resolve().parents[1]
def sha(b): return hashlib.sha256(b).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def fetch(label,url,parent=None,method='GET',fields=None):
 d=ROOT/'originals'/label
 if d.exists():raise RuntimeError('retained evidence exists: '+label)
 d.mkdir(parents=True)
 headers={'User-Agent':'Arkansas-map-research/1.0 public-source archival','Accept':'*/*'}
 start=now()
 with tempfile.TemporaryDirectory() as t:
  p=Path(t);cmd=['curl','--silent','--show-error','--location','--max-redirs','8','--max-time','90','--request',method,'--dump-header',str(p/'headers'),'--output',str(p/'body'),'--write-out','%{json}']
  for k,v in headers.items():cmd+=['--header',k+': '+v]
  if fields is not None:cmd+=['--data',urllib.parse.urlencode(fields)]
  cmd+=[url];r=subprocess.run(cmd,capture_output=True);end=now()
  h=(p/'headers').read_bytes() if (p/'headers').exists() else None
  body=(p/'body').read_bytes() if (p/'body').exists() else None
  metrics=None
  try:metrics=json.loads(r.stdout)
  except Exception:pass
  rec={'label':label,'request':{'url':url,'method':method,'fields':fields,'body':urllib.parse.urlencode(fields) if fields is not None else None,'configured_headers':headers,'parent':parent},'utc_start':start,'utc_end':end,'curl_exit':r.returncode,'curl_stdout':r.stdout.decode(errors='replace'),'curl_stderr':r.stderr.decode(errors='replace'),'metrics':metrics,'response_body_available':body is not None,'response_headers_available':h is not None,'hops':'raw ordered HTTP blocks in headers.bin.gz; curl metrics effective URL and redirects; errors retained'}
  for name,b in [('body',body),('headers',h)]:
   if b is None:rec[name]=None;continue
   packed=gzip.compress(b,mtime=0)
   # Ordered lossless chunks preserve the entire gzip stream, including for large originals.
   paths=[]
   for i in range(0,len(packed),39000000):
    f=d/(name+('.bin.gz' if len(packed)<40000000 else '.bin.gz.part%04d'%(i//39000000)))
    f.write_bytes(packed[i:i+39000000]);paths.append({'path':str(f.relative_to(ROOT)),'bytes':f.stat().st_size,'sha256':sha(f.read_bytes())})
   rec[name]={'bytes':len(b),'sha256':sha(b),'storage':'concatenate ordered stored parts then gzip decompress exactly once','parts':paths}
  (d/'receipt.json').write_text(json.dumps(rec,indent=2,ensure_ascii=False)+'\n')
  print(label,r.returncode,metrics.get('http_code') if metrics else None,len(body) if body is not None else 'unavailable',flush=True)
  return body,rec
if __name__=='__main__':
 import sys
 fetch(sys.argv[1],sys.argv[2],sys.argv[3] if len(sys.argv)>3 else None)
