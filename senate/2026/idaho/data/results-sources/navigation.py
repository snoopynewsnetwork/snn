#!/usr/bin/env python3
"""HTML navigation extraction honors the document base; raw receipts stay immutable."""
from pathlib import Path
from urllib.parse import urljoin
import gzip,json
from bs4 import BeautifulSoup
D=Path(__file__).resolve().parent

def main():
 out=[]
 for p in sorted((D/'receipts').glob('*.json')):
  r=json.loads(p.read_bytes())
  if 'links' not in r:continue
  soup=BeautifulSoup(gzip.decompress((D/r['stored_path']).read_bytes()),'html.parser');b=soup.find('base',href=True);base=urljoin(r['final_url'],b['href']) if b else r['final_url']
  main=soup.find('main') or soup.find('article') or soup
  links=[dict(href=a['href'],text=a.get_text(' ',strip=True),url=urljoin(base,a['href'])) for a in soup.find_all('a',href=True)]
  out.append(dict(receipt=r['id'],document_base=base,literal_base_href=b['href'] if b else None,links=links,complete_main_text=main.get_text(' ',strip=True)))
 (D/'navigation.json.gz').write_bytes(gzip.compress((json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0));print('navigation',len(out))
if __name__=='__main__':main()
