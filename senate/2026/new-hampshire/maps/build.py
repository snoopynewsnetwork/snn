#!/usr/bin/env python3
"""Offline deterministic rebuild. No source fetches, peer writes or geometry repair."""
import os,subprocess,sys,pathlib
p=pathlib.Path(__file__).resolve().parent
env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
for name in ['audit_native.py','geometry.py','render_pdfs.py','build_index.py']:
 subprocess.run([sys.executable,str(p/name)],check=True,env=env)
print('Offline artifacts rebuilt; run validate.py then owned_manifest.py then validate.py --check-manifest.')
