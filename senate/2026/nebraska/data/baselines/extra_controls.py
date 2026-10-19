#!/usr/bin/env python3
"""Independently render/OCR the additional retained native scans; preserve entire source.
Selected page positions are reading-aid leads, not transcription authority. Every
numeric comparison is checked against original render/OCR, with exceptions explicit.
"""
import sys
sys.dont_write_bytecode=True
from extract import Originals,pdftext,sha,jsonl,dump,BASE,DATA
import concurrent.futures,gzip,json,re,subprocess,tempfile
CONFIG={'deuel':[1,2],'garfield':[1,6,13,14],'york':[1,9,18,25,32,41,50,57,63,69,75,82,89]}
def main():
 o=Originals();metadata=[]
 for c,kind in [('nemaha','official'),('clay','official'),('nance','official'),('gosper','official')]:
  sid=f'sos-2024-county-{c}-indexed-{kind}';raw=o.get(sid);text=pdftext(raw)
  jsonl(f'extracts/extra-{c}-pages.jsonl.gz',[dict(source_id=sid,page=i+1,text=p)for i,p in enumerate(text.split('\f')[:-1])])
  metadata.append(dict(source_id=sid,pages=len(text.split('\f'))-1,text_layer=True,scope='County summary contexts; not a native precinct partition'))
 for county,pp in CONFIG.items():
  sid=f'sos-2024-county-{county}-indexed-'+('unofficial'if county=='deuel'else'official');raw=o.get(sid)
  with tempfile.TemporaryDirectory(prefix='ne-baseline-scan-')as td:
   from pathlib import Path
   td=Path(td);pdf=td/'source.pdf';pdf.write_bytes(raw)
   info=subprocess.check_output(['pdfinfo',str(pdf)]).decode();pages=int(re.search(r'^Pages:\s+(\d+)',info,re.M)[1])
   def render(pn):
    dest=td/str(pn);subprocess.run(['pdftoppm','-f',str(pn),'-singlefile','-scale-to','3000','-png',str(pdf),str(dest)],check=True,capture_output=True)
    img=dest.with_suffix('.png')
    if county=='deuel':
     rotated=td/f'r{pn}.png';subprocess.run(['magick',str(img),'-rotate','90',str(rotated)],check=True,capture_output=True);img=rotated
    texts={str(psm):subprocess.check_output(['tesseract',str(img),'stdout','--psm',str(psm)],stderr=subprocess.DEVNULL).decode()for psm in [3,6]}
    # Reuse peer render only when our independent render has exactly the same PNG bytes.
    peer=DATA/'turnout/source'/f'{county}-page{pn}.png';z=img.read_bytes();exact=peer.exists()and sha(peer.read_bytes())==sha(z)
    path=peer if exact else BASE/'source/previews'/f'{county}-page{pn}.png'
    if not exact:path.write_bytes(z)
    return dict(source_id=sid,raw_sha256=sha(raw),page=pn,image_path=str(path.relative_to(DATA.parent)),image_sha256=sha(z),image_bytes=len(z),independent_render_matches_reused_image=exact,render='pdftoppm -scale-to 3000 PNG; Deuel rotated90 clockwise',OCR=texts,OCR_status='reading aid, not authoritative transcription')
   with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:rows=list(pool.map(render,pp))
   jsonl(f'extracts/extra-{county}-ocr.jsonl.gz',rows)
   metadata.append(dict(source_id=sid,pages=pages,text_layer=False,selected_pages=pp,selected_page_count=len(rows),raw_source_complete=True,scope='All selected presidential/two Senate contest pages; unrelated offices remain in complete original bytes. No HTML/PDF unit identity join.'))
   print(county,len(rows),flush=True)
 dump('extracts/extra-source-metadata.json',metadata);dump('source/extra-original-references.json',list(o.used.values()))
if __name__=='__main__':main()
