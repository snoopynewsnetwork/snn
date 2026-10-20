#!/usr/bin/env python3
"""Freeze this original-first worker's exact bodies before any peer derivatives.

Small authored/extracted bodies are independently losslessly gzipped. Unchanged
complete primary HTTP entities stay at their immutable-by-hash original paths.
No peer/coordinator diagnostic vote derivative is read. Never overwrite a freeze.
"""
import datetime,gzip,hashlib,json
from pathlib import Path
D=Path(__file__).resolve().parent;STATE=D.parent.parent
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    target=D/'peer-review-freeze/original-first-v1';assert not target.exists()
    manifest=json.loads((D/'asset-manifest.json').read_bytes())
    paths=[STATE/a['path']for a in manifest['owned_assets']]
    paths += [D/n for n in ['asset-manifest.json','validation.json','final-seal.json']]
    entries=[]
    for p in sorted(paths):
        b=p.read_bytes();rel=p.relative_to(STATE).as_posix()
        if p.name.endswith('.body.gz'):
            entries.append(dict(original_path=rel,bytes=len(b),sha256=sha(b),representation='unchanged primary original, read-only reuse by exact hash',immutable_reference=rel));continue
        z=gzip.compress(b,mtime=0);assert len(z)<40_000_000
        out=target/'bodies'/(rel+'.gz');out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(z)
        entries.append(dict(original_path=rel,bytes=len(b),sha256=sha(b),representation='exact original bytes, losslessly gzip compressed (including nested gzip when input already compressed)',frozen_path=out.relative_to(STATE).as_posix(),stored_bytes=len(z),stored_sha256=sha(z)))
    snapshot=dict(schema='MA-turnout-original-first-freeze-v1',worker_actual_id='eb66a7f4',created_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),basis='Own independent original-first extraction/report/repro/offline seal before actual peer launch or derivative inspection',peer_launched=False,peer_derivatives_inspected=False,coordinator_accepted=False,entries=entries,immutable_reused_input_entities=manifest['reused_originals'],qualification='This freeze records the bounded turnout question state, not reciprocal peer agreement or full state-question acceptance. Later live paths may change; reconstruct exact frozen bodies by gzip decompression and verify bytes/hash.')
    p=target/'snapshot-manifest.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(snapshot,indent=2)+'\n')
    for e in entries:
        if 'frozen_path'in e:
            z=(STATE/e['frozen_path']).read_bytes();b=gzip.decompress(z);assert sha(z)==e['stored_sha256']and sha(b)==e['sha256']and len(b)==e['bytes']
        else:assert sha((STATE/e['immutable_reference']).read_bytes())==e['sha256']
    print('Original-first freeze verified:',len(entries),'exact bodies/references;',len(manifest['reused_originals']),'full primary entity pins.')
if __name__=='__main__':main()
