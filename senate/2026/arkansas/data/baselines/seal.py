#!/usr/bin/env python3
"""Seal first, complete owned manifest LAST; no digest cycles."""
import datetime,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;STATE=P.parent.parent
validation=json.loads((P/'validation.json').read_text());assert validation['status']=='pass'
seal={'sealed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':'AR','scope':'county-partisanship.md; data/county-baselines.csv; data/baselines/**','validation_sha256':hashlib.sha256((P/'validation.json').read_bytes()).hexdigest(),'original_first_core_sha256':hashlib.sha256((P/'history/original-first/core.tar.gz').read_bytes()).hexdigest(),'priority_contract_sha256':'6b945a43a1f47f3dda1c072cd240f692633b00371ef93c4778e37a67afc93355','qualification':'historical research and deterministic arithmetic; external current ballot/geometry/legal/cadence/pool/calibration gaps remain','manifest_rule':'written last and includes every owned artifact except itself; this seal has no manifest hash'}
(P/'final-seal.json').write_text(json.dumps(seal,indent=2)+'\n')
files=sorted([f for f in P.rglob('*') if f.is_file() and f.name!='asset-manifest.json']+[STATE/'county-partisanship.md',P.parent/'county-baselines.csv'])
assets=[{'path':str(f.relative_to(STATE)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in files];assert all(r['bytes']<40000000 for r in assets)
(P/'asset-manifest.json').write_text(json.dumps({'schema':'arkansas-baselines-assets-v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'excludes_only':'data/baselines/asset-manifest.json','assets':assets},indent=2)+'\n')
print(len(assets),'owned assets sealed')
