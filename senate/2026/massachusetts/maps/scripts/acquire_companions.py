"""Bounded explicit map/roster companions from already acquired municipality pages."""
from acquire import *
from acquire_local import safe,Links
import json,re,concurrent.futures,urllib.parse
alltargets=[]
for p in sorted((M/'parents').glob('*.json')):
 x=json.loads(p.read_bytes());choices={};seen={s['url']for s in x['steps']}
 for s in x['steps']:
  for a in s['all_literal_links']:
   href=a['href']
   if not isinstance(href,str):continue
   u=urllib.parse.urljoin(s['url'],href);label=a['text']+' '+urllib.parse.unquote(href)
   if not safe(u)or u in seen or re.search(r'(?i)(sample|specimen|ballot|results|minutes|agenda|application|steward|award|primary|payment|paybill)',label):continue
   if not re.search(r'(?i)\b(precincts?|wards?|subprecincts?|reprecincting|redistricting|polling)\b',label.replace('_',' ').replace('-',' ')):continue
   if re.search(r'(?i)(map|boundar|district|street.?list|polling.?loc|reprecinct|re-precinct)',label):choices[u]=dict(parent_literal=x['parent_literal'],url=u,parent_receipt=s['receipt'],literal_href=href,literal_text=a['text'],discovery='complete literal links retained in municipal chain')
 chosen=sorted(choices.values(),key=lambda a:(0 if re.search('(?i)map|boundar',a['literal_text'])else 1,a['url']))[:2];alltargets.extend(chosen)
# State explicitly delegates Boston map publication to this actual city planning page.
b,r=load(M/'receipts/state-map-585.json');p=Links();p.feed(b.decode())
for a in p.links:
 if a['text'].strip()in ['Wards and Precincts','Precincts']:
  alltargets.append(dict(parent_literal='Boston',url=urllib.parse.urljoin(r['final_url'],a['href']),parent_receipt='receipts/state-map-585.json',literal_href=a['href'],literal_text=a['text'],discovery='actual state-linked Boston planning map index'))
dump(M/'companion-targets.json',alltargets)
def work(x):
 key='companion-'+sha(x['url'].encode())[:16];b,r=fetch(key,x['url'],parent=x['parent_receipt'],literal_href=x['literal_href']);return dict(**x,receipt='receipts/'+key+'.json',status=r.get('status'),complete_pdf=b.startswith(b'%PDF-'),raw_sha256=r.get('raw_sha256'),raw_bytes=r.get('raw_bytes'),format='PDF'if b.startswith(b'%PDF-')else 'other/error; raw retained')
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as ex:out=list(ex.map(work,alltargets))
dump(M/'companion-acquisitions.json',out);print('companions',len(out),'PDFs',sum(x['complete_pdf']for x in out))
