"""FINAL READ-ONLY exact-membership/body/object/rebuild audit after sealing."""
from common import *
from seal import owned
from replay import run as replay
from original_audit import run as originals
from reproduce import run as reproduce
import tarfile,re
def main():
    manifest=parsed(R/'asset-manifest.json');actual={str(p.relative_to(S)) for p in owned() if p!=R/'asset-manifest.json'}
    rows=manifest['owned_assets'];assert manifest['excludes_only_itself'] is True
    assert len(rows)==len({r['path'] for r in rows}) and actual=={r['path'] for r in rows}
    for r in rows:
        verify((S/r['path']).read_bytes(),r);assert r['bytes']<40000000
    capture=parsed(R/'witness/capture.json');st=capture['storage']
    if st['kind']=='tar_gzip':
        p=st['archive'];b=(S/p['path']).read_bytes();verify(b,p);raw=gzip.decompress(b)
    else:
        chunks=[]
        for p in st['parts']:
            b=(S/p['path']).read_bytes();verify(b,p);chunks.append(gzip.decompress(b))
        raw=b''.join(chunks)
    assert len(raw)==st['tar_bytes'] and sha(raw)==st['tar_sha256']
    with tarfile.open(fileobj=io.BytesIO(raw),mode='r:') as tf:
        assert tf.getnames()==[p['path'] for p in capture['frozen_bodies']]
        for p in capture['frozen_bodies']:
            b=tf.extractfile(p['path']).read();verify(b,p);assert b==(S/p['path']).read_bytes()
    for p in capture['immutable_original_refs']:
        b=(S/p['path']).read_bytes();verify(b,p);raw=gzip.decompress(b)
        assert sha(raw)==p['raw_sha256'] and len(raw)==p['raw_bytes']
    # Every recursive pin in every owned valid structured object is verified; ignore only literal source HTML attributes.
    references=0
    def walk(v):
        nonlocal references
        if isinstance(v,dict):
            if {'path','bytes','sha256'}<=v.keys() and isinstance(v['path'],str) and isinstance(v['bytes'],int) and isinstance(v['sha256'],str):
                if v.get('pointer') is not None:
                    from reconstruct import body,resolve
                    body(v['path'],v['sha256'],v['bytes'])
                    if v.get('complete_object'):resolve(v)
                else:verify((S/v['path']).read_bytes(),v)
                references+=1
            for x in v.values():walk(x)
        elif isinstance(v,list):
            for x in v:walk(x)
    for p in rows:
        if p['path'].endswith('.json'):walk(parsed(S/p['path']))
    # Check cited external destinations against actual retained requests or literal official link edges.
    from build import raw_receipts
    known=set()
    def url(u):return u.replace(' ','%20') if isinstance(u,str) else u
    for rec in raw_receipts():known.update([url(rec['url']),url(rec.get('final_url'))])
    for rec in parsed(S/'data/baselines/source/inputs.json'):
        known.update([url(rec['url']),url(rec.get('final_url'))])
    for p in (R/'derived/html').glob('*.json'):
        known.update(url(x['url']) for x in parsed(p)['links'])
    cited=0
    for p in [S/'official-results.md',*R.glob('*.md')]:
        for u in re.findall(r'\]\((https?://[^)]+)\)',p.read_text()):
            assert url(u) in known,(p,u)
            cited+=1
    seal=parsed(R/'final-seal.json');assert seal['no_reverse_manifest_digest'] is True
    assert manifest['authority_path']==seal['authority_path']==AUTHORITY
    rb=reproduce();oa=originals();ar=replay()
    # Ensure everything remains byte-exact after all checks, including membership.
    assert actual=={str(p.relative_to(S)) for p in owned() if p!=R/'asset-manifest.json'}
    for r in rows:verify((S/r['path']).read_bytes(),r)
    print(json.dumps(dict(status='pass_final_read_only_audit',owned_targets=len(rows),recursive_pins=references,external_cited_links=cited,preterminal_whole_bodies=len(capture['frozen_bodies']),immutable_owned_originals=len(capture['immutable_original_refs']),reproduction=rb,originals=oa,authority_replay=ar,manifest=pin(R/'asset-manifest.json'),no_writes_after_seal=True)))
if __name__=='__main__':main()
