#!/usr/bin/env python3
"""Optional network reproduction into a new child directory, never replaces frozen originals.
Public bodies/version clocks may change; new snapshot has independent UTC/headers/hashes.
"""
import argparse,json,pathlib
import acquire
p=argparse.ArgumentParser();p.add_argument('directory',help='new directory under maps/');a=p.parse_args()
old=acquire.ROOT;dest=(old/a.directory).resolve();assert old in dest.parents and not dest.exists()
records=json.loads(acquire.MAN.read_text());dest.mkdir();(dest/'raw').mkdir();acquire.ROOT=dest;acquire.MAN=dest/'acquisition.json'
for r in records:acquire.fetch(r['id'],r['requested_url'],r.get('parent_capture_id'),r['purpose'])
