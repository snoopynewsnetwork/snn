"""Offline clean rebuild into a temporary state tree; compare exact generated bodies."""
import hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
STATE=ROOT.parent.parent
def main():
    copied=set()
    with tempfile.TemporaryDirectory(prefix='va-baselines-reproduce-') as td:
        dest=Path(td)/'virginia';b=dest/'data/baselines';b.mkdir(parents=True)
        def copy(p):
            rel=p.relative_to(STATE);out=dest/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,out);copied.add(str(rel))
        for n in ['extract.py','reconcile.py','controls.py','audit_orders.py','build.py','calculator.py','test_cli.py','render_report.py','source/input-pins.json','peer-capture.tar.gz']:copy(ROOT/n)
        for r in json.loads((ROOT/'source/input-pins.json').read_text())['sources']:
            copy(STATE/r['receipt_path'])
            for e in r['entities']:copy(STATE/e['path'])
        a=json.loads((ROOT/'source/additional-pins.json').read_text());copy(STATE/a['receipt_path']);copy(STATE/a['entity']['path'])
        log=[];env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
        for script in ['extract.py','reconcile.py','controls.py','audit_orders.py','build.py','test_cli.py','render_report.py']:
            p=subprocess.run([sys.executable,'-B',str(b/script)],capture_output=True,text=True,env=env);log.append({'script':script,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr});assert p.returncode==0 and not p.stderr,log[-1]
        results=[]
        for p in sorted(dest.rglob('*')):
            if p.is_file() and str(p.relative_to(dest)) not in copied:
                rel=str(p.relative_to(dest));original=STATE/rel;digest=hashlib.sha256(p.read_bytes()).hexdigest();expected=hashlib.sha256(original.read_bytes()).hexdigest() if original.exists() else None;results.append({'path':rel,'sha256':digest,'expected_sha256':expected,'identical':digest==expected})
        result={'status':'passed' if all(x['identical'] for x in results) else 'failed','generated_files':len(results),'results':results,'executions':log,'network_used':False,'originals_mutated':False,'temporary_tree_removed_on_exit':True}
    (ROOT/'reproduction.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'generated_files':len(results),'differences':[r['path'] for r in results if not r['identical']]}));assert result['status']=='passed'
if __name__=='__main__':main()
