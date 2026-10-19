"""Audit archived execution inputs and outputs without running worker mutations."""
from pathlib import Path
import gzip,hashlib,json

DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/reproduction-104-118'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def checked(p):
 b=(ROOT/p['path']).read_bytes();assert len(b)==p['bytes']and sha(b)==p['sha256'];return b
def freeze(p):
 QA.mkdir(parents=True,exist_ok=True);q=QA/(p.name+'.gz')
 b=gzip.decompress(q.read_bytes())if q.exists()else p.read_bytes()
 if not q.exists():q.write_bytes(gzip.compress(b,mtime=0))
 return b,dict(original=dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b)),lossless_copy=pin(q))
def main():
 folder=DATA/'baselines/source/reproduction-1042020-118stage2018';rb,rpin=freeze(folder/'completion.json');assert sha(rb)=='d69b169599a0dc94b5422d26313ff4bcfce077f05a6856bcdf632127971367c7';r=json.loads(rb);sb,spin=freeze(folder/'start.json');start=json.loads(sb)
 assert r['exit_code']==0 and r['main_checks']==28 and r['complete_native_question']is False
 assert r['started_utc']==start['started_utc']and r['execution_reproducer']==start['execution_reproducer']
 script=checked(r['execution_reproducer']);log=checked(r['log']);final=json.loads(log.decode()[log.decode().rfind('\n{\n  "status":')+1:]);assert final['status']=='pass_county_and_calculator_checks_native_review_in_progress'and len(final['checks'])==28
 artifacts={}
 for p in r['frozen_run_artifacts']:
  z=checked(p['stored']);b=gzip.decompress(z);assert len(b)==p['original']['bytes']and sha(b)==p['original']['sha256'];artifacts[Path(p['original']['path']).name]=b
 assert len(artifacts)==11
 ledger=json.loads(artifacts['native-2018-original-readings.json']);assert len(ledger['sources'])==118
 validation=json.loads(artifacts['validation.json']);assert validation['status']==final['status']and list(validation['checks'])==final['checks']and validation['complete_native_question']is False
 assert json.loads(artifacts['native-2018-validation.json'])['counts']==ledger['counts']
 for p in r['native_input_witnesses']:checked(p)
 assert r['unallocated2018_source_disagreements'][0]['native_minus_printed_TOTAL']['Mike Espy']==-10 and r['unallocated2018_source_disagreements'][0]['unallocated']is True
 for p in r['unallocated2018_source_disagreements']:checked(p['evidence'])
 out=dict(status='pass_bounded_worker_reproduction118_receipt_archived_execution_and_outputs',receipt=rpin,start_receipt=spin,execution_reproducer=pin(ROOT/r['execution_reproducer']['path']),log=freeze(ROOT/r['log']['path'])[1],verified_frozen_run_artifacts=r['frozen_run_artifacts'],native_input_witnesses=r['native_input_witnesses'],recorded_main_checks=28,recorded_log_asset_count=final['assets'],known_unallocated_source_disagreements=r['unallocated2018_source_disagreements'],qualification='The coordinator verifies complete archived run bytes, all11 frozen outputs/implementation bodies, exact pre-launch execution script and input witness hashes. The worker reported exit0 at104 actual2020 publications plus118 distinct2018 stage grids. The manifest captured before final stdout is retained as an execution artifact; it is not claimed to hash the completed log or later126scope. No mutating worker rebuild is executed here, and full independent historical/method/current-geography/native887 gates remain open.',coordinator_executed_worker_reproduction=False,formal_native887_dispatch_accepted=False)
 p=DATA/'coordinator-reproduction-1042020-118stage2018-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
 print(json.dumps(pin(p)))
if __name__=='__main__':main()
