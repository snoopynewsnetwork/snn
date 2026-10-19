#!/usr/bin/env python3
"""Bounded primary refresh. Historical originals are reused by exact hash, never copied.
Run --fetch to refresh; default verifies saved receipts and raw/stored bytes offline.
"""
import argparse,datetime,gzip,hashlib,html,json,re,urllib.parse
from pathlib import Path
BASE=Path(__file__).resolve().parent
def sha(b): return hashlib.sha256(b).hexdigest()
def main():
 import requests
 p=argparse.ArgumentParser();p.add_argument('--fetch',action='store_true');p.add_argument('--linked-documents',action='store_true');args=p.parse_args()
 target=BASE/'source/acquisition.json'
 history=json.loads(target.read_text())if target.exists()else[]
 if args.fetch or args.linked_documents:
  urls=[('elections-parent','https://sos.nebraska.gov/elections'),
   ('certification-parent','https://sos.nebraska.gov/secretary-state-certifies-ballot-2026-general-election'),
   ('previous-elections','https://sos.nebraska.gov/previous-elections'),
   ('canvass-rule','https://nebraskalegislature.gov/laws/statutes.php?statute=32-1038'),
   ('writein-rule','https://nebraskalegislature.gov/laws/statutes.php?statute=32-1005'),
   ('writein-filing-rule','https://nebraskalegislature.gov/laws/statutes.php?statute=32-615')]
  if args.linked_documents:
   urls=[]
   for key,file,pattern in [('current-final-list','elections-parent',r'Final_Statewide_General_Candidate_Filing_List'),('certification-notice','certification-parent',r'certifies%20ballot'),('historical-lists','previous-elections',r'(?:2024|2022|2020)/.*(?:Candidate|Candidates).*\.pdf')]:
    parent=next(a for a in reversed(history)if a['id']==file and a.get('status')==200)
    body=gzip.decompress((BASE/parent['asset']).read_bytes()).decode()
    for href in re.findall(r'href=[\'"]([^\'"]+)[\'"]',body):
     if re.search(pattern,href,re.I):urls.append((key+'-'+str(len(urls)),urllib.parse.urljoin('https://sos.nebraska.gov/',html.unescape(href))))
  out=history[:]
  shared=json.loads((BASE.parent/'news/manifest.json').read_text())
  for key,url in urls:
   at=datetime.datetime.now(datetime.timezone.utc).isoformat()
   try:
    r=requests.get(url,timeout=60);b=r.content;z=gzip.compress(b,mtime=0)
    match=next((a for a in shared if a.get('raw_sha256')==sha(b)),None)
    path=BASE/'source'/f'{key}-{sha(b)[:12]}.gz'
    if match:path=BASE.parent/'news'/match['asset'];z=path.read_bytes()
    else:path.write_bytes(z)
    out.append(dict(id=key,url=url,retrieved_at_utc=at,status=r.status_code,final_url=r.url,
     headers=dict(r.headers),redirects=[dict(url=h.url,status=h.status_code,headers=dict(h.headers)) for h in r.history],
     asset=str(path.relative_to(BASE))if path.is_relative_to(BASE)else'../news/'+path.name,raw_bytes=len(b),raw_sha256=sha(b),stored_bytes=len(z),stored_sha256=sha(z),reused_original_id=match['id']if match else None,
     source_clock_timezone=None,body_scope='complete HTTP entity; requests decoded transfer/content encoding'))
   except requests.RequestException as e: out.append(dict(id=key,url=url,retrieved_at_utc=at,error=str(e)))
  target.write_text(json.dumps(out,indent=2)+'\n')
 data=json.loads(target.read_text())
 for a in data:
  if 'asset' not in a:continue
  z=(BASE/a['asset']).read_bytes();b=gzip.decompress(z)
  assert sha(z)==a['stored_sha256'] and sha(b)==a['raw_sha256'] and len(b)==a['raw_bytes']
 print(json.dumps({'receipts':len(data),'statuses':{a['id']:a.get('status',a.get('error')) for a in data}}))
if __name__=='__main__':main()
