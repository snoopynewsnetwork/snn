"""Bounded public GET acquisition; complete entities and every redirect, no auth."""
import requests,json,gzip,hashlib,datetime,sys,re
from pathlib import Path
from urllib.parse import urljoin,urlsplit
R=Path(__file__).resolve().parents[1];S=R.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def put(b):
 z=gzip.compress(b,mtime=0);h=sha(z);parts=[]
 for i in range(0,len(z),32000000):
  part=z[i:i+32000000];p=R/'bodies'/(h+('.gz' if len(z)<32000000 else '.gz.part%03d'%(i//32000000)));p.parent.mkdir(parents=True,exist_ok=True)
  if not p.exists():p.write_bytes(part)
  parts.append({'path':str(p.relative_to(S)),'bytes':len(part),'sha256':sha(part)})
 return {'raw_bytes':len(b),'raw_sha256':sha(b),'stored_bytes':len(z),'stored_sha256':h,'encoding':'gzip_ordered_parts','parts':parts}
def fetch(key,url,parent=None):
 assert re.fullmatch('[a-z0-9-]+',key)
 p=R/'requests'/(key+'.json');p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():return json.loads(p.read_bytes())
 rec={'key':key,'method':'GET','requested_url':url,'parent':parent,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'entities':[],'error':None,'decoded_content_encoding':True}
 session=requests.Session();session.headers.update({'User-Agent':'PublicElectionResearch/1.0 (bounded official-source inspection)'})
 try:
  for hop in range(9):
   response=session.get(url,timeout=(12,40),allow_redirects=False)
   b=response.content
   ent={'url':url,'status':response.status_code,'headers':dict(response.headers),'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'body':put(b)};rec['entities'].append(ent)
   if response.is_redirect:
    url=urljoin(url,response.headers['Location'])
    if re.search(r'(login|signin|oauth|facebook|twitter|instagram|linkedin|/admin)',url,re.I):rec['error']='navigation stopped at excluded authentication/social/admin redirect';break
   else:break
  else:rec['error']='bounded redirect limit'
 except Exception as e:rec['error']=type(e).__name__+': '+str(e)
 rec['final_url']=url;rec['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();p.write_text(json.dumps(rec,indent=2,ensure_ascii=False)+'\n');return rec
def body(rec):
 if not rec['entities']:return b''
 b=rec['entities'][-1]['body'];z=b''.join((S/p['path']).read_bytes() for p in b['parts']);assert sha(z)==b['stored_sha256'];v=gzip.decompress(z);assert sha(v)==b['raw_sha256'];return v
if __name__=='__main__':
 r=fetch(*sys.argv[1:]);print(json.dumps({k:r[k] for k in ['key','requested_url','final_url','error']}));print([(x['status'],x['body']['raw_bytes']) for x in r['entities']])
