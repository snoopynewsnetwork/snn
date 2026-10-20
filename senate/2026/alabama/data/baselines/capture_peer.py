#!/usr/bin/env python3
"""Optional one-time frozen capture. No peer contact or numerical build input.
Existing capture is immutable: verify it rather than overwrite. Large original
HTTP bodies remain individual read-only references, never duplicated here.
"""
import hashlib,json,pathlib,tarfile
BASE=pathlib.Path(__file__).resolve().parent;STATE=BASE.parent.parent
PIN='4e2a1f5ab3c66508444c112f9e6430006dce94f795a172837c7b95eaee557207'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    archive=BASE/'source/frozen-turnout-peer.tar.gz'
    if archive.exists():
        with tarfile.open(archive) as t:assert sha(t.extractfile('data/turnout/asset-manifest.json').read())==PIN
        print('Existing pinned frozen capture retained');return
    p=STATE/'data/turnout/asset-manifest.json';raw=p.read_bytes();assert sha(raw)==PIN;d=json.loads(raw);refs=[];capture=[]
    for x in d['assets']:
        q=STATE/x['path'];b=q.read_bytes();assert sha(b)==x['sha256'] and len(b)==x['bytes']
        if '/source/http/' in x['path'] and not x['path'].endswith('.receipt.json'):refs.append(x)
        else:capture.append((q,x['path']))
    with tarfile.open(archive,'w:gz',compresslevel=9) as t:
        t.add(p,arcname='data/turnout/asset-manifest.json')
        for q,n in capture:t.add(q,arcname=n)
    (BASE/'source/frozen-peer-original-references.json').write_text(json.dumps({'manifest_sha256':PIN,'asset_count':len(d['assets']),'originals_referenced_read_only':refs,'archive_nonoriginals_count':len(capture)},indent=2)+'\n')
if __name__=='__main__':main()
