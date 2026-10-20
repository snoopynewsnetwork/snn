"""Read-only byte reconstruction. Every retained entity remains materializable."""
from acquire import *
import argparse,sys,csv,io
from reconstruct import read,pointer
p=argparse.ArgumentParser();p.add_argument('--receipt');p.add_argument('--historical-file');p.add_argument('--pointer',default='');p.add_argument('--output');a=p.parse_args()
if a.receipt:
 r=json.loads((M/a.receipt).read_bytes())
 for part in r['parts']:
  b=(M/part['path']).read_bytes();assert len(b)==part['bytes']and sha(b)==part['sha256']
 b=body(r);assert len(b)==r['raw_bytes']and sha(b)==r['raw_sha256']
elif a.historical_file:
 v=pointer(read(a.historical_file),a.pointer);b=(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
else:p.error('specify --receipt or --historical-file')
if a.output:
 dest=Path(a.output).resolve();assert M in dest.parents or str(dest).startswith('/private/tmp/'),'output must be owned maps or private/tmp';dest.write_bytes(b)
else:sys.stdout.buffer.write(b)
