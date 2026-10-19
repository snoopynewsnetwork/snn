#!/usr/bin/env python3
"""Complete owned-output hash inventory; original-byte references remain separate."""
from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent;S=D.parent.parent
assets=[S/'turnout.md',D.parent/'county-turnout.csv']+[p for p in D.rglob('*')if p.is_file()and p.name!='asset-manifest.json'];records=[]
for p in sorted(assets):
 b=p.read_bytes();assert len(b)<40000000;records.append(dict(path=str(p.relative_to(S)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
out=dict(scope='All owned turnout paths only, including report/county CSV/validation/source assets/scripts. Manifest excludes itself because a self-hash cannot be fixed.',owned_assets=records,reused_original_reference_manifests=['data/turnout/source/reused-originals.json','data/turnout/source/reused-national-originals.json','data/turnout/source/source-observations.json'],individual_object_limit_exclusive=40000000)
(D/'asset-manifest.json').write_text(json.dumps(out,indent=2)+'\n');print(f'Manifest: {len(records)} files, {sum(r["bytes"]for r in records):,} bytes; maximum {max(r["bytes"]for r in records):,}.')
