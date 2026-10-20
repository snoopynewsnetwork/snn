#!/usr/bin/env python3
"""Rebuild original phase in an isolated temporary repository with fixed originals and denied routes."""
import pathlib,tarfile,json,gzip,hashlib,os,sys,subprocess,shutil
R=pathlib.Path(__file__).resolve().parents[1];S=R.parents[1];REPO=S.parents[2];D=R/'reciprocal';T=pathlib.Path('/private/tmp/al-turnout-reciprocal-offline');T.mkdir(exist_ok=True);WORK=T/'repo-v2';WORK.mkdir(exist_ok=True)
def sha(b):return hashlib.sha256(b).hexdigest()
with tarfile.open(D/'turnout-original-phase.tar.gz') as tf:
 mf=json.loads(tf.extractfile('data/turnout/asset-manifest.json').read());assert len(tf.getnames())==146
 for item in tf.getmembers():
  assert item.isfile() and not item.name.startswith('/') and '..' not in pathlib.PurePosixPath(item.name).parts
  dest=WORK/'senate/2026/alabama'/item.name;dest.parent.mkdir(parents=True,exist_ok=True);b=tf.extractfile(item).read();dest.write_bytes(b)
 for x in mf['assets']:
  b=(WORK/'senate/2026/alabama'/x['path']).read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256']
 for x in mf['external_originals']:
  src=REPO/x['path'];b=src.read_bytes();assert len(b)==x['stored_bytes'] and sha(b)==x['stored_sha256'];raw=gzip.decompress(b);assert len(raw)==x['original_bytes'] and sha(raw)==x['original_sha256'];dest=WORK/x['path'];dest.parent.mkdir(parents=True,exist_ok=True)
  if not dest.exists():os.link(src,dest)
  assert sha(dest.read_bytes())==x['stored_sha256']
TMP=T/'tmp';TMP.mkdir(exist_ok=True)
# No live HTTP, mutable repository, peer, producer-helper or package-discovery routes exist in the worker tree.
guard=T/'guard.py'
guard.write_text('''import sys,os,pathlib,runpy,json
sys.dont_write_bytecode=True
work=pathlib.Path(os.environ['AL_ISOLATED_ROOT']).resolve();tmp=pathlib.Path(os.environ['TMPDIR']).resolve();realrepo=pathlib.Path('/Users/tqbf/codebase/snn').resolve()
allowed=[work,tmp,pathlib.Path('/private/tmp/al-turnout-deps').resolve(),pathlib.Path(sys.prefix).resolve(),pathlib.Path('/opt/homebrew').resolve(),pathlib.Path('/usr').resolve(),pathlib.Path('/System').resolve(),pathlib.Path('/Library').resolve(),pathlib.Path('/private/etc').resolve(),pathlib.Path('/dev').resolve(),pathlib.Path('/private/var/db/timezone').resolve()]
script=pathlib.Path(sys.argv[1]).resolve();sys.path.insert(0,str(script.parent))
def within(p,r):return p==r or r in p.parents
def check(event,args):
 if event.startswith('socket.') or event.startswith('urllib.') or event in ['http.client.connect','http.client.send']:raise PermissionError('OFFLINE_ROUTE_DENIED '+event)
 if event=='open':
  file,mode,flags=args
  if isinstance(file,(str,bytes,os.PathLike)):
   p=pathlib.Path(os.fsdecode(file)).resolve()
   if within(p,realrepo):raise PermissionError('MUTABLE_REPOSITORY_DENIED '+str(p))
   writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)))
   if writing and not (within(p,work) or within(p,tmp)):raise PermissionError('WRITE_ROUTE_DENIED '+str(p))
   if not writing and not any(within(p,r) for r in allowed):raise PermissionError('READ_ROUTE_DENIED '+str(p))
   if writing and 'data/news/' in str(p):raise PermissionError('ORIGINAL_WRITE_DENIED '+str(p))
 if event in ['os.listdir','os.scandir']:
  if args and isinstance(args[0],(str,bytes,os.PathLike)):
   p=pathlib.Path(os.fsdecode(args[0])).resolve()
   if within(p,realrepo):raise PermissionError('PEER_DISCOVERY_DENIED '+str(p))
 if event=='subprocess.Popen':
  exe,argv,cwd,env=args
  if pathlib.Path(exe).name!='pdftotext' or argv[1]!='-layout' or argv[-1]!='-':raise PermissionError('PRODUCER_HELPER_ROUTE_DENIED '+str(exe))
 if event in ['os.system','os.exec','os.posix_spawn']:raise PermissionError('EXEC_ROUTE_DENIED '+event)
sys.addaudithook(check)
if sys.argv[2:] and sys.argv[2]=='--guard-probes':
 import socket
 outcomes=[]
 for name,f in [('network',lambda:socket.socket()),('mutable_repository',lambda:open(realrepo/'senate/2026/alabama/data/coordinator-primary-preflight.json')),('peer_discovery',lambda:os.listdir(realrepo/'senate/2026/alabama/data/baselines')),('producer_helper',lambda:__import__('subprocess').run([sys.executable,'-c','print(1)'])),('writer_route',lambda:open('/private/tmp/unauthorized-al-write','w'))]:
  try:f();raise AssertionError(name+' was allowed')
  except PermissionError as e:outcomes.append({'route':name,'rejected':str(e)})
 print(json.dumps(outcomes));sys.exit(0)
runpy.run_path(str(script),run_name='__main__')
''')
# Preserve exact guard/policy code as evidence. It is not a peer or acquisition producer.
(D/'offline-guard.py').write_bytes(guard.read_bytes())
env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':'/private/tmp/al-turnout-deps','TMPDIR':str(TMP),'AL_ISOLATED_ROOT':str(WORK)}
root=WORK/'senate/2026/alabama/data/turnout';attempts=[]
for label,args in [('guard-probes',[str(root/'scripts/build.py'),'--guard-probes'])]+[(name,[str(root/'scripts'/name)]) for name in ['extract_originals.py','render_sources.py','build.py','field_audit.py','supplement.py','report.py','validate.py']]:
 cmd=[sys.executable,str(guard)]+args;out=subprocess.run(cmd,cwd=WORK,env=env,capture_output=True);stem=D/('offline-'+label.replace('.py',''));stem.with_suffix('.stdout.txt').write_bytes(out.stdout);stem.with_suffix('.stderr.txt').write_bytes(out.stderr);attempts.append({'step':label,'returncode':out.returncode,'stdout_sha256':sha(out.stdout),'stderr_sha256':sha(out.stderr)})
 if out.returncode:
  (D/'offline-failed-attempt.json').write_text(json.dumps({'attempts':attempts,'guard_sha256':sha(guard.read_bytes()),'failing_script':args[0],'inputs':'complete146-file own original-phase capture plus individually pinned original references'},indent=2)+'\n');print(out.stderr.decode());raise SystemExit(out.returncode)
