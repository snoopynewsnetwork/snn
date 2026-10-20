"""Regenerate deterministic outputs in isolation. All repository reads allowlisted by pins."""
from pathlib import Path
import os,sys,tempfile,json,hashlib,socket,runpy
import build
ROOT=build.ROOT;S=ROOT.parent;REPO=S.parents[2]
inputs=json.loads((ROOT/'build-inputs.json').read_bytes());allowed={(ROOT/p['path']).resolve() for p in inputs['files']}|{(ROOT/'build-inputs.json').resolve(),(S/build.CONTRACT['path']).resolve()}
expected=['original-catalogue.json','manifest.csv','county-investigations.json','admission.json','native-context-index.csv','coverage.json','map-vintage-observations.json','index.html','research-summary.json','precinct-maps.md']
original={name:(S/'precinct-maps.md' if name=='precinct-maps.md' else ROOT/name).read_bytes() for name in expected}
probes=[]
with tempfile.TemporaryDirectory(prefix='al-maps-offline-') as tmp:
 target=Path(tmp).resolve()
 def audit(event,args):
  if event.startswith('socket.') and event not in ['socket.__new__']:raise PermissionError('offline network denied '+event)
  if event.startswith('subprocess.') or event in ['os.system','os.exec','os.posix_spawn']:raise PermissionError('producer/subprocess execution denied')
  if event=='open':
   path,mode,flags=args
   if not isinstance(path,(str,bytes,os.PathLike)):return
   p=Path(os.fsdecode(path)).resolve();writing=bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
   if writing and not p.is_relative_to(target):raise PermissionError('outside temporary outputs writer denied '+str(p))
   if not writing and p.is_relative_to(REPO) and p not in allowed:raise PermissionError('unallowlisted mutable/peer/helper repository read denied '+str(p))
  if event in ['os.remove','os.rmdir','os.mkdir','os.rename','os.chmod']:
   p=Path(os.fsdecode(args[0])).resolve()
   if not p.is_relative_to(target):raise PermissionError('outside temporary outputs mutation denied')
 sys.addaudithook(audit)
 def probe(name,fn):
  try:fn()
  except PermissionError as e:probes.append({'route':name,'status':'DENIED','reason':str(e)})
  else:raise AssertionError('forbidden route permitted: '+name)
 probe('network',lambda:socket.getaddrinfo('www.sos.alabama.gov',443))
 probe('mutable_news_aggregate',lambda:(S/'data/news/source-ledger.json').read_bytes())
 probe('producer_helper',lambda:(S/'data/turnout/scripts/build.py').read_bytes())
 probe('peer_writer',lambda:(S/'data/baselines/build.py').read_bytes())
 probe('owned_write',lambda:(ROOT/'forbidden-probe.txt').write_text('must not exist'))
 summary=build.build(target);records=[]
 for name in expected:
  b=(target/name).read_bytes();assert b==original[name],name
  records.append({'output':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'exact':True})
 result={'status':'PASS','fixed_input_files':len(inputs['files']),'exact_deterministic_outputs':records,'actual_forbidden_route_probes':probes,'network_denied':True,'mutable_aggregate_helper_peer_writer_denied':True,'producer_imports_or_execution':False,'temporary_only_writes':True}
 # TemporaryDirectory uses dirfd-relative cleanup; keep audit limited to path-backed mutations above.
 print(json.dumps(result,indent=2))
