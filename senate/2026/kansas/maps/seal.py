#!/usr/bin/env python3
"""Seal reviewed owned files. Exclude manifest/validation/freeze themselves to avoid cycles."""
import datetime,hashlib,json
from acquire import ROOT
excluded={'asset-manifest.json','validation.json','FROZEN.json'}
paths=sorted([p for p in ROOT.rglob('*') if p.is_file() and p.name not in excluded]+[ROOT.parent/'precinct-maps.md'])
import os
assets=[]
for p in paths:
 b=p.read_bytes();assert len(b)<40000000,p
 assets.append({'path':os.path.relpath(p,ROOT),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
manifest={'schema':'ks-maps-asset-manifest-v1','scope':'Entire maps tree plus precinct-maps.md; all actual acquired originals, failed originals, derivatives, scripts and complete native contexts','self_exclusions':sorted(excluded),'reason':'Avoid recursive hashes; validation and FROZEN pin their dependencies in one direction only','maximum_stored_asset_bytes_exclusive':40000000,'assets':assets}
(ROOT/'asset-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
pins=[]
for p in [ROOT/'asset-manifest.json',ROOT/'readonly-pins.json',ROOT.parent/'precinct-maps.md']:
 pins.append({'path':os.path.relpath(p,ROOT),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
(ROOT/'FROZEN.json').write_text(json.dumps({'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pins':pins,'scope':'Research package frozen for coordinator review; no November/current physical crosswalk approval','next_step':'Run validate.py without modifying originals'},indent=2)+'\n')
print('Sealed',len(assets),'owned assets;',sum(a['bytes'] for a in assets),'bytes; maximum',max(a['bytes'] for a in assets))
