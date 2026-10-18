"""Offline deterministic rebuild of owned derivatives, report, checks and audit."""
from pathlib import Path
import subprocess,sys,os
BASE=Path(__file__).resolve().parent
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
for script in ['extract.py','evidence.py','calculate.py','live.py','legacy_extract.py','registration_controls.py','compare_legacy.py','legacy_calculate.py','compare_peer.py','compare_original_peer.py','report.py','validate.py']:
    args=[sys.executable,str(BASE/script)]
    if script=='live.py':args+=['--fixtures']
    if script=='validate.py':args+=['--refresh-manifest']
    result=subprocess.run(args,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    if result.returncode:sys.stdout.buffer.write(result.stdout);raise SystemExit(result.returncode)
    print(script,'PASS',flush=True)
