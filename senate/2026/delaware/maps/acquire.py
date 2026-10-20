"""Append-only, bounded public HTTP evidence acquisition, complete entities/redirects.
CLI: python3 acquire.py ID URL [PARENT_ID] [LITERAL_HREF]
No refresh overwrites: each ID is immutable. Offline build never calls this tool.
"""
from common import *
import datetime,sys,urllib.parse
import requests
from html.parser import HTMLParser
class Links(HTMLParser):
 def __init__(self,url):super().__init__();self.url=url;self.links=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  for k in ['href','src']:
   if d.get(k):self.links.append(dict(tag=tag,attribute=k,literal=d[k],url=urllib.parse.urljoin(self.url,d[k]),source_character_position=self.getpos()))
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def fetch(i,url,parent=None,literal=None,**extra):
 out=M/'source'/f'{i}.receipt.json'
 if out.exists():
  existing=read(out);assert existing['url']==url,('immutable request ID reused for another URL',i);return existing
 start=now();status=None;raw=b'';redirects=[];headers={};error=None;final=url
 try:
  response=requests.get(url,timeout=(20,90),headers={'User-Agent':'Delaware-election-geography-research/1.0'},allow_redirects=True)
  raw=response.content;status=response.status_code;final=response.url;headers=dict(response.headers)
  redirects=[dict(url=r.url,status=r.status_code,headers=dict(r.headers),body_base64=__import__('base64').b64encode(r.content).decode(),body_sha256=sha(r.content)) for r in response.history]
 except requests.RequestException as e:error=repr(e)
 r=dict(id=i,url=url,parent_id=parent,literal_href=literal,method='GET',query=urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query,keep_blank_values=True),request_body=None,requested_utc=start,completed_utc=now(),status=status,final_url=final,headers=headers,redirects=redirects,error=error,raw_bytes=len(raw),raw_sha256=sha(raw),body_representation='Complete requests content-decoded HTTP entity, gzip stored; transport headers retained',**extra)
 known=read(M/'source/reused-original-receipts.json')
 known += [read(p) for p in sorted((M/'source').glob('*.receipt.json'))]
 same=next((v for v in known if v.get('raw_sha256')==r['raw_sha256'] and v.get('raw_bytes')==len(raw)),None)
 if same:
  body(same);r.update({k:same[k] for k in ['asset_path','stored_bytes','stored_sha256']});r['exact_original_reuse_id']=same['id']
 else:
  compressed=gzip.compress(raw,mtime=0);assert len(compressed)<LIMIT
  p=M/'source'/f'{i}.body.gz';p.write_bytes(compressed);r.update(asset_path=str(p.relative_to(S)),stored_bytes=len(compressed),stored_sha256=sha(compressed))
 if 'html' in headers.get('Content-Type','').lower():
  parser=Links(final);parser.feed(raw.decode('utf-8',errors='replace'));r['literal_links']=parser.links
 write(out,r);print(i,status,len(raw),error or '',flush=True);return r
if __name__=='__main__':fetch(*sys.argv[1:])
