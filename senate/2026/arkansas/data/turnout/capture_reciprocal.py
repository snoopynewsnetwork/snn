#!/usr/bin/env python3
"""One-shot whole-body captures before bounded reciprocal comparison.

Mutable bodies go into exact-path tar members. Existing original gzip bodies
and historical archives are individually immutable-pinned, not duplicated.
This script never writes a producer/peer/shared path.
"""
import datetime,gzip,hashlib,io,json,pathlib,tarfile
P=pathlib.Path(__file__).resolve().parent;S=P.parents[1];REPO=P.parents[4]
H=P/'history/captured-final-reciprocal'
def sha(b):return hashlib.sha256(b).hexdigest()
def capture(label,manifest_path,expected_hash,expected_bytes,expected_targets):
    body=manifest_path.read_bytes();assert len(body)==expected_bytes and sha(body)==expected_hash
    mf=json.loads(body);assert len(mf['assets'])==expected_targets
    entries=mf['assets']+[dict(path=str(manifest_path.relative_to(S)),sha256=sha(body),bytes=len(body))]
    records=[];buf=io.BytesIO()
    with tarfile.open(fileobj=buf,mode='w') as tar:
        for r in entries:
            f=S/r['path'];b=f.read_bytes();assert len(b)==r['bytes'] and sha(b)==r['sha256'];assert len(b)<40000000
            immutable=(f.name.endswith('.body.gz') or f.name.endswith('.tar.gz'))
            rec=dict(r,role='whole original response gzip' if f.name.endswith('.body.gz') else 'whole historical archive' if f.name.endswith('.tar.gz') else 'whole captured authored/extracted/control/order/metadata/history body')
            if immutable:rec.update(storage='immutable-reference',reference_path=str(f.relative_to(REPO)))
            else:
                rec.update(storage='tar-member',member=r['path'])
                ti=tarfile.TarInfo(r['path']);ti.size=len(b);ti.mtime=0;tar.addfile(ti,io.BytesIO(b))
            records.append(rec)
    archive=gzip.compress(buf.getvalue(),mtime=0);assert len(archive)<40000000
    (H/(label+'.tar.gz')).write_bytes(archive)
    return dict(label=label,manifest_sha256=expected_hash,manifest_bytes=expected_bytes,body_count=len(entries),archive=label+'.tar.gz',archive_sha256=sha(archive),archive_bytes=len(archive),records=records)
def main():
    assert not H.exists(),'Capture already exists; never overwrite old bodies'
    # Both manifest populations are verified before writing any capture body.
    for path,h,n,count in [(P/'asset-manifest.json','d1558ec667c3e91f3727e24b5e1898b35d9c19208f3e55056517f310fbcb5693',197356,1027),(S/'data/baselines/asset-manifest.json','6d320e1b8b87fbea6788a7343544e39fab21dc81019c6f3e63251ba81baee8c4',58632,313)]:
        b=path.read_bytes();assert sha(b)==h and len(b)==n;mf=json.loads(b);assert len(mf['assets'])==count
        for r in mf['assets']:
            b=(S/r['path']).read_bytes();assert sha(b)==r['sha256'] and len(b)==r['bytes']
    pins=json.loads((P/'source/original-pins.json').read_text());assert len(pins)==19
    shared=[]
    for r in pins:
        b=(REPO/r['shared_original_path']).read_bytes();raw=gzip.decompress(b)
        assert sha(b)==r['stored_sha256'] and sha(raw)==r['raw_sha256']
        shared.append(dict(path=r['shared_original_path'],sha256=sha(b),bytes=len(b),raw_sha256=sha(raw),raw_bytes=len(raw),role='immutable complete original shared response with individually captured receipt'))
    own_core=P/'history/original-first-core/core.tar.gz';assert own_core.stat().st_size==3763512 and sha(own_core.read_bytes())=='b23716c17084a5a49a3534f1d494667818a36d0c27ec397f6bc9ba08bca2cf3f'
    peer_core=S/'data/baselines/history/original-first/core.tar.gz';assert peer_core.stat().st_size==2907840 and sha(peer_core.read_bytes())=='037de259b4abfd81806db94a5ca4aeadbe41fb56e893944c322310019f13a24a'
    H.mkdir(parents=True)
    own=capture('turnout-before',P/'asset-manifest.json','d1558ec667c3e91f3727e24b5e1898b35d9c19208f3e55056517f310fbcb5693',197356,1027)
    peer=capture('finished-baseline',S/'data/baselines/asset-manifest.json','6d320e1b8b87fbea6788a7343544e39fab21dc81019c6f3e63251ba81baee8c4',58632,313)
    rec=dict(schema='arkansas-complete-captured-final-reciprocal-v1',captured_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),before_peer_numeric_comparison=True,pre_edit_audit=dict(own_manifest_targets=1027,own_membership=1028,shared_originals=19,all_hashes_bytes_membership_passed=True),same_agent='43866295-c1c8-4f15-8933-67a99b3454c0',peer_agent='302e0938-9d85-4b49-99c1-87bbb564364d',profile=dict(name='Verification',provider='codex',model='gpt-6.1-sol',modeId='auto-review',thinkingOptionId='medium',fresh_four_profiles_and_provider_read=True,same_id_update_succeeded=True),own=own,peer=peer,shared_originals=shared,scope='Whole captured-final baseline bodies are provenance, not numerical/outcome equality. Peer producer/current/future outcomes are outside this capture and comparison.')
    (H/'capture.json').write_text(json.dumps(rec,indent=2)+'\n')
    print(json.dumps({k:{x:v[x] for x in ['body_count','archive_bytes','archive_sha256']} for k,v in [('own',own),('peer',peer)]},indent=2))
if __name__=='__main__':main()
