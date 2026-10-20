from pathlib import Path
import json,gzip,hashlib,csv,io
M=Path(__file__).resolve().parents[1]
S=M.parent
AUTHORITY='data/coordinator-priority-acceptance.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def canon(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def semantic(x):return sha(canon(x))
def dump(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False).encode()+b'\n')
def parsed(p):
 p=Path(p); b=p.read_bytes();b=gzip.decompress(b) if p.suffix=='.gz' else b
 name=p.name.removesuffix('.gz')
 if name.endswith('.jsonl'):return [json.loads(s) for s in b.splitlines()]
 if name.endswith('.csv'):return list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))
 return json.loads(b)
def verify(b,p):assert len(b)==p['bytes'] and sha(b)==p['sha256'],p['path']
def original(r):
 return b''.join(gzip.decompress((M/p['path']).read_bytes()) for p in r['parts'])
