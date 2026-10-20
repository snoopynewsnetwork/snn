"""Exact captured whole-file/historical-body and full-object resolver, never latest-file substitution."""
from common import *
import argparse,sys

def resolve(path,expected):
 a=load(AUTH)
 for capture in a['immutable_historical_snapshot_body_resolvers']:
  for r in capture['complete_records']:
   if (r['original_path'],r['original_sha256'])!=(path,expected):continue
   if r['storage']=='tar_gzip_member':
    with tarfile.open(fileobj=io.BytesIO(exact(r['immutable_container'])),mode='r:gz') as t:b=t.extractfile(r['member']).read()
   else:
    b=exact(r['immutable_stored_body']);b=gzip.decompress(b) if r['storage']=='lossless_gzip_body' else b
   assert sha(b)==expected and len(b)==r['original_bytes'];return b
 for r in a['frozen_first_pair_assets']+a['complete_source_companion_files']+[a['frozen_contract']]:
  if (r['path'],r['sha256'])==(path,expected):return exact(r)
 raise ValueError('Exact original path+SHA absent; latest body is not a substitute')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('path');p.add_argument('sha256');p.add_argument('--output',required=True);p.add_argument('--pointer');args=p.parse_args();b=resolve(args.path,args.sha256)
 if args.pointer is not None:
  b=gzip.decompress(b) if args.path.endswith('.gz') else b
  x=[json.loads(l) for l in b.splitlines() if l] if '.jsonl'in args.path else json.loads(b) if '.json'in args.path else list(csv.reader(io.StringIO(b.decode('utf-8-sig'),newline='')))
  b=packed(pointer(x,args.pointer))+b'\n'
 target=Path(args.output).resolve();assert target.is_relative_to(M) or target.is_relative_to(Path('/private/tmp')) or target.is_relative_to(Path('/tmp').resolve());target.write_bytes(b)
