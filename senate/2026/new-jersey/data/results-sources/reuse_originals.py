"""Storage-only exact deduplication; preserve initial receipts, never duplicate huge shared originals."""
from pathlib import Path
import json,gzip,hashlib,os,copy
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 refs=json.loads((ROOT/'data/baselines/source/original-references.json').read_bytes());byhash={};used={};history=[]
 for r in refs:
  if not r.get('body_reference'):continue
  p=(ROOT/'data/baselines/source'/r['body_reference']).resolve();z=p.read_bytes();raw=gzip.decompress(z) if p.suffix=='.gz' else z;assert sha(raw)==r['raw_sha256']
  byhash.setdefault(sha(raw),{'reference_path':os.path.relpath(p,ROOT),'raw_sha256':sha(raw),'raw_bytes':len(raw),'stored_sha256':sha(z),'stored_bytes':len(z),'storage':'read_only_individual_original_body_by_hash','reference_gzip':p.suffix=='.gz'})
 d=P/'receipt-history';d.mkdir(exist_ok=True)
 for f in sorted((P/'requests').glob('*.json')):
  r=json.loads(f.read_bytes());old=f.read_bytes();changed=False
  for h in r['hops']:
   if h['raw_sha256'] in byhash:
    ref=byhash[h['raw_sha256']];used[ref['raw_sha256']]=ref
    if h.get('asset'):
     h['original_storage_observation']={k:h[k] for k in ['asset','stored_sha256','stored_bytes']};h.update(ref);del h['asset'];changed=True
  if changed:
   if not (d/f.name).exists():(d/f.name).write_bytes(old)
   r['storage_reference_migration']='Exact original once-by-hash reused; original_storage_observation retains initial storage observation.';f.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
  if (d/f.name).exists():
   b=(d/f.name).read_bytes();history.append({'request_id':r['id'],'pre_migration_receipt':'receipt-history/'+f.name,'bytes':len(b),'sha256':sha(b),'change':'storage reference only; exact response/entity bytes unchanged'})
 for rawsha in used:
  p=P/'bodies'/f'{rawsha}.gz'
  if p.exists():p.unlink()
 (P/'storage-migration.json').write_text(json.dumps(history,indent=2)+'\n');(P/'shared-body-references.json').write_text(json.dumps(list(used.values()),indent=2)+'\n');print('individual originals reused',len(used),'receipt observations preserved',len(history))
if __name__=='__main__':main()
