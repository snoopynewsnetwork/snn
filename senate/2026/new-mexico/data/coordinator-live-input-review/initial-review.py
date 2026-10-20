"""Actual baseline CLI input audit, no producer imports or writes."""
from pathlib import Path
import json,subprocess,hashlib,copy,sys
S=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent;C=S/'data/baselines/calculator.py'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 base=dict(counted_A=40,counted_B=50,counted_other={'C':5},remaining=100,pair_participation=.8,remaining_A_pair_share=.6,remaining_other_mix={'C':1})
 cases=[]
 for name,key,value in [('boolean_count','counted_A',True),('boolean_target','target_pair_margin',True),('nonfinite_target','target_pair_margin',float('nan')),('nonfinite_other_mix','remaining_other_mix',{'C':float('nan')}),('boolean_other_mix','remaining_other_mix',{'C':True}),('text_other_mix','remaining_other_mix',{'C':'1'}),('null_other_object','counted_other',None),('list_other_object','counted_other',[5]),('text_remaining_with_unknown_preference','remaining','100'),('boolean_participation','pair_participation',True),('infinite_count','counted_A',float('inf')),('out_of_bounds_target','target_pair_margin',1.1)]:
  x=copy.deepcopy(base);x[key]=value
  if name=='text_remaining_with_unknown_preference':x['remaining_A_pair_share']=None
  cases.append((name,x,True))
 for name,x in [('ordinary',base),('unknown_remaining',dict(base,remaining=None)),('zero_pool',dict(base,remaining=0)),('explicit_preference_clipping',dict(base,remaining_A_pair_share=1.2))]:cases.append((name,x,False))
 out=[]
 for name,x,negative in cases:
  p=H/(name+'.input.json');p.write_text(json.dumps(x,allow_nan=True)+'\n');r=subprocess.run([sys.executable,'-B',str(C),'--live-json',str(p)],capture_output=True);parsed=None;error=None
  try:parsed=json.loads(r.stdout,parse_constant=lambda s:(_ for _ in()).throw(ValueError(s)))
  except Exception as exc:error=str(exc)
  valid=r.returncode==0 and not r.stderr and isinstance(parsed,dict)
  rejected=valid and isinstance(parsed.get('status'),str) and parsed['status'].startswith('invalid') and parsed.get('final') is None
  status='pass' if (rejected if negative else valid) else 'fail'
  row=dict(name=name,negative=negative,input_path=p.name,exit_code=r.returncode,stdout=r.stdout.decode('utf8','replace'),stderr=r.stderr.decode('utf8','replace'),strict_JSON_parse_error=error,status=status,observed_status=parsed.get('status') if isinstance(parsed,dict) else None)
  out.append(row)
 proof=dict(status='actual_initial_CLI_input_failures_identified' if any(r['status']=='fail' for r in out) else 'pass_actual_CLI_inputs',producer_calculator=dict(path=str(C.relative_to(S)),bytes=C.stat().st_size,sha256=sha(C.read_bytes())),cases=out,failures=[r['name'] for r in out if r['status']=='fail'],scope='Malformed/null/type/bool/nonfinite target/count/mix inputs must be structured rejections before arithmetic; legitimate unknowns remain unknown, explicit live preference clipping remains supported. All producer bytes unchanged.')
 (H/'initial-finding.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(cases=len(out),failures=proof['failures'],finding_sha256=sha((H/'initial-finding.json').read_bytes()))))
if __name__=='__main__':main()
