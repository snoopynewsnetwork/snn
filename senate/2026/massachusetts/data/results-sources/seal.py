"""Acyclic owned seal. Manifest excludes ONLY itself; validation is included."""
from pathlib import Path
import hashlib,json,subprocess,sys
O=Path(__file__).resolve().parent; S=O.parents[1]
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def main():
 subprocess.run([sys.executable,str(O/'validate.py')],check=True)
 core=[S/'official-results.md',S/'data/official-results-sources.csv',O/'validation.json',O/'reconstruction.json',O/'coverage.json',O/'readonly-inputs.json']
 seal=dict(schema='MA official-results acyclic final seal v1',authority_path='data/coordinator-priority-acceptance.json',bounded_owned_research_finished=True,coordinator_acceptance_or_publication=False,current_admission=False,future_exhaustion=False,pinned_owned=[pin(p) for p in core],manifest_relationship='asset-manifest.json covers this file; no reverse pin')
 (O/'final-seal.json').write_text(json.dumps(seal,indent=2)+'\n')
 paths=sorted([S/'official-results.md',S/'data/official-results-sources.csv',*[p for p in O.rglob('*') if p.is_file() and p!=O/'asset-manifest.json']])
 for p in paths:assert p.stat().st_size<40000000
 manifest=dict(schema='MA official-results exact owned manifest v1',authority_path='data/coordinator-priority-acceptance.json',excludes_only='data/results-sources/asset-manifest.json',owned=[pin(p) for p in paths])
 (O/'asset-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');assert (O/'asset-manifest.json').stat().st_size<40000000
 print(json.dumps(dict(status='sealed',owned_entries=len(paths),excludes_only_itself=True)))
if __name__=='__main__':main()
