"""Rebuild only assigned outputs; no Git, network by default, or peer mutations."""
import argparse,os,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--acquire',action='store_true');args=ap.parse_args()
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
for script,extra in ([('acquire.py',[])] if args.acquire else [])+[('extract.py',[]),('reconcile_canvass.py',[]),('build.py',[]),('calculator.py',['--build']),('reconcile_peer.py',[]),('render_report.py',[]),('validate.py',[])]:
 r=subprocess.run([sys.executable,str(H/script)]+extra,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 print(script, 'PASS' if r.returncode==0 else 'FAILED',flush=True)
 if r.returncode:print(r.stdout);sys.exit(r.returncode)
