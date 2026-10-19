"""Hash every owned deliverable and reference original shared bytes read-only.

The manifest excludes itself to avoid a self-hash cycle. Validation is written
first, then this manifest is built and all listed hashes checked in memory.
"""
import gzip,json
from acquire_sources import BASE,OUT,receipts,sha,savejson
def main():
 dest=OUT/'asset-manifest.json';files=[BASE/'turnout.md',BASE/'data/county-turnout.csv']+[p for p in OUT.rglob('*') if p.is_file() and p!=dest and '__pycache__' not in p.parts]
 rows=[]
 for p in sorted(files):
  b=p.read_bytes();assert len(b)<40_000_000,p
  r=dict(path=str(p.relative_to(BASE)),bytes=len(b),sha256=sha(b))
  if p.suffix=='.gz':
   raw=gzip.decompress(b);r.update(compression='gzip_lossless_ordered_entity_reconstruction',uncompressed_bytes=len(raw),uncompressed_sha256=sha(raw))
  rows.append(r)
 shared=[]
 for r in receipts:
  if r.get('storage')=='owned':continue
  p=BASE/r['path'];b=p.read_bytes();assert sha(b)==r['stored_sha256']
  shared.append(dict(source_id=r['id'],path=r['path'],stored_bytes=len(b),stored_sha256=r['stored_sha256'],raw_sha256=r['raw_sha256'],ownership='read_only_external_to_owned_deliverables',acquisition_receipt='data/turnout/source/acquisition.json'))
 savejson(dest,dict(schema='ms-turnout-owned-assets-1',self_exclusion='This asset-manifest.json excludes itself because a self-hash is impossible; every other owned non-cache deliverable is included. Validation is written before this manifest.',owned_assets=rows,read_only_shared_original_references=shared))
 for r in rows:assert sha((BASE/r['path']).read_bytes())==r['sha256']
 print('Manifest verified:',len(rows),'owned assets;',len(shared),'shared original references')
if __name__=='__main__':main()
