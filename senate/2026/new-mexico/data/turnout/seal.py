#!/usr/bin/env python3
"""Acyclic final seal, exact all-file manifest, and read-only final audit."""
from pathlib import Path
import sys,json,hashlib,gzip
D=Path(__file__).resolve().parent;S=D.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
def owned():return sorted(set([S/'turnout.md',S/'data/county-turnout.csv']+[p for p in D.rglob('*')if p.is_file()and p!=D/'asset-manifest.json']))
def sources():
 out={}
 for r in json.loads((D/'acquisition.json').read_text()):
  for z in [r]+r.get('redirects',[]):
   if 'asset'not in z:continue
   p=S/z['asset'];b=p.read_bytes();assert sha(b)==z['stored_sha256']and sha(gzip.decompress(b))==z['raw_sha256'];out[z['asset']]=dict(path=z['asset'],sha256=sha(b),bytes=len(b),raw_sha256=z['raw_sha256'])
 # Exact read-only primary dependencies of the frozen peer capture also remain pinned.
 cap=json.loads((D/'history/baseline-final-peer/capture.json').read_text());rec=next(r for r in cap['records']if r['path']=='data/baselines/asset-manifest.json');mf=json.loads(gzip.decompress((S/rec['body']).read_bytes()))
 for r in mf['external_original_assets']:
  b=(S/r['path']).read_bytes();assert sha(b)==r['sha256']and len(b)==r['bytes']
  if r.get('raw_sha256'):assert sha(gzip.decompress(b))==r['raw_sha256']
  if r['path']not in out:out[r['path']]=dict(path=r['path'],sha256=r['sha256'],bytes=r['bytes'],raw_sha256=r.get('raw_sha256'),scope='immutable_captured_peer_primary_reference_not_new_source_admission')
 return list(out.values())
def audit():
 mf=json.loads((D/'asset-manifest.json').read_text());actual={str(p.relative_to(S))for p in owned()};declared={r['path']for r in mf['owned_assets']};assert actual==declared,(actual-declared,declared-actual)
 checks=0
 for r in mf['owned_assets']+mf['source_assets']:
  b=(S/r['path']).read_bytes();assert len(b)==r['bytes']and sha(b)==r['sha256']and len(b)<40_000_000;checks+=3
 assert not any(p.name in ['__pycache__','node_modules','.venv','venv']for p in D.rglob('*')if p.is_dir())
 assert not any(r['path']=='data/turnout/asset-manifest.json'for r in mf['owned_assets'])
 seal=json.loads((D/'final-seal.json').read_text());assert 'current_manifest_sha256'not in seal
 for path,h in seal['sealed_target_hashes'].items():assert sha((S/path).read_bytes())==h;checks+=1
 print(json.dumps(dict(audit='passed_read_only',checks=checks,owned_files=len(actual),source_objects=len(mf['source_assets']),manifest_sha256=sha((D/'asset-manifest.json').read_bytes()))))
def main():
 if '--audit'in sys.argv:audit();return
 v=json.loads((D/'validation.json').read_text());r=json.loads((D/'peer-reconciliation.json').read_text());assert v['status']=='offline_pass_qualified_research_scope'and r['status']=='passed_bounded_source_core'
 targets=[S/'turnout.md',S/'data/county-turnout.csv']+[D/x for x in ['validation.json','peer-reconciliation.json','negative-fixtures.json','registration-grand-controls.json','priority-set.json','original-first-witness-v2.json','history/turnout-pre-peer/capture.json','history/baseline-final-peer/capture.json']]
 seal=dict(schema='nm-turnout-final-seal-1',status='qualified_source_core_peer_agreement_complete',validation_checks=v['passed_checks'],peer_comparison_checks=r['comparison_checks'],independent_negative_fixtures=13,peer_agent_id=r['peer_agent_id'],comparison_scope=r['coverage'],exclusions=r['exclusions'],coordinator_acceptance=False,accepted_for_dispatch=False,certified_native_minimum80=None,dispatch_keys=[],source_counts_keys_orders_unchanged=True,immutable_history_reconstruction='history/turnout-pre-peer/capture.json and history/baseline-final-peer/capture.json',sealed_target_hashes={str(p.relative_to(S)):sha(p.read_bytes())for p in targets},acyclic='Seal written after validation and before manifest. Neither seal nor validation hashes the current manifest; historical/peer manifest pins are snapshot evidence only.')
 (D/'final-seal.json').write_text(json.dumps(seal,ensure_ascii=False,indent=2)+'\n')
 files=owned();assert all(p.stat().st_size<40_000_000 for p in files)
 mf=dict(schema_version=2,self_exclusion='Exclude ONLY this current asset-manifest.json to avoid recursive self hashing. Every other owned file, including validation, final seal, histories, archived manifests, proof and reproduction, is included.',owned_assets=[dict(path=str(p.relative_to(S)),sha256=sha(p.read_bytes()),bytes=p.stat().st_size,ownership='NM turnout exclusive')for p in files],source_assets=sources(),all_objects_strictly_below_40000000=True)
 (D/'asset-manifest.json').write_text(json.dumps(mf,ensure_ascii=False,indent=2)+'\n');audit()
if __name__=='__main__':main()
