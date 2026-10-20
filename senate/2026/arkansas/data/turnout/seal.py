#!/usr/bin/env python3
"""Write seal, then full owned manifest LAST. Run only after offline validation.

Subsequent command must be validate.py --sealed (read-only). This script does
not write a manifest digest into any file and creates no self-hash cycle.
"""
import datetime,hashlib,json,pathlib
P=pathlib.Path(__file__).resolve().parent;S=P.parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    validation=json.loads((P/'validation.json').read_text());assert validation['status']=='pass'
    core=['turnout.md','data/county-turnout.csv','data/turnout/priority-set.json','data/turnout/validation.json','data/turnout/source/original-pins.json','data/turnout/orders/2024-xlsx.csv','data/turnout/orders/statistics.json']
    seal=dict(sealed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='research complete within stated reported-candidate source scopes; independent peer and coordinator acceptance pending',primary_native_count=2841,parents=75,total_votes=1182676,minimum80_count=1056,minimum80_votes=946377,preceding_count=1055,preceding_votes=946007,remaining_count=1785,remaining_votes=236299,peer_inputs_read=False,core_outputs=[dict(path=r,sha256=digest(S/r),bytes=(S/r).stat().st_size) for r in core],manifest_rule='Every owned file except asset-manifest.json; no self-hash or reverse manifest digest. Manifest is written after this seal. Subsequent verification is read-only.')
    (P/'final-seal.json').write_text(json.dumps(seal,indent=2)+'\n')
    files=sorted([S/'turnout.md',S/'data/county-turnout.csv']+[f for f in P.rglob('*') if f.is_file() and f!=P/'asset-manifest.json'])
    assert all(f.stat().st_size<40000000 for f in files)
    manifest=dict(schema='arkansas-turnout-assets-v1',scope=['turnout.md','data/county-turnout.csv','data/turnout/**'],excluded_only='data/turnout/asset-manifest.json',assets=[dict(path=str(f.relative_to(S)),bytes=f.stat().st_size,sha256=digest(f)) for f in files])
    (P/'asset-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(assets=len(files),total_stored_bytes=sum(f.stat().st_size for f in files),largest_object_bytes=max(f.stat().st_size for f in files),manifest_sha256=digest(P/'asset-manifest.json'),priority_sha256=digest(P/'priority-set.json')),indent=2))
if __name__=='__main__':main()
