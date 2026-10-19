#!/usr/bin/env python3
"""Split only whole stored gzip streams; concatenation restores exact gzip then full entity."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;STATE=ROOT.parents[1]
p=ROOT/'acquisition.json';rs=json.loads(p.read_text());changes={}
for r in rs:
 name=r.get('body_path')
 if not name or r.get('body_parts'):continue
 f=STATE/name
 if f.stat().st_size<40000000:continue
 b=f.read_bytes();parts=[]
 for n,start in enumerate(range(0,len(b),32000000),1):
  q=f.with_name(f.name+f'.part{n:03d}');chunk=b[start:start+32000000];q.write_bytes(chunk);parts.append({'path':q.relative_to(STATE).as_posix(),'bytes':len(chunk),'sha256':hashlib.sha256(chunk).hexdigest()})
 changes[name]=parts
for r in rs:
 if r.get('body_path') in changes:r.update(body_parts=changes[r['body_path']],body_path=None,reconstruction='concatenate ordered body_parts, verify stored stream SHA256, gzip decompress to complete response entity')
p.write_text(json.dumps(rs,indent=2,ensure_ascii=False)+'\n')
for name in changes:(STATE/name).unlink()
print('Oversized streams split:',len(changes))
