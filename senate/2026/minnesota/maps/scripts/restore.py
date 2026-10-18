#!/usr/bin/env python3
"""Reconstruct retained original entity byte-for-byte, to stdout. Example:
python3 scripts/restore.py lcc2025-27053 > Hennepin.zip
"""
import sys,json
sys.dont_write_bytecode=True
from acquire import ROOT,read,sha
m=json.loads((ROOT/'evidence'/(sys.argv[1]+'.request.json')).read_text());b=read(m)
assert len(b)==m['original_entity_bytes'] and sha(b)==m['original_entity_sha256']
sys.stdout.buffer.write(b)
