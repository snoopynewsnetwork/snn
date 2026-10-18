#!/usr/bin/env python3
"""Explicit URL acquisition. Entity bytes are gzip lossless; split BEFORE storage at 30 MB.
HTTP library removes content-transfer encoding; full entity and stored hashes are recorded.
Every response including errors retained. No HTML accepted as GIS/PDF by this routine.
"""
import sys,json,gzip,hashlib,datetime,requests
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(b): return hashlib.sha256(b).hexdigest()
def fetch(key,url,params=None):
 meta_path=ROOT/'evidence'/f'{key}.request.json'
 if meta_path.exists():
  m=json.loads(meta_path.read_text()); return read(m),m
 start=datetime.datetime.now(datetime.timezone.utc).isoformat()
 try:
  r=requests.get(url,params=params,timeout=(20,180),headers={'User-Agent':'Minnesota election research; public source archival audit'})
  b=r.content
  m={'key':key,'requested_url':url,'params':params,'prepared_url':r.request.url,'final_url':r.url,'retrieved_utc':start,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':r.status_code,'headers':dict(r.headers),'redirects':[{'url':x.url,'status':x.status_code,'headers':dict(x.headers)} for x in r.history],'original_entity_bytes':len(b),'original_entity_sha256':sha(b),'magic_hex':b[:20].hex(),'entity_note':'requests response entity after HTTP content-encoding decoding; no textual recoding'}
 except Exception as e:
  b=b''; m={'key':key,'requested_url':url,'params':params,'retrieved_utc':start,'status':None,'error':str(e),'original_entity_bytes':0,'original_entity_sha256':sha(b)}
 reuse=None
 for oldp in sorted((ROOT/'evidence').glob('*.request.json')):
  old=json.loads(oldp.read_text())
  if old['original_entity_sha256']==m['original_entity_sha256']:
   assert read(old)==b;reuse=old;break
 if reuse is not None:
  m['ordered_parts']=reuse['ordered_parts'];m['identical_entity_reused_from']={'key':reuse['key'],'sha256':m['original_entity_sha256'],'scope':'Identical entity only; independent request observation.'};meta_path.write_text(json.dumps(m,indent=2)+'\n');return b,m
 parts=[]
 for i,offset in enumerate(range(0,max(len(b),1),30000000)):
  stored=gzip.compress(b[offset:offset+30000000],mtime=0)
  p=ROOT/'originals'/f'{key}.part{i:03d}.gz';p.write_bytes(stored)
  parts.append({'path':str(p.relative_to(ROOT)),'offset':offset,'entity_bytes':len(b[offset:offset+30000000]),'stored_bytes':len(stored),'stored_sha256':sha(stored)})
 m['ordered_parts']=parts;meta_path.write_text(json.dumps(m,indent=2)+'\n')
 print(key,m['status'],len(b),flush=True)
 return b,m
def read(m): return b''.join(gzip.decompress((ROOT/p['path']).read_bytes()) for p in m['ordered_parts'])
if __name__=='__main__': fetch(sys.argv[1],sys.argv[2],json.loads(sys.argv[3]) if len(sys.argv)>3 else None)
