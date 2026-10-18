import gzip,hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1];GA=ROOT.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def js(p):return json.loads(p.read_text())
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def entity(r):
 b=((GA/r['shared_path']) if 'shared_path' in r else ROOT/r['path']).read_bytes()
 return gzip.decompress(b) if b.startswith(b'\x1f\x8b') else b
