"""Reconstruct one exact complete acquisition body from its full receipt."""
from pathlib import Path
import gzip,json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
r=json.loads((ROOT/sys.argv[1]).read_bytes());parts=[]
for p in r['entity']['parts']:
 b=(ROOT/p['path']).read_bytes();assert len(b)==p['bytes'] and hashlib.sha256(b).hexdigest()==p['sha256'];parts.append(b)
b=gzip.decompress(b''.join(parts));assert len(b)==r['entity']['bytes'] and hashlib.sha256(b).hexdigest()==r['entity']['sha256']
target=Path(sys.argv[2]).resolve();assert not target.is_relative_to(ROOT), 'original reconstruction target must be temporary/outside sealed package';target.write_bytes(b)
