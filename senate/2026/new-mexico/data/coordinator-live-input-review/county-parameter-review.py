"""Bounded actual CLI parameter surface regressions; no producer writes/imports."""
from pathlib import Path
import json,hashlib,subprocess,sys
H=Path(__file__).resolve().parent;S=H.parents[1];C=S/'data/baselines/calculator.py'
def main():
 tests=[('uniform_nan_target',['--target-margin-pp','nan']),('uniform_infinite_target',['--target-margin-pp','inf']),('selected_nan_target',['--county','Bernalillo','--target-margin-pp','nan']),('selected_infinite_other_shift',['--county','Bernalillo','--others-shift-pp','inf']),('unknown_county',['--county','NO_SUCH_SOURCE_COUNTY'])]
 rows=[]
 for name,args in tests:
  r=subprocess.run([sys.executable,'-B',str(C),*args],capture_output=True);parsed=None;error=None
  try:parsed=json.loads(r.stdout,parse_constant=lambda s:(_ for _ in ()).throw(ValueError(s)))
  except Exception as exc:error=repr(exc)
  good=r.returncode==0 and not r.stderr and isinstance(parsed,dict) and str(parsed.get('status')).startswith('invalid')
  rows.append(dict(name=name,argv=args,exit_code=r.returncode,stdout=r.stdout.decode(),stderr=r.stderr.decode(),strict_JSON_error=error,status='pass'if good else'fail'))
 b=C.read_bytes();out=dict(status='actual_initial_parameter_surface_failures'if any(r['status']=='fail'for r in rows)else'pass_actual_CLI_parameters',calculator=dict(path=str(C.relative_to(S)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest()),cases=rows,failures=[r['name']for r in rows if r['status']=='fail'],scope='Same bounded finite/typed-target and named-source-input validation expectation; no new mathematical functionality or source changes.')
 p=H/'county-parameter-finding.json';p.write_text(json.dumps(out,indent=2)+'\n');print(dict(cases=len(rows),failures=out['failures'],finding_sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
if __name__=='__main__':main()
