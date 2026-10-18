#!/usr/bin/env python3
"""Retain public GET responses, errors, redirects, original hashes and lossless bytes.
No credentials. Idempotent by evidence name; refreshing requires a new name.
"""
import sys
sys.dont_write_bytecode=True
import pathlib,json,gzip,hashlib,datetime,requests
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def fetch(name,url,params=None,parent=None,suffix=None):
 meta=ROOT/'raw'/f'{name}.request.json'
 if meta.exists():return json.loads(meta.read_text())
 req=requests.Request('GET',url,params=params).prepare(); now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 try:
  r=requests.Session().send(req,timeout=(20,120));b=r.content
  record={'id':name,'method':'GET','requested_url':req.url,'final_url':r.url,'retrieved_at_utc':now,'status':r.status_code,'headers':dict(r.headers),'redirects':[{'url':x.url,'status':x.status_code,'headers':dict(x.headers)} for x in r.history],'parent':parent,'original_bytes':len(b),'original_sha256':sha(b),'entity_note':'requests-decoded HTTP entity; Content-Encoding transport may differ; exact entity bytes preserved'}
 except Exception as e:
  b=b'';record={'id':name,'requested_url':req.url,'retrieved_at_utc':now,'error':str(e),'status':None,'parent':parent,'original_bytes':0,'original_sha256':sha(b)}
 if suffix is None:suffix='.pdf' if b.startswith(b'%PDF') else '.zip' if b.startswith(b'PK\x03\x04') else '.body.gz'
 stored=gzip.compress(b,mtime=0) if suffix.endswith('.gz') else b
 if len(stored)>=40000000:
  parts=[]
  for i in range(0,len(b),30000000):
   q=ROOT/'raw'/f'{name}.part{i//30000000:03d}.gz';z=gzip.compress(b[i:i+30000000],mtime=0);assert len(z)<40000000;q.write_bytes(z);parts.append({'path':str(q.relative_to(ROOT)),'stored_bytes':len(z),'stored_sha256':sha(z),'offset':i,'original_bytes':len(b[i:i+30000000])})
  record['ordered_parts']=parts;record['reconstruction']='concatenate gzip-decompressed parts in array order'
 else:
  q=ROOT/'raw'/f'{name}{suffix}';q.write_bytes(stored);record.update(path=str(q.relative_to(ROOT)),stored_bytes=len(stored),stored_sha256=sha(stored),compression='gzip' if suffix.endswith('.gz') else 'none')
 meta.write_text(json.dumps(record,indent=2)+'\n');return record
def body(name):
 d=json.loads((ROOT/'raw'/f'{name}.request.json').read_text())
 if 'ordered_parts' in d:return b''.join(gzip.decompress((ROOT/x['path']).read_bytes()) for x in d['ordered_parts'])
 b=(ROOT/d['path']).read_bytes();return gzip.decompress(b) if d['compression']=='gzip' else b
def js(name):return json.loads(body(name))
if __name__=='__main__':
 d=fetch(sys.argv[1],sys.argv[2]);print(json.dumps(d,indent=2))
