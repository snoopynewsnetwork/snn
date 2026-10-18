#!/usr/bin/env python3
"""One-shot immutable HTTP entity capture. No periodic collection; no route guessing."""
import argparse,datetime,gzip,hashlib,json,pathlib,re,requests,sys,urllib.parse
ROOT=pathlib.Path(__file__).resolve().parent

def sha(b):return hashlib.sha256(b).hexdigest()
def fetch(key,url,parent=None,purpose=None):
 assert re.fullmatch('[a-zA-Z0-9_.-]+',key)
 receipt=ROOT/'raw'/f'{key}.receipt.json'
 if receipt.exists():
  r=json.loads(receipt.read_text());assert r['request_url']==url,(key,url,r['request_url']);return r
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();data=b''
 r={'source_id':key,'request_url':url,'parent_source_id':parent,'purpose':purpose,'retrieval_started_utc':start,'source_clock':None,'source_clock_zone':None,'request_headers':{'User-Agent':'Florida-precinct-map-research/1.0 (public primary-source archival research)','Accept-Encoding':'identity'},'entity_encoding_note':'Requests-decoded HTTP entity bytes; Accept-Encoding identity requested. HTTP Content-Encoding retained; not TLS/wire bytes.'}
 try:
  q=requests.get(url,headers=r['request_headers'],timeout=(20,120));data=q.content
  r.update(status=q.status_code,final_url=q.url,response_headers=dict(q.headers),redirects=[{'url':x.url,'status':x.status_code,'headers':dict(x.headers)} for x in q.history],encoding=q.encoding,error=None)
 except Exception as e:r.update(status=None,final_url=None,response_headers={},redirects=[],encoding=None,error=repr(e))
 r['retrieved_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();r['original_bytes']=len(data);r['original_sha256']=sha(data)
 # A content-addressed reference avoids duplicate original entities within ownership.
 same=None
 for p in (ROOT/'raw').glob('*.receipt.json'):
  z=json.loads(p.read_text())
  if z.get('original_sha256')==r['original_sha256'] and z.get('original_bytes')==len(data):same=z;break
 if same:r['stored_path']=same['stored_path'];r['deduplicated_to_source_id']=same['source_id']
 else:
  stored=gzip.compress(data,mtime=0);path=ROOT/'raw'/f'{key}.body.gz'
  if len(stored)<40000000:path.write_bytes(stored);r['stored_path']=str(path.relative_to(ROOT))
  else:
   parts=[]
   for i in range(0,len(data),30000000):
    b=data[i:i+30000000];p=ROOT/'raw'/f'{key}.part-{i//30000000:04d}';p.write_bytes(b);parts.append({'path':str(p.relative_to(ROOT)),'bytes':len(b),'sha256':sha(b)})
   r['ordered_byteparts']=parts;r['stored_path']=None;r['reconstruction']='Concatenate ordered byteparts as listed; original_bytes and original_sha256 verify result.'
 if r.get('stored_path'):
  b=(ROOT/r['stored_path']).read_bytes();r.update(stored_bytes=len(b),stored_sha256=sha(b),compression='gzip')
 tmp=receipt.with_suffix('.tmp');tmp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');tmp.replace(receipt);return r

def body(key):
 r=json.loads((ROOT/'raw'/f'{key}.receipt.json').read_text())
 if not r.get('stored_path'):return b''.join((ROOT/p['path']).read_bytes() for p in r['ordered_byteparts'])
 b=(ROOT/r['stored_path']).read_bytes();return gzip.decompress(b) if r.get('compression')=='gzip' else b
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('key');p.add_argument('url');p.add_argument('--parent');p.add_argument('--purpose');a=p.parse_args();r=fetch(a.key,a.url,a.parent,a.purpose);print(json.dumps({k:r.get(k) for k in ['source_id','status','original_bytes','original_sha256','error']}))
