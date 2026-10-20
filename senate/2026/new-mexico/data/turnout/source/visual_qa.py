#!/usr/bin/env python3
"""Render selected source table pages for human-readable verification; no PDF editing."""
from common import *
import tempfile,subprocess
Q=D/'source/qa';Q.mkdir(exist_ok=True)
def main():
 rows=[]
 for id,page in [('official-2024-file-2',1),('official-2020-file-1',1),('official-2022-file-1',1),('registration-9-state',1),('registration-9-county',57)]:
  target=Q/f'{id}-p{page}'
  with tempfile.NamedTemporaryFile(suffix='.pdf')as f:
   f.write(body(id));f.flush();subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-scale-to','2000','-png','-singlefile',f.name,str(target)],check=True)
  path=target.with_suffix('.png');rows.append(dict(source_id=id,original_sha256=sha(body(id)),page=page,render_path=str(path.relative_to(STATE)),sha256=sha(path.read_bytes()),bytes=path.stat().st_size))
 dump(Q/'renders.json',dict(renderer='Poppler pdftoppm -scale-to 2000 -png -singlefile',purpose='Source layout verification only, no geography/geometry approval',renders=rows))
if __name__=='__main__':main()
