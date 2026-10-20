"""Read-only peer capture; no peer writer is imported or executed."""
import io,tarfile,gzip,json,hashlib
from common import *
def run():
    peer=STATE/'data/baselines';mb=(peer/'asset-manifest.json').read_bytes()
    assert len(mb)==116652 and sha(mb)=='f3b33d30631cec93796c4aab2becec82a49982da39878421f11c22ea5e1a8620'
    m=json.loads(mb);assert len(m['owned_assets'])==234
    for path,size,digest in [('final-seal.json',45808,'7193431c53e45c059a468cb24d821f149d27a57a42c3c7006540c1e956f353bd'),('validation.json',51323,'b4111149b7661d2f2965ebe50354b0f05f81be7b8e0576135aeb259d5d9d131a'),('witness/original-first-proof.json',16162,'a3cdfdbde06e4b18bcefc2616f3fcf84089d27ec6a6049d223e67da3ed432a01'),('reciprocal/reconciliation.json',3963007,'77b4fc4aebcd3dc88aff8fb6de7ae10312b320b5a4ce7ba514bfe1b4ee95ad0a')]:
        b=(peer/path).read_bytes();assert len(b)==size and sha(b)==digest
    old=json.loads((ROOT/'qa/pre-peer-body-witness.json').read_text());original_hashes={x['raw_sha256']for x in old['immutable_original_references']}
    records=m['owned_assets']+[dict(path='data/baselines/asset-manifest.json',sha256=sha(mb),bytes=len(mb))];frozen={};refs=[]
    for item in records:
        b=(STATE/item['path']).read_bytes();assert len(b)==item['bytes']and sha(b)==item['sha256']
        try:raw=gzip.decompress(b)
        except (OSError,EOFError):raw=b
        if sha(raw)in original_hashes:refs.append(dict(**item,raw_sha256=sha(raw),raw_bytes=len(raw),compression='gzip'if raw!=b else None))
        else:frozen[item['path']]=b
    out=io.BytesIO()
    with tarfile.open(fileobj=out,mode='w',format=tarfile.PAX_FORMAT)as t:
        for name,b in sorted(frozen.items()):
            e=tarfile.TarInfo(name);e.size=len(b);e.mtime=0;e.mode=420;t.addfile(e,io.BytesIO(b))
    tar=out.getvalue();packed=gzip.compress(tar,mtime=0);dest=ROOT/'reciprocal/peer-finished-capture';dest.mkdir(parents=True,exist_ok=True);parts=[]
    for i,start in enumerate(range(0,len(packed),30000000)):
        b=packed[start:start+30000000];name=f'bodies.tar.gz.part{i:03}';(dest/name).write_bytes(b);parts.append(dict(path=name,bytes=len(b),sha256=sha(b)))
    # Reconstruct all235 complete peer bodies, including peer manifest/seal/proof.
    with tarfile.open(fileobj=io.BytesIO(gzip.decompress(b''.join((dest/x['path']).read_bytes()for x in parts))))as t:
        for item in records:
            b=t.extractfile(item['path']).read()if item['path']in frozen else (STATE/item['path']).read_bytes();assert sha(b)==item['sha256']and len(b)==item['bytes']
    dump(dest/'capture.json',dict(schema='finished-peer235-full-body-capture-v1',peer_id='5d9f9b63-0cf2-4b55-b52b-579cbc1d76d1',manifest_sha256=sha(mb),all235=records,immutable_original_references=refs,tar_gzip_parts_in_order=parts,tar_sha256=sha(tar),gzip_sha256=sha(packed),reconstruction='Concatenate ordered parts, gzip.decompress, open tar; original bodies reused by exact complete path/hash references. No peer writer executed.',captured_before_semantic_comparison=True,peer_reverse_proof_scope='Historical comparison against turnout original phase only; peer scenarios/calculators/outcomes/reproduction/later bytes excluded from semantic equality.'))
    print(dict(files=len(records),frozen_bodies=len(frozen),original_refs=len(refs),compressed_bytes=len(packed),parts=len(parts),capture_sha256=sha((dest/'capture.json').read_bytes())))
if __name__=='__main__':run()
