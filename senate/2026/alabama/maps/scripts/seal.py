"""Seal first, manifest LAST. No current-manifest reverse digest."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];S=ROOT.parent

def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();assert len(b)<40000000
 return {'path':str(p.relative_to(S)),'bytes':len(b),'sha256':sha(b)}
validation=json.loads((ROOT/'validation.json').read_bytes());assert validation['status']=='PASS'
seal={'schema':'AL-original-maps-research-seal-v1','status':'bounded_original_source_research_complete_pending_sole_coordinator_review','authority_path':'data/coordinator-priority-acceptance.json','contract_path':'data/turnout/priority-set.json','validation_sha256':sha((ROOT/'validation.json').read_bytes()),'source_graph_full':True,'full_historical_contexts':2085,'priority':887,'remainder':1198,'parents':67,'priority_parents':63,'current_legal_live_approval':False,'report':pin(S/'precinct-maps.md'),'final_readonly_audit_required':True,'manifest_omits_only_itself':True,'manifest_reverse_digest':None,'preservation_qualification':'Prohibited authority digest literal omitted from retained failed self-scanner template/trace; authority body/digest is not a downstream artifact. Exact source/producer bodies/flags remain unchanged.'}
(ROOT/'final-seal.json').write_text(json.dumps(seal,indent=2)+'\n')
files=sorted([p for p in ROOT.rglob('*') if p.is_file() and p!=ROOT/'asset-manifest.json']+[S/'precinct-maps.md'])
assets=[pin(p) for p in files]
manifest={'schema':'AL-original-maps-full-owned-membership-v1','scope':'precinct-maps.md plus EVERY maps/** file, excludes ONLY maps/asset-manifest.json itself','assets':assets,'count':len(assets),'stored_bytes':sum(x['bytes'] for x in assets),'strict_file_limit':40000000,'current_approval':False}
(ROOT/'asset-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'status':'SEALED_PENDING_FINAL_READONLY_AUDIT','targets':len(assets),'stored_bytes':manifest['stored_bytes']}))
