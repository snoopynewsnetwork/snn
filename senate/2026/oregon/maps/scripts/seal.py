"""Acyclic self-only manifest: fixed proofs -> finalseal -> manifest last. No writes after audit."""
from common import *
from audit import all_owned,membership
if __name__=='__main__':
 assert not (M/'asset-manifest.json').exists(),'Already sealed; frozen bytes must not be rewritten'
 validation=load('maps/qa/validation.json');assert validation['status']=='pass'
 proofs=['precinct-maps.md','maps/qa/source-replay.json','maps/qa/original-reconstruction.json','maps/qa/geography.json.gz','maps/qa/binary-summary.json','maps/qa/fixtures.json','maps/qa/visual-review.json','maps/qa/validation.json','maps/inventory.json.gz','maps/history/research-history.json','maps/renders/index.json','maps/SCHEMA.md']
 save('maps/finalseal.json',{'schema':'oregon.maps.acyclic-finalseal.v1','bounded_research_complete':True,'coordinator_acceptance':False,'authority_path':AUTH,'proofs':[ref(p) for p in proofs],'manifest_excludes_only_itself':True,'no_reverse_manifest_pin':True,'final_read_only_command':'PYTHONDONTWRITEBYTECODE=1 python -B senate/2026/oregon/maps/scripts/audit.py','scope':'All36parents/510full known contexts/31unavailable cases; current/legal/leaf/resultID/eligible/live/cadence/outstanding/forecast/calibration approvals remain false/unknown, no inferred joins or spatial allocation.'})
 files=[ref(p) for p in all_owned()];membership(files,all_owned());save('maps/asset-manifest.json',{'schema':'oregon.maps.self-only-excluded-manifest.v1','owned_scopes':['precinct-maps.md','maps/**'],'excluded_only':'maps/asset-manifest.json','files':files})
 print(json.dumps({'manifest':ref('maps/asset-manifest.json'),'targets':len(files),'owned_files':len(files)+1,'finalseal':ref('maps/finalseal.json'),'report':ref('precinct-maps.md')}))
