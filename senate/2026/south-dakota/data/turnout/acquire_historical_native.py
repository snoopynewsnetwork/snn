#!/usr/bin/env python3
"""Follow observed historic links and literal public Senate precinct controls.
No inferred IDs. GET and read-only export POST receipts retain exact request fields.
"""
from pathlib import Path
import datetime,gzip,hashlib,json,re
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urljoin
import requests
D=Path(__file__).resolve().parent;S=D/'source'
def sha(b):return hashlib.sha256(b).hexdigest()
class Form(HTMLParser):
 def __init__(self):super().__init__();self.inputs=[];self.action=None
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if tag=='form':self.action=d.get('action')
  if tag=='input':self.inputs.append(d)
def capture(key,r,extra):
 raw=r.content;z=gzip.compress(raw,mtime=0);assert len(z)<40000000;p=S/(key+'.body.gz');p.write_bytes(z)
 a={'id':key,'requested_url':r.request.url,'request_method':r.request.method,'final_url':r.url,'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'http_status':r.status_code,'headers':dict(r.headers),'redirects':[{'url':h.url,'status':h.status_code,'location':h.headers.get('Location')}for h in r.history],'raw_bytes':len(raw),'raw_sha256':sha(raw),'stored_bytes':len(z),'stored_sha256':sha(z),'asset':p.name,**extra};(S/(key+'.receipt.json')).write_text(json.dumps(a,indent=2)+'\n');print(key,r.status_code,len(raw),flush=True);return raw

def main():
 for year in [2022,2020]:
  key=f'public-native-senate-{year}'
  if (S/(key+'.receipt.json')).exists():continue
  parentkey=f'enr-{year}-observed-history-link';par=json.loads((S/(parentkey+'.receipt.json')).read_text());h=gzip.decompress((S/(parentkey+'.body.gz')).read_bytes()).decode()
  href=next(unescape(v)for v in re.findall(r'href="([^"]+)"',h)if 'resultsSW.aspx?type=SWR'in v)
  session=requests.Session();r=session.get(urljoin(par['final_url'],href),timeout=45);raw=capture(key+'-parent',r,{'parent_source_receipt':parentkey+'.receipt.json','observed_href':href});r.raise_for_status();s=raw.decode();f=Form();f.feed(s)
  assert f.action is not None
  title=re.search(r'<h1>\s*United States Senator\s*</h1>(.*?)(?:<h1>|$)',s,re.S);assert title
  node=Form();node.feed(title[1]);button=next(v for v in node.inputs if v.get('value')=='Precinct Level')
  fields={v['name']:v.get('value','')for v in f.inputs if v.get('type')=='hidden'and v.get('name')};assert fields['ctl00$hidElectionDate'].endswith(str(year))
  m=re.search(r"__doPostBack\('([^']+)','([^']*)'\)",button['onclick']);assert m;fields['__EVENTTARGET']=m[1];fields['__EVENTARGUMENT']=m[2]
  out=session.post(urljoin(r.url,f.action),data=fields,timeout=45);capture(key,out,{'parent_source_receipt':key+'-parent.receipt.json','observed_control_attributes':button,'request_form_fields':fields,'source_date_assertion':fields['ctl00$hidElectionDate'],'request_semantics':'Published read-only historical export control; no guessed contestID or reinterpretation of current setup.'})
if __name__=='__main__':main()
