#!/usr/bin/env python3
"""Exact owned membership; excludes only manifest itself. No Git operations."""
import sys
sys.dont_write_bytecode=True
from common import *
import argparse
MANIFEST=ROOT/'asset-manifest.json'
def owned():return sorted([STATE/'official-results.md',STATE/'data/official-results-sources.csv']+[p for p in ROOT.rglob('*') if p.is_file() and p!=MANIFEST],key=str)
def make():
 paths=owned();assert all(p.stat().st_size<40000000 for p in paths);assert not any('__pycache__' in p.parts or p.suffix=='.pyc' for p in paths)
 deps=json.loads((ROOT/'dependency-verification.json').read_text())['exact_read_only_references']
 return {'schema':'SD-official-results-exact-owned-manifest-v1','paths_relative_to':'senate/2026/south-dakota','self_exclusion_only':'data/results-sources/asset-manifest.json','authority_path_only':'data/coordinator-priority-acceptance.json','owned_assets':[pin(p) for p in paths],'read_only_dependencies':deps,'stored_object_limit_exclusive':40000000,'qualification':'Historical/source research complete. Current identity/geography/feed/legal exhaustive review remains qualified and external; no self-approval.'}
def audit():
 expected=json.loads(MANIFEST.read_text());actual=make();assert actual==expected,'Exact manifest mismatch';return {'owned_entries':len(actual['owned_assets']),'read_only_dependencies':len(actual['read_only_dependencies']),'largest_owned_bytes':max(x['bytes'] for x in actual['owned_assets']),'exact_membership_and_hashes':True}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 if a.write:dump('asset-manifest.json',make())
 print(json.dumps(audit(),indent=2))
