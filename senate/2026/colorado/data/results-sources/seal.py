#!/usr/bin/env python3
"""Seal research assets only; not acceptance or publication. Final validation is read-only."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;STATE=ROOT.parents[1]
paths=[STATE/'official-results.md',STATE/'data/official-results-sources.csv']+[p for p in ROOT.rglob('*') if p.is_file() and p!=ROOT/'asset-manifest.json']
assert not any('__pycache__' in p.parts or p.suffix=='.pyc' for p in paths),'Remove runtime cache artifacts before seal'
assets=[]
for p in sorted(paths):
 b=p.read_bytes();assert len(b)<40000000;assets.append({'path':p.relative_to(STATE).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
manifest={'schema':'CO-official-source-research-seal-v1','status':'research-complete-external-coordinator-review-required','self_only_exclusion':'data/results-sources/asset-manifest.json','external_authority_path':'data/coordinator-priority-acceptance.json','assets':assets,'immutable_external_files':json.loads((ROOT/'immutable-external-files.json').read_text()),'current_admission':False,'current_geography_approved':False,'collector_approved':False,'coordinator_acceptance':False}
(ROOT/'asset-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Sealed',len(assets),'owned assets; final read-only validate.py --sealed required')
