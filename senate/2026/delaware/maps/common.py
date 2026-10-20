"""Exact-byte references and complete semantic bodies; no producer imports."""
from pathlib import Path
import csv,gzip,hashlib,io,json
M=Path(__file__).resolve().parent
S=M.parent
LIMIT=40_000_000
def sha(b):return hashlib.sha256(b).hexdigest()
def encoded(x):return (json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def semantic(x):return sha(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode())
def read(p):
 p=Path(p);b=p.read_bytes();b=gzip.decompress(b) if p.suffix=='.gz' else b
 n=p.name.removesuffix('.gz')
 if n.endswith('.jsonl'):return [json.loads(v) for v in b.splitlines() if v]
 if n.endswith('.csv'):return list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))
 return json.loads(b)
def pointer(x,p):
 for k in p.split('/')[1:]:
  k=k.replace('~1','/').replace('~0','~');x=x[int(k)] if isinstance(x,list) else x[k]
 return x
def write(p,x):
 p=Path(p);p=p if p.is_absolute() else M/p;b=encoded(x)
 if p.suffix=='.gz':b=gzip.compress(b,mtime=0)
 assert len(b)<LIMIT;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();assert len(b)<LIMIT
 return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))
def verify(r):
 p=S/r['path'];b=p.read_bytes();assert len(b)==r['bytes'] and sha(b)==r['sha256'],r['path'];return b
def body(r):
 b=(S/r['asset_path']).read_bytes();assert len(b)==r['stored_bytes'] and sha(b)==r['stored_sha256'],r['id']
 raw=gzip.decompress(b);assert len(raw)==r['raw_bytes'] and sha(raw)==r['raw_sha256'],r['id'];return raw
