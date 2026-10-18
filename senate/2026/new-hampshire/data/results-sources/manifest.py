#!/usr/bin/env python3
"""Complete owned inventory; immutable first-wave/raw inputs reused read only."""
import json,pathlib
from acquire import ROOT,SOURCE,dump,sha,LIMIT
STATE=ROOT.parent.parent
def owned():
    return sorted([STATE/'official-results.md',STATE/'data/official-results-sources.csv']+[p for p in ROOT.rglob('*') if p.is_file() and p!=ROOT/'asset-manifest.json'])
def record(p):
    b=p.read_bytes();assert len(b)<LIMIT,p
    return {'path':str(p.relative_to(STATE)),'bytes':len(b),'sha256':sha(b)}
def reference_paths():
    paths=set()
    # Both first-wave manifests are final freezes, independently verified before this step.
    for path in ['data/turnout/asset-manifest.json','data/baselines/asset-manifest.json']:
        paths.add(path)
        for r in json.load(open(STATE/path))['assets']:paths.add(r['path'])
    paths.update(['data/coordinator-priority-acceptance.json','data/coordinator-priority-keys.txt','data/coordinator-native-contract-review.json'])
    # Retain every original/metadata/parent capture cited in the frozen turnout source chain.
    for r in json.load(open(STATE/'data/turnout/source-inventory.json')):
        for k in ['path','metadata_path']:
            if r.get(k):paths.add(str((STATE/'data/turnout'/r[k]).resolve().relative_to(STATE)))
    for refname in ['history-original-references.json','control-original-references.json','current-ballot-references.json']:
        for r in json.load(open(SOURCE/refname)):
            for k in ['path','metadata_path','headers_path','parent_metadata_path']:
                if r.get(k):paths.add(r[k])
    # Farmington parent original/HTTP headers, not merely the parent metadata.
    for path in ['data/baselines/source/farmington-clerk.body.gz','data/baselines/source/farmington-clerk.headers.txt']:
        if (STATE/path).exists():paths.add(path)
    # The shared original record already embeds headers; no mutable coordinator aggregate news manifest pin.
    return sorted(paths)
def build():
    assets=[record(p) for p in owned()];refs=[record(STATE/p) for p in reference_paths()]
    assert not any('data/maps' in r['path'] or r['path']=='data/news/manifest.json' for r in refs)
    dump(ROOT/'asset-manifest.json',{'schema_version':'nh-official-owned-assets-1','scope':'official-results.md; data/official-results-sources.csv; data/results-sources/**','self_exclusion':'Only data/results-sources/asset-manifest.json excludes its own recursive hash. All other owned files, including deterministic validation, are included.','path_base':'senate/2026/new-hampshire','owned_assets':assets,'owned_asset_count':len(assets),'owned_asset_bytes':sum(r['bytes'] for r in assets),'read_only_references':refs,'read_only_reference_count':len(refs),'reference_policy':'Final first-wave owned assets and exact immutable raw originals/source metadata. Coordinator acceptance is external authority, no reverse contract hash. No mutable maps/news aggregate/report pins.','object_limit_exclusive':LIMIT})
    verify()
    print('PASS: owned manifest',len(assets),'files;',len(refs),'read-only references; every object <40000000')
def verify():
    m=json.load(open(ROOT/'asset-manifest.json'));assert m['owned_asset_count']==len(m['owned_assets'])
    assert [r['path'] for r in m['owned_assets']]==[str(p.relative_to(STATE)) for p in owned()]
    for r in m['owned_assets']+m['read_only_references']:assert record(STATE/r['path'])==r,r['path']
if __name__=='__main__':build()
