#!/usr/bin/env python3
"""Reproduce all visual QA previews from complete saved PDFs (Poppler)."""
import gzip,json,pathlib,subprocess
R=pathlib.Path(__file__).resolve().parent
spec=[('court-injunction-july16',54,['-r','110']),('court-appeal-oct2',8,['-r','110']),('johnson-notice',1,['-r','110']),('sos-av1',2,['-r','110']),('montgomery-generalnotice',1,['-r','110']),('pottawatomie-report',1,['-r','110']),('riley-2024-abstract',1,['-r','110']),('barton-2024',1,['-r','100']),('barton-2024',2,['-r','100']),('ellis-2024',1,['-r','100']),('ellis-2024',2,['-scale-to','1800']),('riley-canvass',1,['-scale-to','1800']),('saline-general-notice',1,['-scale-to','1800']),('franklin-primary',1,['-scale-to','2000']),('franklin-primary',2,['-scale-to','1800'])]
spec += [(sid,p,['-scale-to','1800']) for sid,pages in [('riley-generalnotice',range(1,5)),('saline-general-notice',range(2,5)),('montgomery-generalnotice',[2])] for p in pages]
for sid,page,opts in spec:
 m=json.loads((R/'raw'/f'{sid}.meta.json').read_text());p=R/'extracts'/f'{sid}.temporary.pdf';p.write_bytes(gzip.decompress((R/m['body_path']).read_bytes()))
 try:subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-singlefile',*opts,'-png',str(p),str(R/'extracts'/f'{sid}-page{page}')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 finally:p.unlink(missing_ok=True)
print('rendered',len(spec),'complete-original evidence pages')
