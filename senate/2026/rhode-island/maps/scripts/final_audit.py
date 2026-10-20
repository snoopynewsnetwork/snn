"""Read-only full membership/hash/size/object/source/original reconstruction after seal."""
from common import *
from seal import owned,originals,pin
import replay,audit_historical,audit_publications,validate,reproduce

def run():
 manifest_before=pin(M/'manifest.json');mf=parsed(M/'manifest.json');assert mf['excludes_only']=='maps/manifest.json' and mf['authority_path']==AUTHORITY
 actual=[pin(p) for p in owned() if p!=M/'manifest.json'];assert actual==mf['owned_files'],'whole owned membership/hash/size mismatch'
 for r in mf['fixed_external_build_inputs']:verify((S/r['path']).read_bytes(),r)
 assert originals()==mf['external_complete_original_references']
 for r in parsed(M/'final-seal.json')['proofs']:verify((S/r['path']).read_bytes(),r)
 first={p['path']:p for p in actual}
 a=replay.run();h=audit_historical.run();pub=audit_publications.run();v=validate.run(final=True);r=reproduce.run()
 last={pin(p)['path']:pin(p) for p in owned() if p!=M/'manifest.json'};assert last==first,'audit modified owned bytes'
 assert pin(M/'manifest.json')==manifest_before,'manifest changed during read-only audit'
 return dict(status='pass',read_only_after_seal=True,owned_files=len(actual),all_graph_counts=a['counts'],historical_counts=h['counts'],publication_counts=pub['counts'],validation_counts=v['counts'],deterministic_generated_bodies=r['compared_full_generated_bodies'],manifest_pin=pin(M/'manifest.json'),seal_pin=pin(M/'final-seal.json'),report_pin=pin(S/'precinct-maps.md'))
if __name__=='__main__':print(json.dumps(run()))
