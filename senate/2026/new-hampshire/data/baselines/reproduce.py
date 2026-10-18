#!/usr/bin/env python3
"""Offline rebuild. Sources stay pinned; does not fetch or mutate shared paths."""
import os,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent
env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
for script in ['acquire.py','extract.py','build.py','scenarios.py','evidence.py']:
    subprocess.run([sys.executable,str(H/script)],env=env,check=True,stdout=subprocess.DEVNULL)
with (H/'synthetic-results.json').open('w') as f:
    subprocess.run([sys.executable,str(H/'calculator.py'),'--live',str(H/'synthetic-inputs.json')],env=env,check=True,stdout=f)
for script in ['report.py','validate.py']:
    subprocess.run([sys.executable,str(H/script)],env=env,check=True)
