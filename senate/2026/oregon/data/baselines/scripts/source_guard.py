"""Own-process audit guard: deny mutable discovery routes without changing shared files.
Usage: python3 -B source_guard.py originals.py --proof  OR validate.py [--write].
"""
import hashlib,json,os,runpy,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];STATE=R.parent.parent
BLOCKED={str(STATE/'data/news/manifest.json'),str(STATE/'data/audit_precinct_archives.py'),str(STATE/'data/turnout/source/shared-original-pins.json')}
ACQUIRED=STATE/'data/turnout/source/acquired';events=[]
def pathstr(value):
 try:return os.path.abspath(os.fsdecode(value))
 except (TypeError,ValueError):return ''
def hook(event,args):
 if event=='open':
  path=pathstr(args[0])
  if path in BLOCKED or (path.startswith(str(ACQUIRED)+os.sep) and path.endswith('.receipt.json')):events.append({'event':event,'path':path});raise PermissionError('guard: mutable source metadata/helper denied')
 if event in ['os.scandir','os.listdir','pathlib.Path.glob','pathlib.Path.rglob'] and pathstr(args[0])==str(ACQUIRED):events.append({'event':event,'path':str(ACQUIRED)});raise PermissionError('guard: peer acquisition enumeration denied')
 if event in ['socket.connect','socket.getaddrinfo']:raise PermissionError('guard: network denied')
 if event=='subprocess.Popen' and 'audit_precinct_archives.py' in repr(args):raise PermissionError('guard: mutable helper execution denied')
def main():
 target=sys.argv[1];proof='--proof' in sys.argv;arguments=[x for x in sys.argv[2:] if x!='--proof'];before={}
 if proof:
  inv=json.loads((R/'source/independent-original-inventory.json').read_bytes())
  for name in ['source/independent-original-inventory.json','source/original-read-receipts.json']+[x['text_path'] for x in inv]:before[name]=hashlib.sha256((R/name).read_bytes()).hexdigest()
 sys.addaudithook(hook)
 negatives=[]
 tests=[('news aggregate',lambda:(STATE/'data/news/manifest.json').read_bytes()),('shared helper',lambda:(STATE/'data/audit_precinct_archives.py').read_bytes()),('peer receipt',lambda:(ACQUIRED/'benton-2020-precincts.receipt.json').read_bytes()),('peer pins',lambda:(STATE/'data/turnout/source/shared-original-pins.json').read_bytes()),('peer directory',lambda:list(ACQUIRED.iterdir()))]
 for name,fn in tests:
  try:fn()
  except PermissionError:negatives.append({'case':name,'denied':True})
  else:raise AssertionError('guard negative did not fail: '+name)
 sys.argv=[str(R/'scripts'/target),*arguments];runpy.run_path(sys.argv[0],run_name='__main__')
 if proof:
  after={n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in before};assert before==after
  result={'scope':'immutable receipt original-reader rebuild only; no new sources or scenario/model regeneration','mutable_routes_denied':negatives,'guard_denial_events':events,'before_after_identical':True,'unchanged_output_hashes':after,'original_entity_texts':len(inv),'ZIP_members':sum('archive_source_id' in x['origin'] for x in inv),'old_complete_reproduction_evidence':'source/history/seal-input-repair-v1/inventory.json retains old validation, witness, manifest and all prior payload bodies; prior full offline run separately reported before this packaging repair'}
  (R/'source/repair-proofs/original-rebuild.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'source_guard_target':target,'mutable_route_negative_checks':len(negatives),'guarded_run_passed':True,'outputs_byte_identical':bool(proof)}))
if __name__=='__main__':main()
