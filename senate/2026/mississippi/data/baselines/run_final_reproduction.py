"""Execute and freeze one complete offline source/calculator rebuild receipt."""
import datetime,gzip,json,os,subprocess,sys
from sources import OUT,BASE,save,sha

def pin(p):return dict(path=str(p.relative_to(BASE)),bytes=p.stat().st_size,sha256=sha(p.read_bytes()))
def main():
 folder=OUT/'source/reproduction-complete-original-v1';folder.mkdir(exist_ok=True);cp=folder/'completion.json';assert not cp.exists(),'Use a new immutable version for any subsequent run'
 repro=OUT/'reproduce.py';execution=folder/'execution-reproduce.py';execution.write_bytes(repro.read_bytes());start=datetime.datetime.now(datetime.timezone.utc).isoformat();log=folder/'reproduction.log'
 with log.open('wb') as f:r=subprocess.run([sys.executable,str(repro)],stdout=f,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
 if r.returncode:print('rebuild failed; exact log retained',log);sys.exit(r.returncode)
 v=json.loads((OUT/'validation.json').read_text());assert v['complete_owned_question'];pins=[]
 for name in ['validation.json','asset-manifest.json','printed-field-source-scope.json','source/reviewed-source-scope.json','native-2018-target-validation.json','native-2020-target-validation.json','native-final-validation.json']:
  p=OUT/name;raw=p.read_bytes();z=gzip.compress(raw,mtime=0);f=folder/(name.replace('/','--')+'.gz');assert len(z)<40000000;f.write_bytes(z);pins.append(dict(original_path=str(p.relative_to(BASE)),original_bytes=len(raw),original_sha256=sha(raw),stored_path=str(f.relative_to(BASE)),stored_bytes=len(z),stored_sha256=sha(z)))
 witnesses=[OUT/'source'/name/'snapshot.json' for name in ['native-2020-104views-v1','native-2018-164views-v1','native-allfield-82views','native-priority-v1','native-2018-peer-41views-v3','2024-all11-complete-peer-v1']]
 save(cp,dict(started_at_UTC=start,completed_at_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),exit_code=r.returncode,complete_owned_question=True,completed_main_checks=len(v['checks']),execution_reproducer=pin(execution),log=pin(log),input_witnesses=[pin(p) for p in witnesses],frozen_run_outputs=pins,qualification='Full offline rebuild from pinned original inputs and retained manual original-reading scripts: all1042020 publications/all1642018 stages/all84alternative2024 views, required located source controls and bounded scenarios. Frozen output manifest includes then-running log size; this completion log pin supersedes that dated log entry. Final outer validator audits current assets/receipt afresh. Source gaps/unprinted values, bounded historical independent-peer scope, future2026 evidence and unaccepted887proposal remain qualified. No online acquisition, Git, peer/shared writes or external publication.'))
 print('COMPLETE offline source rebuild',len(v['checks']),'checks',cp)
if __name__=='__main__':main()
