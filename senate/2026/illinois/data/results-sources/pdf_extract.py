"""Complete text extraction from originals; preview rendering is separate from visual review."""
from common import *
import subprocess,tempfile

def extract_bytes(b,out):
 with tempfile.TemporaryDirectory(prefix='il-pdf-') as d:
  p=Path(d)/'original.pdf';p.write_bytes(b);r=subprocess.run(['pdftotext','-layout',str(p),'-'],capture_output=True)
  if r.returncode:write(out.with_suffix('.error.json'),dict(error=r.stderr.decode(errors='replace')));return
  gzwrite(out,r.stdout)

def main():
 reg=parsefile(STATE/'data/baselines/source/registry.json.gz');plans=[]
 for x in reg:
  if x['id'] in ['isbe-2026-authority-guide','isbe-2026-calendar']:
   p=STATE/'data/baselines'/x['path'];b=gzip.decompress(p.read_bytes());extract_bytes(b,HERE/'text'/f"{x['id']}.txt.gz");plans.append(dict(id=x['id'],path=str(p.resolve().relative_to(STATE.resolve())),complete_source_receipt=x))
 write(HERE/'manual-original-references.json',plans)
 for p in sorted((HERE/'receipts').glob('*.json')):
  m=json.loads(p.read_bytes())
  if not m.get('complete'):continue
  b=body(m)
  if b.startswith(b'%PDF'):extract_bytes(b,HERE/'text'/f"{m['id']}.txt.gz")
if __name__=='__main__':
 (HERE/'text').mkdir(exist_ok=True);main()
