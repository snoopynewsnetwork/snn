"""Seal every owned file, excluding exactly this manifest and no other owned file."""
from common import *
from validate import owned_files
def main():
 files=owned_files();assets=[]
 for p in files:
  b=p.read_bytes();assert len(b)<40000000;assets.append(dict(path=str(p.relative_to(STATE)),bytes=len(b),sha256=sha(b)))
 write(HERE/'asset-manifest.json',dict(schema='il-official-results-owned-seal/v1',scope='exact complete owned membership; historical external authority consulted by path only',excluded_owned_paths=['data/results-sources/asset-manifest.json'],owned_assets=assets,external_authority_path='data/coordinator-priority-acceptance.json',original_asset_reference_ledger='data/results-sources/original-asset-references.json',all_current_joins_and_admissions_unapproved=True))
 print('sealed',len(assets),'assets',sum(v['bytes'] for v in assets),'bytes')
if __name__=='__main__':main()
