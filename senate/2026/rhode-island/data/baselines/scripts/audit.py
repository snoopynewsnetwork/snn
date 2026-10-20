"""Final read-only audit of every sealed body/reference and all source/order/calculator checks.
Never writes owned files, dependency/cache trees, or a reverse manifest digest.
"""
import gzip,io,json,subprocess,sys,tarfile
from common import *
def main():
    mp=BASE/'asset-manifest.json';mb=mp.read_bytes();mf=json.loads(mb)
    expected={r['path']:r for r in mf['owned_assets']}
    actual={str(p.relative_to(STATE)) for p in BASE.rglob('*') if p.is_file() and p!=mp}|{'county-partisanship.md','data/county-baselines.csv'}
    assert set(expected)==actual,('manifest coverage',set(expected)^actual)
    for r in mf['owned_assets']:
        p=STATE/r['path'];b=p.read_bytes();assert len(b)==r['bytes'] and sha(b)==r['sha256'] and len(b)<40000000,r['path']
    for r in mf['external_original_references']:
        s=(STATE/r['path']).read_bytes();b=gzip.decompress(s)
        assert len(s)==r['stored_bytes'] and sha(s)==r['stored_sha256'] and len(b)==r['raw_bytes'] and sha(b)==r['raw_sha256'] and len(s)<40000000,r['id']
    witness=json.loads((BASE/'witness/pre-peer-body-witness.json').read_text());tarbytes=(BASE/witness['archive']).read_bytes();assert sha(tarbytes)==witness['sha256']
    with tarfile.open(fileobj=io.BytesIO(tarbytes)) as tar:
        for r in witness['bodies']:
            b=tar.extractfile(r['path']).read();assert sha(b)==r['sha256'] and len(b)==r['bytes'],r['path']
    seal=json.loads((BASE/'final-seal.json').read_text());assert seal['reverse_current_manifest_digest'] is None
    for r in seal['bodies_before_seal']:
        b=(STATE/r['path']).read_bytes();assert sha(b)==r['sha256'] and len(b)==r['bytes'],r['path']
    result=subprocess.run([sys.executable,'-B',str(BASE/'scripts/validate.py'),'--read-only'],capture_output=True,text=True)
    if result.returncode:raise RuntimeError(result.stderr+result.stdout)
    validation=json.loads(result.stdout)
    assert mp.read_bytes()==mb,'manifest changed during audit'
    # Every captured peer body is audited by reciprocal capture hash and remains independent of later peer changes.
    for r in json.loads((BASE/'reciprocal/capture-additional.json').read_text()):
        if r.get('missing'):continue
        b=gzip.decompress((BASE/r['frozen_path']).read_bytes());assert sha(b)==r['sha256'] and len(b)==r['bytes'],r['path']
    print(json.dumps({'all_passed':True,'manifest_sha256':sha(mb),'owned_assets':len(expected),
        'original_references':len(mf['external_original_references']),'pre_peer_bodies':len(witness['bodies']),
        'validation':validation,'largest_owned_artifact':max(r['bytes'] for r in mf['owned_assets']),
        'owned_writes_performed':0,'current_mapping_or_coordinator_approval_claimed':False},indent=2))
if __name__=='__main__':main()
