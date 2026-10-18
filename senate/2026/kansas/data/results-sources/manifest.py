#!/usr/bin/env python3
"""One-way manifest; does not hash itself. Validation never pins manifest hash."""
import hashlib,json,pathlib
R=pathlib.Path(__file__).resolve().parent
files=[p for p in R.rglob('*') if p.is_file() and p.name!='artifact-manifest.json' and '__pycache__' not in p.parts]
files += [R.parent/'official-results-sources.csv',R.parent.parent/'official-results.md']
assets=[]
for p in sorted(files,key=lambda p:str(p)):
 b=p.read_bytes();assert len(b)<40000000,(p,len(b));assets.append({'path':str(p.relative_to(R)) if p.is_relative_to(R) else '../official-results-sources.csv' if p.name=='official-results-sources.csv' else '../../official-results.md','bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
o={'schema':'Kansas official-results artifact manifest v1','hash_policy':'SHA256 of exact stored bytes; self excluded. Validation is included, but validation output omits manifest hash/count/size, preventing a reverse cycle. Shared assets remain external read-only references in frozen-inputs.json and per-request metadata.','asset_count':len(assets),'stored_bytes':sum(x['bytes'] for x in assets),'exclusive_per_file_byte_limit':40000000,'assets':assets}
(R/'artifact-manifest.json').write_text(json.dumps(o,indent=2)+'\n');print('manifest',len(assets),'assets',o['stored_bytes'],'bytes')
