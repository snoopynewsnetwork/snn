"""Rebuild all deterministic map derivatives offline in isolation, compare exact bytes."""
from common import *
import tempfile,shutil,subprocess,os

def generated(m):
 rows=[]
 for directory in ['derived','previews','renders','parents']:
  rows += [p for p in (m/directory).rglob('*') if p.is_file()]
 rows += [m/p for p in ['index.html','priority.html','full.html','remainder.html','publications.html','qa/native-audit.json','qa/pdf-rendering.json','source/acquisition-index.json']]
 return sorted(rows)
def run():
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');expected=generated(M)+[S/'precinct-maps.md'];snap={str(p.relative_to(S)):(len(p.read_bytes()),sha(p.read_bytes())) for p in expected}
 with tempfile.TemporaryDirectory(prefix='ri-maps-reproduction-') as tmp:
  state=Path(tmp)/'state';maps=state/'maps';state.mkdir();shutil.copytree(M,maps)
  # The only external producer derivative consumed by map generation is this exact whole frozen contract.
  # Never copy the external authority; full authority replay is separately read-only at its original PATH.
  ext=state/'data/turnout/priority-set.json';ext.parent.mkdir(parents=True);ext.write_bytes((S/'data/turnout/priority-set.json').read_bytes())
  for p in generated(maps):p.unlink()
  logs=[]
  for script in ['audit_native.py','render_pdfs.py','build.py','make_report.py']:
   p=subprocess.run([os.sys.executable,'-B',str(maps/'scripts'/script)],cwd=state,env=env,capture_output=True)
   assert p.returncode==0,(script,p.stdout.decode(),p.stderr.decode());logs.append(dict(script=script,status=p.returncode))
  actual=generated(maps)+[state/'precinct-maps.md'];pins={str(p.relative_to(state)):(len(p.read_bytes()),sha(p.read_bytes())) for p in actual}
  assert pins==snap,[k for k in set(pins)|set(snap) if pins.get(k)!=snap.get(k)][:20]
  for p in maps.rglob('*'):assert p.name not in ['__pycache__','node_modules']
 return dict(status='pass',compared_full_generated_bodies=len(snap),compared_bytes=sum(v[0] for v in snap.values()),steps=logs,scope='Complete native attrs/coordinate audits and all previews; every PDF page/layout/metadata; entire source contract/observations and all static atlas/report bytes. Isolated temp tree removed. Original source authority never copied; no network/producer writer/peer discovery.',generated_body_pins=[dict(path=k,bytes=v[0],sha256=v[1]) for k,v in sorted(snap.items())])
if __name__=='__main__':
 import sys
 r=run()
 if '--write' in sys.argv:dump(M/'qa/reproduction.json',r)
 print(json.dumps({k:v for k,v in r.items() if k!='generated_body_pins'}))
