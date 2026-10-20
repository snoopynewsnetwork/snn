#!/usr/bin/env python3
"""Freeze an owned file before replacing it. Histories are immutable gzip bodies."""
import gzip,hashlib,json,pathlib,datetime,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
def freeze(p):
 p=pathlib.Path(p).resolve()
 if not p.exists():return
 assert p==ROOT.parent/'county-turnout.csv' or p==ROOT.parents[1]/'turnout.md' or ROOT in p.parents
 b=p.read_bytes();h=hashlib.sha256(b).hexdigest();d=ROOT/'history';d.mkdir(exist_ok=True)
 q=d/(h+'.gz')
 if not q.exists():q.write_bytes(gzip.compress(b,mtime=0))
 r=d/(h+'.json'); info={'original_path':str(p.relative_to(ROOT.parents[1])),'sha256':h,'original_bytes':len(b),'stored_body':q.name,'first_frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 if not r.exists():r.write_text(json.dumps(info,indent=2)+'\n')
def write(p,b):
 p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True);b=b.encode() if isinstance(b,str) else b
 if p.exists() and p.read_bytes()==b:return
 freeze(p);p.write_bytes(b)
if __name__=='__main__':
 for p in sys.argv[1:]:freeze(p)
