#!/usr/bin/env python3
"""Offline derivatives only; report narrative and field notes are curated owned inputs."""
import os,subprocess,sys,pathlib
root=pathlib.Path(__file__).resolve().parent
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
for script in ['extract.py','augment.py','reconcile_history.py','build.py']:
 subprocess.run([sys.executable,str(root/script)],check=True,env=env)
print('Offline extracts reproduced. Run validate.py --record, manifest.py, then validate.py read-only to freeze.')
