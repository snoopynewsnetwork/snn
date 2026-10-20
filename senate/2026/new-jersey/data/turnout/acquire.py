#!/usr/bin/env python3
"""Fetch exact published links; immutable per-request original receipts. No shared writes."""
from pathlib import Path
import requests,gzip,json,hashlib,datetime,re,concurrent.futures,sys,os
from urllib.parse import urljoin
D=Path(__file__).resolve().parent; S=D/'source'; N=D.parent/'news'
def sha(b):return hashlib.sha256(b).hexdigest()
def fetch(item):
 sid,url,parent=item; receipt=S/(sid+'.receipt.json')
 if receipt.exists():
  old=json.loads(receipt.read_text())
  if not (old.get('error') and os.environ.get('NJ_RETRY')):return old
  receipt.rename(S/(sid+'.network-restricted.receipt.json'))
 now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 try:
  r=requests.get(url,timeout=90); b=r.content
  z=gzip.compress(b,mtime=0);assert len(z)<40000000
  (S/(sid+'.body.gz')).write_bytes(z)
  a={'id':sid,'requested_url':url,'final_url':r.url,'retrieved_at_utc':now,'status':r.status_code,'headers':dict(r.headers),'redirects':[{'url':h.url,'status':h.status_code,'headers':dict(h.headers)} for h in r.history],'parent':parent,'raw_sha256':sha(b),'raw_bytes':len(b),'stored_sha256':sha(z),'stored_bytes':len(z),'asset':sid+'.body.gz'}
 except Exception as e:a={'id':sid,'requested_url':url,'retrieved_at_utc':now,'parent':parent,'error':repr(e)}
 receipt.write_text(json.dumps(a,indent=2)+'\n');return a

def pin_shared():
 mf=json.loads((N/'manifest.json').read_text());out=[]
 for a in mf:
  if a['id'].startswith('sos-') or a['id'] in ['nj-election-night','nj-election-info','news12-senate-general-data']:
   z=(N/a['asset']).read_bytes();b=gzip.decompress(z)
   assert sha(z)==a['stored_sha256'] and sha(b)==a['raw_sha256']
   p={**a,'reference_path':'../../news/'+a['asset'],'stored_bytes':len(z),'raw_bytes':len(b),'reference_type':'immutable_hash_pinned_read_only_original'}
   target=S/('shared-'+a['id']+'.receipt.json');serialized=json.dumps(p,indent=2)+'\n'
   if target.exists():assert target.read_text()==serialized,'Shared pin changed; retain a new explicitly versioned receipt instead.'
   else:target.write_text(serialized)
   out.append(p)
 return out
if __name__=='__main__':
 pin_shared(); jobs=[]
 if len(sys.argv)>2 and sys.argv[1]=='--jobs':
  jobs=json.loads(Path(sys.argv[2]).read_text())
 elif len(sys.argv)>2:
  jobs=[(sys.argv[1],sys.argv[2],sys.argv[3] if len(sys.argv)>3 else 'manual-discovery')]
 else:
  for yr in [2024,2020,2022,2018]:
   sid=f'sos-{yr}-index';html=gzip.decompress((N/(sid+'.html.gz')).read_bytes()).decode()
   for href,label in re.findall(r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',html,re.S):
    if (yr==2024 and any(x in href for x in ['general-results-us-senate-','general-results-president-','general-result-ballotscast-','official-general-candidates-us-senate.pdf'])) or (yr==2020 and any(x in href for x in ['general-results-us-senate-','general-result-ballotscast-','general-voter-turnout'])) or (yr==2022 and 'general-result-ballotscast-' in href) or (yr==2018 and ('turnout' in href or 'general-election-results-us-senate-' in href)):
     jobs.append((href.rsplit('/',1)[-1].removesuffix('.pdf'),urljoin('https://nj.gov/state/elections/',href),sid))
  jobs += [('current-results','https://nj.gov/state/elections/election-results.shtml',None),('current-2024-index','https://nj.gov/state/elections/election-information-2024.shtml',None),('county-officials','https://nj.gov/state/elections/vote-county-election-officials.shtml','current-results')]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for a in pool.map(fetch,jobs):print(a['id'],a.get('status',a.get('error')),a.get('raw_bytes'))
