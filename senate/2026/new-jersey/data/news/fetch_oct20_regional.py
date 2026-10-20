"""Bounded literal-source coordinator GETs with complete redirect entities."""
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
import gzip,hashlib,json,sys,urllib.parse
import requests
from bs4 import BeautifulSoup
S=Path(sys.argv[1]);O=S/'data/news/coordinator-oct20-regional';O.mkdir(parents=True,exist_ok=True)
def sha(b):return hashlib.sha256(b).hexdigest()
def one(item):
 key,job=item;out=dict(id=key,**job,method='GET',request_headers={'Accept-Encoding':'identity'},requested_utc=datetime.now(timezone.utc).isoformat(),redirects=[])
 url=job['url'];seen=set()
 try:
  for hop in range(8):
   assert url not in seen;seen.add(url);a=requests.get(url,headers=out['request_headers'],allow_redirects=False,timeout=30);raw=a.content;stored=gzip.compress(raw,mtime=0);assert len(stored)<40000000
   p=O/f'{key}-hop{hop}-{sha(raw)[:12]}.gz';p.write_bytes(stored)
   r=dict(url=url,status=a.status_code,headers=dict(a.headers),retrieved_utc=datetime.now(timezone.utc).isoformat(),raw_bytes=len(raw),raw_sha256=sha(raw),asset_path=str(p.relative_to(S)),stored_bytes=len(stored),stored_sha256=sha(stored),entity_scope='Complete HTTP content-decoded response entity; original wire headers retained; lossless gzip stored')
   if a.status_code in [301,302,303,307,308]and 'Location'in a.headers:
    out['redirects'].append(r);url=urllib.parse.urljoin(url,a.headers['Location']);continue
   out.update(r,final_url=a.url)
   if 'html'in a.headers.get('Content-Type','').lower():
    dom=BeautifulSoup(raw,'html.parser');out['title']=dom.title.get_text(' ',strip=True)if dom.title else None;out['literal_links']=[dict(href=x['href'],text=x.get_text(' ',strip=True),url=urllib.parse.urljoin(a.url,x['href']))for x in dom.find_all('a',href=True)];out['literal_iframes']=[dict(x.attrs)for x in dom.find_all('iframe')]
   out['November_counts_admitted']=False;return out
  raise RuntimeError('bounded redirect limit reached')
 except Exception as e:out.update(error=repr(e),status=0,final_url=url);return out
jobs=json.loads(Path(sys.argv[2]).read_bytes());rows=list(ThreadPoolExecutor(max_workers=4).map(one,jobs.items()));p=O/sys.argv[3];assert not p.exists();p.write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps([dict(id=x['id'],status=x['status'],bytes=x.get('raw_bytes'),title=x.get('title'),links=len(x.get('literal_links',[])),frames=x.get('literal_iframes'))for x in rows],indent=2))
