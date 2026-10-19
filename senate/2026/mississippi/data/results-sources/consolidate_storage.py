"""Lossless owned-storage deduplication against exact read-only originals.
Changes receipt storage locators only; requested entity/headers/status remain.
No external file is written or removed. Keep audit of each storage-only change.
"""
import json,gzip
import acquire as a
def run():
    changes=[]
    for p in sorted((a.OUT/'receipts').glob('*.json')):
        r=json.loads(p.read_bytes());shared=a.SHARED.get(r.get('entity_sha256'))
        if not shared or r.get('storage')=='external_exact_original_read_only':continue
        entity=a.entity(r);sp=a.ROOT/shared['path'];sb=sp.read_bytes()
        assert a.sha(sb)==shared['stored_sha256']
        assert(gzip.decompress(sb)if sp.suffix=='.gz'else sb)==entity
        before={k:r.get(k)for k in ['storage','path','stored_bytes','stored_sha256']}
        r.update(storage='external_exact_original_read_only',**shared,stored_bytes=len(sb));a.save(p,r)
        changes.append(dict(source=r['id'],entity_sha256=r['entity_sha256'],previous_storage=before,current_storage=shared,entity_unchanged=True))
    used={json.loads(p.read_bytes()).get('path')for p in(a.OUT/'receipts').glob('*.json')}
    removed=[]
    for p in sorted((a.OUT/'entities').glob('*.gz')):
        rel=str(p.relative_to(a.ROOT))
        if rel not in used:
            removed.append(a.pin(p));p.unlink()
    old=a.OUT/'storage-consolidation.json'
    previous=json.loads(old.read_bytes())if old.exists()else dict(changes=[],removed_owned_unreferenced_entities=[])
    previous['changes']+=changes;previous['removed_owned_unreferenced_entities']+=removed
    previous['scope']='Exact wire-entity equality proven before replacing duplicate owned storage by shared original locator. All HTTP observations preserved. External originals read-only.'
    a.save(old,previous);return dict(references_reused=len(changes),owned_duplicates_removed=len(removed))
if __name__=='__main__':print(run())
