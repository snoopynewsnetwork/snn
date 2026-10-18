#!/usr/bin/env python3
"""Run final offline extraction/calculation/report/QA; reject frozen data drift."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
D=Path(__file__).resolve().parent
def digest(p):
    b=p.read_bytes();return dict(sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def main():
    paths=[D.parent/'county-turnout.csv',D/'priority-set.json',D/'priority-freeze.json',D/'calculation.json',D/'sensitivity.json',D/'source/shared-source-references.json']+sorted((D/'extracts').glob('*'))
    paths=[p for p in paths if p.is_file()];before={str(p.relative_to(D.parent.parent)):digest(p) for p in paths}
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');steps=[]
    for script in ['build_turnout.py','verify_federal.py','build_report.py','compare_peer.py']:
        r=subprocess.run([sys.executable,str(D/script)],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True);steps.append(dict(script=script,returncode=r.returncode))
    after={str(p.relative_to(D.parent.parent)):digest(p) for p in paths};assert before==after,'Reproducible historical data changed'
    import build_turnout
    bad=json.loads((D/'priority-set.json').read_text());bad['coordinator_accepted']=True
    try:build_turnout.write_contract(bad)
    except AssertionError:pass
    else:raise AssertionError('Frozen priority drift must be refused')
    assert digest(D/'priority-set.json')==after['data/turnout/priority-set.json']
    record=dict(status='pass',offline=True,steps=steps,stable_generated_assets=before,frozen_drift_refused=True,coordinator_acceptance_path='data/coordinator-priority-acceptance.json',scope='Original-source extraction, calculations and report rebuilt; independent peer read-only; no network/Git')
    (D/'reproducibility.json').write_text(json.dumps(record,indent=2)+'\n')
    r=subprocess.run([sys.executable,str(D/'validate_turnout.py')],env=env,check=True)
    print('PASS offline rebuild; unchanged generated data and frozen contract; drift refused')
if __name__=='__main__':main()
