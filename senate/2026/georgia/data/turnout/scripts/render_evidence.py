#!/usr/bin/env python3
"""Reconstruct original PDFs from gzip for Poppler extraction/previews; remove temporary copies."""
import gzip,subprocess,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
for key,pages in [('court-disqualification',[1,5]),('calendar-2026-detail',[16,18]),('habersham-2024-summary',[1])]:
 p=R/'source'/(key+'.pdf');p.write_bytes(gzip.decompress((R/'source'/(key+'.body.gz')).read_bytes()))
 try:
  subprocess.run(['pdftotext','-layout',str(p),str(R/'source'/(key+'.txt'))],check=True)
  for page in pages:subprocess.run(['pdftoppm','-f',str(page),'-singlefile','-scale-to','1400','-png',str(p),str(R/'qa'/(key+'-p'+str(page)))],check=True)
 finally:p.unlink()

refs=json.loads((R/"source/source-chain-references.json").read_text())
m=next(m for m in refs if m["id"]=="fec-2024-presidential-original")
b=gzip.decompress((R.parent.parent/m["path"]).read_bytes());assert hashlib.sha256(b).hexdigest()==m["raw_sha256"]
p=R/"qa/fec-temp.pdf";p.write_bytes(b)
try:
 subprocess.run(["pdftotext","-layout",str(p),str(R/"source/fec-2024-presidential.txt")],check=True)
 for page in [2,3,4,5,6]:subprocess.run(["pdftoppm","-f",str(page),"-singlefile","-scale-to","1800","-png",str(p),str(R/"qa"/("fec-2024-p"+str(page)))],check=True)
finally:p.unlink()
(R/"qa/liberty-2024-summary-p1.jpg").write_bytes(gzip.decompress((R/"source/liberty-2024-summary-image-1.body.gz").read_bytes()))
