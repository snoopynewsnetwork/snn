#!/usr/bin/env python3
"""Bounded public GET capture. Original decoded entity bytes retained losslessly; no API guessing."""
import argparse,datetime,gzip,hashlib,json,pathlib,requests,sys,concurrent.futures
from html.parser import HTMLParser
from urllib.parse import urljoin
ROOT=pathlib.Path(__file__).resolve().parent
class Links(HTMLParser):
 def __init__(self,s):super().__init__(convert_charrefs=True);self.s=s;self.items=[];self.current=None;self.text=[];self.line=[0];self.line.extend(i+1 for i,c in enumerate(s) if c=='\n')
 def handle_starttag(self,tag,attrs):
  a=dict(attrs); attr='href' if tag in ('a','link') else 'src' if tag in ('script','iframe','img') else 'action' if tag=='form' else None
  if attr and attr in a:
   ln,col=self.getpos();self.items.append({'index':len(self.items),'tag':tag,'attrs':a,'line':ln,'column':col,'character_offset':self.line[ln-1]+col,'text':''})
   if tag=='a':self.current=self.items[-1]
 def handle_endtag(self,tag):
  if tag=='a':self.current=None
 def handle_data(self,d):
  self.text.append(d)
  if self.current is not None:self.current['text']+=d

def fetch(task):
 ident,url=task['id'],task['url'];out=ROOT/'raw'/f'{ident}.body.gz';meta=ROOT/'raw'/f'{ident}.meta.json'
 if meta.exists():return json.loads(meta.read_text())
 rec={'id':ident,'requested_url':url,'parent':task.get('parent'),'locator':task.get('locator'),'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'request_policy':'one public GET, timeout 35s, requests default redirect limit, no auth, no retry; Accept-Encoding identity; <=4 concurrent hosts/tasks','request_headers':{'User-Agent':'Mozilla/5.0 (public election source research)','Accept-Encoding':'identity'}}
 try:
  r=requests.get(url,headers=rec['request_headers'],timeout=35);b=r.content
  rec.update(status=r.status_code,final_url=r.url,headers=dict(r.headers),redirects=[{'url':h.url,'status':h.status_code,'headers':dict(h.headers)} for h in r.history],raw_bytes=len(b),raw_sha256=hashlib.sha256(b).hexdigest(),body_semantics='complete requests-decoded HTTP entity; wire transfer encoding not retained')
  packed=gzip.compress(b,mtime=0)
  if len(packed)>=40000000:raise ValueError('oversize compressed object; acquisition not stored')
  out.write_bytes(packed);rec.update(body=str(out.relative_to(ROOT)),stored_bytes=len(packed),stored_sha256=hashlib.sha256(packed).hexdigest(),magic=b[:20].hex())
  if 'html' in r.headers.get('Content-Type','') or b.lstrip().startswith((b'<!DOCTYPE',b'<html',b'<HTML')):
   s=b.decode(r.encoding or 'utf-8',errors='replace');p=Links(s);p.feed(s)
   for a in p.items:a['resolved_url']=urljoin(r.url,a['attrs'].get('href',a['attrs'].get('src',a['attrs'].get('action',''))))
   (ROOT/'raw'/f'{ident}.links.json').write_text(json.dumps(p.items,ensure_ascii=False,indent=2)+'\n');(ROOT/'raw'/f'{ident}.text.txt').write_text(''.join(p.text));rec['entity_check']='challenge' if ('validate.perfdrive.com' in r.url or 'made us think that you are a bot' in s.lower() or 'captcha-delivery.com' in r.url) else 'html_document'
  elif b.startswith(b'%PDF-'):rec['entity_check']='pdf_magic'
  elif b.startswith(b'PK'):rec['entity_check']='zip_magic'
  else:rec['entity_check']='inspect_schema'
 except Exception as e:rec['error']=repr(e)
 meta.write_text(json.dumps(rec,indent=2)+'\n');return rec
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('tasks');a=p.parse_args();tasks=json.loads(pathlib.Path(a.tasks).read_text())
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
  for r in ex.map(fetch,tasks):print(r['id'],r.get('status'),r.get('raw_bytes'),r.get('entity_check'),r.get('error',''))
