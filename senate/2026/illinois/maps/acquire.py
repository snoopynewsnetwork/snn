"""Public original acquisition. Individual immutable receipts; no aggregate writer dependency.
A repeat invocation reuses exact complete saved responses. --refresh is intentionally absent.
"""
from common import *
from datetime import datetime,timezone
from urllib.parse import urljoin,urlsplit,unquote
from html.parser import HTMLParser
import requests,re,argparse
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.href=None;self.label=''
 def handle_starttag(self,t,a):
  if t=='a':self.href=dict(a).get('href');self.label=''
 def handle_data(self,d):
  if self.href is not None:self.label+=d
 def handle_endtag(self,t):
  if t=='a' and self.href is not None:self.links.append(dict(href=self.href,label=self.label.strip()));self.href=None

def links(b):
 p=Links();p.feed(b.decode('utf-8',errors='replace'));return p.links

def body(r):
 b=b''.join((S/x['path']).read_bytes() for x in r.get('stored_parts',[]))
 if not b:return b
 raw=gzip.decompress(b);assert len(raw)==r['raw_bytes'] and sha(raw)==r['raw_sha256'];return raw

def fetch(id,url,parent=None,literal_href=None,basis=None,method='GET'):
 path=M/'source'/f'{id}.receipt.json'
 if path.exists():
  r=load(path)
  for x in r.get('stored_parts',[]):exact(x)
  return r,body(r)
 now=lambda:datetime.now(timezone.utc).isoformat()
 r=dict(id=id,method=method,requested_url=url,parent=parent,literal_href=literal_href,discovery_basis=basis,started_utc=now(),request_headers={'User-Agent':'Mozilla/5.0 (Illinois historical map research)'},query=urlsplit(url).query,request_body=None)
 try:
  response=requests.request(method,url,headers=r['request_headers'],timeout=(15,30))
  r.update(status=response.status_code,final_url=response.url,headers=list(response.raw.headers.items()),redirects=[dict(url=h.url,status=h.status_code,headers=list(h.raw.headers.items()),raw_body_bytes=len(h.content),raw_body_sha256=sha(h.content),body_hex=h.content.hex()) for h in response.history])
  b=response.content;z=gzip.compress(b,mtime=0);parts=[]
  for i,start in enumerate(range(0,len(z),39000000)):
   part=z[start:start+39000000];name=f'source/{id}.body.gz'+(f'.part{i:03}' if len(z)>=39000000 else '')
   (M/name).write_bytes(part);parts.append(dict(path='maps/'+name,bytes=len(part),sha256=sha(part)))
  r.update(raw_bytes=len(b),raw_sha256=sha(b),stored_parts=parts,storage='Concatenate parts then gzip.decompress: complete requests-decoded HTTP entity; no truncation',publisher_clock={k:v for k,v in response.headers.items() if k.lower() in ['date','last-modified','etag']},publisher_display_clock=None,publisher_display_timezone=None)
 except requests.RequestException as e:r.update(status=None,error=repr(e),redirects=[],stored_parts=[]);b=b''
 r['finished_utc']=now();dump('source/'+path.name,r)
 return r,b

def norm(s):return re.sub('[^a-z0-9]','',s.lower())
def bootstrap():
 for id,u in [('sbe-map-page','https://www.elections.il.gov/Main/PrecinctMaps.aspx'),('sbe-map-root','https://www.elections.il.gov/precinctmaps/'),('census-vtd-directory','https://www2.census.gov/geo/tiger/TIGER2020PL/LAYER/VTD/2020/'),('census-techdoc','https://www2.census.gov/geo/pdfs/maps-data/data/tiger/tgrshp2020pl/TGRSHP2020PL_TechDoc.pdf')]:
  r,b=fetch(id,u,basis='Official URL observed in primary public web search; no inferred IDs')
  if id=='sbe-map-root':dump('derived/state-archive-links.json',links(b))
  if id=='census-vtd-directory':
   link=next(x for x in links(b) if x['href']=='tl_2020_17_vtd20.zip')
   v,_=fetch('census-illinois-vtd2020',urljoin(u,link['href']),id,link['href'],'Actual Illinois statewide ZIP href in observed directory')
   print('statewide',v['status'],v.get('raw_bytes'))

def authorities():
 a=load(S/ACCEPTANCE);p=json.loads(exact(a['frozen_contract']));root=load(M/'source/sbe-map-root.receipt.json');ls=links(body(root));out=[]
 for x in p['authority_inventory']:
  n=norm(x['name']).replace('county','').replace('cityof','')
  # Literal archive names are independently compared, not synthesized URL paths.
  aliases={'eaststlouis':'eaststlouis','stclair':'stclair'}
  candidates=[l for l in ls if norm(l['label'])==aliases.get(n,n)]
  assert len(candidates)==1,(x['authority_id'],x['name'],candidates)
  l=candidates[0];r,b=fetch('authority-'+x['authority_id']+'-archive',urljoin(root['final_url'],l['href']),'sbe-map-root',l['href'],'Literal state archive folder name matches historical authority name; this establishes only an archive research chain')
  child=links(b);files=[l for l in child if re.search(r'\.(pdf|zip|shp|json|geojson|kml|kmz|xlsx?|docx?|txt|jpe?g|png|tiff?)(\?|$)',l['href'],re.I)]
  row=dict(authority_id=x['authority_id'],name=x['name'],priority=any(k in set(p['ordered_priority_keys']) for k in x['native_constituent_keys']),archive_receipt='maps/source/'+r['id']+'.receipt.json',archive_status=r['status'],archive_files=files,selected_asset_receipts=[])
  row['leaf_access_receipts']=[]
  out.append(row);dump('derived/authority-investigations.json',out)
  print(x['authority_id'],x['name'],r['status'],'files',len(files),'selected',len(row['selected_asset_receipts']),flush=True)
 assert len(out)==108 and sum(x['priority'] for x in out)==97

