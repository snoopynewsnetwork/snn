"""Follow an actual numbered page action in the normal public records form."""
from urllib.parse import urlencode,urljoin
import argparse,gzip,json,re
import requests
from bs4 import BeautifulSoup
from search_observed_2024_native_phrase import NEWS,retain
def controls(form):
 out={}
 for node in form.select('input[name]'):
  typ=node.get('type','text')
  if typ in ['submit','button']or typ in ['radio','checkbox']and not node.has_attr('checked'):continue
  out[node['name']]=node.get('value','')
 for node in form.select('select[name]'):
  option=node.select_one('option[selected]')or node.select_one('option');out[node['name']]=option['value']
 return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--page',type=int,required=True);args=ap.parse_args()
 rows=json.loads((NEWS/'manifest.json').read_bytes());byid={r['id']:r for r in rows};seed=f'sos-2024-catalog-page{args.page}-fresh-form';post=f'sos-2024-catalog-page{args.page}-normal-navigation'
 if post in byid:
  r=byid[post];raw=gzip.decompress((NEWS/r['asset']).read_bytes())
 else:
  assert seed not in byid,'Interrupted fresh session retained; choose a separately documented attempt'
  parent=byid['sos-observed-2024-notes-phrase-fresh-form'];session=requests.Session();response=session.get(parent['url'],timeout=45)
  r,raw=retain(seed,parent['url'],parent['id'],response,'Fresh actual bookmarked public Notes Word2024 form before clicking one numbered navigation link.');assert r['status']==200
  soup=BeautifulSoup(raw,'html.parser');form=soup.select_one('form');anchor=next(a for a in soup.select('.rgPager a')if a.get_text(strip=True)==str(args.page))
  match=re.fullmatch(r"javascript:__doPostBack\('([^']+)','([^']*)'\)",anchor['href']);assert match
  payload=controls(form);payload['__EVENTTARGET']=match[1];payload['__EVENTARGUMENT']=match[2]
  url=urljoin(r['final_url'],form['action']);response=session.post(url,data=payload,timeout=45)
  r,raw=retain(post,url,seed,response,f'Literal published numbered page{args.page} __doPostBack action, normal current form controls/hidden fields; no guessed record IDs or private API.',urlencode(payload).encode());assert r['status']==200
 soup=BeautifulSoup(raw,'html.parser');header=soup.find(id='ContentPlaceHolder1_lblGridheader');records=[tr.get_text(' ',strip=True)for tr in soup.select('tr')if tr.select('a[href*="btnView"]')]
 print(json.dumps(dict(header=header.get_text(' ',strip=True)if header else None,page_rows=records),indent=2))
if __name__=='__main__':main()
