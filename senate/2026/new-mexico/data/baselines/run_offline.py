#!/usr/bin/env python3
"""Rebuild from exact retained originals only; no source producer imports or network."""
import os,subprocess,sys
from pathlib import Path
D=Path(__file__).resolve().parent
def main():
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
    for script in ['source/acquire.py','source/extract.py','controls.py','registration_native.py','build.py','supplement.py','compare_peer.py','render_report.py','input_regression.py','repair_check.py','validate.py','seal.py']:
        subprocess.run([sys.executable,str(D/script)],check=True,env=env)
    subprocess.run([sys.executable,str(D/'validate.py'),'--audit'],check=True,env=env)
if __name__=='__main__':main()
