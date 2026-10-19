#!/usr/bin/env python3
"""Pin every owned file and every reused input without duplicating original bodies."""
import csv,gzip,hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parent;STATE=BASE.parent.parent
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p,kind):
 b=p.read_bytes();assert len(b)<40000000
 return dict(path=str(p.relative_to(STATE)),bytes=len(b),sha256=sha(b),kind=kind)
def main():
 refs={}
 def add(p,kind):refs[str(p.resolve())]=pin(p.resolve(),kind)
 for filename in ['source/reused-originals.json','source/extra-original-references.json']:
  x=json.loads((BASE/filename).read_text());rr=x['receipts']if isinstance(x,dict)else x
  for r in rr:add(STATE/r['shared_path'],'reused complete original or explicitly incomplete historical observation; gzip raw hash in source receipt')
 for r in json.loads((BASE/'source/acquisition.json').read_text()):
  if 'asset'in r and '..'in r['asset']:add((BASE/r['asset']).resolve(),'reused original independently freshly byte-matched')
 cr=json.loads((BASE/'source/census-original-reference.json').read_text())
 for key in ['path','receipt_path']:add(STATE/cr[key],'official Census original/reference receipt')
 for p in BASE.glob('extracts/extra-*-ocr.jsonl.gz'):
  for s in gzip.decompress(p.read_bytes()).splitlines():
   r=json.loads(s);q=STATE/r['image_path'];assert sha(q.read_bytes())==r['image_sha256'];add(q,'independent render byte-matched source-page reading derivative')
 peer=json.loads((BASE/'peer-reconciliation.json').read_text())
 for r in peer['pins']:
  p=STATE/r['path'];assert sha(p.read_bytes())==r['sha256'];add(p,'independent peer comparison input, not extraction authority')
 uq=json.loads((BASE/'universe-peer-QA.json').read_text());p=STATE/uq['peer_path'];assert sha(p.read_bytes())==uq['peer_sha256'];add(p,'independent peer universe QA input')
 # The package's used original receipts preserve failures/parents in the growing shared ledger;
 # a frozen receipt inventory is copied once as metadata, no duplicate large originals.
 ledger=BASE.parent/'news/manifest.json';frozen=BASE/'source/shared-news-ledger-observed.json';frozen.write_bytes(ledger.read_bytes())
 files=[STATE/'county-partisanship.md',BASE.parent/'county-baselines.csv',*BASE.rglob('*')]
 assets=[pin(p.resolve(),'owned report/data/reproducible code/evidence')for p in files if p.is_file()and p.name!='asset-manifest.json']
 owned={r['path']for r in assets};references=[r for r in refs.values()if r['path']not in owned]
 manifest=dict(schema='NE-baselines-assets-v1',self_hash_excluded=True,assets=sorted(assets,key=lambda r:r['path']),references=sorted(references,key=lambda r:r['path']),
  raw_reconstruction='For gzip originals, gzip.decompress(stored bytes) reproduces exact raw entity; raw and stored SHA256/bytes are in pinned receipt files. No lossy truncation/simplification. Existing1MiB truncated archive observations remain explicitly partial.',
  maximum_stored_bytes=max(r['bytes']for r in assets+references),all_assets_strictly_below_40000000=True)
 (BASE/'asset-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(dict(owned=len(assets),reused=len(references),max_bytes=manifest['maximum_stored_bytes'])))
if __name__=='__main__':main()
