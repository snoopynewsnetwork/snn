"""Exact historical path+SHA resolver and whole JSON-pointer reconstruction."""
from common import *
from functools import lru_cache
import tarfile,sys

@lru_cache(maxsize=8)
def archive(parts):
    pins=json.loads(parts);compressed=b''
    for p in pins:
        b=(S/p['path']).read_bytes();verify(b,p);compressed+=b
    return gzip.decompress(compressed)
@lru_cache(maxsize=16)
def body(path,digest,size):
    p=S/path
    if p.exists():
        b=p.read_bytes()
        if sha(b)==digest and len(b)==size:return b
    # Entire external authority consumed only in memory; it is never copied/pinned downstream.
    a=parsed(S/AUTHORITY)
    matches=[r for r in a['historical_full_body_resolvers'] if (r['path'],r['sha256'],r['bytes'])==(path,digest,size)]
    assert matches,('Exact historical body unavailable',path,digest)
    r=matches[0];st=r['storage']
    if st['kind']=='immutable_original_reference':
        b=(S/st['file']['path']).read_bytes();verify(b,st['file'])
    else:
        pins=[st['archive']] if st['kind']=='tar_gzip_member' else st['parts']
        tar=archive(json.dumps(pins,sort_keys=True))
        if st['kind']=='ordered_tar_gzip_member':assert sha(tar)==st['tar_sha256']
        with tarfile.open(fileobj=io.BytesIO(tar),mode='r:') as tf:b=tf.extractfile(st['member']).read()
    verify(b,dict(path=path,sha256=digest,bytes=size));return b
@lru_cache(maxsize=8)
def obj(path,digest,size):
    b=body(path,digest,size)
    if path.endswith('.gz'):b=gzip.decompress(b)
    if '.csv' in path:return list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))
    if '.jsonl' in path:return [json.loads(x) for x in b.splitlines() if x]
    return json.loads(b)
def resolve(r):
    v=obj(r['path'],r['sha256'],r['bytes'])
    for k in r['pointer'].split('/')[1:]:
        k=k.replace('~1','/').replace('~0','~');v=v[int(k)] if isinstance(v,list) else v[k]
    if r.get('full_object_semantic_sha256') is not None:assert sem(v)==r['full_object_semantic_sha256']
    return v
if __name__=='__main__':
    if sys.argv[1]=='--object':
        refs=parsed(Path(sys.argv[2]));value=refs
        for k in sys.argv[3].split('/')[1:]:value=value[int(k)] if isinstance(value,list) else value[k]
        sys.stdout.buffer.write(dump(resolve(value)))
    else:
        path,digest,size=sys.argv[1:4];sys.stdout.buffer.write(body(path,digest,int(size)))
