#!/usr/bin/env python3
"""Offline only. Rebuild derived evidence and manifest from immutable saved originals."""
import os,pathlib,subprocess,sys
p=pathlib.Path(__file__).resolve().parent;env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
for script in ['verify_native_originals.py','build_maps.py','render_pdfs.py','catalog.py']:
 subprocess.run([sys.executable,str(p/script)],check=True,env=env)
# Bootstrap generated self-links explicitly as pending before substantive validation.
if not (p/'validation.json').exists():
 (p/'validation.json').write_text('{"status":"pending_offline_validation"}\n')
subprocess.run([sys.executable,str(p/'validate.py'),'--write-manifest'],check=True,env=env)
subprocess.run([sys.executable,str(p/'validate.py')],check=True,env=env)
subprocess.run([sys.executable,str(p/'validate.py'),'--write-manifest'],check=True,env=env)
subprocess.run([sys.executable,str(p/'validate.py'),'--check-manifest'],check=True,env=env)
