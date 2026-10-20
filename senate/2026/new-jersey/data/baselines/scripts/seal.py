#!/usr/bin/env python3
"""Seal every owned artifact; only asset-manifest itself is excluded from membership."""
from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parents[1];STATE=D.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 validation=json.loads((D/'validation.json').read_text());repro=json.loads((D/'reproduction.json').read_text());assert validation['pass'] and repro['pass']
 core=D/'source/pre-peer-witness.json';assert sha(core.read_bytes())=='d8a93b13b137b8336b2bb47a0ab4373aff6ca5212363dbe76dbb8711137bfc40'
 final={'status':'bounded research/calculator package complete, coordinator review/publication pending','validation_sha256':sha((D/'validation.json').read_bytes()),'validation_checks':validation['checks'],'reproduction_sha256':sha((D/'reproduction.json').read_bytes()),'original_only_rebuild_products':repro['product_count'],'core_witness_sha256':sha(core.read_bytes()),'report_sha256':sha((STATE/'county-partisanship.md').read_bytes()),'county_csv_sha256':sha((STATE/'data/county-baselines.csv').read_bytes()),'priority_sha256':sha((D/'priority-set.json').read_bytes()),'core_peer_comparison_sha256':sha((D/'peer-comparison.json').read_bytes()),'finer_peer_comparison_sha256':sha((D/'peer-finer-comparison.json').read_bytes()),'source_reference_index_sha256':sha((D/'source/original-references.json').read_bytes()),'manifest_reverse_pin':None,'acyclic_membership':'asset-manifest pins this finalseal and validation; neither pins current manifest bytes','review_scope':'frozen original-first peer core only, separate finer original-first comparison; no future-final equality assertion','coordinator_priority_accepted':False,'current_reporting_geometry_approved':False,'statewide_eligible_write_in_allocation_verified':False,'collector_implemented':False,'calibrated_probability':False,'real2026_turnout_projection':False}
 (D/'finalseal.json').write_text(json.dumps(final,indent=2,allow_nan=False)+'\n')
 mf=D/'asset-manifest.json';paths=[STATE/'county-partisanship.md',STATE/'data/county-baselines.csv']+[p for p in D.rglob('*') if p.is_file() and p!=mf];paths=sorted(paths,key=lambda p:str(p.relative_to(STATE)));files=[]
 for p in paths:
  b=p.read_bytes();assert len(b)<40000000,(p,len(b));assert not any(x in p.parts for x in ['__pycache__','node_modules','.venv','.cache']);files.append({'path':str(p.relative_to(STATE)),'sha256':sha(b),'bytes':len(b)})
 assert len(files)==len({r['path'] for r in files})
 mf.write_text(json.dumps({'scope':'county-partisanship.md,data/county-baselines.csv,data/baselines/**; complete membership','excluded_only':'data/baselines/asset-manifest.json','self_hash_impossible':True,'files':files,'file_count_excluding_self':len(files),'bytes_excluding_self':sum(r['bytes'] for r in files),'max_stored_bytes':max(r['bytes'] for r in files),'external_original_dependencies':'source/original-references.json exact read-only body/receipt/hash pins, validated separately; no mutable-news/peer numerical build dependency'},indent=2)+'\n');assert mf.stat().st_size<40000000
 print(json.dumps({'sealed':True,'owned_files_including_manifest':len(files)+1,'total_bytes_excluding_manifest':sum(r['bytes'] for r in files),'max_stored_bytes':max(r['bytes'] for r in files),'manifest_sha256':sha(mf.read_bytes()),'finalseal_sha256':sha((D/'finalseal.json').read_bytes())}))
if __name__=='__main__':main()
