"""Author once: seal first, full self-only-exclusion manifest last. No reverse manifest pin."""
from common import *

def owned():return sorted([p for p in M.rglob('*') if p.is_file()]+[S/'precinct-maps.md'])
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))
def originals():
 # These immutable full original reference lists are producer source contracts, not mutable news manifests.
 seen={}
 for name in ['data/turnout/asset-manifest.json','data/baselines/asset-manifest.json']:
  for p in parsed(S/name)['external_original_references']:
   b=(S/p['path']).read_bytes();assert len(b)==p['stored_bytes'] and sha(b)==p['stored_sha256']
   raw=gzip.decompress(b) if p.get('compression')=='gzip' else b
   assert len(raw)==p['raw_bytes'] and sha(raw)==p['raw_sha256']
   seen.setdefault(p['stored_sha256'],dict(path=p['path'],stored_bytes=len(b),stored_sha256=sha(b),raw_bytes=len(raw),raw_sha256=sha(raw),compression=p.get('compression')))
 return list(seen.values())
def run():
 assert not (M/'final-seal.json').exists() and not (M/'manifest.json').exists(),'Frozen seal/manifest exists'
 for p in ['qa/authority-replay.json','qa/historical-reconstruction.json','qa/publication-reconstruction.json','qa/validation.json','qa/reproduction.json']:
  assert parsed(M/p)['status']=='pass'
 seal=dict(schema='ri-maps-final-seal-v1',status='finished-qualified-historical-research',authority_path=AUTHORITY,scope='Original required fourth question. Full source/current/historical/original replay and deterministic offline map package. No optional coordinator or active official-worker dependency.',proofs=[pin(M/p) for p in ['qa/authority-replay.json','qa/historical-reconstruction.json','qa/publication-reconstruction.json','qa/native-audit.json','qa/pdf-rendering.json','qa/manual-visual-review.json','qa/validation.json','qa/reproduction.json']],read_only_after_manifest=True,external_admission_qualifications={k:'false/unknown: separate exact current/legal/source admission evidence not established here' for k in ['coordinator_acceptance','current_geography','current_reporting_IDs','legal_boundary','legal_native80_robustness','eligible_writein_exhaustion','November_returns','feed','measured_cadence','exact_remainder','collector','forecast','calibration']})
 dump(M/'final-seal.json',seal)
 manifest=dict(schema='ri-maps-full-manifest-v1',authority_path=AUTHORITY,excludes_only='maps/manifest.json',owned_files=[pin(p) for p in owned() if p!=M/'manifest.json'],external_complete_original_references=originals(),fixed_external_build_inputs=[pin(S/'data/turnout/priority-set.json'),pin(S/'data/baselines/extracts/native-inventory.json'),pin(S/'data/baselines/extracts/native-baselines.jsonl.gz')],source_graph_reconstruction='The entire external authority graph is replayed in memory at its fixed path. Its body/digest is never copied or reverse-pinned.',reconstruction='Every original response hop is reconstructed from ordered lossless gzip parts in each complete requests object; whole historical inputs use their exact immutable source references; final_audit.py independently reconstructs them.')
 assert all(r['bytes']<40000000 for r in manifest['owned_files']);dump(M/'manifest.json',manifest)
 print(json.dumps(dict(owned_files=len(manifest['owned_files']),external_originals=len(manifest['external_complete_original_references']),manifest=pin(M/'manifest.json'),seal=pin(M/'final-seal.json'),report=pin(S/'precinct-maps.md'))))
if __name__=='__main__':run()
