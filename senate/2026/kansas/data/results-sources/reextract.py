#!/usr/bin/env python3
"""Offline replay of complete saved HTML links/text and PDF text.
Requires requests+beautifulsoup4 outside repository and pdftotext. Never downloads.
"""
import gzip,json,pathlib,subprocess,urllib.parse
from bs4 import BeautifulSoup
R=pathlib.Path(__file__).resolve().parent
n=0
for mp in sorted((R/'raw').glob('*.meta.json')):
 m=json.loads(mp.read_text())
 if not m.get('body_path'):continue
 b=gzip.decompress((R/m['body_path']).read_bytes());sid=m['id'];ct=next((v for k,v in m.get('headers',{}).items() if k.lower()=='content-type'),'')
 if 'html' in ct.lower() or b.lstrip().lower().startswith((b'<!doctype html',b'<html')):
  s=BeautifulSoup(b,'html.parser');links=[]
  for i,a in enumerate(s.find_all(['a','iframe','script','link'])):
   attr='href' if a.name in ['a','link'] else 'src'
   if a.get(attr):links.append({'position':i,'tag':a.name,'label':a.get_text(' ',strip=True),'literal':a[attr],'url':urllib.parse.urljoin(m['final_url'],a[attr])})
  (R/'extracts'/f'{sid}.links.json').write_text(json.dumps(links,indent=2,ensure_ascii=False)+'\n')
  for x in s(['script','style']):x.decompose()
  (R/'extracts'/f'{sid}.txt').write_text(s.get_text('\n',strip=True));n+=1
 elif b.startswith(b'%PDF'):
  p=R/'extracts'/f'{sid}.temporary.pdf';p.write_bytes(b)
  try:subprocess.run(['pdftotext','-layout',str(p),str(R/'extracts'/f'{sid}.txt')],check=True);n+=1
  finally:p.unlink(missing_ok=True)
 elif b.startswith(b'\x89PNG\r\n\x1a\n'):
  (R/'extracts'/f'{sid}.png').write_bytes(b);n+=1
print('reextracted complete originals',n)
