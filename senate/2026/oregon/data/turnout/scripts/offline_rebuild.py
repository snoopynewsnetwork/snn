#!/usr/bin/env python3
"""Rebuild the original-first turnout phase in an isolated temporary tree.
Frozen scripts/receipts are inputs, immutable primary responses reused read-only.
No peer script is executed. OCR/visual readings remain retained source locators;
this is not a fresh OCR or all-page raster audit. No network.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import os,tempfile,subprocess,json,hashlib,shutil,argparse
from reciprocal import O,T,S,sha,enc

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();O.verify();records=[]
 with tempfile.TemporaryDirectory(prefix='oregon-turnout-rebuild-')as temp:
  state=Path(temp)/'oregon';out=state/'data/turnout'
  for name in O.idx:
   p=state/name;p.parent.mkdir(parents=True,exist_ok=True)
   # Original response entities retained once, symlinked read-only and hash verified.
   r=O.idx[name]
   if 'immutable_original_path'in r:p.symlink_to((S/r['immutable_original_path']).resolve())
   else:p.write_bytes(O.read(name))
  for r in O.inv['external_immutable_originals']:
   p=state/r['path'];p.parent.mkdir(parents=True,exist_ok=True);p.symlink_to((S/r['path']).resolve())
  # Frozen full source receipts replace mutable news manifest discovery inside the isolated tree.
  (state/'data/news/manifest.json').write_bytes(O.read('data/turnout/source/shared-authority-chain-snapshot.json'))
  original_temp=Path('/tmp/oregon-turnout-originals');assert not original_temp.exists(),'avoid reusing an unrelated temporary directory';original_temp.mkdir()
  try:
   for name in ['extract_originals.py','extract_acquired.py','county_controls.py','participation_controls.py','nonadditive_presentations.py','native_extract.py','scope_fields.py','build.py','report.py']:
    p=subprocess.run([sys.executable,'-B',str(out/'scripts'/name)],env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True)
    records.append(dict(script=name,returncode=p.returncode,stdout=p.stdout.decode(errors='replace'),stderr=p.stderr.decode(errors='replace')))
    assert p.returncode==0,records[-1]
  finally:shutil.rmtree(original_temp)
  changed=[];checked=[]
  for name,r in O.idx.items():
   p=state/name;b=p.read_bytes()
   if (len(b),sha(b))!=(r['bytes'],r['sha256']):changed.append(dict(path=name,before_sha256=r['sha256'],rebuilt_sha256=sha(b),before_bytes=r['bytes'],rebuilt_bytes=len(b)))
   checked.append(dict(path=name,bytes=len(b),sha256=sha(b)))
  assert not changed,changed
  assert not list(state.rglob('__pycache__'))
  result=dict(status='pass',phase='original-first complete isolated offline rebuild',scripts=records,reconstructed_bodies=len(checked),all_original_first_bodies_identical=True,checked=checked,qualification='Nine original frozen turnout scripts executed without peer code or network. Retained OCR/visual locators reused; no new OCR/all-page raster reading. Current reciprocal report/status are a later layer, not part of the original-first body equality claim.')
  b=enc(result);p=T/'source/offline-rebuild.json'
  if args.write:p.write_bytes(b)
  else:
   saved=json.loads(p.read_bytes());assert saved['checked']==checked and saved['all_original_first_bodies_identical']and len(saved['scripts'])==9
   assert all(r['returncode']==0 for r in records)
  print(json.dumps(dict(status='pass',scripts=len(records),byte_exact_original_first_bodies=len(checked),retained_transcript_sha256=sha(p.read_bytes()),mode='write'if args.write else 'read-only proof validation')))
if __name__=='__main__':main()
