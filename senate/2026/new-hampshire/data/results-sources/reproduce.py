#!/usr/bin/env python3
"""Offline extraction/build/QA. No network, Git, agents or peer writes."""
import os,pathlib,subprocess,sys
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parent
env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
for script in ['extract_history.py','extract_documents.py','review_samples.py','audit_controls.py','check_peers.py','build_evidence.py','build_inventory.py','build_report.py','manifest.py','validate.py','manifest.py']:
    r=subprocess.run([sys.executable,str(ROOT/script)],env=env,capture_output=True,text=True)
    if r.returncode:
        print(r.stdout[-3000:]);print(r.stderr[-5000:]);raise SystemExit(r.returncode)
    if script=='extract_documents.py':print('PASS: complete retained PDF text/page extraction')
    else:print(r.stdout.strip())
from manifest import verify
verify()
print('PASS: complete offline reproduction and final exact owned/read-only asset verification')
