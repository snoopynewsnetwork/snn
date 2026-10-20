#!/usr/bin/env python3
"""Network-free full rebuild and byte-preservation audit of the pre-reciprocal package."""
from pathlib import Path
import subprocess,json,hashlib,os,sys
D=Path(__file__).resolve().parent;ST=D.parent.parent
results=[]
for name in ['extract_sources.py','build_turnout.py','build_native.py','audit_native.py','compare_peer_core.py','build_package.py']:
 p=subprocess.run([sys.executable,str(D/name)],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
 results.append({'script':name,'exit_code':p.returncode});print(name,'PASS' if p.returncode==0 else 'FAIL',flush=True)
 if p.returncode:print(p.stdout,p.stderr);raise SystemExit(p.returncode)
prior=json.loads((D/'reciprocal-review/pre-reciprocal-capture.json').read_text())
allowed={'turnout.md','data/turnout/source/SCHEMA.md','data/turnout/build_package.py','data/turnout/validate_turnout.py','data/turnout/reproducibility.json','data/turnout/asset-manifest.json','data/turnout/priority-set.json','data/turnout/validation.json'}
changed=[];checked=0
for a in prior['records']:
 if a['path'] in allowed:continue
 b=(ST/a['path']).read_bytes();checked+=1
 if len(b)!=a['bytes'] or hashlib.sha256(b).hexdigest()!=a['sha256']:changed.append(a['path'])
result={'status':'pass' if not changed else 'fail','offline_builds':results,'prior_invariant_bodies_compared':checked,'unexpected_changed_prior_bodies':changed,'explicit_metadata_report_qa_change_allowlist':sorted(allowed),'raw_network_calls':0,'peer_input_scope':'immutable captured completed original-first core only','prior_witness_sha256':hashlib.sha256((D/'pre-peer-witness.json').read_bytes()).hexdigest()}
(D/'reproducibility.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
raise SystemExit(0 if not changed else 1)
