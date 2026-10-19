#!/usr/bin/env python3
"""Reconstruct exact retained HTTP entity bytes, including ordered gzip parts."""
import argparse,gzip,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def read_capture(source_id):
 row=next(r for r in json.loads((ROOT/'manifest.json').read_text()) if r['id']==source_id)
 if 'asset_parts' in row:
  pieces=[]
  for p in row['asset_parts']:
   b=(ROOT/p['asset']).read_bytes();assert len(b)==p['bytes']<40000000 and hashlib.sha256(b).hexdigest()==p['sha256'];pieces.append(b)
  stored=b''.join(pieces);assert len(stored)==row['stored_bytes']
 else:stored=(ROOT/row['asset']).read_bytes()
 assert hashlib.sha256(stored).hexdigest()==row['stored_sha256'];raw=gzip.decompress(stored);assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['raw_sha256'];return raw
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('source_id');parser.add_argument('--output',type=Path);args=parser.parse_args();raw=read_capture(args.source_id)
 if args.output:args.output.write_bytes(raw)
 print(json.dumps({'source_id':args.source_id,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'output':str(args.output) if args.output else None}))
