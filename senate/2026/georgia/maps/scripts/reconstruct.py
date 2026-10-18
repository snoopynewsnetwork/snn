#!/usr/bin/env python3
"""Verify/reconstruct exact HTTP entity bytes from identity/gzip/ordered slices."""
import argparse
from acquire import ROOT,read_record,entity,sha
p=argparse.ArgumentParser();p.add_argument('id');p.add_argument('--output');a=p.parse_args()
r=read_record(a.id);b=entity(r);assert len(b)==r['entity_bytes'] and sha(b)==r['entity_sha256']
if a.output:
    out=(ROOT/a.output).resolve();assert out.is_relative_to(ROOT)
    out.parent.mkdir(exist_ok=True,parents=True)
    if out.exists():assert out.read_bytes()==b
    else:out.write_bytes(b)
print(f'{a.id}: exact {len(b)} entity bytes SHA256 {sha(b)}')
