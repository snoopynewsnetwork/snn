#!/usr/bin/env python3
"""Seal the independent package without Git or peer inputs.

The v1 witness uses exclusive creation. It must never be overwritten on resume.
The asset manifest excludes only itself to avoid circular self-hashing.
"""
from pathlib import Path
import datetime,hashlib,json
OUT=Path(__file__).resolve().parents[1];STATE=OUT.parents[1];NEWS=OUT.parent/'news'
sha=lambda b:hashlib.sha256(b).hexdigest()
def record(p):
    b=p.read_bytes();assert len(b)<40000000
    return dict(path=str(p.relative_to(STATE)),bytes=len(b),sha256=sha(b))
def allowned():return [STATE/'turnout.md',OUT.parent/'county-turnout.csv']+sorted(p for p in OUT.rglob('*')if p.is_file())
def main():
    witness=OUT/'pre-peer-witness-v1.json';assert not witness.exists(),'Immutable v1 witness already exists; do not overwrite it.'
    snapshot=json.loads((NEWS/'manifest.json').read_bytes())
    official=[r for r in snapshot if r['id'].startswith('sos-')]
    # Metadata snapshot binds the shared public parent/form/CDX routes and
    # unsuccessful observations without copying any large response body.
    (OUT/'source/shared-authority-chain-snapshot.json').write_text(json.dumps(official,indent=2)+'\n')
    # Caller must regenerate validation after this new snapshot is present.
    validation=json.loads((OUT/'validation.json').read_bytes())
    planned_count=len(allowned())+2  # witness and manifest
    assert validation['checks'][-1]['detail']['owned_files_after_seal']==planned_count, 'Run validate.py --write after preparing authority snapshot'
    files=[p for p in allowned()if p.name not in ['asset-manifest.json','pre-peer-witness-v1.json']]
    obj=dict(schema_version='oregon.turnout.pre-peer-witness.v1',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        immutable=True,worker_role='Oregon turnout original-first',peer_agent_id=None,
        peer_derivatives_consulted=False,
        independence_statement='Original PDF/CSV/ZIP bytes independently parsed. Coordinator narrative and preflight scripts were read for required orientation; no coordinator result JSON or peer numeric derivative was an extraction/build input. Candidate count tables are bound to original source positions. No peer was launched or contacted.',
        coverage='All36 county candidate and statistical participation controls; 510 verified 2024 native rows in5 parents;31 unclosed priority-year parents; historical native normalization partial.',
        canonical_native_priority_available=False,coordinator_acceptance=False,
        pinned_files=[record(p)for p in sorted(files)])
    with witness.open('x')as f:json.dump(obj,f,indent=2);f.write('\n')
    shared={}
    for r in official:
        names=[]
        if r.get('asset'):names.append(r['asset'])
        names +=[p['asset']for p in r.get('asset_parts',[])]
        names +=[v for k,v in r.items()if k.endswith('_asset')and isinstance(v,str)]
        for name in names:
            p=NEWS/name
            assert p.exists(),(r['id'],name)
            shared[str(p)]=record(p)
    shared[str(OUT.parent/'audit_precinct_archives.py')]=record(OUT.parent/'audit_precinct_archives.py')
    manifest=dict(schema_version='oregon.turnout.asset-manifest.v1',self_exclusion='asset-manifest.json only; SHA256 self-reference is not defined',
        owned_assets=[record(p)for p in sorted(allowned())if p.name!='asset-manifest.json'],
        shared_assets=sorted(shared.values(),key=lambda r:r['path']),
        original_reconstruction='source/shared-original-pins.json, source/original-inventory.json and source/shared-authority-chain-snapshot.json retain raw/original/stored/member hashes, headers, public parent/download chains and exact ordered-byte recipes. Shared original bodies are not duplicated.',
        strict_individual_artifact_byte_limit=40000000)
    (OUT/'asset-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(witness_sha256=sha(witness.read_bytes()),manifest_sha256=sha((OUT/'asset-manifest.json').read_bytes()),owned_assets=len(manifest['owned_assets']),shared_assets=len(manifest['shared_assets']))))
if __name__=='__main__':main()
