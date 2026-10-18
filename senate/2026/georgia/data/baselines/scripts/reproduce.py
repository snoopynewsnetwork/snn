#!/usr/bin/env python3
"""One offline command; no Git, network, shared writes or third-party dependencies."""
import os,pathlib,subprocess,sys
P=pathlib.Path(__file__).resolve().parent
for name in ['extract.py','calculate.py','methods.py','peer_check.py','render_report.py','schema.py','validate.py']:
 subprocess.run([sys.executable,'-S',str(P/name)],check=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
