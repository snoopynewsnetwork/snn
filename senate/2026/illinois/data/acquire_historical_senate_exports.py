"""Replay observed public county-results election selector and literal Senate export anchors."""
from pathlib import Path
import datetime,gzip,hashlib,json,requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
N=Path(__file__).resolve().parent/'news'
def main():
 manifest=json.loads((N/'manifest.json').read_bytes());known={x['id']:x for x in manifest};session=requests.Session()
 def capture(sid,url,parent,method='GET',data=None):
  if sid in known:
   x=known[sid];assert x['url']==url and x.get('method','GET')==method
  else:
   x={'id':sid,'url':url,'method':method,'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'parent_source_id':parent,'discovery_basis':'Actual public results form/selected election option or literal returned ByOffice download link; historical read-only queries only.'}
   if data is not None:x['public_form_fields']=data
   try:
    response=session.request(method,url,data=data,timeout=(15,45));b=response.content;p=N/(sid+'.html.gz');p.write_bytes(gzip.compress(b,mtime=0));x.update(status=response.status_code,final_url=response.url,headers=dict(response.headers),redirects=[{'url':h.url,'status':h.status_code,'headers':dict(h.headers)}for h in response.history],bytes=len(b),raw_sha256=hashlib.sha256(b).hexdigest(),asset=p.name,stored_sha256=hashlib.sha256(p.read_bytes()).hexdigest())
   except requests.RequestException as e:x.update(error=type(e).__name__+': '+str(e))
   x['finished_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();manifest.append(x);known[sid]=x;(N/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
  print(sid,x.get('status'),x.get('bytes'),flush=True)
  assert x.get('status')==200,(sid,x.get('status'),x.get('error'));z=(N/x['asset']).read_bytes();assert hashlib.sha256(z).hexdigest()==x['stored_sha256'];b=gzip.decompress(z);assert hashlib.sha256(b).hexdigest()==x['raw_sha256'];return x,b
 county2024=known['sos-observed-historical-selector-initial'];soup2024=BeautifulSoup(gzip.decompress((N/county2024['asset']).read_bytes()),'html.parser');a2024=soup2024.find('a',id='ContentPlaceHolder1_hypFederalStatewide');assert a2024 is not None
 capture('sos-observed-2024-federal-statewide-page',urljoin(county2024['final_url'],a2024['href']),'sos-observed-historical-selector-initial')
 url=known['state-results']['url'];initial,raw=capture('sos-observed-historical-search-form',url,'state-results');soup=BeautifulSoup(raw,'html.parser');select=soup.find('select',attrs={'name':'ctl00$ContentPlaceHolder1$ddlElections'});assert select is not None
 button=soup.find('input',attrs={'name':'ctl00$ContentPlaceHolder1$btnSearch'});assert button is not None and "__doPostBack('ctl00$ContentPlaceHolder1$btnSearch','')"in button['onclick']
 for year,value in [('2020','58'),('2022','62')]:
  assert any(o.get('value')==value and year+' GENERAL ELECTION'in o.get_text()for o in select.find_all('option'))
  form=select.find_parent('form');action=urljoin(initial['final_url'],form.get('action')or initial['final_url']);payload={x['name']:x.get('value','')for x in form.find_all('input',attrs={'type':'hidden'})if x.get('name')}
  for x in form.find_all('select'):
   if x.get('name'):
    o=x.find('option',selected=True)or x.find('option');payload[x['name']]=o.get('value',o.get_text())
  payload['__EVENTTARGET']=button['name'];payload['__EVENTARGUMENT']='';payload[select['name']]=value
  row,body=capture('sos-observed-'+year+'-public-search',action,'sos-observed-historical-search-form','POST',payload);s=BeautifulSoup(body,'html.parser');current=s.find('select',attrs={'name':select['name']});assert current.find('option',selected=True)['value']==value
  a=s.find('a',id='ContentPlaceHolder1_hypCounty');assert a is not None and a.has_attr('href')
  countyurl=urljoin(row['final_url'],a['href']);county,body=capture('sos-observed-'+year+'-county-page',countyurl,row['id']);s=BeautifulSoup(body,'html.parser')
  statewide=s.find('a',id='ContentPlaceHolder1_hypFederalStatewide');assert statewide is not None and statewide.has_attr('href')
  capture('sos-observed-'+year+'-federal-statewide-page',urljoin(county['final_url'],statewide['href']),county['id'])
  anchors=[a for a in s.find_all('a',href=True)if'ByOffice'in a['href']and'UNITED STATES SENATOR'in a['href']];assert len(anchors)==1,[a['href']for a in anchors]
  literal=anchors[0]['href'];download=urljoin(county['final_url'],'/'+literal.replace('\\','/').lstrip('/'));capture('sos-observed-'+year+'-senate-native-csv',download,county['id'])
if __name__=='__main__':main()
