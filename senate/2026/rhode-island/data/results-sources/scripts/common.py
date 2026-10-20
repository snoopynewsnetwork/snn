"""Standalone read-only source utilities. No producer imports."""
from pathlib import Path
import csv, gzip, hashlib, io, json
S = Path(__file__).resolve().parents[3]
R = S / 'data/results-sources'
AUTHORITY = 'data/coordinator-priority-acceptance.json'
def sha(b): return hashlib.sha256(b).hexdigest()
def canon(v): return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def sem(v): return sha(canon(v))
def dump(v): return json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False).encode()+b'\n'
def pin(p):
    b=p.read_bytes()
    return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))
def verify(b,p):
    assert len(b)==p['bytes'] and sha(b)==p['sha256'],p['path']
def parsed(p):
    b=p.read_bytes()
    if p.suffix=='.gz': b=gzip.decompress(b)
    if '.csv' in p.name:return list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))
    if '.jsonl' in p.name:return [json.loads(x) for x in b.splitlines() if x]
    return json.loads(b)
def write(p,b):
    p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists() and p.read_bytes()==b:return
    p.write_bytes(b)
