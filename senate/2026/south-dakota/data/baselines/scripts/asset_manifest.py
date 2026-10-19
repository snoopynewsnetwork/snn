#!/usr/bin/env python3
"""Complete owned manifest and exact read-only evidence dependency pins; no duplicated originals."""
import hashlib,json
from pathlib import Path
from extract import BASE,DATA,SRC,NEWS,PEER,js
def pin(p):return dict(path=str(p.relative_to(DATA.parent)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
 owned=[p for p in BASE.rglob('*')if p.is_file()and p.name!='asset-manifest.json']+[DATA/'county-baselines.csv',DATA.parent/'county-partisanship.md']
 assert not any('__pycache__'in p.parts for p in owned)
 refs=set();receipts=json.loads((SRC/'shared-news-receipts.json').read_text())
 for r in receipts:
  if 'asset'in r:refs.add(NEWS/r['asset'])
  for part in r.get('asset_parts',[]):refs.add(NEWS/part['asset'])
 for p in [NEWS/'manifest.json',NEWS/'reconstruct_evidence.py',DATA/'preflight_primary_sources.py',DATA/'preflight_2024_public_native_export.py',DATA/'acquire_published_precinct_export.py',DATA/'coordinator-primary-preflight.json',DATA/'coordinator-2024-public-native-export-preflight.json']:
  refs.add(p)
 # Preserve actual peer acquisition chains, including parent bodies, failures and form controls.
 for p in PEER.iterdir():
  if p.is_file()and(p.name.endswith('.receipt.json')or p.name.endswith('.failed-request.json')):
   refs.add(p);r=json.loads(p.read_text())
   if r.get('asset')and(PEER/r['asset']).exists():refs.add(PEER/r['asset'])
 for p in [DATA/'turnout/acquire.py',DATA/'turnout/acquire_historical_native.py']:
  if p.exists():refs.add(p)
 for r in json.loads((BASE/'peer-reconciliation.json').read_text())['read_only_peer_pins']:refs.add(DATA.parent/r['path'])
 assert all(p.stat().st_size<40000000 for p in owned+list(refs))
 result=dict(schema_version=1,paths_relative_to='senate/2026/south-dakota',hash='SHA256 exact stored bytes',object_size_rule='strictly less than 40000000 bytes; full raw originals may be larger if stored losslessly compressed/split',self_hash_exclusion='Only asset-manifest.json excludes its own entry to avoid circularity. validation.json and every other owned file are included.',owned_assets=[pin(p)for p in sorted(set(owned))],read_only_references=[pin(p)for p in sorted(refs)],original_entity_receipts=['data/baselines/source/shared-news-receipts.json','data/baselines/source/peer-original-receipts.json','data/baselines/source/senate-public-original-receipts.json'],no_original_entity_available_for_current_ballot='Primary web observation succeeds; direct download404empty receipts retained separately; parsed web output not mislabeled raw PDF',original2020_county_reconstruction='Concatenate ordered gzip parts from shared news manifest, verify parts+complete gzip SHA/bytes, decompress exact149141181-byte original, verify raw SHA a9d55c618d479aaf9e207d0c49a3511206458756d329c42f830ab52c36930e72')
 js(BASE/'asset-manifest.json',result);print(json.dumps(dict(owned=len(result['owned_assets']),read_only_references=len(result['read_only_references']),maximum_owned_bytes=max(a['bytes']for a in result['owned_assets']),maximum_referenced_stored_bytes=max(a['bytes']for a in result['read_only_references']))))
if __name__=='__main__':main()
