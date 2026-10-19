#!/usr/bin/env python3
"""Offline rebuild, with output restricted to the partisanship-owned tree."""
from pathlib import Path
import subprocess,sys,os
D=Path(__file__).resolve().parent
def main():
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
 for name in ['preflight_primary_sources.py','preflight_historical_controls.py','preflight_public_historical_exports.py','extract.py','augment_controls.py','calculate.py','presentation_evidence.py','audit_sources.py','compare_peer.py','render_report.py']:
  result=subprocess.run([sys.executable,str(D/name)],capture_output=True,check=True,env=env)
  (D/'source'/('replay-'+name+'.txt')).write_bytes(result.stdout+result.stderr)
  print(name,'PASS',flush=True)
 # All logs are closed before the manifest is built. No owned file changes after audit.
 subprocess.run([sys.executable,str(D/'validate.py')],check=True,env=env)
if __name__=='__main__':main()
