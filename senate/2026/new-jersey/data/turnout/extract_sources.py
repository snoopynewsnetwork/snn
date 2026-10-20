#!/usr/bin/env python3
from pathlib import Path
import gzip,hashlib,json,subprocess,tempfile
D=Path(__file__).resolve().parent;S=D/'source';E=D/'extract'
def extract(b):
 with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
  f.write(b);f.flush();return subprocess.run(['pdftotext','-layout',f.name,'-'],capture_output=True,check=True).stdout
if __name__=='__main__':
 for p in sorted(S.glob('*.receipt.json')):
  a=json.loads(p.read_text())
  if a.get('status')!=200:continue
  b=gzip.decompress((S/a['asset']).read_bytes()) if not a.get('reference_path') else gzip.decompress((S/a['reference_path']).read_bytes())
  assert hashlib.sha256(b).hexdigest()==a['raw_sha256']
  if not b.startswith(b'%PDF'):continue
  t=extract(b);(E/(p.name.replace('.receipt.json','.txt.gz'))).write_bytes(gzip.compress(t,mtime=0))
 print('text extracts',len(list(E.glob('*.txt.gz'))))
