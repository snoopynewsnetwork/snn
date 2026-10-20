#!/usr/bin/env python3
"""Seal all owned assets and exact shared immutable compressed originals; no self-hash cycle."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent

def main():
 paths={str(f.relative_to(P)) for f in P.rglob('*') if f.is_file() and f.name!='asset-manifest.json'}|{'../../county-partisanship.md','../county-baselines.csv'}
 for r in json.loads((P/'source/shared-sources.json').read_text()):paths.add(r['shared_asset'])
 out=[]
 for name in sorted(paths):
  f=P/name;b=f.read_bytes();assert len(b)<40000000,name;out.append(dict(path=name,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),ownership='read-only shared original' if name.startswith('../news/') else 'assigned report/data'))
 (P/'asset-manifest.json').write_text(json.dumps(dict(schema='1',self_exclusion='This manifest alone is excluded to avoid recursive self hashing. Validation included; final validator --check-assets is read-only.',assets=out,files=len(out),largest=max(r['bytes'] for r in out)),indent=2)+'\n');print(len(out),'assets sealed; largest',max(r['bytes'] for r in out))
if __name__=='__main__':main()
