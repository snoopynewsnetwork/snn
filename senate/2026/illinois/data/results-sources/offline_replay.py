"""Reconstruct every owned generated hierarchy/table/schema/sample twice-identically.
No networking, acquisition module or external producer code is executed.
"""
from common import *
import os,subprocess,sys

def pins():
 names=['source-schema-inventory.json','historical-parent-hierarchy.json.gz','investigations-priority.jsonl.gz','investigations-remainder.jsonl.gz','hierarchy-index.json','acquisition-summary.json','discovery-scope-findings.json','parent-findings.md','november-candidate-scope.json','previews/actual-visual-review.json']
 paths=[HERE/n for n in names]+[STATE/'data/official-results-sources.csv']+sorted((HERE/'parents').glob('*.json'))+sorted((HERE/'samples').glob('*.json.gz'))
 return {str(p.relative_to(STATE)):dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in paths}
def main():
 before=pins();runs=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
 for name in ['schema_samples.py','build.py','describe_sources.py']:
  r=subprocess.run([sys.executable,'-B',str(HERE/name)],env=env,capture_output=True,text=True)
  assert r.returncode==0,(name,r.stderr);runs.append(dict(script=name,exit=r.returncode,stdout=r.stdout,stderr=r.stderr))
 after=pins();assert before==after,sorted(k for k in set(before)|set(after) if before.get(k)!=after.get(k))
 write(HERE/'offline-replay.json',dict(status='pass',network_used=False,external_producer_code_executed=False,complete_generated_files=len(before),complete_generated_bytes=sum(v['bytes'] for v in before.values()),exact_generated_byte_pins=before,runs=runs,qualification='Owned deterministic reconstruction only; external complete-object validation is performed separately by validate.py. No current source admission or peer dependency.'))
 print('identical reconstructed files',len(before))
if __name__=='__main__':main()
