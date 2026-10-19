#!/usr/bin/env python3
"""Offline ordered reproduction. No Git, shared writes, network or research workers."""
from pathlib import Path
import subprocess,sys
BASE=Path(__file__).resolve().parent
def main():
 for script in ['extract.py','scan_parse.py','universe.py','reconcile_peer.py','build.py','write_report.py','validate.py','audit_assets.py']:
  subprocess.run([sys.executable,'-B',str(BASE/script)],check=True)
 subprocess.run([sys.executable,'-B',str(BASE/'validate.py'),'--check-manifest'],check=True)
if __name__=='__main__':main()
