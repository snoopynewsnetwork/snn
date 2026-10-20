import sys,os,pathlib,runpy,json
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
