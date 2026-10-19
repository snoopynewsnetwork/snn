#!/usr/bin/env python3
"""Full owned asset membership; manifest self is the only exclusion."""
import pathlib,sys
sys.dont_write_bytecode=True
from acquire import D,readj,writej
from build import pin
S=D.parent.parent
def owned():return sorted([S/'official-results.md',S/'data/official-results-sources.csv']+[p for p in D.rglob('*')if p.is_file()and p!=D/'asset-manifest.json'])
def main():
    assets=[pin(p)for p in owned()];assert all(r['bytes']<40000000 for r in assets)
    refs={x['path']:x for x in readj(D/'frozen-inputs.json')['verified_inputs']}
    for r in readj(D/'optional-news-receipts.json')['append6_observations']:
        if r.get('asset'):
            p=S/'data/news'/r['asset'];refs[str(p.relative_to(S))]=pin(p)
    out=dict(schema='NE-official-owned-assets-v1',algorithm='SHA256',owned_artifacts=assets,exact_membership=True,excluded_self_only='data/results-sources/asset-manifest.json',validation_no_reverse_manifest_pin=True,external_original_references=sorted(refs.values(),key=lambda r:r['path']),historical_authority_path_only='data/coordinator-priority-acceptance.json',mutable_coordinator_or_news_aggregate_dependency=False,maximum_owned_stored_bytes=max(r['bytes']for r in assets),all_owned_stored_strictly_below40000000=True)
    writej(D/'asset-manifest.json',out);print('Manifest owned',len(assets),'external exact references',len(refs),'maximum',out['maximum_owned_stored_bytes'])
if __name__=='__main__':main()
