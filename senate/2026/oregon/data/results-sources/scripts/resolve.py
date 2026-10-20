"""Resolve a complete expected path+SHA, or a complete JSON-pointer object."""
from replay_inputs import load_catalogs,read,parse,semantic,sha,S
import gzip,json,io,tarfile,sys,argparse
from functools import lru_cache
@lru_cache(maxsize=16)
def archive(path,n,h):return tarfile.open(fileobj=io.BytesIO(read({'path':path,'bytes':n,'sha256':h})),mode='r:gz')
def resolve_body(path,expected_sha):
 a=load_catalogs()
 current=next((x for x in a['frozen_first_pair_assets'] if x['path']==path and x['sha256']==expected_sha),None)
 if current:return read(current)
 for c in a['immutable_historical_snapshot_body_resolvers']:
  for r in c['complete_records']:
   if r['original_path']==path and r['original_sha256']==expected_sha:
    if r['storage']=='tar_gzip_member':
     t=r['immutable_container'];b=archive(t['path'],t['bytes'],t['sha256']).extractfile(r['member']).read()
    else:
     b=read(r['immutable_stored_body'])
     if r['storage']=='lossless_gzip_body':b=gzip.decompress(b)
    assert len(b)==r['original_bytes'] and sha(b)==expected_sha;return b
 raise ValueError('no exact immutable body for expected path+SHA')
def pointer_value(x,p):
 if p=='':return x
 assert p.startswith('/')
 for part in p[1:].split('/'):
  part=part.replace('~1','/').replace('~0','~');x=x[int(part)] if isinstance(x,list) else x[part]
 return x
@lru_cache(maxsize=8)
def parsed(path,n,h):return parse({'path':path,'bytes':n,'sha256':h})
def resolve_object(r):
 f=r['file'];x=pointer_value(parsed(f['path'],f['bytes'],f['sha256']),r['pointer']);assert semantic(x)==r['whole_object_semantic_sha256'];return x
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('path');ap.add_argument('expected_sha');args=ap.parse_args();sys.stdout.buffer.write(resolve_body(args.path,args.expected_sha))