def leaves():
 from concurrent.futures import ThreadPoolExecutor
 rows=load(M/'derived/authority-investigations.json')
 def task(row):
  # Exactly one independently observed leaf per authority; complete prior downloads reused.
  files=row['archive_files']
  if not files:return row
  ranked=sorted(files,key=lambda l:(not bool(re.search(r'county|overall|township|precinct.*map|all.*precinct|city.*map',l['label'],re.I)),l['label']))
  f=ranked[0];ar=load(S/f.get('parent_receipt',row['archive_receipt']));url=urljoin(ar['final_url'],f['href']);id=row['authority_id']
  prior=M/'source'/('authority-'+id+'-asset-0.receipt.json')
  if prior.exists():
   r=load(prior);body(r);row['selected_asset_receipts']=['maps/source/'+prior.name]
   row['leaf_access_receipts']=['maps/source/'+prior.name];return row
  r,_=fetch('authority-'+id+'-leaf-head',url,ar['id'],f['href'],'Bounded original access: actual HEAD of one observed archive map leaf; large original remains unacquired, Census fallback complete',method='HEAD')
  row['leaf_access_receipts']=['maps/source/'+r['id']+'.receipt.json']
  headers={k.lower():v for k,v in r.get('headers',[])}
  length=int(headers.get('content-length','0'))
  if r['status']==200 and 0<length<=1500000:
   q,b=fetch('authority-'+id+'-asset-0',url,ar['id'],f['href'],'Complete observed archive leaf under bounded 1500000-byte HEAD size; no partial original admitted')
   row['leaf_access_receipts'].append('maps/source/'+q['id']+'.receipt.json')
   if q['status']==200:row['selected_asset_receipts']=['maps/source/'+q['id']+'.receipt.json']
  else:row['original_access_gap']='Selected leaf HEAD only: missing/large Content-Length or unavailable response. No partial body admitted. Complete historical Census geographic-context fallback retained.'
  print('leaf',id,'HEAD',r['status'],length,'acquired',len(row['selected_asset_receipts']),flush=True);return row
 with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(task,rows))
 dump('derived/authority-investigations.json',rows)

def deepen():
 rows=load(M/'derived/authority-investigations.json')
 pattern=r'\.(pdf|zip|shp|json|geojson|kml|kmz|xlsx?|docx?|txt|jpe?g|png|tiff?)(\?|$)'
 for row in rows:
  ar=load(S/row['archive_receipt']);pending=[ar];nested=[];files=[];visited=set()
  while pending:
   r=pending.pop(0)
   if r['id'] in visited:continue
   visited.add(r['id']);ls=links(body(r))
   files.extend(dict(x,parent_receipt='maps/source/'+r['id']+'.receipt.json') for x in ls if re.search(pattern,x['href'],re.I))
   for l in ls:
    url=urljoin(r['final_url'],l['href'])
    if url.startswith(ar['final_url']) and url!=ar['final_url'] and url.endswith('/'):
     id='authority-'+row['authority_id']+'-subdir-'+sha(url.encode())[:12]
     q,b=fetch(id,url,r['id'],l['href'],'Literal child directory in observed state archive; actual linked hierarchy only')
     pending.append(q);nested.append('maps/source/'+id+'.receipt.json')
  row['archive_files']=files;row['nested_archive_receipts']=list(dict.fromkeys(nested))
  if not files:row['archive_gap']='No recognized map original links in fully traversed observed archive hierarchy.'
  print('hierarchy',row['authority_id'],len(nested),len(files),flush=True)
 dump('derived/authority-investigations.json',rows)

def supplements():
 from concurrent.futures import ThreadPoolExecutor
 rows=load(M/'derived/authority-investigations.json')
 targets=[('16','Barrington Township Package.pdf'),('104','2014LargeBloomington6-2014.pdf'),('110','CityMapIndexNoSections20120727a.pdf'),('88','Abbreviations  Map Precinct.docx')]
 def task(target):
  id,label=target;row=next(x for x in rows if x['authority_id']==id);f=next(x for x in row['archive_files'] if x['label']==label);ar=load(S/f['parent_receipt'])
  r,b=fetch('authority-'+id+'-supplement',urljoin(ar['final_url'],f['href']),ar['id'],f['href'],'Additional complete shared historical county/city map or literal abbreviations companion; no child boundary crosswalk implied')
  if r['status']==200:
   path='maps/source/'+r['id']+'.receipt.json'
   if path not in row['selected_asset_receipts']:row['selected_asset_receipts'].append(path)
   if path not in row['leaf_access_receipts']:row['leaf_access_receipts'].append(path)
   for access in row['leaf_access_receipts']:
    head=load(S/access)
    if head['method']=='HEAD' and head['requested_url']==r['requested_url']:row.pop('original_access_gap',None)
  print('supplement',id,r['status'],r.get('raw_bytes'),flush=True)
 with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(task,targets))
 dump('derived/authority-investigations.json',rows)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['bootstrap','authorities','leaves','deepen','supplements']);args=ap.parse_args()
 globals()[args.stage]()
if __name__=='__main__':main()
