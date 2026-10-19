"""One exact public historical export postback observed on its actual parent."""
from pathlib import Path
from urllib.parse import urljoin
import datetime,gzip,hashlib,json,re
import requests
from bs4 import BeautifulSoup

DATA=Path(__file__).resolve().parent
NEWS=DATA/'news'
URL='https://electionresults.sd.gov/resultsSW.aspx?type=SWR&map=CTY&eid=684'
KEY='sos-2024-public-presidential-precinct-export-684'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 path=NEWS/'manifest.json';manifest=json.loads(path.read_bytes());known={r['id']for r in manifest}
 if KEY in known:print('Exact bounded observation already retained');return
 def save(key,response,extra):
  assert key not in known
  raw=response.content;stored=gzip.compress(raw,mtime=0)
  row={'id':key,'url':response.request.url,'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
   'request_method':response.request.method,'status':response.status_code,'final_url':response.url,
   'redirects':[{'url':r.url,'status':r.status_code,'location':r.headers.get('Location')}for r in response.history],
   'headers':dict(response.headers),'bytes':len(raw),'raw_sha256':sha(raw),'stored_sha256':sha(stored),**extra}
  if len(stored)<40000000:
   p=NEWS/(key+'.html.gz');p.write_bytes(stored);row['asset']=p.name
  else:
   row['asset_parts']=[];row['stored_bytes']=len(stored)
   for i,at in enumerate(range(0,len(stored),32000000),1):
    p=NEWS/(key+f'.html.gz.part{i:03}');part=stored[at:at+32000000];p.write_bytes(part)
    row['asset_parts'].append({'asset':p.name,'bytes':len(part),'sha256':sha(part)})
  manifest.append(row);known.add(key);path.write_text(json.dumps(manifest,indent=2)+'\n')
  print(key,response.status_code,len(raw),response.headers.get('Content-Type'),response.headers.get('Content-Disposition'),flush=True)
 try:
  session=requests.Session();parent=session.get(URL,timeout=35)
  save(KEY+'-parent-form',parent,{'discovery_basis':'Fresh actual2024 statewide parent, exact href observed from original general history/default; no electionID guessed.'})
  dom=BeautifulSoup(parent.content,'html.parser');form=dom.find('form');assert form
  button=next(b for b in form.find_all('input')if b.get('value')=='Precinct Level'and b.get('raceid')=='12665')
  match=re.search(r"__doPostBack\('([^']+)','([^']*)'\)",button['onclick']);assert match
  fields={x['name']:x.get('value','')for x in form.find_all('input',attrs={'type':'hidden'})if x.get('name')}
  assert fields.get('ctl00$hidElectionDate')=='11/5/2024'
  fields['__EVENTTARGET']=match[1];fields['__EVENTARGUMENT']=match[2]
  result=session.post(urljoin(parent.url,form.get('action')or parent.url),data=fields,timeout=45)
  save(KEY,result,{'parent_form_source_id':KEY+'-parent-form','observed_published_control_attributes':button.attrs,
   'request_form_fields':fields,'discovery_basis':'Exact public Precinct Level control on actual historical Presidential Electors race12665; current flags/IDs not inferred. Read-only export POST.'})
 except (requests.RequestException,AssertionError,StopIteration)as error:
  manifest.append({'id':KEY,'url':URL,'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'error':repr(error),'discovery_basis':'Single bounded attempt at exact observed historical public precinct-export control.'})
  path.write_text(json.dumps(manifest,indent=2)+'\n');print('Retained bounded export failure',type(error).__name__,flush=True)
if __name__=='__main__':main()
