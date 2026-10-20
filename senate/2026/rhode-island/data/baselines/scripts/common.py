import csv,gzip,hashlib,io,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
STATE=BASE.parents[1]
def sha(b): return hashlib.sha256(b).hexdigest()
def write_json(path, obj):
    path=BASE/path; path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,allow_nan=False,ensure_ascii=False)+'\n')
def write_gz(path, rows):
    b=''.join(json.dumps(r,allow_nan=False,ensure_ascii=False,separators=(',',':'))+'\n' for r in rows).encode()
    (BASE/path).write_bytes(gzip.compress(b,mtime=0))
def read_gz(path): return [json.loads(s) for s in gzip.decompress((BASE/path).read_bytes()).splitlines()]
def inputs(): return {x['id']:x for x in json.loads((BASE/'source/inputs.json').read_text())}
def body(ident):
    r=inputs()[ident]; s=(STATE/r['body_path']).read_bytes()
    assert sha(s)==r['stored_sha256'],ident
    b=gzip.decompress(s);assert sha(b)==r['raw_sha256'] and len(b)==r['raw_bytes'],ident
    return b
def write_csv(path, rows):
    rows=list(rows); p=BASE/path;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
