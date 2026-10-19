#!/usr/bin/env python3
"""Freeze immutable individual bodies, never an appendable ledger or optional review."""
import json,gzip,hashlib,os
from pathlib import Path
from verify_history import checkpin,verify
from native import receipts,body
MAPS=Path(__file__).resolve().parents[1];ROOT=MAPS.parent

def freeze():
 verify();a=json.loads((ROOT/'data/coordinator-priority-acceptance.json').read_text());refs={}
 def pin(path):
  p=ROOT/path;b=p.read_bytes();assert len(b)<40000000;entry=dict(path=os.path.relpath(p.resolve(),ROOT),bytes=len(b),sha256=hashlib.sha256(b).hexdigest());refs[entry['path']]=entry
 for e in [a['frozen_contract']]+a['frozen_first_pair_assets']+a['independent_coordinator_reviews']+a['complete_source_companion_files']:pin(e['path'])
 for seal in a['producer_seals']:
  m=json.loads((ROOT/seal['manifest']['path']).read_text());base=(ROOT/seal['manifest']['path']).parent
  for e in m.get('owned_assets',m.get('owned')):pin(e['path'])
  for e in m.get('read_only_references',[]):
   path=os.path.relpath((base/e['path']).resolve(),ROOT)
   if path!='data/news/manifest.json':pin(path)
 for r in receipts():body(r);pin(r['asset_path'])
 return dict(authority_path='data/coordinator-priority-acceptance.json',policy='Authority path only; every other frozen dependency is an individual complete immutable body. No optional preparation manifest/review, appendable news ledger or producer mutation required.',references=sorted(refs.values(),key=lambda e:e['path']))
if __name__=='__main__':
 j=freeze();(MAPS/'frozen-references.json').write_text(json.dumps(j,indent=2)+'\n');print(json.dumps(dict(frozen_references=len(j['references']))))
