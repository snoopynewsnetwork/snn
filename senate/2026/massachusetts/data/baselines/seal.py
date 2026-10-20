#!/usr/bin/env python3
"""Final manifest excludes ONLY itself; seal has no reverse manifest digest."""
import datetime,json
from extract_originals import ROOT,dump,sha
from validate import owned,main as validate
STATE=ROOT.parent.parent
def entry(p):return dict(path=str(p.relative_to(STATE)),bytes=p.stat().st_size,sha256=sha(p.read_bytes()))
def main():
    validate()
    seal=ROOT/'final-seal.json'
    assert not seal.exists(),'Do not overwrite an existing reviewed final seal'
    chosen=[STATE/'county-partisanship.md',ROOT.parent/'county-baselines.csv',ROOT/'validation.json',ROOT/'source/original-first-freeze.json',ROOT/'source/statistics-original-first-freeze.json',ROOT/'priority-set.json',ROOT/'scenarios/settings.json',ROOT/'calculate.py',ROOT/'peer-audit/comparison.json']
    dump(seal,dict(status='completed_qualified_historical_research',sealed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),pinned_completed_outputs=[entry(p) for p in chosen],priority_basis='All2394 literal2024Warren/Deaton native contexts;1470minimum80',asset_integrity='Final asset inventory excludes only its own self; this seal pins no inventory digest',current_geometry_approved=False,coordinator_acceptance=False,calibrated_probability=False))
    path=ROOT/'asset-manifest.json';assets=[entry(p) for p in owned() if p!=path]
    pins=json.loads((ROOT/'source/shared-originals.json').read_text())['sources'];reused={}
    for r in pins:
        p=(ROOT/r['shared_path']).resolve();reused[str(p)]=entry(p)
    p=ROOT.parent/'preflight_primary_sources.py';reused[str(p)]=entry(p)
    dump(path,dict(schema='MA-baselines-final-assets-v1',owned_assets=assets,reused_readonly_inputs=list(reused.values()),self_exclusion='data/baselines/asset-manifest.json only',byte_limit_strict=40000000,compression='Lossless gzip mtime0; no split/reconstruction required; every stored original and derivative is below limit'))
    validate(sealed=True)
if __name__=='__main__':main()
