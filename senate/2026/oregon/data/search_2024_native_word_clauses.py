"""Submit the documented public Notes Word clauses, preserving the response."""
from pathlib import Path
from urllib.parse import urlencode,urljoin
import gzip,json
import requests
from bs4 import BeautifulSoup
from search_observed_2024_native_phrase import retain
DATA=Path(__file__).resolve().parent
NEWS=DATA/'news'
def main():
 rows=json.loads((NEWS/'manifest.json').read_bytes());byid={r['id']:r for r in rows}
 seed='sos-2024-two-notes-words-fresh-form';post='sos-2024-two-notes-words-result'
 if post in byid:
  r=byid[post];raw=gzip.decompress((NEWS/r['asset']).read_bytes())
 else:
  assert seed not in byid,'Retain interrupted session and choose a distinct explicitly documented attempt'
  parent=byid['sos-observed-2024-notes-phrase-fresh-form'];session=requests.Session()
  response=session.get(parent['url'],timeout=45)
  receipt,body=retain(seed,parent['url'],parent['id'],response,'Fresh normal public search form, following published Help single-word and advanced AND instructions.');assert response.status_code==200
  soup=BeautifulSoup(body,'html.parser');form=soup.select_one('form');payload={}
  for node in form.select('input[name]'):
   typ=node.get('type','text')
   if typ in ['submit','button']or typ in ['radio','checkbox']and not node.has_attr('checked'):continue
   payload[node['name']]=node.get('value','')
  for node in form.select('select[name]'):
   option=node.select_one('option[selected]')or node.select_one('option');payload[node['name']]=option['value']
  for n,term in [(1,'2024'),(2,'Precinct'),(3,'')]:
   name=f'ctl00$ContentPlaceHolder1$ddlSearchType{n}';sel=form.find('select',attrs={'name':name});value='notes'if term else'-1';assert sel.find('option',attrs={'value':value})
   payload[name]=value;payload[f'ctl00$ContentPlaceHolder1$txtSearch{n}']=term
  button=form.find('input',attrs={'type':'submit','value':'Search'});assert button;payload[button['name']]=button['value']
  url=urljoin(receipt['final_url'],form['action']);response=session.post(url,data=payload,timeout=45)
  r,raw=retain(post,url,seed,response,'Actual current normal public form: Notes Word2024 AND Notes WordPrecinct, thirdclauseempty. Checked AND radios, all current hidden fields and actual Search submit retained. No fullphrase/exhaustiveness assumption.',urlencode(payload).encode());assert response.status_code==200
 soup=BeautifulSoup(raw,'html.parser');header=soup.find(id='ContentPlaceHolder1_lblGridheader');records=[tr.get_text(' ',strip=True)for tr in soup.select('tr')if tr.select('a[href*="btnView"]')]
 print(json.dumps(dict(result_header=header.get_text(' ',strip=True)if header else None,first_page_rows=records),indent=2))
if __name__=='__main__':main()
