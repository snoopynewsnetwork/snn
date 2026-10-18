#!/usr/bin/env python3
"""Create once after final input review. Normal reproduction never repins inputs."""
import gzip,hashlib,json,pathlib,os
R=pathlib.Path(__file__).resolve().parent;D=R.parent
out=R/'frozen-inputs.json';assert not out.exists(),'frozen inputs already exist; do not silently repin'
s=json.loads((R/'shared-inputs.json').read_text());paths={ (R/x['path']).resolve() for x in s['pinned_files'] }
for x in s['full_original_source_objects']:
 p=(D/'turnout'/x['path']).resolve();z=p.read_bytes();b=gzip.decompress(z) if z.startswith(b'\x1f\x8b') else z
 assert hashlib.sha256(z).hexdigest()==x['stored_sha256']
 if x.get('original_sha256'):assert hashlib.sha256(b).hexdigest()==x['original_sha256']
 paths.add(p)
for mp in (R/'raw').glob('*.meta.json'):
 x=json.loads(mp.read_text())
 if x.get('body_path'):
  p=(R/x['body_path']).resolve()
  if not p.is_relative_to(R):paths.add(p)
assets=[]
for p in sorted(paths):
 assert p.is_relative_to(D.parent.parent) and not p.is_relative_to(R)
 b=p.read_bytes();assets.append({'path':os.path.relpath(p,R),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
out.write_text(json.dumps({'scope':'immutable external read-only input pins, final coordinator bytes; normal reproduction never rewrites this file','hash_direction':'worker -> external source; external sources do not pin worker output','assets':assets},indent=2)+'\n');print('frozen external inputs',len(assets))
