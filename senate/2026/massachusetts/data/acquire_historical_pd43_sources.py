"""Read-only historical PD43 public-form queries and literal download anchors."""
from pathlib import Path
import datetime,gzip,hashlib,json,os
from urllib.parse import urlencode,urljoin
import requests
from bs4 import BeautifulSoup
DATA=Path(__file__).resolve().parent
NEWS=DATA/'news'
MANIFEST=NEWS/'manifest.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def get(key,url,parent,basis,form_fields=None):
 rows=json.loads(MANIFEST.read_bytes());old=next((r for r in rows if r['id']==key),None)
 if old:
  assert old['url']==url;b=gzip.decompress((NEWS/old['asset']).read_bytes());assert len(b)==old['bytes']and sha(b)==old['raw_sha256'];return old,b
 before=datetime.datetime.now(datetime.timezone.utc).isoformat();r=requests.get(url,timeout=45)
 raw=r.content;a=next((x['asset']for x in rows if x.get('raw_sha256')==sha(raw)),None)
 if a is None:
  a=key+'.html.gz';p=NEWS/a;assert not p.exists();p.write_bytes(gzip.compress(raw,mtime=0))
 stored=(NEWS/a).read_bytes();assert len(stored)<40_000_000
 row=dict(id=key,url=url,method='GET',parent_source_id=parent,discovery_basis=basis,retrieved_at_utc=before,status=r.status_code,final_url=r.url,redirects=[dict(url=z.url,status=z.status_code,headers=dict(z.headers))for z in r.history],headers=dict(r.headers),bytes=len(raw),raw_sha256=sha(raw),asset=a,stored_sha256=sha(stored))
 if form_fields is not None:row['observed_public_form_fields']=form_fields
 rows.append(row);tmp=MANIFEST.with_suffix('.tmp');tmp.write_text(json.dumps(rows,indent=2)+'\n');os.replace(tmp,MANIFEST)
 assert r.status_code==200,(key,r.status_code)
 print(key,r.status_code,len(raw),flush=True);return row,raw
def main():
 rows=json.loads(MANIFEST.read_bytes());root=next(r for r in rows if r['id']=='sos-pd43-root');raw=gzip.decompress((NEWS/root['asset']).read_bytes());assert sha(raw)==root['raw_sha256'];doc=BeautifulSoup(raw,'html.parser');form=doc.select_one('#search_form_elections form');assert form['method'].lower()=='get';action=urljoin(root['url'],form['action'])
 for year,office,label in [(2020,'U.S. Senate','2020-senate'),(2022,'Governor','2022-governor'),(2024,'President','2024-president')]:
  opts=[o for o in form.select('select[name=office_id] option')if o.get_text(' ',strip=True)==office];assert len(opts)==1
  assert form.select_one(f'select[name=year_from] option[value="{year}"]')and form.select_one(f'select[name=year_to] option[value="{year}"]')
  assert any(o.get('value')=='General'for o in form.select('select[name=stage] option'))
  fields=dict(year_from=str(year),year_to=str(year),office_id=opts[0]['value'],stage='General');key='sos-observed-'+label+'-search';r,b=get(key,action+'?'+urlencode(fields),root['id'],'Literal public election search form with observed year, office and General option values.',fields)
  s=BeautifulSoup(b,'html.parser');links=[]
  for a in s.select('a[href]'):
   item=a.find_parent('tr',class_='election_item')
   if '/elections/view/'in a['href']and item is not None and office in item.get_text(' ',strip=True)and str(year)in item.get_text(' ',strip=True)and 'Statewide'in item.get_text(' ',strip=True):links.append(urljoin(r['final_url'],a['href']))
  links=list(dict.fromkeys(links));assert len(links)==1,(label,links)
  key='sos-observed-'+label+'-view';r,b=get(key,links[0],r['id'],'Literal matching historical election href returned by observed public form query.')
  s=BeautifulSoup(b,'html.parser');downloads={}
  for a in s.select('a[href]'):
   if '/elections/download/'in a['href']:
    for v,scope in [('0','municipal'),('1','precinct')]:
     if 'precincts_include:'+v in a['href']:downloads[scope]=urljoin(r['final_url'],a['href'])
  assert set(downloads)=={'municipal','precinct'},(label,downloads)
  for scope,url in downloads.items():get('sos-observed-'+label+'-'+scope+'-csv',url,r['id'],'Literal '+scope+' CSV download anchor on the actual historical election page.')
if __name__=='__main__':main()
