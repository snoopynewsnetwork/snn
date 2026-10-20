#!/usr/bin/env python3
"""Offline owned-path reproduction from retained original bytes; no Git/network/delegation."""
from pathlib import Path
import subprocess,sys,os,shutil
P=Path(__file__).resolve().parent

def main():
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
 # Imports need no retained bytecode/cache; only our own generated caches are removed.
 for p in P.rglob('__pycache__'):
  if p.is_dir():shutil.rmtree(p)
 for script in ['check_preflight.py','extract.py','enrich.py','registration.py','build.py','scoped_controls.py','synthetic.py','reconcile_peer.py','reconcile_ranking.py','reconcile_supplement.py','render_report.py','validate.py','asset_audit.py']:
  print('Reproduce',script,flush=True);r=subprocess.run([sys.executable,str(P/script)],env=env,capture_output=True,text=True)
  if r.returncode:print(r.stdout+r.stderr);raise SystemExit(r.returncode)
  print(r.stdout.splitlines()[-1] if r.stdout.splitlines() else 'OK',flush=True)
 subprocess.run([sys.executable,str(P/'validate.py'),'--check-assets'],env=env,check=True)
 print('Complete offline reproduction, validation and final asset seal passed.')
if __name__=='__main__':main()
