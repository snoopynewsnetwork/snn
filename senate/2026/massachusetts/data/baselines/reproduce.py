#!/usr/bin/env python3
"""Offline replay; no manifest/witness resealing or shared writes."""
import json,os,subprocess,sys
from extract_originals import ROOT,sha
def main():
    manifest=ROOT/'asset-manifest.json';pins=json.loads(manifest.read_text())['owned_assets'] if manifest.exists() else []
    expected={ROOT.parent.parent/a['path']:a['sha256'] for a in pins}
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
    for script,args in [('extract_originals.py',[]),('replay_preflight.py',[]),('verify_chains.py',[]),('extract_controls.py',[]),('build_scenarios.py',[]),('test_calculators.py',[]),('audit_peer.py',['--frozen']),('audit_statistics.py',[]),('build_report.py',[]),('validate.py',[])]:
        r=subprocess.run([sys.executable,str(ROOT/script),*args],env=env,capture_output=True,text=True)
        if r.returncode:print(r.stdout,r.stderr);raise SystemExit(r.returncode)
        print(script,'PASS')
    for p,h in expected.items():assert sha(p.read_bytes())==h,('Reproduction changed a sealed artifact',str(p))
    print('Offline reconstruction matches every existing sealed output hash; immutable witnesses unchanged.')
if __name__=='__main__':main()
