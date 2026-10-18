#!/usr/bin/env python3
"""Hash every owned asset, including QA, report and CSV; exclude only self."""
import hashlib
import json
import pathlib

ROOT=pathlib.Path(__file__).resolve().parent
STATE=ROOT.parent.parent


def main():
    paths=[STATE/'turnout.md',ROOT.parent/'county-turnout.csv']+sorted(p for p in ROOT.rglob('*')if p.is_file()and p.name!='asset-manifest.json')
    assets=[]
    for p in paths:
        assert '__pycache__'not in p.parts and p.suffix!='.pyc',p
        b=p.read_bytes();assert len(b)<40_000_000
        assets.append(dict(path=str(p.relative_to(STATE)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
    obj=dict(schema_version='nh-owned-assets-1',scope='Only turnout.md, data/county-turnout.csv, data/turnout/**',self_exclusion='asset-manifest.json excluded from its own hash inventory to avoid recursive self-hash; every other owned file included.',original_reference_policy='Shared originals reused read-only by exact stored/decoded hashes in source/shared-originals.json; not duplicated.',assets=assets)
    (ROOT/'asset-manifest.json').write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps(dict(owned_assets=len(assets),largest_bytes=max(x['bytes']for x in assets),total_stored_bytes=sum(x['bytes']for x in assets))))


if __name__=='__main__':main()
