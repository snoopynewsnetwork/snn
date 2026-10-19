#!/usr/bin/env python3
"""Reconstruct an exact acquired/preparation entity to an explicitly selected file."""
import argparse,json,pathlib
from acquire import ROOT,STATE,body,sha
from native import prep,raw
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('id');p.add_argument('output');a=p.parse_args();rp=ROOT/'receipts'/f'{a.id}.json'
 if rp.exists():r=json.loads(rp.read_text());b=body(r);expected=r['original_sha256']
 else:r=next(x for x in prep() if x['id']==a.id);b=raw(r);expected=r['raw_sha256']
 assert sha(b)==expected
 dest=pathlib.Path(a.output);assert not dest.exists(),'Do not overwrite an existing original';dest.write_bytes(b);print(len(b),expected,str(dest))
