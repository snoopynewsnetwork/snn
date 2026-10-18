#!/usr/bin/env python3
"""Store directly usable small PDF/ZIP originals once; migrate only owned storage."""
import json
from acquire import ROOT, entity, sha, dump
def materialize():
    canonical={}
    for p in sorted((ROOT/'receipts').glob('*.json')):
        r=json.loads(p.read_text());b=entity(r)
        if r.get('status')!=200:continue
        ext='pdf' if b.startswith(b'%PDF-') else 'zip' if b.startswith(b'PK\x03\x04') else None
        if not ext or len(b)>=40_000_000:continue
        out=canonical.get((sha(b),ext),ROOT/'originals'/f'{r["id"]}.{ext}');out.parent.mkdir(exist_ok=True)
        if out.exists():assert out.read_bytes()==b
        else:out.write_bytes(b)
        canonical[(sha(b),ext)]=out
        r['storage']=[dict(path=str(out.relative_to(ROOT)),encoding='identity',order=0,
                           entity_bytes=len(b),entity_sha256=sha(b),stored_bytes=len(b),stored_sha256=sha(b))]
        dump(p,r)
    used={s['path'] for p in (ROOT/'receipts').glob('*.json') for s in json.loads(p.read_text())['storage']}
    for p in (ROOT/'objects').glob('*.gz'):
        if str(p.relative_to(ROOT)) not in used:p.unlink()
    for p in (ROOT/'originals').glob('*'):
        if str(p.relative_to(ROOT)) not in used:p.unlink()
if __name__=='__main__':materialize()
