#!/usr/bin/env python3
"""Complete owned-file manifest, with explicit self exclusion."""
from acquire import ROOT,sha
import json
STATE=ROOT.parent
paths=sorted([STATE/'precinct-maps.md']+[p for p in ROOT.rglob('*')if p.is_file()and p.name!='asset-manifest.json'])
assets=[]
for p in paths:
 b=p.read_bytes();assert len(b)<40000000,p;assert '__pycache__'not in p.parts and p.suffix!='.pyc';assets.append({'path':str(p.relative_to(STATE)),'bytes':len(b),'sha256':sha(b)})
(ROOT/'asset-manifest.json').write_text(json.dumps({'schema_version':'nh-map-owned-assets-1','scope':'Only precinct-maps.md and maps/**; all other paths read-only','self_exclusion':'maps/asset-manifest.json excluded to avoid recursive hash. Validation included. No reverse acceptance hash.','assets':assets},indent=2)+'\n')
print('Manifest',len(assets),'files;total',sum(x['bytes']for x in assets),'max',max(x['bytes']for x in assets))
