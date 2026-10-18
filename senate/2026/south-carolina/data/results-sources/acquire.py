#!/usr/bin/env python3
"""Bounded, public read-only observations. Retains complete HTTP entity bytes losslessly.
No implicit crawler: every URL supplied here or in explicit input has an authority/asset parent.
"""
import argparse,concurrent.futures,datetime,gzip,hashlib,json,pathlib,re,requests
from html.parser import HTMLParser
from urllib.parse import urljoin
ROOT=pathlib.Path(__file__).resolve().parent
CAP=39_000_000

def fetch(item):
 ident,url,parent=item
 existing=ROOT/"raw"/f"{ident}.meta.json"
 if existing.exists():return json.loads(existing.read_text())
 meta={'id':ident,'requested_url':url,'parent':parent,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'request_headers':{'User-Agent':'Mozilla/5.0 (public election research)','Accept-Encoding':'identity'},'method':'GET','cap':CAP}
 try:
  r=requests.get(url,headers=meta['request_headers'],timeout=(15,45),stream=True)
  meta.update(final_url=r.url,http_status=r.status_code,headers=dict(r.headers),redirects=[{'url':x.url,'status':x.status_code,'headers':dict(x.headers)} for x in r.history])
  b=r.raw.read(CAP+1,decode_content=False)
  meta['complete']=len(b)<=CAP
  if not meta['complete']: raise ValueError('entity exceeds cap; partial bytes deliberately not retained')
  digest=hashlib.sha256(b).hexdigest();p=ROOT/'raw'/f'{ident}.body.gz'
  for previous in (ROOT/'raw').glob('*.meta.json'):
   old=json.loads(previous.read_text())
   if old.get('original_sha256')==digest and old.get('entity_encoding','identity')==r.headers.get('Content-Encoding','identity'):
    p=ROOT/old['body_path'];meta['reused_identical_entity_from']=old['id'];break
  if not p.exists():p.write_bytes(gzip.compress(b,mtime=0))
  meta.update(body_path=str(p.relative_to(ROOT)),original_bytes=len(b),original_sha256=hashlib.sha256(b).hexdigest(),stored_bytes=p.stat().st_size,stored_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),stored_encoding='gzip',entity_encoding=r.headers.get('Content-Encoding','identity'))
 except Exception as e: meta['error']=repr(e)
 (ROOT/'raw'/f'{ident}.meta.json').write_text(json.dumps(meta,indent=2)+'\n')
 return meta

def entity(meta):
 b=gzip.decompress((ROOT/meta['body_path']).read_bytes())
 if meta.get('entity_encoding')=='gzip': b=gzip.decompress(b)
 elif meta.get('entity_encoding')=='br':
  import brotli
  b=brotli.decompress(b)
 return b

class Page(HTMLParser):
 def __init__(self,url): super().__init__();self.url=url;self.links=[];self.assets=[];self.text=[];self.anchor=None;self.skip=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag in ["script","style"]:self.skip+=1
  if tag=='a' and a.get('href'):
   self.anchor={'url':urljoin(self.url,a['href']),'label':'','raw_href':a['href']};self.links.append(self.anchor)
  if tag in ['script','iframe'] and a.get('src'):self.assets.append({'kind':tag,'url':urljoin(self.url,a['src'])})
 def handle_endtag(self,tag):
  if tag in ['script','style']:self.skip=max(0,self.skip-1)
  if tag=='a':self.anchor=None
 def handle_data(self,data):
  if self.skip:return
  self.text.append(data)
  if self.anchor is not None:self.anchor['label']+=data

def inspect(meta):
 if 'body_path' not in meta:return {}
 b=entity(meta);s=Page(meta['final_url']);s.feed(b.decode('utf-8','replace'));return {'id':meta['id'],'url':meta['final_url'],'text':' '.join(' '.join(s.text).split()),'links':s.links,'assets':s.assets}

def batch(items):
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
  out=list(ex.map(fetch,items))
 for m in out:
  if m.get('body_path') and ('html' in m.get('headers',{}).get('Content-Type','').lower() or 'text' in m.get('headers',{}).get('Content-Type','').lower()):
   (ROOT/'raw'/f"{m['id']}.inspect.json").write_text(json.dumps(inspect(m),indent=2)+'\n')
 return out
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('input');args=a.parse_args();out=batch(json.loads(pathlib.Path(args.input).read_text()));print(json.dumps([{k:m.get(k) for k in ['id','http_status','original_bytes','error']} for m in out],indent=2))
