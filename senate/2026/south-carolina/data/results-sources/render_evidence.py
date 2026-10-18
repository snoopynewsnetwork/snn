#!/usr/bin/env python3
"""Read-only source-PDF extraction/rendering; intermediate decoded PDFs are removed."""
import json,pathlib,subprocess
from acquire import ROOT,entity
Q=ROOT/'qa';Q.mkdir(exist_ok=True)
for ident in ['greenville-candidates','candidate-senate-print-search2','lexington-parent-child-99','grant-opinion','poll-manager-handbook','august-signed-canvass']:
 meta=json.loads((ROOT/'raw'/f'{ident}.meta.json').read_text());b=entity(meta);assert b.startswith(b'%PDF');p=Q/f'{ident}.pdf';p.write_bytes(b)
 txt=Q/f'{ident}.txt';subprocess.run(['pdftotext','-layout',str(p),str(txt)],check=True);pages=txt.read_text().split('\f')
 selected=[1] if ident!='grant-opinion' else [28,29]
 if ident=='poll-manager-handbook':
  selected=[i+1 for i,t in enumerate(pages) if 'extend' in t.lower() and ('court' in t.lower() or 'hours' in t.lower())][:2]
 for page in selected:
  subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-scale-to','1500','-png','-singlefile',str(p),str(Q/f'{ident}-p{page}')],check=True)
 print(ident,'selected',selected,'pages',len(pages)-1)
 p.unlink()