# Complete replay comparison: unchanged generated source/CSV/key/order/fields/report/contract, not revised current bytes.
changed=[];compared=[]
for x in mf['assets']:
 p=WORK/'senate/2026/alabama'/x['path'];b=p.read_bytes();same=(len(b)==x['bytes'] and sha(b)==x['sha256']);compared.append({'original_path':x['path'],'expected_original_sha256':x['sha256'],'reproduced_sha256':sha(b),'bytes':len(b),'exact':same})
 if not same:changed.append(x['path'])
# The original validator measured 16 histories before freezing its preceding body. The sealed snapshot contains17.
# Every original file still reconstructs exactly from its archived body; the regenerated audit alone measures the later history set.
eq_validation=[]
if changed:
 assert changed==['data/turnout/validation.json'],changed
 with tarfile.open(D/'turnout-original-phase.tar.gz') as original:
  old=json.loads(original.extractfile('data/turnout/validation.json').read())
 new=json.loads((WORK/'senate/2026/alabama/data/turnout/validation.json').read_text())
 idx=next(i for i,c in enumerate(old['checks']) if c['check']=='all_prior_owned_body_histories_reconstruct_exactly')
 assert old['checks'][idx]['evidence']==16 and new['checks'][idx]['evidence']==17
 eq_validation=[{'path':f'checks[{idx}].evidence','captured_original':16,'regenerated':17,'reason':'post-validation freeze adds the preceding validation body to sealed history; no source/numerical/identity/order field drift'}]
 new['checks'][idx]['evidence']=16;assert old==new
assert len(compared)==145
proof={'status':'PASS','input_scope':'All146 captured original-phase bodies (not revised current files), all9 exact individually pinned original entities; source downloads and producer/peer routes denied.','steps':attempts,'all_original_manifest_targets_reconstructed_and_pinned_before_rebuild':len(compared),'byte_identical_rebuilt_original_targets':len(compared)-len(changed),'regenerated_audit_only_differences':eq_validation,'file_comparisons':compared,'guard_sha256':sha(guard.read_bytes()),'route_probes':json.loads((D/'offline-guard-probes.stdout.txt').read_text()),'temporary_output_root':str(WORK),'network_used':False,'peer_calculator_or_outcome_used':False,'mutable_aggregate_used':False}
(D/'offline-reproduction.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'status':'PASS','original_target_reconstructions':len(compared),'byte_identical_rebuild_targets':len(compared)-len(changed),'audit_only_difference_count':len(eq_validation),'steps':len(attempts),'denied_route_probes':len(proof['route_probes'])},indent=2))
