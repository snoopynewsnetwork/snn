"""Freeze full original-first bodies, fixed seal, then owned manifest LAST.
Run validate_turnout.py --write first. Final audit is a separate read-only command.
"""
import io,tarfile,datetime,json
from common import *
from acquire import allreceipts
def owned():return sorted([STATE/'turnout.md',STATE/'data/county-turnout.csv']+[p for p in ROOT.rglob('*')if p.is_file()])
def run():
    assert not (ROOT/'final-seal.json').exists(),'Immutable seal already exists; do not overwrite'
    validation=json.loads((ROOT/'validation.json').read_text());assert validation['status']=='passed'
    excluded={ROOT/'asset-manifest.json',ROOT/'final-seal.json',ROOT/'qa/pre-peer-body-witness.json',ROOT/'qa/pre-peer-bodies.tar.gz'}
    rawpaths={};references={}
    for r in allreceipts():
        for h in ([r]if 'stored_path'in r else [])+r.get('hops',[]):
            path=(ROOT/h['stored_path']).resolve();stored=path.read_bytes();raw=original(h)
            info=dict(path=str(path.relative_to(STATE)),stored_sha256=sha(stored),stored_bytes=len(stored),raw_sha256=sha(raw),raw_bytes=len(raw),compression=h.get('compression'),source_ids=[])
            if info['stored_sha256']not in references:references[info['stored_sha256']]=info
            references[info['stored_sha256']]['source_ids'].append(r['id'])
            rawpaths[path]=True
    buffer=io.BytesIO();items=[]
    with tarfile.open(fileobj=buffer,mode='w',format=tarfile.PAX_FORMAT)as tar:
        for p in owned():
            if p in excluded or p.resolve()in rawpaths:continue
            b=p.read_bytes();name=str(p.relative_to(STATE));entry=tarfile.TarInfo(name);entry.size=len(b);entry.mtime=0;entry.mode=0o644;entry.uid=entry.gid=0;entry.uname=entry.gname='';tar.addfile(entry,io.BytesIO(b));items.append(dict(path=name,sha256=sha(b),bytes=len(b)))
    by=buffer.getvalue();gzwrite(ROOT/'qa/pre-peer-bodies.tar.gz',by);packed=(ROOT/'qa/pre-peer-bodies.tar.gz').read_bytes();assert len(packed)<40000000
    for v in references.values():v['source_ids']=sorted(set(v['source_ids']))
    dump(ROOT/'qa/pre-peer-body-witness.json',dict(schema='ri-original-first-full-body-witness-v1',frozen_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),peer_derivative_accessed=False,peer_agent_id='5d9f9b63-0cf2-4b55-b52b-579cbc1d76d1',frozen_bodies=items,immutable_original_references=list(references.values()),body_archive=dict(path='qa/pre-peer-bodies.tar.gz',stored_sha256=sha(packed),stored_bytes=len(packed),compression='gzip',uncompressed_tar_sha256=sha(by),uncompressed_tar_bytes=len(by)),reconstruction='gzip.decompress the body archive, then read each exact tar member path; original entity bytes are gzip.decompress of each referenced stored body. Every complete witness body and original is verified byte-for-byte; no partial metadata-only witness.',exclusions='Raw original objects reused by exact immutable references, never duplicate huge ZIP/PDF bytes. Seal and manifest are subsequent terminal evidence and are not inputs to earlier bodies.'))
    witness=(ROOT/'qa/pre-peer-body-witness.json').read_bytes();v=(ROOT/'validation.json').read_bytes();contract=(ROOT/'priority-set.json').read_bytes()
    dump(ROOT/'final-seal.json',dict(schema='ri-turnout-final-seal-v1',phase='original-first offline research complete; peer/coordinator acceptance pending',peer_derivatives_accessed=False,peer_agent_id='5d9f9b63-0cf2-4b55-b52b-579cbc1d76d1',primary_contract=dict(path='priority-set.json',sha256=sha(contract),bytes=len(contract)),validation=dict(path='validation.json',sha256=sha(v),bytes=len(v),status='passed',checks=len(validation['checks'])),full_body_witness=dict(path='qa/pre-peer-body-witness.json',sha256=sha(witness),bytes=len(witness)),body_archive=dict(path='qa/pre-peer-bodies.tar.gz',sha256=sha(packed),bytes=len(packed)),final_read_only_audit_command='python3 -B senate/2026/rhode-island/data/turnout/validate_turnout.py',final_audit_required_after_manifest=True,no_manifest_reverse_pin=True))
    assets=[]
    for p in owned():
        if p==ROOT/'asset-manifest.json':continue
        b=p.read_bytes();assert len(b)<40000000;assets.append(dict(path=str(p.relative_to(STATE)),sha256=sha(b),bytes=len(b)))
    # Last owned write. All following operations are strictly read-only.
    dump(ROOT/'asset-manifest.json',dict(schema='ri-turnout-owned-assets-v1',excludes_only_itself=True,owned_assets=assets,external_original_references=[x for x in references.values()if not (STATE/x['path']).resolve().is_relative_to(ROOT)],peer_agreement='pending',coordinator_acceptance='pending'))
    print(json.dumps(dict(seal_sha256=sha((ROOT/'final-seal.json').read_bytes()),manifest_sha256=sha((ROOT/'asset-manifest.json').read_bytes()),witness_sha256=sha(witness),contract_sha256=sha(contract),owned_assets=len(assets),witness_bodies=len(items),immutable_original_objects=len(references),archive_stored_bytes=len(packed))))
if __name__=='__main__':run()
