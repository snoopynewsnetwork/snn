"""Bounded Colorado October19 coordinator news recheck; old news ledger unchanged.

CLI takes a JSON mapping id -> {url,parent_id,literal_href}. No URL fabrication,
native geometry joining or repair. All question workers remain independent.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import gzip,hashlib,json,sys,urllib.parse
import requests
from bs4 import BeautifulSoup
N=Path(__file__).resolve().parent;D=N.parent;S=D.parent;O=N/'coordinator-oct19-recheck';O.mkdir(exist_ok=True)
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 jobs=json.loads(Path(sys.argv[1]).read_bytes());mf=O/'acquisition.json';old=json.loads(mf.read_bytes())if mf.exists()else[];ids={r['id']for r in old};todo=[(k,v)for k,v in jobs.items()if k not in ids]
 previous=json.loads((D/'news/manifest.json').read_bytes());bodies={r['raw_sha256']:dict(path='data/news/'+r['asset'],stored_sha256=r['stored_sha256'],id=r['id'])for r in previous if 'asset'in r}
 for r in old:
  if 'asset_path'in r:bodies[r['raw_sha256']]=dict(path=r['asset_path'],stored_sha256=r['stored_sha256'],id=r['id'])
 def fetch(item):
  key,v=item
  if isinstance(v,str):v=dict(url=v,parent_id=None,literal_href=None)
  r=dict(id=key,**v,method='GET',retrieved_at_utc=datetime.now(timezone.utc).isoformat())
  try:
   a=requests.get(v['url'],timeout=35);raw=a.content;z=gzip.compress(raw,mtime=0);assert len(z)<40_000_000
   r.update(status=a.status_code,final_url=a.url,headers=dict(a.headers),redirects=[dict(url=h.url,status=h.status_code,headers=dict(h.headers))for h in a.history],raw_bytes=len(raw),raw_sha256=sha(raw),body_representation='Complete requests decoded HTTP entity; lossless gzip storage, wire Content-Encoding/Content-Length retained in headers')
   r['_raw']=raw;r['_stored']=z
  except requests.RequestException as e:r.update(status=0,error=repr(e),final_url=None)
  return r
 new=list(ThreadPoolExecutor(max_workers=4).map(fetch,todo))
 for r in new:
  if '_raw'not in r:continue
  raw=r.pop('_raw');z=r.pop('_stored');key=r['raw_sha256']
  if key in bodies:
   ref=bodies[key];existing=(S/ref['path']).read_bytes();assert gzip.decompress(existing)==raw and sha(existing)==ref['stored_sha256'];r.update(asset_path=ref['path'],stored_bytes=len(existing),stored_sha256=sha(existing),exact_original_reuse_id=ref['id'])
  else:
   p=O/(r['id']+'-'+key[:12]+'.gz');assert not p.exists();p.write_bytes(z);r.update(asset_path=str(p.relative_to(S)),stored_bytes=len(z),stored_sha256=sha(z));bodies[key]=dict(path=r['asset_path'],stored_sha256=sha(z),id=r['id'])
  if 'html'in r['headers'].get('Content-Type','').lower():
   dom=BeautifulSoup(raw,'html.parser');r['literal_links']=[dict(href=a.get('href'),text=a.get_text(' ',strip=True),url=urllib.parse.urljoin(r['final_url'],a.get('href','')))for a in dom.find_all('a',href=True)]
   r['literal_iframes']=[dict(x.attrs)for x in dom.find_all('iframe')]
 assert len({r['id']for r in old+new})==len(old)+len(new)
 mf.write_text(json.dumps(old+new,indent=2)+'\n')
 print(json.dumps([dict(id=r['id'],status=r['status'],raw_bytes=r.get('raw_bytes'),raw_sha256=r.get('raw_sha256'),actual_link_count=len(r.get('literal_links',[])))for r in new],indent=2))
if __name__=='__main__':main()

