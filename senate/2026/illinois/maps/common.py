"""Owned paths and lossless formats. No producer mutation, network or acceptance pin."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import gzip,hashlib,json,io,csv
M=Path(__file__).resolve().parent
S=M.parent
ACCEPTANCE='data/coordinator-priority-acceptance.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(path,obj):
 p=M/path;p.parent.mkdir(parents=True,exist_ok=True)
 b=(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
 p.write_bytes(gzip.compress(b,mtime=0) if p.suffix=='.gz' else b)
def load(path):
 p=Path(path);b=p.read_bytes()
 if p.suffix=='.gz':b=gzip.decompress(b)
 return json.loads(b)
def parsed(path):
 b=(S/path).read_bytes()
 if path.endswith('.gz'):b=gzip.decompress(b)
 name=path.removesuffix('.gz')
 if name.endswith('.jsonl'):return [json.loads(x) for x in b.splitlines() if x]
 if name.endswith('.csv'):return list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))
 return json.loads(b)
def sem(v):return sha(json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode())
def resolve(v,p):
 if not p:return v
 for k in p.removeprefix('/').split('/'):
  k=k.replace('~1','/').replace('~0','~');v=v[int(k)] if isinstance(v,list) else v[k]
 return v
def exact(pin,base=S):
 b=(base/pin['path']).read_bytes()
 assert len(b)==pin['bytes']<40_000_000 and sha(b)==pin['sha256'],pin['path']
 return b
