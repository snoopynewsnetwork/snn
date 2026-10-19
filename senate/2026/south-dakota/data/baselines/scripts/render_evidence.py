#!/usr/bin/env python3
"""Bounded page derivatives for actual visual checks; originals retained losslessly once."""
import json,subprocess,tempfile
from pathlib import Path
from extract import SRC,NEWS,original
def main():
 mf={r['id']:r for r in json.loads((SRC/'shared-news-receipts.json').read_text())}
 for sid,page,name in [('sos-2024-general-county-aurora-clark',40,'visual-brookings-2024'),('sos-2024-county-marshall-ziebach',2,'visual-marshall-2024'),('sos-2020-general-canvass',3,'visual-senate-2020-column-order')]:
  with tempfile.NamedTemporaryFile(suffix='.pdf')as f:
   f.write(original(mf[sid],NEWS));f.flush()
   subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-scale-to','1400','-png','-singlefile',f.name,str(SRC/name)],check=True,capture_output=True)
if __name__=='__main__':main()
