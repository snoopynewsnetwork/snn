"""Seal exact owned path set. Manifest excludes only itself; no external writes."""
import json
import acquire as a
def owned():
    return sorted([a.ROOT/'official-results.md',a.ROOT/'data/official-results-sources.csv']+[p for p in a.OUT.rglob('*')if p.is_file()and p!=a.OUT/'asset-manifest.json'])
def run():
    entries=[a.pin(p)for p in owned()]
    assert all(e['bytes']<40_000_000 for e in entries)
    result=dict(schema='exact_owned_asset_manifest_v1',root='senate/2026/mississippi',ownership=['official-results.md','data/official-results-sources.csv','data/results-sources/**'],exclusion_paths=['data/results-sources/asset-manifest.json'],entries=entries,total_files=len(entries),total_bytes=sum(e['bytes']for e in entries),external_original_policy='Exact read-only original references verified separately; never duplicated or included as owned files.')
    a.save(a.OUT/'asset-manifest.json',result)
    assert(a.OUT/'asset-manifest.json').stat().st_size<40_000_000
    return result
if __name__=='__main__':
    r=run();print(r['total_files'],r['total_bytes'],a.pin(a.OUT/'asset-manifest.json'))
