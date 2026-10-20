#!/usr/bin/env python3
"""Seal all owned assets and pinned shared originals after offline validation."""
import hashlib,json,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;STATE=D.parent.parent
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def main():
    validator=runpy.run_path(str(D/'validate_turnout.py'))
    validation=validator['main'](check_manifest=False,write_result=True)
    assert validation['status'].startswith('pass_')and validation['independent_peer_agreement']is True
    names=['validation.json','priority-set.json','peer-audit/comparison.json','source/shared-originals.json',
           'peer-review-freeze/original-first-v1/snapshot-manifest.json',
           'peer-review-freeze/reciprocal-resume-v1/snapshot-manifest.json',
           'peer-review-freeze/baseline-final-v1/snapshot-manifest.json',
           '../../turnout.md','../county-turnout.csv']+[p.name for p in sorted(D.glob('*.py'))]
    sealed={n:dict(bytes=(D/n).stat().st_size,sha256=sha((D/n).read_bytes()))for n in names}
    dump(D/'final-seal.json',dict(status='sealed_original_source_and_bounded_reciprocal_offline_QA_coordinator_pending',sealed_files=sealed,independent_peer_agreement=True,coordinator_accepted=False,current_geometry_approved=False,manifest_policy='Every owned file except only current asset-manifest.json. Validation/finalseal carry no reverse current-manifest digest. Manifest externally pinned; exact final membership checked read-only.'))
    paths=[STATE/'turnout.md',STATE/'data/county-turnout.csv']+[p for p in D.rglob('*')if p.is_file()and p!=D/'asset-manifest.json']
    assert not any('__pycache__'in p.parts or 'node_modules'in p.parts for p in paths)
    assets=[]
    for p in sorted(paths):
        b=p.read_bytes();assert len(b)<40_000_000;assets.append(dict(path=p.relative_to(STATE).as_posix(),bytes=len(b),sha256=sha(b)))
    reused=[]
    for r in json.loads((D/'source/shared-originals.json').read_bytes()):
        p=STATE/r['immutable_body_path'];reused.append(dict(path=r['immutable_body_path'],source_id=r['id'],raw_bytes=r['bytes'],raw_sha256=r['raw_sha256'],stored_bytes=p.stat().st_size,stored_sha256=r['stored_sha256']))
    for r in json.loads((D/'source/municipal-authority-originals.json').read_bytes()):reused.append(dict(path=r['asset_path'],source_id=r['id'],raw_bytes=r['raw_bytes'],raw_sha256=r['raw_sha256'],stored_bytes=r['stored_bytes'],stored_sha256=r['stored_sha256']))
    dump(D/'asset-manifest.json',dict(schema='MA-turnout-assets-v2-complete-self-exclusion-only',base='senate/2026/massachusetts',owned_assets=assets,reused_originals=reused,hash_cycle_exclusions=['asset-manifest.json'],strict_byte_limit=40_000_000))
    before={p:sha(p.read_bytes())for p in [D/'asset-manifest.json',D/'validation.json',D/'final-seal.json']}
    validator['main'](check_manifest=True,write_result=False)
    assert all(sha(p.read_bytes())==h for p,h in before.items())
    print('Final complete manifest verified read-only:',len(assets),'owned assets; excludes only itself. SHA256',sha((D/'asset-manifest.json').read_bytes()))
if __name__=='__main__':main()
