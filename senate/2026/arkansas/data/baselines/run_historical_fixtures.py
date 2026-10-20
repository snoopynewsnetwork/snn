#!/usr/bin/env python3
"""Saved actual CLI runs with complete historical native/county universes."""
import json,subprocess,sys,os
from pathlib import Path
P=Path(__file__).resolve().parent
runs={}
for label,scenario,target in [('primary-native','2024-xlsx-U.S. President-native-own-history',.01),('named-libertarian','2020-api-named-preferences-2024-volume-county',0)]:
 d=json.loads((P/'scenarios'/f'{scenario}.input.json').read_text());d['target_margin']=target;d['selected_unit']=d['units'][0]['key'];name='actual-history-'+label
 inp=P/'fixtures'/f'{name}.input.json';inp.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n');proc=subprocess.run([sys.executable,str(P/'calculator.py'),str(inp)],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
 (P/'fixtures'/f'{name}.stdout.json').write_text(proc.stdout);(P/'fixtures'/f'{name}.stderr.txt').write_text(proc.stderr);r=json.loads(proc.stdout);assert proc.returncode==0 and not proc.stderr and r['status']=='ok';assert len(r['units'])==len(d['units']);assert abs(r['uniform']['target']['objective_residual_net_votes'])<1e-6
 runs[label]={'scenario':scenario,'units':len(d['units']),'exit':proc.returncode,'stderr_bytes':len(proc.stderr),'target_margin':target,'selected_key':d['selected_unit'],'named_pair':r['named_pair'],'bounded_shift':r['uniform']['bounded_common_share_shift'],'final_pair_denominator':r['final_pair_denominator'],'final_all_candidate_denominator':r['final_all_candidate_denominator']}
(P/'fixtures/actual-history-receipts.json').write_text(json.dumps(runs,indent=2,allow_nan=False)+'\n')
print('actual historical CLI runs pass', {k:v['units'] for k,v in runs.items()})
