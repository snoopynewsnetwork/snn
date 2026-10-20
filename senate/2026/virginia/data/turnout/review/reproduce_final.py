#!/usr/bin/env python3
"""Offline isolated final renderer/metadata rebuild against immutable original semantic bodies."""
import json,os,shutil,subprocess,sys,tempfile,traceback,gzip
from pathlib import Path
from captured import T,S,H,sha,Capture

def run():
 old=Capture('turnout-original-first');cfg=json.loads((T/'review/peer-settings.json').read_text());finding=json.loads((H/'finding-finding.json').read_text())
 with tempfile.TemporaryDirectory(prefix='va-final-offline-',dir='/private/tmp') as td:
  state=Path(td)/'virginia';out=state/'data/turnout';out.mkdir(parents=True);(out/'source').symlink_to(T/'source',target_is_directory=True);(out/'review').mkdir()
  for n in ['extract_originals.py','source_controls.py','build_turnout.py','render_prose.py','apply_review_metadata.py']:shutil.copyfile(T/n,out/n)
  shutil.copyfile(T/'review/peer-settings.json',out/'review/peer-settings.json')
  guard=Path(td)/'guard.py';guard.write_text('''import sys,runpy\nfrom pathlib import Path\ndef audit(e,a):\n if e.startswith('socket.'):raise PermissionError('offline sockets denied')\n if e=='open' and any(x in str(a[0]) for x in ['/data/baselines/','/data/news/manifest.json','coordinator-primary-preflight','preflight_primary_sources']):raise PermissionError('mutable/helper/peer route denied')\nsys.addaudithook(audit)\nfor forbidden in ['/data/baselines/asset-manifest.json','/data/news/manifest.json','coordinator-primary-preflight','preflight_primary_sources']:\n try:open(forbidden);raise AssertionError('guard failed')\n except PermissionError:pass\nsys.path.insert(0,str(Path(sys.argv[1]).parent))\nrunpy.run_path(sys.argv[1],run_name='__main__')\n''')
  runs=[]
  for name in ['extract_originals.py','source_controls.py','build_turnout.py']:
   p=subprocess.run([sys.executable,'-B',str(guard),str(out/name)],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});runs.append({'script':name,'code':p.returncode,'stdout':p.stdout,'stderr':p.stderr});assert p.returncode==0,p.stderr
  checked=[]
  for e in old.index['bodies']:
   p=state/e['path']
   if not p.exists() or '/source/' in e['path'] or p.suffix=='.py':continue
   b=p.read_bytes();before=old.read(e['path'])
   if e['path']=='turnout.md':
    expected=before.decode().replace(finding['wrong_report_target'],finding['actual_retained_requested_final_URL'])
    for edit in cfg['report_replacements']:assert expected.count(edit['before'])==1;expected=expected.replace(edit['before'],edit['after'])
    assert b.decode()==expected
   elif p.name=='priority-set.json':
    a=json.loads(b);o=json.loads(before);assert a['peer']==cfg['peer_metadata'];a['peer']=o['peer'];assert a==o
   else:assert b==before,e['path']
   assert b==(S/e['path']).read_bytes(),('current final differs from isolated build',e['path']);checked.append({'path':e['path'],'bytes':len(b),'sha256':sha(b),'original_semantics_unchanged':True})
  return {'status':'pass','network_calls':0,'peer_numeric_input':False,'input_policy':'Only own frozen source receipts/entities for extraction/calculation; fixed captured-peer status is applied after numeric build. Mutable aggregate/helper/peer routes and sockets denied; guard denial fixtures executed.','runs':runs,'outputs':checked,'unchanged_native_csv_sha256':sha((state/'data/county-turnout.csv').read_bytes()),'allowed_report_changes':'confirmed URL correction and exact settings-listed captured-source-core status/history statements only','allowed_contract_changes':['peer'],'checker_sha256':sha(Path(__file__).read_bytes())}
if __name__=='__main__':
 try:
  r=run();(T/'review/final-reproduction.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':'pass','outputs':len(r['outputs']),'native_csv':r['unchanged_native_csv_sha256']}))
 except Exception:
  n=len(list(H.glob('final-reproduction-failure-*')));(H/f'final-reproduction-failure-{n}.txt').write_text(traceback.format_exc());(H/f'final-reproduction-failure-{n}.py.gz').write_bytes(gzip.compress(Path(__file__).read_bytes(),mtime=0));raise
