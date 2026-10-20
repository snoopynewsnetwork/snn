"""Try one literal phrase in the observed anonymous public Notes Word form."""
from pathlib import Path
from urllib.parse import urlencode,urljoin
import datetime,gzip,hashlib,json,os
import requests
from bs4 import BeautifulSoup
DATA=Path(__file__).resolve().parent
NEWS=DATA/'news'
MANIFEST=NEWS/'manifest.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def retain(sid,url,parent,response,basis,request=None):
 rows=json.loads(MANIFEST.read_bytes());assert sid not in {r['id']for r in rows};raw=response.content;asset=next((r['asset']for r in rows if r.get('raw_sha256')==sha(raw)and r.get('asset')),None)
 if asset is None:
  asset=sid+'.html.gz';p=NEWS/asset;assert not p.exists();p.write_bytes(gzip.compress(raw,mtime=0))
 record=dict(id=sid,url=url,parent_source_id=parent,request_method='POST observed public read-only Search button'if request else'GET',retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status=response.status_code,final_url=response.url,headers=dict(response.headers),redirects=[dict(url=r.url,status=r.status_code,headers=dict(r.headers))for r in response.history],bytes=len(raw),raw_sha256=sha(raw),asset=asset,stored_sha256=sha((NEWS/asset).read_bytes()),discovery_basis=basis)
 if request is not None:
  p=NEWS/(sid+'.request.txt.gz');assert not p.exists();p.write_bytes(gzip.compress(request,mtime=0));record.update(request_body_asset=p.name,request_body_sha256=sha(request),request_body_stored_sha256=sha(p.read_bytes()))
 rows.append(record);tmp=MANIFEST.with_suffix('.tmp');tmp.write_text(json.dumps(rows,indent=2)+'\n');os.replace(tmp,MANIFEST);print(sid,response.status_code,len(raw),flush=True);return record,raw
def main():
 rows=json.loads(MANIFEST.read_bytes());seedid='sos-observed-2024-notes-phrase-fresh-form';postid='sos-observed-2024-notes-phrase-search';existing={r['id']:r for r in rows}
 if postid in existing:
  r=existing[postid];raw=gzip.decompress((NEWS/r['asset']).read_bytes());assert sha(raw)==r['raw_sha256'];print('Existing exact source observation replayed',len(raw));return
 assert seedid not in existing,'Interrupted session must be retained and a separately named fresh attempt explicitly chosen'
 parent=existing['sos-native-search-form-seed'];sess=requests.Session();response=sess.get(parent['url'],timeout=45);r,raw=retain(seedid,parent['url'],parent['id'],response,'Fresh same-session GET of previously observed public search-form URL before the normal read-only submit.');assert r['status']==200
 soup=BeautifulSoup(raw,'html.parser');form=soup.select_one('form');assert form['method'].lower()=='post';payload={}
 for item in form.select('input[name]'):
  typ=item.get('type','text')
  if typ in ['submit','button']or typ in ['checkbox','radio']and not item.has_attr('checked'):continue
  payload[item['name']]=item.get('value','')
 for sel in form.select('select[name]'):
  option=sel.select_one('option[selected]')or sel.select_one('option');payload[sel['name']]=option['value']
 for i in [1,2,3]:
  sel=form.find('select',attrs={'name':f'ctl00$ContentPlaceHolder1$ddlSearchType{i}'});value='notes'if i==3 else'-1';assert sel.find('option',attrs={'value':value});payload[sel['name']]=value;payload[f'ctl00$ContentPlaceHolder1$txtSearch{i}']='2024 General Election Precinct Level Results'if i==3 else''
 button=form.find('input',attrs={'type':'submit','value':'Search'});assert button;payload[button['name']]=button['value'];url=urljoin(r['final_url'],form['action']);response=sess.post(url,data=payload,timeout=45);r,raw=retain(postid,url,seedid,response,'Only the third observed Notes Word clause contains the literal complete2024 General Election Precinct Level Results phrase; first two clauses explicitly--Select--/empty. Same anonymous session, current hidden form fields and actual Search button; response filtering/exhaustiveness not assumed.',urlencode(payload).encode());assert r['status']==200
 soup=BeautifulSoup(raw,'html.parser');records=[tr.get_text(' ',strip=True)for tr in soup.select('tr')if tr.select('a[href*="btnView"]')]
 print(json.dumps(dict(observed_result_rows=len(records),rows=records),indent=2))
if __name__=='__main__':main()
