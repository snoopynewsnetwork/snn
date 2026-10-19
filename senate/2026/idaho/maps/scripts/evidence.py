#!/usr/bin/env python3
"""Complete immutable original-body and ordered-part verification."""
import gzip,hashlib,json
from pathlib import Path
MAPS=Path(__file__).resolve().parents[1];ROOT=MAPS.parent

def sha(b):return hashlib.sha256(b).hexdigest()
def stored(e):
 b=(ROOT/e['stored_path']).read_bytes();assert len(b)==e['stored_bytes']<40000000 and sha(b)==e['stored_sha256'];return b

def original(r):
 if 'stored_parts' in r:
  parts=[];offset=0
  for e in r['stored_parts']:
   assert e['offset']==offset;b=gzip.decompress(stored(e));assert len(b)==e['raw_bytes'] and sha(b)==e['raw_sha256'];parts.append(b);offset+=len(b)
  b=b''.join(parts)
 else:
  b=stored(r);b=gzip.decompress(b) if r['stored_path'].endswith('.gz') else b
 assert len(b)==r['raw_bytes'] and sha(b)==r['raw_sha256'];return b

def own_receipts():return [json.loads(p.read_text()) for p in sorted((MAPS/'source').glob('*.receipt.json')) if not p.name.startswith('native-')]
