#!/usr/bin/env python3
"""One-shot evidence capture, not a live collector. Complete decoded HTTP entities.
Usage acquire.py tasks.json; existing task receipts skipped. Python requests/bs4.
Shared immutable original hash reuse; never overwrites any shared source.
"""
import concurrent.futures, datetime, gzip, hashlib, json, pathlib, sys, requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
ROOT=pathlib.Path(__file__).resolve().parents[2]; OUT=ROOT/'data/results-sources'; SRC=OUT/'source'
def sha(b):return hashlib.sha256(b).hexdigest()
def readbody(r):
 p=ROOT/r['body_path'];b=p.read_bytes();return gzip.decompress(b) if p.suffix=='.gz' else b
def normalize_shared():
 idx={}
 for d in ['data/turnout/source','data/baselines/source']:
  for p in (ROOT/d).glob('*.receipt.json'):
   try:
    r=json.loads(p.read_text());sp=r.get('stored_path');q=p.parent.parent/sp if sp and sp.startswith('source/') else ROOT/sp if sp else None
    if q and q.exists():idx[r['raw_sha256']]={'body_path':str(q.relative_to(ROOT)),'receipt_path':str(p.relative_to(ROOT)),'raw_bytes':r['raw_bytes'],'raw_sha256':r['raw_sha256'],'stored_sha256':sha(q.read_bytes())}
   except (KeyError,TypeError):pass
 for r in json.loads((ROOT/'data/news/manifest.json').read_text()):
  q=ROOT/'data/news'/r['asset']
  if q.exists():idx[r['raw_sha256']]={'body_path':str(q.relative_to(ROOT)),'receipt_path':'data/news/manifest.json','raw_sha256':r['raw_sha256'],'raw_bytes':r['bytes'],'stored_sha256':sha(q.read_bytes())}
 for p in SRC.glob('*.receipt.json'):
  r=json.loads(p.read_text())
  if r.get('raw_sha256'):idx[r['raw_sha256']]={k:r[k] for k in ['body_path','raw_sha256','raw_bytes','stored_sha256']}|{'receipt_path':str(p.relative_to(ROOT))}
 return idx
SHARED=normalize_shared()
def capture(t):
 dst=SRC/(t['id']+'.receipt.json')
 if dst.exists():
  saved=json.loads(dst.read_text());assert saved['url']==t['url'], ('ID collision',t['id']);return saved
 started=datetime.datetime.now(datetime.timezone.utc).isoformat();headers={'User-Agent':'Mozilla/5.0 (compatible; public election research)','Accept-Encoding':'gzip, deflate'}
 meta=dict(t)|{'retrieved_utc':started,'request_headers':list(headers.items()),'source_clock':None,'source_clock_timezone':None,'source_clock_note':'HTTP Date/Last-Modified are transport metadata; publisher clock requires separate semantic review.'}
 try:
  r=requests.request(t.get('method','GET'),t['url'],data=t.get('form'),headers=headers,timeout=(15,55));b=r.content
  meta.update(request_url=r.request.url,request_method=r.request.method,request_body=r.request.body,final_url=r.url,status=r.status_code,headers=list(r.raw.headers.items()),redirects=[{'request_url':h.request.url,'url':h.url,'status':h.status_code,'headers':list(h.raw.headers.items())} for h in r.history],encoding=r.encoding,raw_bytes=len(b),raw_sha256=sha(b),entity_encoding='requests decoded Content-Encoding; exact full decoded response entity, not wire framing',complete=True)
  old=SHARED.get(sha(b))
  if old:meta.update(old,storage='immutable original reused by exact SHA256; no duplicate body')
  else:
   gz=gzip.compress(b,mtime=0);assert len(gz)<40000000
   q=SRC/(t['id']+'.body.gz');q.write_bytes(gz);meta.update(body_path=str(q.relative_to(ROOT)),stored_sha256=sha(gz),stored_bytes=len(gz),storage='lossless gzip; gzip.decompress restores complete entity')
  ct=r.headers.get('Content-Type','')
  if 'html' in ct or b.lstrip().startswith((b'<!DOCTYPE',b'<html')):
   soup=BeautifulSoup(b,'html.parser');base=urljoin(r.url,soup.base.get('href','')) if soup.base else r.url
   links=[]
   for pos,n in enumerate(soup.find_all(['a','iframe','script','base','form','link','object','embed'])):
    attr='href' if n.name in ['a','base','link'] else 'action' if n.name=='form' else 'data' if n.name=='object' else 'src'
    if n.has_attr(attr):links.append({'source_position_0based':pos,'tag':n.name,'attribute':attr,'raw':n[attr],'resolved_url':urljoin(base,n[attr]),'text':n.get_text(' ',strip=True),'attrs':dict(n.attrs)})
   (SRC/(t['id']+'.links.json')).write_text(json.dumps({'receipt':str(dst.relative_to(ROOT)),'base_url':base,'links':links},ensure_ascii=False,indent=2)+'\n')
 except Exception as e:meta.update(error=repr(e),status=None,complete=False)
 meta['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();dst.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');return meta
if __name__=='__main__':
 tasks=json.loads(pathlib.Path(sys.argv[1]).read_text());assert len({t['id'] for t in tasks})==len(tasks), 'Task IDs must be unique'
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
  for r in ex.map(capture,tasks):print(r['id'],r.get('status'),r.get('raw_bytes'),r.get('final_url',r['url']),flush=True)
