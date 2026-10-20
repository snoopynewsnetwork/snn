#!/usr/bin/env python3
"""Offline original-only deterministic rebuild. Never runs acquisition or peer scripts."""
from pathlib import Path
import os,json,subprocess,sys,hashlib,gzip
D=Path(__file__).resolve().parents[1];STATE=D.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def products():
 names=['native-baselines.csv','ballot-native.csv','exact-label-ballot-links.json','ballot-link-summary.json','discrepancy-ledger.json','scenario-settings.json','targets.csv','state-scenarios.json','all-source-orders.json','county-chains.json','native-hierarchy.json','current-general-publication.json','current-authority-evidence.json','finer-controls.json','calculator-tests.json','quarantine.json']
 return [STATE/'county-partisanship.md',STATE/'data/county-baselines.csv']+[D/n for n in names]+sorted((D/'extract').glob('*'))+sorted((D/'synthetic').glob('*'))
def main():
 ps=products();before={str(p.relative_to(STATE)):sha(p.read_bytes()) for p in ps};w=D/'source/pre-peer-witness.json';wsha=sha(w.read_bytes());env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'};steps=[]
 for script in ['extract_originals.py','extract_finer.py','extract_current.py','build.py','summarize_finer.py','quarantine.py','test_calculator.py','build_report.py']:
  p=subprocess.run([sys.executable,str(D/'scripts'/script)],env=env,capture_output=True,text=True);steps.append({'script':script,'exit':p.returncode,'stdout':p.stdout.strip(),'stderr':p.stderr.strip()})
  if p.returncode:
   (D/'reproduction.json').write_text(json.dumps({'pass':False,'steps':steps},indent=2)+'\n');raise SystemExit('Rebuild failed '+script)
 after={str(p.relative_to(STATE)):sha(p.read_bytes()) for p in products()};changed=[p for p,h in before.items() if after.get(p)!=h];added=sorted(set(after)-set(before));removed=sorted(set(before)-set(after));assert sha(w.read_bytes())==wsha,'immutable core witness changed'
 poppler=subprocess.run(['pdftotext','-v'],capture_output=True,text=True)
 result={'pass':not changed and not added and not removed,'scope':'eight scripts, original source bytes only; no acquisition/peer vote/rank/review numerical dependencies','steps':steps,'product_count':len(after),'changed':changed,'added':added,'removed':removed,'exact_products':after,'unchanged_core_witness_sha256':wsha,'python':sys.version.split()[0],'pdftotext':poppler.stderr.splitlines()[0] if poppler.stderr else poppler.stdout.strip(),'immutable_witnesses_not_rebuilt':True}
 (D/'reproduction.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps({'pass':result['pass'],'products':len(after),'changed':changed,'added':added,'removed':removed}))
 if not result['pass']:raise SystemExit(1)
if __name__=='__main__':main()
