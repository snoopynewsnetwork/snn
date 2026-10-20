#!/usr/bin/env python3
"""Replay the captured original-only builder in an isolated temporary tree.

No mutable producer or peer derivative is an input. Audit hooks deny network,
non-pdftotext child processes and writes outside the isolated tree. Every
generated body must equal its whole captured old body, not a current file.
"""
import argparse,hashlib,json,os,pathlib,subprocess,sys,tempfile
from reciprocal import Capture,REPO,P,S,H,sha
def main(write=True):
    cap=Capture('own');cap.audit();inputs=[];proof=dict(schema='arkansas-isolated-original-replay-v1',status='running',builder_sha256=sha(cap.own('build.py')),inputs=[],outputs=[],network_allowed=False,producer_writes_allowed=False,peer_derivatives_allowed=False)
    with tempfile.TemporaryDirectory(prefix='arkansas-turnout-original-replay-') as tmp:
        root=pathlib.Path(tmp);state=root/'senate/2026/arkansas';turnout=state/'data/turnout'
        for name in ['source/acquired','extracted','orders']:(turnout/name).mkdir(parents=True,exist_ok=True)
        (turnout/'build.py').write_bytes(cap.own('build.py'))
        allow=[]
        def link(relative,actual,expected):
            actual=actual.resolve();assert sha(actual.read_bytes())==expected
            target=root/relative;target.parent.mkdir(parents=True,exist_ok=True)
            if not target.exists():target.symlink_to(actual)
            assert sha(target.read_bytes())==expected;allow.append(str(actual))
        for path in cap.records:
            if path=='data/turnout/source/original-pins.json' or (path.startswith('data/turnout/source/') and path.endswith('.receipt.json')):
                body=cap.read(path);target=state/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body);inputs.append(dict(path=path,sha256=sha(body),bytes=len(body),role='whole captured immutable original receipt/pins'))
                if path.endswith('.receipt.json'):
                    r=json.loads(body)
                    if r.get('shared_original_path'):
                        rel=r['shared_original_path'];actual=REPO/rel
                    else:
                        rel=str(pathlib.PurePosixPath('senate/2026/arkansas')/pathlib.PurePosixPath(path).parent/r['asset']);actual=REPO/rel
                    link(rel,actual,r['stored_sha256'])
        # Explicit pinned original read allowlist; all old generated outputs start absent.
        before={str(f.relative_to(state)) for f in state.rglob('*') if f.is_file()}
        (root/'tmp').mkdir();runner=root/'runner.py'
        runner.write_text('''import sys,os,pathlib,runpy,json
root=pathlib.Path(sys.argv[1]).resolve();allowed=set(json.loads(sys.argv[2]));base=pathlib.Path(sys.base_prefix).resolve();children=[]
def audit(event,args):
    if event.startswith('socket.'):raise RuntimeError('DENIED network '+event)
    if event=='subprocess.Popen':
        if pathlib.Path(os.fsdecode(args[0])).name!='pdftotext':raise RuntimeError('DENIED non-pdftotext child')
        children.append(list(map(str,args[1])))
    if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)):
        path=pathlib.Path(os.fsdecode(args[0])).resolve();mode=args[1];flags=args[2]
        writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)))
        inside=path.is_relative_to(root)
        if writing and not inside:raise RuntimeError('DENIED producer/outside write '+str(path))
        if not writing and not (inside or str(path) in allowed or path.is_relative_to(base) or str(path).startswith('/opt/homebrew/')):raise RuntimeError('DENIED mutable/non-original read '+str(path))
sys.addaudithook(audit)
runpy.run_path(str(root/'senate/2026/arkansas/data/turnout/build.py'),run_name='__main__')
print('AUDIT_CHILDREN='+json.dumps(children))
''')
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',TMPDIR=str(root/'tmp'));env.pop('PYTHONPATH',None)
        proc=subprocess.run([sys.executable,str(runner),str(root),json.dumps(sorted(set(allow)))],capture_output=True,env=env,cwd=root)
        proof.update(inputs=inputs,original_body_references=len(set(allow)),returncode=proc.returncode,stdout=proc.stdout.decode(errors='replace'),stderr=proc.stderr.decode(errors='replace'),audit_runner=runner.read_text())
        if proc.returncode:
            proof['status']='fail'
            if write:(P/'isolated-replay.json').write_text(json.dumps(proof,indent=2)+'\n')
            raise RuntimeError(proc.stderr.decode())
        outputs=sorted(f for f in state.rglob('*') if f.is_file() and str(f.relative_to(state)) not in before)
        for f in outputs:
            path=str(f.relative_to(state));b=f.read_bytes();expected=cap.read(path);assert b==expected,(path,sha(b),sha(expected))
            proof['outputs'].append(dict(path=path,sha256=sha(b),bytes=len(b),equals_whole_captured_old_body=True))
        assert len(proof['outputs'])>=40
        proof['status']='pass';proof['all_generated_outputs_equal_captured_original_scope']=True
    if write:(P/'isolated-replay.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:v for k,v in proof.items() if k not in ['inputs','outputs','audit_runner','stdout']},indent=2));print('exact rebuilt bodies',len(proof['outputs']))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args();main(not args.check)
