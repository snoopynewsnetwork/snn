#!/usr/bin/env python3
"""Bounded, immutable public acquisition. Originals retained once, decoded HTTP entity bytes.
Use: python3 acquire.py ID URL [--parent ID] [--note TEXT]. No refresh overwrites.
"""
import argparse,datetime,gzip,hashlib,json,pathlib,requests,sys
ROOT=pathlib.Path(__file__).resolve().parent
MAN=ROOT/'acquisition.json'
def sha(b): return hashlib.sha256(b).hexdigest()
def fetch(key,url,parent=None,note=''):
 records=json.loads(MAN.read_text()) if MAN.exists() else []
 existing=next((x for x in records if x['id']==key),None)
 if existing:
  if existing['requested_url']!=url: raise ValueError('ID already used for different URL')
  return existing,read(existing)
 rec={'id':key,'requested_url':url,'parent_capture_id':parent,'purpose':note,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'clock_policy':'Retrieval UTC; HTTP Date/Last-Modified and body dates preserved separately; none establishes election approval/cadence.'}
 try:
  r=requests.get(url,timeout=(20,90),headers={'User-Agent':'Kansas-election-geography-public-research/1.0','Accept-Encoding':'identity'})
  b=r.content
  rec.update(final_url=r.url,status=r.status_code,headers=dict(r.headers),redirects=[{'url':x.url,'status':x.status_code,'headers':dict(x.headers)} for x in r.history],original_bytes=len(b),original_sha256=sha(b),original_definition='Complete response entity after requests HTTP content decoding; not a packet/wire capture')
  prior=next((x for x in records if x.get('original_sha256')==sha(b)),None)
  if prior:
   rec['storage']=prior['storage'];rec['same_body_as']=prior['id']
  else:
   pdf=b.startswith(b'%PDF-')
   stored=b if pdf and len(b)<40000000 else gzip.compress(b,mtime=0)
   suffix='.pdf' if pdf and len(b)<40000000 else '.body.gz'
   paths=[]
   for n,pos in enumerate(range(0,len(stored),30000000)):
    part=stored[pos:pos+30000000]; name=key+suffix+(f'.part{n:03}' if len(stored)>=40000000 else '')
    p=ROOT/'raw'/name;p.write_bytes(part);paths.append({'path':p.relative_to(ROOT).as_posix(),'bytes':len(part),'sha256':sha(part)})
   rec['storage']={'encoding':'identity' if suffix=='.pdf' else 'gzip','ordered_parts':paths,'stored_bytes':len(stored),'stored_sha256':sha(stored)}
 except requests.RequestException as e:
  rec.update(error=repr(e),status=None,storage=None);b=b''
 records.append(rec);MAN.write_text(json.dumps(records,indent=2,ensure_ascii=False)+'\n')
 print(key,rec.get('status'),rec.get('original_bytes'),flush=True)
 return rec,b

def read(rec):
 s=rec.get('storage')
 if not s:return b''
 b=b''.join((ROOT/x['path']).read_bytes() for x in s['ordered_parts'])
 return gzip.decompress(b) if s['encoding']=='gzip' else b

def links(key):
 from html.parser import HTMLParser
 from urllib.parse import urljoin
 rec=next(x for x in json.loads(MAN.read_text()) if x['id']==key)
 class Parser(HTMLParser):
  def __init__(self): super().__init__();self.a=[];self.current=None;self.text=[];self.base=rec.get('final_url',rec['requested_url'])
  def handle_starttag(self,t,attrs):
   d=dict(attrs)
   if t=='base' and d.get('href'):self.base=urljoin(self.base,d['href'])
   if t=='a' and 'href' in d:self.current={'text':'','url':urljoin(self.base,d['href'])}
  def handle_data(self,d):
   self.text.append(d)
   if self.current is not None:self.current['text']+=d+' '
  def handle_endtag(self,t):
   if t=='a' and self.current is not None:self.current['text']=self.current['text'].strip();self.a.append(self.current);self.current=None
 parser=Parser();parser.feed(read(rec).decode('utf-8','replace'));a=parser.a
 (ROOT/'extracts'/f'{key}.links.json').write_text(json.dumps(a,indent=2,ensure_ascii=False)+'\n')
 (ROOT/'extracts'/f'{key}.txt').write_text(' '.join(parser.text))
 return a
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('id');p.add_argument('url');p.add_argument('--parent');p.add_argument('--note',default='');a=p.parse_args();fetch(a.id,a.url,a.parent,a.note)
