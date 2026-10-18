"""Share exact duplicate owned entities while preserving each original acquisition receipt."""
from common import *
seen={};n=0
for mp in sorted((ROOT/'raw').glob('*.http.json')):
 r=js(mp)
 if not r.get('raw_sha256') or 'path' not in r:continue
 if r['raw_sha256'] in seen:
  previous=seen[r['raw_sha256']];b=(ROOT/r['path']).read_bytes();assert sha(gzip.decompress(b))==r['raw_sha256']
  (ROOT/r['path']).unlink();r['shared_path']='data/results-sources/'+previous['path'];r.pop('path');r['stored_bytes']=previous['stored_bytes'];r['stored_sha256']=previous['stored_sha256'];r['deduplicated_exact_entity']=True;save(mp,r);n+=1
 else:seen[r['raw_sha256']]=r
print('Exact duplicate owned entities shared',n)
