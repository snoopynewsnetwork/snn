#!/usr/bin/env python3
"""Seal complete owned assets; manifest excludes ONLY itself. No recursive hashes.
Run after final edits/QA. Does not refresh source data, touch peers or use Git.
"""
import sys
sys.dont_write_bytecode=True
import json,subprocess
from acquire import ROOT,sha
STATE=ROOT.parent;MF=ROOT/'asset-manifest.json'
def manifest():
 files=sorted([p for p in ROOT.rglob('*') if p.is_file() and p!=MF]+[STATE/'precinct-maps.md'])
 assets=[]
 for p in files:
  b=p.read_bytes();assert len(b)<40000000,p
  assets.append({'path':str(p.relative_to(STATE)),'bytes':len(b),'sha256':sha(b)})
 MF.write_text(json.dumps({'scope':'Every owned maps/** object and precinct-maps.md; one self-exclusion only. Read-only input pins are references, not duplicate originals.','self_exclusion':'maps/asset-manifest.json','asset_count':len(assets),'assets':assets},indent=2)+'\n')
# Bootstrap artifact existence for link checks; replaced before final sealing.
if not (ROOT/'validation.json').exists():(ROOT/'validation.json').write_text('{}\n')
manifest()
subprocess.run([sys.executable,str(ROOT/'scripts/validate.py'),'--write'],check=True)
manifest()
subprocess.run([sys.executable,str(ROOT/'scripts/validate.py')],check=True)
print('FROZEN',MF,sha(MF.read_bytes()))
