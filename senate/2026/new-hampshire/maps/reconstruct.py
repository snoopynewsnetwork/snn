#!/usr/bin/env python3
"""Write exact original response to stdout, or --output outside owned tree if >40MB."""
import argparse,hashlib,json,gzip,sys,pathlib
from acquire import ROOT
p=argparse.ArgumentParser();p.add_argument('id');p.add_argument('--output');a=p.parse_args();m=json.loads((ROOT/'source'/f'{a.id}.meta.json').read_text())
if a.output:
 q=pathlib.Path(a.output).resolve()
 if ROOT in q.parents and m['original_bytes']>=40_000_000:raise SystemExit('Large reconstruction must be outside maps/; retained parts are the deliverable')
 out=q.open('wb')
else:out=sys.stdout.buffer
h=hashlib.sha256();n=0
for x in sorted(m['objects'],key=lambda x:x['order']):
 b=(ROOT/x['path']).read_bytes();assert hashlib.sha256(b).hexdigest()==x['sha256'];b=gzip.decompress(b) if x['encoding']=='gzip' else b;assert hashlib.sha256(b).hexdigest()==x['decoded_sha256'];h.update(b);n+=len(b);out.write(b)
assert h.hexdigest()==m['original_sha256'] and n==m['original_bytes']
if a.output:out.close()
