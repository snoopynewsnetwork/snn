#!/usr/bin/env python3
"""Offline exact original reconstruction in memory, optionally emitted as small ordered chunks."""
import argparse,gzip,hashlib,json
from pathlib import Path
from evidence import own_receipts,original,sha,MAPS,ROOT
from native import receipts,body
from verify_history import pointer,semantic,reference_bytes

def reconstruct(source):
 own={r['id']:r for r in own_receipts()};native={r['id']:r for r in receipts()}
 if source in own:return original(own[source])
 if source in native:return body(native[source])
 overrides=json.loads((MAPS/'source/frozen-reference-overrides.json').read_text())['overrides']
 if source in {e['original_state_relative_path'] for e in overrides}:return reference_bytes(ROOT/source)
 refs={e['path']:e for e in json.loads((MAPS/'frozen-references.json').read_text())['references']}
 assert source in refs,source;b=(ROOT/source).read_bytes();e=refs[source];assert len(b)==e['bytes'] and sha(b)==e['sha256'];return gzip.decompress(b) if source.endswith('.gz') else b

def chunks(b,n=16000000):return [b[s:s+n] for s in range(0,len(b),n)] or [b'']
def main():
 p=argparse.ArgumentParser();p.add_argument('--source',required=True,help='Owned/native receipt ID, or exact frozen state-relative path');p.add_argument('--pointer',help='Optional complete JSON object, a semantic derivative rather than original whole-file bytes');p.add_argument('--parts-dir',type=Path);a=p.parse_args();b=reconstruct(a.source)
 if a.pointer is not None:b=(json.dumps(pointer(json.loads(b),a.pointer),ensure_ascii=False,indent=2)+'\n').encode()
 parts=chunks(b);assert b''.join(parts)==b and all(len(x)<40000000 for x in parts)
 out=dict(source=a.source,pointer=a.pointer,complete_bytes=len(b),complete_sha256=sha(b),parts=[dict(order=i,bytes=len(x),sha256=sha(x)) for i,x in enumerate(parts)])
 if a.parts_dir:
  a.parts_dir.mkdir(parents=True,exist_ok=True)
  for e,x in zip(out['parts'],parts):
   name=f'original.part{e["order"]:04d}';(a.parts_dir/name).write_bytes(x);e['path']=name
  (a.parts_dir/'reconstruction.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
