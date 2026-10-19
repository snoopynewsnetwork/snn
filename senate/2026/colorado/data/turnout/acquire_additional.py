#!/usr/bin/env python3
from pathlib import Path
import requests,gzip,json,hashlib,datetime,re
from urllib.parse import urljoin
O=Path(__file__).resolve().parent;S=O/'source'
def main():
 a=json.loads((S/'acquisition.json').read_text())
 def get(sid,url,parent):
  r=requests.get(url,timeout=90);b=r.content;z=gzip.compress(b,mtime=0);p=S/(sid+'.body.gz');p.write_bytes(z);a.append(dict(id=sid,requested_url=url,final_url=r.url,retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status=r.status_code,headers=dict(r.headers),redirects=[dict(url=x.url,status=x.status_code,headers=dict(x.headers))for x in r.history],raw_sha256=hashlib.sha256(b).hexdigest(),raw_bytes=len(b),stored_sha256=hashlib.sha256(z).hexdigest(),stored_bytes=len(z),asset=p.name,parent=parent,entity_scope='complete decoded response body'));assert len(z)<40000000;(S/'acquisition.json').write_text(json.dumps(a,indent=2)+'\n');print(sid,r.status_code,len(b),flush=True);return b
 rules=next(x for x in a if x['id']=='rules-current');html=gzip.decompress((S/rules['asset']).read_bytes()).decode()
 for href,label in re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',html,re.S):
  if re.search(r'Rule (7\.|16\.|18\.|25\.)|8 CCR 1505-1 Rules',label):get('rule-'+href.rsplit('/',1)[-1].replace('.pdf',''),urljoin(rules['final_url'],href),'rules-current observed anchor '+label)
 get('uocava-current','https://www.sos.state.co.us/pubs/elections/FAQs/UOCAVA.html','clerks-2026 observed link')
 get('usps-tro','https://coag.gov/app/uploads/2026/08/218.-Order-granting-TRO-in-part-1.pdf','AG article literal TRO link inspected research browser; requests article returned202empty')
 u='https://www.supremecourt.gov/docket/docketfiles/html/public/26a305.html';html=get('scotus-26a305',u,'official docket found current USPS court change search').decode()
 for href,label in re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',html,re.S):
  if label=='Opinion':get('scotus-stay-opinion',urljoin(u,href),'scotus-26a305 September14 literal Opinion link');break
 get('census-county-fips','https://api.census.gov/data/2020/dec/pl?get=NAME&for=county:*&in=state:08','Census public geography API, county FIPS only; no election geography inference')
 get('senate-class-II','https://www.senate.gov/senators/Class_II.htm','US Senate official class list')
 # Original complete vendor booklet linked from actual2022 SSR, preserve native material outside contests too.
 get('booklet-2022-vendor','https://co.elstats2.civera.com/eng/files/serve/497','current-2022-senate contest.files[0].file.url observed SSR')
if __name__=='__main__':main()
