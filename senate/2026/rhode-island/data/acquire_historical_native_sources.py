"""Acquire only observed primary pages and their literal historical download links."""
from pathlib import Path
from urllib.parse import urljoin
import datetime,gzip,hashlib,json,os
import requests
from bs4 import BeautifulSoup
DATA=Path(__file__).resolve().parent
NEWS=DATA/'news'
def sha(b):return hashlib.sha256(b).hexdigest()
def get(sid,url,parent,basis):
 rows=json.loads((NEWS/'manifest.json').read_bytes());existing=next((r for r in rows if r['id']==sid),None)
 if existing:
  assert existing['url']==url
  if not existing.get('asset'):return existing,b''
  z=(NEWS/existing['asset']).read_bytes();b=gzip.decompress(z);assert sha(z)==existing['stored_sha256']and sha(b)==existing['raw_sha256'];return existing,b
 record=dict(id=sid,url=url,parent_source_id=parent,request_method='GET',retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),discovery_basis=basis)
 try:
  response=requests.get(url,timeout=40);raw=response.content
  asset=next((r['asset']for r in rows if r.get('raw_sha256')==sha(raw)and r.get('asset')),None)
  if asset is None:
   asset=sid+'.html.gz';path=NEWS/asset;assert not path.exists();z=gzip.compress(raw,mtime=0);assert len(z)<40000000;path.write_bytes(z)
  record.update(status=response.status_code,final_url=response.url,headers=dict(response.headers),redirects=[dict(url=r.url,status=r.status_code,headers=dict(r.headers))for r in response.history],bytes=len(raw),raw_sha256=sha(raw),asset=asset,stored_sha256=sha((NEWS/asset).read_bytes()))
 except requests.RequestException as e:record['error']=str(e);raw=b''
 rows.append(record);path=NEWS/'manifest.tmp';path.write_text(json.dumps(rows,indent=2)+'\n');os.replace(path,NEWS/'manifest.json');print(sid,record.get('status','transport_failure'),len(raw),flush=True);return record,raw
def main():
 for year,seed in [('2020','https://www.ri.gov/election/results/2020/general_election/data/'),('2022','https://www.ri.gov/election/results/2022/general_election/')]:
  sid=f'ri-{year}-observed-historical-seed';r,raw=get(sid,seed,None,'Exact historical primary URL returned by public search;2020 data index and2022 statewide summary, not a guessed contest/download ID.')
  assert r['status']==200;soup=BeautifulSoup(raw,'html.parser')
  if year=='2022':
   anchor=next(a for a in soup.select('a[href]')if a.get_text(' ',strip=True)=='Data files');url=urljoin(r['final_url'],anchor['href']);sid='ri-2022-observed-data-index';r,raw=get(sid,url,r['id'],'Literal Data files anchor on actual2022 official-results summary.');assert r['status']==200;soup=BeautifulSoup(raw,'html.parser')
  else:
   # The summary is linked in the same observed historical navigation.
   anchor=next(a for a in soup.select('a[href]')if a.get_text(' ',strip=True)=='Statewide summary');url=urljoin(r['final_url'],anchor['href']);get('ri-2020-observed-state-summary',url,r['id'],'Literal Statewide summary anchor on actual2020 data index.')
  for label,tag in [('Short format','short-zip'),('Long format','long-zip'),('Data description','format-description')]:
   anchor=next(a for a in soup.select('a[href]')if a.get_text(' ',strip=True)==label);url=urljoin(r['final_url'],anchor['href']);get(f'ri-{year}-observed-{tag}',url,r['id'],f'Literal {label} download anchor in actual{year} data index; all original ZIP members/source vintages remain separate.')
if __name__=='__main__':main()
