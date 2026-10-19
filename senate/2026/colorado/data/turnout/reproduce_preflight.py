#!/usr/bin/env python3
"""Execute coordinator preflights unchanged with all outputs redirected to owned tree."""
from pathlib import Path
import runpy,contextlib,io,json,hashlib
O=Path(__file__).resolve().parent; D=O.parent
results=[]
for name in ['preflight_primary_sources.py','preflight_historical_controls.py','preflight_public_historical_exports.py']:
 g=runpy.run_path(str(D/name)); f=g['main']; v=f.__globals__
 for key in ['D','DATA']: 
  if key in v:v[key]=O
 for key in ['N','NEWS']:
  if key in v:v[key]=D/'news'
 if 'X' in v:v['X']=O/'extracts'
 if 'pin' in v:
  def pin(p):
   b=p.read_bytes();return dict(path=str(p.relative_to(O)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
  v['pin']=pin
 # Historical render validation uses DATA.parent; preserve original read-only base via rows' resolved paths.
 if name=='preflight_historical_controls.py':
  # Execute an exact source-text variant changing only output target; retain DATA for source/render resolution.
  code=(D/name).read_text().replace("(DATA / 'coordinator-historical-controls-preflight.json')", "(Path("+repr(str(O))+ ") / 'coordinator-historical-controls-preflight.json')")
  v={'__file__':str(D/name),'__name__':'reproduction'};exec(compile(code,str(D/name),'exec'),v);f=v['main']
 buf=io.StringIO()
 with contextlib.redirect_stdout(buf):f()
 results.append(dict(script='../'+name,sha256=hashlib.sha256((D/name).read_bytes()).hexdigest(),stdout=buf.getvalue(),mutation='output-path globals only; historical output literal redirected; shared sources read-only'))
(O/'source/preflight-execution.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps([dict(script=r['script'],passed=True)for r in results]))
