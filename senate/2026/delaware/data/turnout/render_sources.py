#!/usr/bin/env python3
"""Reproduce PDF text/raster evidence with system Poppler; no persistent dependency cache."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import subprocess,gzip,json
D=Path(__file__).resolve().parent;S=D/'source';N=D.parent/'news'
def run(sid,stem,kind,pages=None):
 receipt=S/(sid+'.receipt.json')
 if receipt.exists():a=json.loads(receipt.read_text());b=gzip.decompress((S/a['body_path']).read_bytes())
 else:
  a=next(a for a in json.loads((D/'source/original-inputs.json').read_text()) if a['id']==sid);b=gzip.decompress((N/a['asset']).read_bytes())
 f=S/(stem+'.temporary.pdf');f.write_bytes(b)
 try:
  subprocess.run(['pdftotext','-layout',str(f),str(S/(stem+'.txt'))],check=True)
  if kind=='all':subprocess.run(['pdftoppm','-scale-to','1700','-png',str(f),str(S/stem)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  if pages:
   for page in pages:subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-scale-to','1700','-png',str(f),str(S/stem)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 finally:f.unlink()
if __name__=='__main__':
 for y,sid in [(2024,'sos-2024-valid-writeins'),(2022,'sos-observed-2022-writeins'),(2020,'sos-observed-2020-writeins')]:run(sid,f'writeins-{y}','all')
 run('district-structure','district-structure','select',[2,5,16])
 run('registration-information','registration-information','none')
 for y in [2024,2022]:run(f'registration-{y}-november-pdf',f'registration-{y}-november','none')
 if (S/'calendar-2026.receipt.json').exists():run('calendar-2026','calendar-2026','none')
