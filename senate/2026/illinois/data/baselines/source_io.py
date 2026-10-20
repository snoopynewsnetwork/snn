"""Audited source bytes; shared originals are immutable references, never inputs from peer tables."""
from pathlib import Path
import gzip, hashlib, json,functools

ROOT=Path(__file__).resolve().parent
STATE=ROOT.parent.parent
def sha(b): return hashlib.sha256(b).hexdigest()
def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    b=(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
    path.write_bytes(gzip.compress(b,mtime=0)if path.suffix=='.gz'else b)
@functools.lru_cache(maxsize=1)
def pins(): return json.loads(gzip.decompress((ROOT/'source/registry.json.gz').read_bytes()))
def raw(sid):
    x=next(x for x in pins() if x['id']==sid)
    p=(ROOT/x['path']).resolve(); z=p.read_bytes()
    assert sha(z)==x['stored_sha256'], (sid,'stored hash')
    b=gzip.decompress(z) if x.get('compression')=='gzip' else z
    assert sha(b)==x['raw_sha256'] and len(b)==x['bytes'], (sid,'raw hash/size')
    return b
def initialize():
    import os
    mf=json.loads((STATE/'data/news/manifest.json').read_text())
    out=[]
    for x in mf:
        if not x['id'].startswith('sos-'): continue
        a=dict(x); a['path']=os.path.relpath(STATE/'data/news'/a['asset'],ROOT)
        a['compression']='gzip'; a['reuse']='Read-only exact-hash shared original; no coordinator parsed values used.'
        out.append(a)
    dump(ROOT/'source/registry.json.gz',out)

if __name__=='__main__': initialize()
