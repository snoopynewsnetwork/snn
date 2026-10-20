"""Complete owned asset seal and exact shared-original hash references; no self hash."""
import json,sys
from source_io import ROOT,STATE,sha,dump,pins,raw
def main():
    manifest=ROOT/'asset-manifest.json';paths=[STATE/'county-partisanship.md',STATE/'data/county-baselines.csv']+[p for p in ROOT.rglob('*')if p.is_file()and p!=manifest]
    paths=sorted(set(paths));assets=[]
    for p in paths:
        b=p.read_bytes();assert len(b)<40000000 and '__pycache__'not in p.parts and p.suffix!='.pyc'
        assets.append(dict(path=str(p.relative_to(STATE)),bytes=len(b),sha256=sha(b)))
    refs=[]
    for x in pins():
        if 'path'not in x:continue
        p=ROOT/x['path'];b=p.read_bytes();assert sha(b)==x['stored_sha256'];raw(x['id'])
        refs.append(dict(source_id=x['id'],path=x['path'],bytes=len(b),sha256=sha(b),raw_bytes=x['bytes'],raw_sha256=x['raw_sha256'],qualification='Complete exact referenced bytes; gzip decompression reconstructs exact decoded HTTP entity. No truncation/simplification.'))
    if '--check'in sys.argv:
        old=json.loads(manifest.read_text());assert old['owned_assets']==assets,'Owned asset changed after seal';assert old['source_references']==refs,'Source reference changed after seal'
        print(json.dumps({'status':'pass','owned_assets':len(assets),'source_references':len(refs),'strict_file_limit':40000000,'maximum_owned_bytes':max(x['bytes']for x in assets)}));return
    dump(manifest,dict(owned_assets=assets,source_references=refs,exclusions=['asset-manifest.json itself: no recursive self hash'],audit=dict(owned_assets=len(assets),source_references=len(refs),strict_stored_file_limit=40000000,all_source_bytes_hash_verified=True,all_originals_complete=True,dependencies_or_cache_directories_retained=False)))
    print(json.dumps({'status':'sealed','owned_assets':len(assets),'source_references':len(refs)}))
if __name__=='__main__':main()
