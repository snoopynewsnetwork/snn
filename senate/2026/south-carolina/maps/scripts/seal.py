#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import pathlib,json,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def row(p):
 b=p.read_bytes();return {'path':str(p.relative_to(ROOT.parent)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def run():
 owned=sorted([p for p in ROOT.rglob('*') if p.is_file() and p!=ROOT/'manifest.json']+[ROOT.parent/'precinct-maps.md'],key=lambda x:str(x));external={ROOT.parent/'data/turnout/priority-set.json',ROOT.parent/'data/coordinator-priority-acceptance.json',ROOT.parent/'turnout.md',ROOT.parent/'county-partisanship.md',ROOT.parent/'data/county-turnout.csv',ROOT.parent/'data/county-baselines.csv',ROOT.parent/'data/turnout/asset-manifest.json',ROOT.parent/'data/turnout/validation.json',ROOT.parent/'data/baselines/asset-manifest.json'}
 external|={p for p in (ROOT.parent/'data/map-preflight').glob('*') if p.is_file()}
 for p in (ROOT/'raw').glob('*.request.json'):
  d=json.loads(p.read_text())
  for key in ['path','shared_exact_original_metadata_path']:
   if d.get(key,'').startswith('../'):external.add((ROOT/d[key]).resolve())
 for r in json.loads((ROOT/'supplement-inventory.json').read_text()):
  for key in ['external_original_path','external_metadata_path']:
   if r.get(key):external.add(ROOT.parent/r[key])
 result={'schema':'sc-map-owned-manifest-v1','self_exclusion':'maps/manifest.json only; all other owned files plus precinct-maps.md included, with no mutable aggregate dependency back to manifest','owned_assets':[row(p) for p in owned],'external_inputs':[row(p) for p in sorted(external,key=lambda x:str(x))],'stored_asset_cap_bytes_exclusive':40000000,'file_scope':'Only precinct-maps.md and maps/** are writable assignment paths. External inputs remain read-only.'};assert all(r['bytes']<40000000 for r in result['owned_assets']);out=(json.dumps(result,indent=2)+'\n').encode();(ROOT/'manifest.json').write_bytes(out);print(json.dumps({'owned_files':len(owned),'owned_bytes':sum(r['bytes'] for r in result['owned_assets']),'manifest_sha256':hashlib.sha256(out).hexdigest(),'manifest_bytes':len(out)}))
if __name__=='__main__':run()
