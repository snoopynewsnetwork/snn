#!/usr/bin/env python3
"""Offline rebuild from retained primary sources; no acquisition or peer mutations."""
import os,subprocess,sys
from pathlib import Path
D=Path(__file__).resolve().parent
def main():
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
 for args in [('extract.py',),('supplement.py',),('reconcile_peer.py',),('calculate.py','--build'),('live_remainder.py','--samples'),('render_report.py',),('validate.py',),('make_handoff.py',),('asset_manifest.py',),('validate.py','--verify-assets')]:
  subprocess.run([sys.executable,str(D/args[0]),*args[1:]],check=True,env=env)
if __name__=='__main__':main()
