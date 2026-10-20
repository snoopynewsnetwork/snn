"""Actual official indexed contest pages and their literal CSV/document links."""
from pathlib import Path
import datetime,gzip,hashlib,json,os
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
DATA=Path(__file__).resolve().parent
NEWS=DATA/'news'
MANIFEST=NEWS/'manifest.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def get(key,url,parent,basis,referer=None):
 rows=json.loads(MANIFEST.read_bytes());old=next((r for r in rows if r['id']==key),None)
 if old:
  assert old['url']==url;b=gzip.decompress((NEWS/old['asset']).read_bytes());assert len(b)==old['bytes']and sha(b)==old['raw_sha256'];return old,b
 headers={'Referer':referer}if referer else {};started=datetime.datetime.now(datetime.timezone.utc).isoformat();r=requests.get(url,headers=headers,timeout=45);raw=r.content
 asset=next((r['asset']for r in rows if r.get('raw_sha256')==sha(raw)),None)
 if asset is None:
  asset=key+'.html.gz';p=NEWS/asset;assert not p.exists();p.write_bytes(gzip.compress(raw,mtime=0))
 stored=(NEWS/asset).read_bytes();assert len(stored)<40_000_000
 row=dict(id=key,url=url,method='GET',parent_source_id=parent,discovery_basis=basis,retrieved_at_utc=started,status=r.status_code,final_url=r.url,request_headers=headers,headers=dict(r.headers),redirects=[dict(url=z.url,status=z.status_code,headers=dict(z.headers))for z in r.history],bytes=len(raw),raw_sha256=sha(raw),asset=asset,stored_sha256=sha(stored));rows.append(row);tmp=MANIFEST.with_suffix('.tmp');tmp.write_text(json.dumps(rows,indent=2)+'\n');os.replace(tmp,MANIFEST);print(key,r.status_code,len(raw),flush=True);return row,raw
def main():
 targets=[('2020-senate','https://electionstats.sos.nm.gov/contest/13251'),('2022-governor','https://electionstats.sos.nm.gov/contest/11090'),('2024-president','https://electionstats.sos.nm.gov/contest/14877')]
 for tag,url in targets:
  r,b=get('elstats-observed-'+tag+'-view',url,None,'Exact primary Secretary ElectionStats historical contest URL returned by public search for the named year, candidates and statewide office; no numeric ID guessed.');assert r['status']==200
  s=BeautifulSoup(b,'html.parser');csvs=list(dict.fromkeys(urljoin(r['final_url'],a['href'])for a in s.select('a[href]')if 'download_contest/'in a['href']and '.csv'in a['href']));assert len(csvs)==1,(tag,csvs)
  cr,cb=get('elstats-observed-'+tag+'-native-csv',csvs[0],r['id'],'Literal downloadable Results CSV href on actual historical contest page.');assert cr['status']==200 and len(cb)>500
  docs=list(dict.fromkeys(urljoin(r['final_url'],a['href'])for a in s.select('a[href]')if '/document/'in a['href']));assert len(docs)==1,(tag,docs)
  dr,db=get('elstats-observed-'+tag+'-document',docs[0],r['id'],'Literal Official Sources document href on actual historical contest page.');assert dr['status']==200
  soup=BeautifulSoup(db,'html.parser');embed=soup.select_one('embed[src]');assert embed;url=embed['src'].split('#')[0]
  get('elstats-observed-'+tag+'-canvass-original',url,dr['id'],'Literal embedded PDF original on official document viewer, requested with that public viewer as normal Referer.',dr['final_url'])
if __name__=='__main__':main()
