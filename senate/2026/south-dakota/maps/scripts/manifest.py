"""Exact owned asset membership. Self-exclusion only; validation stays included."""
from common import *
def main():
 paths=[STATE/'precinct-maps.md']+[p for p in MAPS.rglob('*') if p.is_file() and p!=MAPS/'asset-manifest.json']
 assert not any('__pycache__' in p.parts for p in paths)
 entries=[pin(p)for p in sorted(paths,key=lambda p:str(p))]
 assert all(p['bytes']<40000000 for p in entries)
 dump('asset-manifest.json',dict(schema='SD-exact-owned-map-assets-v1',paths_relative_to='senate/2026/south-dakota',stored_limit_exclusive=40000000,self_exclusion_only='maps/asset-manifest.json',owned_assets=entries,read_only_reference_manifest='maps/source/read-only-references.json',approval_scope='Qualified historical research only; coordinator alone reviews/publishes.'))
 print(len(entries),'owned files',sum(e['bytes']for e in entries),'bytes; largest',max(entries,key=lambda x:x['bytes']))
if __name__=='__main__':main()
