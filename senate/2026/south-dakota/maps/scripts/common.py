"""Precinct maps: exact inputs and lossless originals; no network on import."""
from pathlib import Path
import json, hashlib, gzip
MAPS=Path(__file__).resolve().parents[1]
STATE=MAPS.parent
ACCEPTANCE='data/coordinator-priority-acceptance.json'
CONTRACT='data/turnout/priority-set.json'
def sha(b): return hashlib.sha256(b).hexdigest()
def pin(p):
 p=Path(p); b=p.read_bytes(); return dict(path=str(p.relative_to(STATE)),bytes=len(b),sha256=sha(b))
def check(p):
 b=(STATE/p['path']).read_bytes(); assert len(b)==p['bytes'] and sha(b)==p['sha256'],p['path']; assert len(b)<40000000;return b
def load(p): return json.loads((MAPS/p).read_bytes())
def dump(p,x):
 p=MAPS/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def semantic(x):return sha(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def walk(x):
 yield x
 if isinstance(x,dict):
  for v in x.values():yield from walk(v)
 elif isinstance(x,list):
  for v in x:yield from walk(v)
def original(e):
 if 'asset_path' in e:
  z=check(dict(path=e['asset_path'],bytes=e['stored_bytes'],sha256=e['stored_sha256']))
 else:z=b''.join(check(p) for p in e['stored_objects'])
 b=gzip.decompress(z);assert len(b)==e['raw_bytes'] and sha(b)==e['raw_sha256'],e['id'];return b
