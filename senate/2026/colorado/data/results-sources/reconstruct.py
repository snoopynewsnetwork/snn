#!/usr/bin/env python3
"""Offline lossless reconstruction: --receipt ID [--decode-http] [--output /tmp/file].
--reference N outputs the complete recursively referenced JSON object, 1-based.
No fetches, subsets, identity joins or default file writes.
"""
import argparse,gzip,hashlib,json,csv,io,sys,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent;STATE=ROOT.parents[1]
def main():
 a=argparse.ArgumentParser();a.add_argument('--receipt');a.add_argument('--reference',type=int);a.add_argument('--decode-http',action='store_true');a.add_argument('--output');args=a.parse_args()
 if args.receipt:
  rs=json.loads((ROOT/'acquisition.json').read_text());r=next(r for r in rs if r['id']==args.receipt)
  stored=b''.join((STATE/p['path']).read_bytes() for p in r['body_parts']) if r.get('body_parts') else (STATE/r['body_path']).read_bytes()
  assert hashlib.sha256(stored).hexdigest()==r['stored_sha256'];assert len(stored)==r['stored_bytes'];b=gzip.decompress(stored);assert hashlib.sha256(b).hexdigest()==r['raw_sha256'];assert len(b)==r['raw_bytes']
  if args.decode_http:
   e=next((v for k,v in r['headers'].items() if k.lower()=='content-encoding'),'');b=gzip.decompress(b) if e=='gzip' else zlib.decompress(b) if e=='deflate' else b
 elif args.reference:
  c=json.loads(gzip.decompress((ROOT/'historical-conservation.json.gz').read_bytes()));ref=c['complete_source_object_references'][args.reference-1];p=STATE/ref['file'];raw=p.read_bytes();raw=gzip.decompress(raw) if p.suffix=='.gz' else raw
  if '.jsonl' in p.name:x=json.loads(raw.splitlines()[ref['JSONL_record']-1])
  else:
   x=json.loads(raw)
   for token in ref['pointer'].strip('/').split('/'):
    token=token.replace('~1','/').replace('~0','~');x=x[int(token)] if isinstance(x,list) else x[token]
  b=(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'))).encode();assert hashlib.sha256(b).hexdigest()==ref['full_recursive_semantic_sha256']
 else:a.error('--receipt or --reference is required')
 if args.output:Path(args.output).write_bytes(b)
 else:sys.stdout.buffer.write(b)
if __name__=='__main__':main()
