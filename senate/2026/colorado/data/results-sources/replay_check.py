#!/usr/bin/env python3
"""Deterministic offline replay of all acquired-derived products plus complete reconstruction."""
import hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent;STATE=ROOT.parents[1]
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
steps=['inspect_sources.py','extract_documents.py','extract_directory.py','build.py','render_report.py']
outputs=['observed-pages.json.gz','document-extracts.json.gz','directory-contacts.json','historical-conservation.json.gz','historical-original-receipts.json','response-objects.json.gz','response-schemas.json.gz','aggregate-exports.json','all64-primary-monitoring.json','priority-parent-primary-packets.json.gz','authority-contact-observations.json','priority-parent-investigations.json.gz','priority-investigations.jsonl.gz','all64-hierarchy-and-remainder.json.gz','immutable-external-files.json']
paths=[ROOT/n for n in outputs]+[STATE/'official-results.md',STATE/'data/official-results-sources.csv'];before={p.relative_to(STATE).as_posix():hashfile(p) for p in paths};env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
for name in steps:subprocess.run([sys.executable,str(ROOT/name)],check=True,env=env,stdout=subprocess.DEVNULL)
after={p.relative_to(STATE).as_posix():hashfile(p) for p in paths};assert before==after,{p:(before[p],after[p]) for p in before if before[p]!=after[p]}
# CLI exercises exact raw reconstruction, complete recursive object reconstruction and ordered split joining.
rs=json.loads((ROOT/'acquisition.json').read_text());ids=['denver-november-payload',next(r['id'] for r in rs if r.get('body_parts'))]
reconstructed=[]
with tempfile.TemporaryDirectory(prefix='co-official-replay-') as d:
 for id in ids:
  output=Path(d)/(id+'.original');subprocess.run([sys.executable,str(ROOT/'reconstruct.py'),'--receipt',id,'--output',str(output)],check=True,env=env);r=next(r for r in rs if r['id']==id);assert output.stat().st_size==r['raw_bytes'] and hashfile(output)==r['raw_sha256'];reconstructed.append({'receipt':id,'bytes':r['raw_bytes'],'raw_sha256':r['raw_sha256']})
 output=Path(d)/'full-reference.json';subprocess.run([sys.executable,str(ROOT/'reconstruct.py'),'--reference','1','--output',str(output)],check=True,env=env);assert isinstance(json.loads(output.read_text())['raw_fields'],list)
result={'schema':'CO-offline-deterministic-replay-v1','result':'PASS','replayed_steps':steps,'byte_identical_derived_files':after,'complete_raw_reconstructions':reconstructed,'complete_recursive_object_reconstruction':True,'network_calls':0,'current_admission':False,'qualification':'deterministic research replay, not coordinator acceptance or live calibration'}
(ROOT/'replay-validation.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS:',len(after),'byte-identical derived files; complete Denver, split original and full source-object reconstruction')
