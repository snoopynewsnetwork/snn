"""Authoring only: complete preterminal witness, seal, manifest LAST; no reverse pin."""
from common import *
import tarfile
def owned():
    return [S/'official-results.md',S/'data/official-results-sources.csv',*sorted(p for p in R.rglob('*') if p.is_file())]
def main():
    assert not (R/'final-seal.json').exists() and not (R/'asset-manifest.json').exists()
    for name in ['validation','reproduction','authority-replay','original-audit']:
        assert parsed(R/'qa'/f'{name}.json')['status']=='pass',name
    before=owned();originals=[];frozen=[];buffer=io.BytesIO()
    with tarfile.open(fileobj=buffer,mode='w',format=tarfile.PAX_FORMAT) as tf:
        for p in before:
            rec=pin(p);assert rec['bytes']<40000000
            if p.name.endswith('.body.gz'):
                b=p.read_bytes();raw=gzip.decompress(b);assert p.name==sha(raw)+'.body.gz'
                originals.append(dict(**rec,raw_sha256=sha(raw),raw_bytes=len(raw),storage='immutable_original_reference'))
            else:
                b=p.read_bytes();ti=tarfile.TarInfo(rec['path']);ti.size=len(b);ti.mode=0o644;ti.mtime=0;ti.uid=ti.gid=0;ti.uname=ti.gname='';tf.addfile(ti,io.BytesIO(b));frozen.append(rec)
    raw=buffer.getvalue();compressed=gzip.compress(raw,mtime=0)
    # Whole streams split losslessly if either raw or compressed representation reaches40M.
    if len(raw)>=40000000:
        parts=[]
        for i,start in enumerate(range(0,len(raw),39000000)):
            part=gzip.compress(raw[start:start+39000000],mtime=0);assert len(part)<40000000
            p=R/'witness'/f'bodies.tar.part{i:03}.gz';write(p,part);parts.append(pin(p))
        storage=dict(kind='ordered_raw_tar_parts_gzip',parts=parts,tar_bytes=len(raw),tar_sha256=sha(raw))
    else:
        assert len(compressed)<40000000
        p=R/'witness/bodies.tar.gz';write(p,compressed)
        storage=dict(kind='tar_gzip',archive=pin(p),tar_bytes=len(raw),tar_sha256=sha(raw))
    capture=dict(schema='ri-official-complete-preterminal-witness-v1',storage=storage,frozen_bodies=frozen,immutable_original_refs=originals,
        scope='Every preterminal owned body complete, original entities referenced once. Witness index/seal/manifest are terminal acyclic records, all included in final manifest; no acceptance body/digest retained.')
    write(R/'witness/capture.json',dump(capture))
    write(R/'final-seal.json',dump(dict(schema='ri-official-final-seal-v1',authority_path=AUTHORITY,status='bounded_research_complete_bytes_frozen_after_final_audit',capture=pin(R/'witness/capture.json'),validation=pin(R/'qa/validation.json'),reproduction=pin(R/'qa/reproduction.json'),authority_replay=pin(R/'qa/authority-replay.json'),original_audit=pin(R/'qa/original-audit.json'),current_admission=False,collector_approval=False,forecast_approval=False,coordinator_alone_publishes=True,no_reverse_manifest_digest=True)))
    files=owned();mf=R/'asset-manifest.json'
    assert mf not in files
    write(mf,dump(dict(schema='ri-official-exact-manifest-v1',excludes_only_itself=True,owned_assets=[pin(p) for p in sorted(files)],external_inputs=pin(R/'external-inputs.json'),authority_path=AUTHORITY,qualification='Final audit must be read-only after this manifest. No reverse current-manifest pin or acceptance digest. All external complete body/history/object references are exact and read-only.')))
    print(json.dumps(dict(owned_targets=len(files),manifest=pin(mf),preterminal_bodies=len(frozen),immutable_originals=len(originals))))
if __name__=='__main__':main()
