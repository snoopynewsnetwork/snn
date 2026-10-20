"""Lossless owned-only storage normalization. Reconstruct every original stored body by mapping."""
from common import *
import shutil

def main():
 mapping=[]
 for p in sorted((HERE/'receipts').glob('*.json')):
  m=parsefile(p)
  if m.get('complete'):
   old=STATE/m['path'];b=old.read_bytes();assert sha(b)==m['stored_sha256'];canonical=HERE/'raw'/(m['raw_sha256']+'.gz')
   if not canonical.exists():canonical.write_bytes(b)
   else:assert canonical.read_bytes()==b
   if old!=canonical:
    mapping.append(dict(original_storage_path=m['path'],canonical_storage_path=str(canonical.relative_to(STATE)),bytes=len(b),sha256=sha(b)))
    old.unlink();m['initial_storage_path']=m['path'];m['path']=str(canonical.relative_to(STATE));write(p,m)
  inspect(m)
 # Every complete parse remains losslessly gzipped; raw original bytes remain canonical.
 for p in (HERE/'parsed').glob('*.json'):
  q=p.with_suffix('.json.gz')
  assert q.exists();p.unlink()
 for p in list(HERE.rglob('__pycache__')):shutil.rmtree(p)
 old=HERE/'storage-layout.json'
 if old.exists():mapping=parsefile(old)['mappings']+mapping
 # preserve unique old-to-canonical references if rerun
 unique={x['original_storage_path']:x for x in mapping}
 write(old,dict(scope='owned raw entities deduplicated by complete raw SHA256; stored gzip bytes identical; no source fields lost',mappings=[unique[k] for k in sorted(unique)]))
 print('canonical raw bodies',len(list((HERE/'raw').glob('*.gz'))),'mapped names',len(unique))
if __name__=='__main__':main()
