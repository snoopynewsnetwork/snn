"""Bounded public GET acquisition. Every hop entity, error and header is retained."""
from pathlib import Path
from datetime import datetime,timezone
import requests,json,gzip,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def store(b):
 z=gzip.compress(b,mtime=0);parts=[]
 for i in range(0,len(z),30000000):
  q=z[i:i+30000000];p=ROOT/'source'/(sha(q)+'.gzpart');p.parent.mkdir(parents=True,exist_ok=True)
  if not p.exists():p.write_bytes(q)
  else:assert p.read_bytes()==q
  parts.append({'path':str(p.relative_to(ROOT)),'bytes':len(q),'sha256':sha(q)})
 return {'bytes':len(b),'sha256':sha(b),'compression':'one gzip stream, concatenate ordered parts before decompressing','parts':parts}
def fetch(url,parent=None,method='GET',fields=None):
 assert method in ['GET','POST'] and url.startswith(('https://','http://'))
 rec={'requested_url':url,'method':method,'fields':fields,'request_body':None if fields is None else requests.models.RequestEncodingMixin._encode_params(fields),'parent':parent,'utc_start':now(),'hops':[],'configured_headers':{'User-Agent':'Alabama-boundary-research/1.0 (public read-only archive)','Accept':'*/*','Accept-Encoding':'identity'},'qualification':'HTTP/cache/source clocks are not boundary adoption or election-update clocks.'}
 session=requests.Session();session.headers.clear();session.headers.update(rec['configured_headers']);current=url;verb=method
 try:
  for i in range(8):
   start=now();r=session.request(verb,current,data=fields if verb=='POST' else None,timeout=(20,90),allow_redirects=False)
   body=r.content;end=now();h={'url':r.url,'method':verb,'utc_start':start,'utc_end':end,'status':r.status_code,'reason':r.reason,'headers':[[k,v] for k in r.raw.headers for v in r.raw.headers.getlist(k)],'sent_headers':list(r.request.headers.items()),'sent_body':r.request.body,'entity':store(body)};rec['hops'].append(h)
   if r.status_code in [301,302,303,307,308] and 'Location' in r.headers:
    from urllib.parse import urljoin
    current=urljoin(r.url,r.headers['Location'])
    if r.status_code==303 or (r.status_code in [301,302] and verb=='POST'):verb='GET'
    continue
   rec.update({'final_url':r.url,'status':r.status_code,'entity':h['entity']});break
  else:raise ValueError('bounded redirect limit')
 except Exception as e:rec.update({'error':repr(e),'status':None,'final_url':None,'entity':None,'unavailable_metadata':'No response entity/status/headers for failed request; actual start/end only.'})
 rec['utc_end']=now();name=rec['utc_start'].replace(':','').replace('.','')+'-'+sha(url.encode())[:12]+'.receipt.json';p=ROOT/'source'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(rec,indent=2)+'\n')
 return str(p.relative_to(ROOT)),rec
if __name__=='__main__':
 p,r=fetch(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else None);print(json.dumps({'receipt':p,'url':r['requested_url'],'status':r['status'],'error':r.get('error'),'entity':r['entity']}))
