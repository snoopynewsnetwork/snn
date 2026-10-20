"""Exact deterministic reconstruction under read/network/write guard, into temporary outputs."""
from pathlib import Path
import hashlib,json,os,sys,tempfile
from build import ROOT,STATE,build,load,dumps

def run(write=False):
 # Preload imports before applying guard; no network/subprocess calls are needed by build.
 raw_files={p.resolve() for p in (ROOT/'originals').rglob('*') if p.is_file()}
 allowed=raw_files|{(STATE/'data/turnout/priority-set.json').resolve()}
 proof=None
 with tempfile.TemporaryDirectory(prefix='arkansas-map-offline-') as temp:
  out=Path(temp)/'reconstructed';out.mkdir();outroot=out.resolve();events=[]
  def hook(event,args):
   if event.startswith(('socket.','urllib.','http.')) or event in ['subprocess.Popen','os.system','os.exec','os.posix_spawn']:raise PermissionError('network/process route denied')
   if event=='open':
    path=args[0]
    if isinstance(path,int):return
    p=Path(path).resolve();flags=args[2] if len(args)>2 and isinstance(args[2],int) else 0;mode=args[1] if len(args)>1 else None
    writing=bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)) or isinstance(mode,str) and any(c in mode for c in 'wax+')
    if writing:
     if not p.is_relative_to(outroot):raise PermissionError('write outside isolated reconstruction denied')
    elif p not in allowed and not p.is_relative_to(outroot):raise PermissionError('mutable aggregate/helper/peer/writer read denied: '+str(p))
   if event in ['os.listdir','os.scandir']:
    p=Path(args[0]).resolve()
    if not (p==ROOT/'originals' or p.is_relative_to(ROOT/'originals') or p.is_relative_to(outroot)):raise PermissionError('external directory discovery denied')
  sys.addaudithook(hook)
  paths=build(out);rows=[]
  for name in paths:
   b=(out/name).read_bytes();assert b==(ROOT/name).read_bytes() if (ROOT/name).resolve() in allowed else True
   # Owned expected derived reads are permitted below only after reconstruction guard removed.
   rows.append({'path':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
  # A Python audit hook cannot be removed; compare expected derived output through preloaded bytes.
  proof={'status':'reconstructed','isolated_generated_files':rows,'guards':{'network':False,'subprocess':False,'mutable_aggregate_helper_peer_writer_reads':False,'writes_outside_temporary_output':False},'qualification':'Exact expected output bytes are loaded before guard installation by parent verifier; see verify mode.'}
  # Returning inside TemporaryDirectory would trigger allowed deletion cleanup; removals are scoped.
 return proof
if __name__=='__main__':
 # Parent process loads exact output expectations, then child runs guarded reconstruction.
 # --child stdout contains only hashes; no source data or authority hash is persisted.
 if '--child' in sys.argv:print(json.dumps(run()));raise SystemExit
 import subprocess
 p=subprocess.run([sys.executable,'-B',str(Path(__file__).resolve()),'--child'],capture_output=True)
 if p.returncode:sys.stderr.buffer.write(p.stderr);raise SystemExit(p.returncode)
 proof=load(p.stdout)
 for row in proof['isolated_generated_files']:
  b=(ROOT/row['path']).read_bytes();assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'],row['path']
 proof['status']='pass_exact';proof['qualification']='All outputs reconstructed under deny-network/mutable-helper/peer/writer guard and matched exact retained bytes by independent parent verification. No producer module or mutable discovery supplies output.'
 if '--write' in sys.argv:(ROOT/'qa/offline-reconstruction.json').write_text(dumps(proof))
 else:assert load((ROOT/'qa/offline-reconstruction.json').read_bytes())==proof
 print('Exact guarded offline reconstruction passed:',len(proof['isolated_generated_files']),'files')
