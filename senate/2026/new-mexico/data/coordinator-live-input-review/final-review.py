"""Re-execute exact immutable failures against repaired actual CLI; no producer writes."""
from pathlib import Path
import subprocess,json,hashlib,sys
H=Path(__file__).resolve().parent;S=H.parents[1];C=S/'data/baselines/calculator.py'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))
def strict(b):return json.loads(b,parse_constant=lambda s:(_ for _ in()).throw(ValueError(s)))
def main():
 old=json.loads((H/'initial-finding.json').read_text());params=json.loads((H/'county-parameter-finding.json').read_text());rows=[]
 for r in old['cases']:
  command=[sys.executable,'-B',str(C),'--live-json',str(H/r['input_path'])];p=subprocess.run(command,capture_output=True);z=strict(p.stdout);assert p.returncode==0 and p.stderr==b''
  if r['negative']:assert z['status'].startswith('invalid') and z.get('final') is None,(r['name'],z)
  else:
   before=strict(r['stdout'])
   for key in ['status','final','pair_target','fixed_counted_votes','clipped_preference','remaining_pair_pool']:assert z.get(key)==before.get(key),(r['name'],key)
  rows.append(dict(name=r['name'],negative=r['negative'],argv=command[3:],exit_code=p.returncode,status=z['status'],strict_JSON_stdout=z,stderr_empty=True))
 for r in params['cases']:
  command=[sys.executable,'-B',str(C),*r['argv']];p=subprocess.run(command,capture_output=True);z=strict(p.stdout);assert p.returncode==0 and p.stderr==b'' and z['status'].startswith('invalid'),(r['name'],z)
  rows.append(dict(name=r['name'],negative=True,argv=r['argv'],exit_code=p.returncode,status=z['status'],strict_JSON_stdout=z,stderr_empty=True))
 assert len(rows)==21
 math=json.loads((S/'data/coordinator-first-pair-math-review.json').read_text())
 for r in math['output_pins']+math['source_inputs']:
  p=S/r['path'];assert pin(p)==r
 source=json.loads((S/'data/coordinator-baseline-source-review.json').read_text());m=json.loads((S/'data/baselines/asset-manifest.json').read_text());assert source['final_manifest']==pin(S/'data/baselines/asset-manifest.json')
 out=dict(status='pass_actual_repaired_CLI_regression_and_unchanged_historical_arithmetic',actual_cases=21,previously_failing_cases=16,all_exact_actual_failures_resolved=True,positive_controls_unchanged=True,cases=rows,calculator=pin(C),final_baseline_manifest=pin(S/'data/baselines/asset-manifest.json'),complete_baseline_source_review=pin(S/'data/coordinator-baseline-source-review.json'),initial_failure_evidence=[pin(H/'initial-finding.json'),pin(H/'county-parameter-finding.json')],independent_historical_event_math_review=pin(S/'data/coordinator-first-pair-math-review.json'),all_prior_historical_scenario_source_bytes_exact=True,no_producer_import_or_write=True,current_geography_returns_cadence_remainder_probability_approved=False)
 p=H/'review.json';p.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print(dict(cases=21,previous_failures_resolved=16,proof=pin(p)))
if __name__=='__main__':main()
