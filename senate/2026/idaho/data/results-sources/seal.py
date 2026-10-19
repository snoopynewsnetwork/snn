#!/usr/bin/env python3
"""Seal owned membership only; no Git operations and no acceptance hash."""
from pathlib import Path
import gzip,hashlib,json
D=Path(__file__).resolve().parent;S=D.parent.parent

def pin(p):
 b=p.read_bytes();assert len(b)<40000000,(str(p),len(b));v=dict(path=str(p.relative_to(S)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 if p.suffix=='.gz':
  raw=gzip.decompress(b);v.update(reconstructed_bytes=len(raw),reconstructed_sha256=hashlib.sha256(raw).hexdigest())
 return v

def main():
 paths=[p for p in D.rglob('*') if p.is_file() and p!=D/'manifest.json']+[S/'official-results.md',S/'data/official-results-sources.csv'];g=json.loads((D/'historical-source-graph.json').read_bytes());out=dict(schema='idaho-official-research-seal-v1',external_acceptance_path='data/coordinator-priority-acceptance.json',self_excluded_to_avoid_cycle='data/results-sources/manifest.json',owned=[pin(p) for p in sorted(paths)],immutable_external_complete_references=g['immutable_complete_files'],current_approved=False)
 b=(json.dumps(out,indent=2,ensure_ascii=False)+'\n').encode();assert len(b)<40000000;(D/'manifest.json').write_bytes(b);print('sealed owned entries',len(paths),'external complete references',len(g['immutable_complete_files']),'manifest bytes',len(b))
if __name__=='__main__':main()
