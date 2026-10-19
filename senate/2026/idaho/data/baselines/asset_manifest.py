#!/usr/bin/env python3
"""Seal all owned paths plus exact read-only source references; excludes self-hash."""
import gzip,json
from pathlib import Path
from extract import D,STATE,sha,save
def main():
 owned=[STATE/'county-partisanship.md',D.parent/'county-baselines.csv']+[p for p in D.rglob('*')if p.is_file()and p.name!='asset-manifest.json'and'__pycache__'not in p.parts];entries=[]
 for p in sorted(owned):
  b=p.read_bytes();assert len(b)<40000000
  r=dict(path=str(p.relative_to(STATE)),bytes=len(b),sha256=sha(b))
  if p.suffix=='.gz':raw=gzip.decompress(b);r.update(reconstructed_bytes=len(raw),reconstructed_sha256=sha(raw),encoding='gzip, exact ordered-byte decompression')
  entries.append(r)
 refs=[]
 for file in ['source/reused-originals.json','source/additional-reused-originals.json','source/independent-reference-receipts.json']:
  for r in json.loads((D/file).read_text()):
   if not r.get('relative_path'):continue
   p=D/r['relative_path'];b=p.read_bytes();raw=gzip.decompress(b);assert sha(b)==r['stored_sha256']and sha(raw)==r.get('raw_sha256',r.get('original_sha256'));assert len(b)<40000000
   refs.append(dict(source_id=r['id'],path=r['relative_path'],stored_bytes=len(b),stored_sha256=sha(b),raw_bytes=len(raw),raw_sha256=sha(raw),ledger=file,read_only=True))
   for field in ['original_record_path','headers_record_path']:
    if r.get(field):
     p=STATE.parent/r[field];b=p.read_bytes();expected=r['original_metadata_sha256']if field=='original_record_path'else r['headers_sha256'];assert sha(b)==expected
     refs.append(dict(source_id=r['id']+'_'+field,path='../../../'+r[field],stored_bytes=len(b),stored_sha256=sha(b),read_only=True))
 # These immutable parent receipts/body references support the current ballot chain.
 for p in [STATE/'data/news/manifest.json',STATE/'data/news/coordinator-oct19-recheck/acquisition-ballot-stage-v3.json',STATE/'data/news/coordinator-oct19-recheck/current-ballot-original-review.json']:
  b=p.read_bytes();refs.append(dict(source_id='immutable_source_ledger',path=str(Path('../news')/p.relative_to(STATE/'data/news')),stored_bytes=len(b),stored_sha256=sha(b),read_only=True))
 save('asset-manifest.json',dict(version=1,owned=entries,read_only_references=refs,maximum_stored_bytes=max(r['bytes']for r in entries),strict_limit=40000000,self_hash_excluded=True,source_unrelated_offices_preserved_in_complete_originals=True))
 print('sealed owned files',len(entries),'read-only references',len(refs))
if __name__=='__main__':main()
