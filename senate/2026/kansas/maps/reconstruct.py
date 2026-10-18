#!/usr/bin/env python3
"""Reconstruct exact original entity bytes from an acquisition ID; verify before writing.
python3 reconstruct.py johnson-shp --output /desired/path/precincts.zip
python3 reconstruct.py shawnee-features-000 > native-response.json
"""
import argparse,gzip,hashlib,json,sys,pathlib
from acquire import ROOT,MAN
p=argparse.ArgumentParser();p.add_argument('id');p.add_argument('--output');a=p.parse_args()
r=next(x for x in json.loads(MAN.read_text()) if x['id']==a.id);s=r['storage'];parts=[]
for part in s['ordered_parts']:
 b=(ROOT/part['path']).read_bytes();assert len(b)==part['bytes'] and hashlib.sha256(b).hexdigest()==part['sha256'];parts.append(b)
b=b''.join(parts);assert len(b)==s['stored_bytes'] and hashlib.sha256(b).hexdigest()==s['stored_sha256']
if s['encoding']=='gzip':b=gzip.decompress(b)
assert len(b)==r['original_bytes'] and hashlib.sha256(b).hexdigest()==r['original_sha256']
if a.output:pathlib.Path(a.output).write_bytes(b)
else:sys.stdout.buffer.write(b)
