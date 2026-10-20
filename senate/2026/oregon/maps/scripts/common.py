"""Map-owned deterministic serialization and exact original-byte resolver."""
from pathlib import Path
import json,gzip,hashlib,io,csv,tarfile
S=Path(__file__).resolve().parents[2];M=S/'maps'
AUTH='data/coordinator-source-research-acceptance.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def packed(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def semantic(x):return sha(packed(x))
def save(path,x):
 p=S/path;p.parent.mkdir(parents=True,exist_ok=True);b=packed(x)+b'\n';p.write_bytes(gzip.compress(b,mtime=0) if str(p).endswith('.gz') else b)
def ref(path):
 p=S/path;b=p.read_bytes();return {'path':path,'bytes':len(b),'sha256':sha(b)}
def exact(r):
 b=(S/r['path']).read_bytes();assert len(b)==r['bytes'] and sha(b)==r['sha256'],r['path'];return b
def load(path):
 b=(S/path).read_bytes();return json.loads(gzip.decompress(b) if str(path).endswith('.gz') else b)
def parse(r):
 b=exact(r);name=r['path'];b=gzip.decompress(b) if name.endswith('.gz') else b
 if '.jsonl' in name:return [json.loads(l) for l in b.splitlines() if l]
 if '.json' in name:return json.loads(b)
 return list(csv.reader(io.StringIO(b.decode('utf-8-sig'),newline='')))
def pointer(x,p):
 if not p:return x
 for k in p.split('/')[1:]:
  k=k.replace('~1','/').replace('~0','~');x=x[int(k)] if isinstance(x,list) else x[k]
 return x
def walk(x,p=''):
 if isinstance(x,(dict,list)):
  yield p,x
  for k,v in (x.items() if isinstance(x,dict) else enumerate(x)):
   yield from walk(v,p+'/'+str(k).replace('~','~0').replace('/','~1'))
def original(body):
 z=b''.join(exact(p) for p in body['parts']);assert len(z)==body['stored_bytes'] and sha(z)==body['stored_sha256']
 b=gzip.decompress(z) if 'gzip' in body['encoding'] else z
 assert len(b)==body['raw_bytes'] and sha(b)==body['raw_sha256'];return b
