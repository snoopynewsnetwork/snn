#!/usr/bin/env python3
"""Offline full text, anchor/constructor/config extraction using the standard library."""
import gzip,json,re,zlib
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
ROOT=Path(__file__).resolve().parent; STATE=ROOT.parents[1]
class Page(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True);self.links=[];self.text=[];self.scripts=[];self.nodes=[];self.active=None;self.script=None;self.style=False
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if tag=='style':self.style=True
  self.nodes.append({'tag':tag,'attributes':attrs})
  if tag in ['a','area','iframe','link','form'] and any(k in d for k in ['href','src','action']):
   self.links.append({'tag':tag,'attributes':attrs,'href':d.get('href',d.get('src',d.get('action'))),'text':d.get('alt','')});self.active=self.links[-1] if tag=='a' else None
  if tag=='script':self.script={'attributes':attrs,'body':''};self.scripts.append(self.script)
 def handle_endtag(self,tag):
  if tag=='a':self.active=None
  if tag=='script':self.script=None
  if tag=='style':self.style=False
 def handle_data(self,data):
  if self.script is not None:self.script['body']+=data
  elif not self.style:self.text.append(data)
  if self.active is not None:self.active['text']+=data
 def result(self,url):
  base=next((dict(n['attributes']).get('href') for n in self.nodes if n['tag']=='base' and dict(n['attributes']).get('href')),url)
  base=urljoin(url,base)
  for x in self.links:
   x['text']=' '.join(x['text'].split());x['resolved_url']=urljoin(base,(x['href'] or '').strip())
  return {'text':' '.join(' '.join(self.text).split()),'links':self.links,'scripts':self.scripts,'nodes':self.nodes}
def read_receipt(r):
 if r.get('body_parts'):return gzip.decompress(b''.join((STATE/x['path']).read_bytes() for x in r['body_parts']))
 if not r['body_path']:return b''
 return gzip.decompress((STATE/r['body_path']).read_bytes())
def inspect(r):
 raw=read_receipt(r)
 encoding=next((v for k,v in r['headers'].items() if k.lower()=='content-encoding'),'').lower()
 if encoding=='gzip':raw=gzip.decompress(raw)
 elif encoding=='deflate':raw=zlib.decompress(raw)
 t=raw.decode('utf-8',errors='replace');p=Page();p.feed(t);return p.result(r['final_url'])
def main():
 receipts=json.loads((ROOT/'acquisition.json').read_text());out={}
 for r in receipts:
  ct=str(r['headers'].get('Content-Type',r['headers'].get('content-type','')))
  if 'html' in ct:out[r['id']]=inspect(r)
 (ROOT/'observed-pages.json.gz').write_bytes(gzip.compress((json.dumps(out,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0))
 print('Complete inspected pages',len(out))
if __name__=='__main__':main()
