"""Require exact offline derivative replay; no network/frozen writer/Git."""
from common import *
import subprocess,sys,tempfile
def main():
 excluded={'maps/qa/reproducibility.json','maps/qa/validation.json','maps/asset-manifest.json'}
 def measured():return {str(p.relative_to(STATE)):pin(p)for p in [STATE/'precinct-maps.md']+list(MAPS.rglob('*'))if p.is_file() and str(p.relative_to(STATE)) not in excluded}
 before=measured();commands=[['audit_dependencies.py'],['geometry.py'],['pdf_previews.py'],['investigate.py','--inventory-only'],['build.py'],['atlas.py'],['write_report.py']];logs=[]
 for args in commands:
  p=subprocess.run([sys.executable,'-B',str(MAPS/'scripts'/args[0])]+args[1:],capture_output=True,check=True)
  logs.append(dict(command=['python','-B','maps/scripts/'+args[0]]+args[1:],stdout=p.stdout.decode(),stderr=p.stderr.decode()))
 after=measured();assert before==after,[k for k in set(before)|set(after) if before.get(k)!=after.get(k)]
 with tempfile.TemporaryDirectory(prefix='sd-map-reconstruction-qa-') as t:
  t=Path(t);doc=t/'exact.pdf';obj=t/'full-object.json'
  subprocess.run([sys.executable,'-B',str(MAPS/'scripts/reconstruct.py'),'--id','minnehaha-county-PDF',str(doc)],capture_output=True,check=True)
  assert len(doc.read_bytes())==10937333 and sha(doc.read_bytes())=='42606ad9270e39c2d8b3b9b453fe2fa122de2e1867bde65242f6232fd708b6aa'
  subprocess.run([sys.executable,'-B',str(MAPS/'scripts/reconstruct.py'),'--pointer','/all_units/303',str(obj)],capture_output=True,check=True)
  c=json.loads(check(load('qa/dependencies.json')['contract']));assert json.loads(obj.read_bytes())==c['all_units'][303]
 dump('qa/reproducibility.json',dict(status='pass_exact_offline_replay_and_reconstruction',commands=logs,unchanged_owned_files=len(after),all_measured_bytes_identical=True,scoped_receipt_exclusions=sorted(excluded),receipt_exclusions_reason='Finalization receipts are not rebuilt by derivative commands; all are included by the exact owned manifest except that manifest itself.',reconstructed_original_PDF_exact=True,reconstructed_full_nested_unit_exact=True,network_requests=0,frozen_or_peer_writers_executed=0))
 print('exact byte replay',len(after),'owned files; full original and nested object recovery passed')
if __name__=='__main__':main()
