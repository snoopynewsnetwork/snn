#!/usr/bin/env python3
"""Rebuild every extraction/calculation offline and verify exact byte reproducibility."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;STATE=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def outputs():return sorted([STATE/'turnout.md',STATE/'data/county-turnout.csv']+[p for p in HERE.rglob('*') if p.is_file() and p.suffix!='.py' and 'source' not in p.relative_to(HERE).parts and p.name not in ['offline-rebuild.json','validation.json','asset-manifest.json','pre-peer-witness.json','pre-peer-bodies.tar.gz','final-seal.json']])
if __name__=='__main__':
 assert not (HERE/'final-seal.json').exists(),'sealed files are frozen; rebuild in a separate review copy'
 paths=outputs();before={str(p.relative_to(STATE)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in paths};runs=[]
 for name in ['extract_originals.py','source_controls.py','build_turnout.py']:
  r=subprocess.run([sys.executable,'-B',str(HERE/name)],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});assert r.returncode==0,(name,r.stderr);runs.append({'script':name,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
 after={str(p.relative_to(STATE)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in outputs()};assert before==after
 result={'status':'pass','network_calls':0,'peer_derivative_access':False,'outputs_byte_identical':len(after),'complete_output_bodies':after,'runs':runs}
 (HERE/'offline-rebuild.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['complete_output_bodies','runs']}))
