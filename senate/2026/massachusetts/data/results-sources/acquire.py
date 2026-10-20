"""Bounded public acquisition, explicit observed URLs only. No guessed routes.
Run with a requests/BeautifulSoup environment; complete response entities are
stored once by SHA256. Redirects, including their complete bodies, are retained.
"""
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urljoin,urlsplit
from concurrent.futures import ThreadPoolExecutor
import gzip,hashlib,json,re,requests,sys
from bs4 import BeautifulSoup
O=Path(__file__).resolve().parent
EXISTING={r['requested_url']:r for p in (O/'source/http').glob('*.json') for r in [json.loads(p.read_text())]}
def sha(b):return hashlib.sha256(b).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def safe(u):
 p=urlsplit(u);h=(p.hostname or '').lower()
 social=any(h==x or h.endswith('.'+x)for x in ['facebook.com','twitter.com','instagram.com','x.com'])
 return p.scheme in ('http','https') and not p.username and not p.password and not social and not re.search(r'(?i)(/(?:wp-)?admin(?:/|$)|/login|/signin|/auth(?:/|$)|/account|/password)',p.path)
def body(b):
 h=sha(b);z=gzip.compress(b,mtime=0);p=O/'source'/'byhash'/(h+'.gz')
 if len(z)>=40000000:
  parts=[]
  for i,start in enumerate(range(0,len(b),30000000),1):
   raw=b[start:start+30000000];stored=gzip.compress(raw,mtime=0);q=O/'source/byhash'/f'{h}.part{i:04d}.gz';assert len(stored)<40000000
   if not q.exists():q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(stored)
   parts.append(dict(path=str(q.relative_to(O)),raw_bytes=len(raw),raw_sha256=sha(raw),stored_bytes=len(stored),stored_sha256=sha(stored),byte_start=start,byte_end_exclusive=start+len(raw)))
  return dict(parts=parts,raw_bytes=len(b),raw_sha256=h,encoding='ordered exact raw-byte splits, each lossless gzip; concatenate decompressed parts')
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z)
 return dict(path=str(p.relative_to(O)),raw_bytes=len(b),raw_sha256=h,stored_bytes=len(z),stored_sha256=sha(z),encoding='gzip of requests transport-decoded complete entity')
def fetch(id,url,parent=None,literal_href=None,reason=None,retry_failed_body=False):
 p=O/'source'/'http'/(id+'.json')
 if p.exists():return json.loads(p.read_text())
 if url in EXISTING and not (retry_failed_body and 'oversize response' in str(EXISTING[url].get('error'))):return EXISTING[url]
 rec=dict(id=id,requested_url=url,method='GET',query=urlsplit(url).query,request_body=None,parent=parent,literal_href=literal_href,reason=reason,started_utc=now(),redirects=[],status=None,error=None,final_url=None)
 if not safe(url):
  rec.update(error='excluded nonpublic/auth/social URL; no request issued',policy_excluded=True,finished_utc=now());dump(p,rec);return rec
 current=url;session=requests.Session()
 try:
  for i in range(9):
   r=session.get(current,timeout=(12,35),allow_redirects=False)
   hop=dict(requested_url=current,final_url=r.url,utc=now(),status=r.status_code,request_headers=dict(r.request.headers),response_headers=dict(r.headers),body=body(r.content))
   rec['redirects'].append(hop)
   if r.status_code not in (301,302,303,307,308) or not r.headers.get('Location'):break
   current=urljoin(r.url,r.headers['Location'])
   if not safe(current):raise ValueError('redirect to excluded path')
  else:raise ValueError('redirect bound exhausted')
  rec.update(status=r.status_code,final_url=r.url,body=hop['body'],headers=dict(r.headers))
 except Exception as e:rec['error']=str(e)
 rec['finished_utc']=now();rec.update(publisher_update_clock=None,publisher_timezone=None,measured_cadence=None,eligible_remaining_pool=None);dump(p,rec);return rec
def content(r):
 if 'body' not in r:return b''
 b=r['body'];return b''.join(gzip.decompress((O/p['path']).read_bytes())for p in b.get('parts',[b]))
def inspect(r):
 b=content(r);s=BeautifulSoup(b,'html.parser');links=[]
 for i,a in enumerate(s.find_all(['a','iframe','script','link','form']),1):
  attr='action' if a.name=='form' else 'href' if a.has_attr('href') else 'src'
  if a.get(attr) is None:continue
  raw=a.get(attr);u=urljoin(r.get('final_url',r['requested_url']),raw)
  links.append(dict(ordinal=i,tag=a.name,literal_href=raw,url=u,text=a.get_text(' ',strip=True),attributes=dict(a.attrs),public_fetch_allowed=safe(u)))
 result=dict(source_id=r['id'],status=r['status'],final_url=r.get('final_url'),title=s.title.get_text(' ',strip=True) if s.title else None,text=s.get_text('\n',strip=True),links=links,forms=[str(x) for x in s.find_all('form')],inline_scripts=[x.get_text() for x in s.find_all('script') if not x.get('src')],embedded_json=[x.get_text() for x in s.select('script[type="application/json"],script[type="application/ld+json"]')],original_body=r.get('body'),scope='complete HTML structural/text extract; original entity retained; not browser rendering')
 dump(O/'source'/'inspect'/(r['id']+'.json'),result);return result
def main():
 submitted_jobs=json.loads(Path(sys.argv[1]).read_text());jobs=list({j['url']:j for j in reversed(submitted_jobs)}.values())
 def one(j):
  r=fetch(**j)
  if 'body' in r and ('html'in r.get('headers',{}).get('Content-Type','').lower() or content(r).lstrip().startswith((b'<',b'<!'))):inspect(r)
  return dict(id=r['id'],status=r['status'],error=r['error'],bytes=r.get('body',{}).get('raw_bytes'))
 with ThreadPoolExecutor(max_workers=6) as pool:
  for r in pool.map(one,jobs):print(json.dumps(r),flush=True)
if __name__=='__main__':main()
