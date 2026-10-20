#!/usr/bin/env python3
"""Bounded public primary navigation only. Never overwrites a receipt."""
from pathlib import Path
from datetime import datetime,timezone
from html.parser import HTMLParser
from urllib.parse import urljoin,urlparse
import requests,json,gzip,hashlib,sys
D=Path(__file__).resolve().parents[1];S=D/'source'
def sha(b):return hashlib.sha256(b).hexdigest()
def fetch(sid,url,parent=None):
 sid=('public-network-' if '--public-network' in sys.argv else '')+sid
 p=S/(sid+'.receipt.json')
 if p.exists():return json.loads(p.read_text())
 rec={'id':sid,'requested_url':url,'parent':parent,'retrieved_at_utc':datetime.now(timezone.utc).isoformat()}
 try:
  r=requests.get(url,timeout=45);b=r.content;z=gzip.compress(b,mtime=0);a=S/(sid+'.body.gz');assert len(z)<40000000;a.write_bytes(z)
  rec.update(final_url=r.url,status=r.status_code,headers=dict(r.headers),redirects=[{'url':h.url,'status':h.status_code,'headers':dict(h.headers)} for h in r.history],asset=a.name,raw_sha256=sha(b),raw_bytes=len(b),stored_sha256=sha(z),stored_bytes=len(z))
 except requests.RequestException as e:rec['client_error']=str(e)
 p.write_text(json.dumps(rec,indent=2)+'\n');return rec
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.href=None;self.txt=''
 def handle_starttag(self,t,a):
  if t=='a':self.href=dict(a).get('href');self.txt=''
 def handle_data(self,d):
  if self.href:self.txt+=d
 def handle_endtag(self,t):
  if t=='a' and self.href:self.links.append((self.href,self.txt.strip()));self.href=None

def main():
 fetch('senate-class-II','https://www.senate.gov/senators/Class_II.htm')
 fetch('senate-class-I','https://www.senate.gov/senators/Class_I.htm')
 info=fetch('current-2026-info','https://www.nj.gov/state/elections/election-information-2026.shtml')
 fetch('current-results-authority','https://www.nj.gov/state/elections/election-results.shtml')
 fetch('current-election-rule','https://www.nj.gov/state/dos-statutes-elections-19-01-09.shtml')
 if info.get('status')==200:
  p=Links();p.feed(gzip.decompress((S/info['asset']).read_bytes()).decode())
  selected=[]
  for href,label in p.links:
   if (('official-general-candidates-us-senate.pdf' in href) or ('certification-of-general-election-nominees_us-senate_us-house.pdf' in href) or ('chron-general-election' in href)):
    url=urljoin(info['final_url'],href);assert urlparse(url).hostname in ['www.nj.gov','nj.gov'];sid='current-'+('senate-roster' if 'candidates-us-senate' in href else 'general-certification' if 'certification' in href else 'general-calendar');rec=fetch(sid,url,{'id':info['id'],'literal_href':href,'literal_label':label});selected.append({'source_id':sid,'url':url,'label':label})
  (S/'current-navigation.json').write_text(json.dumps(selected,indent=2)+'\n')
 print('bounded navigation complete')
if __name__=='__main__':main()
