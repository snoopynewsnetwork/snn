#!/usr/bin/env python3
"""Offline rebuild. No downloads, Git, peer writes, or external authority mutations."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
D=Path(__file__).resolve().parent
os.environ['PYTHONDONTWRITEBYTECODE']='1'
steps=[('parse_sources.py',[]),('build.py',[]),('controls.py',[]),('calculate.py',[]),('live_remainder.py',['--examples']),('compare_peer.py',[]),('render_report.py',[])]
for script,args in steps:
 print('Reproducing',script,flush=True);subprocess.run([sys.executable,str(D/script),*args],check=True,env=os.environ)
pins=json.loads((D/'deterministic-data-pins.json').read_text())
for name,pin in pins.items():
 p=D/name;assert len(p.read_bytes())==pin['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==pin['sha256'],name
proof={'offline':True,'transformation_steps_passed':[{'script':s,'arguments':a,'exit_code':0} for s,a in steps],'frozen_data_pins_verified':True,'frozen_pin_path':'deterministic-data-pins.json','validation_path':'validation.json','note':'Transformation proof; final validator independently checks all originals/outputs and writes its result. No hash cycle with external acceptance or manifests.'}
(D/'reproduction-check.json').write_text(json.dumps(proof,indent=2)+'\n')
subprocess.run([sys.executable,str(D/'validate.py')],check=True,env=os.environ)
