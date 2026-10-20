"""Read entire external acceptance in memory; write immutable full-body references.
Acceptance remains path-only, with no hash/size/build dependency back to acceptance.
Never imports/runs a producer or reads a mutable newsroom manifest.
"""
from pathlib import Path
import csv,gzip,hashlib,io,json
R=Path(__file__).resolve().parent; S=R.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def sem(v):return sha(json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode())
def load(p):
    b=p.read_bytes();b=gzip.decompress(b) if p.suffix=='.gz' else b
    n=p.name.removesuffix('.gz')
    if n.endswith('.jsonl'):return [json.loads(x) for x in b.splitlines() if x]
    if n.endswith('.csv'):return list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))
    return json.loads(b)
def pointer(v,p):
    for k in p.split('/')[1:]:
        k=k.replace('~1','/').replace('~0','~');v=v[int(k)] if isinstance(v,list) else v[k]
    return v
def pin(p):
    b=p.read_bytes();assert len(b)<40_000_000
    return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))
def write(name,v):
    b=(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode();p=R/name
    if p.suffix=='.gz':b=gzip.compress(b,mtime=0)
    assert len(b)<40_000_000
    if p.exists():assert p.read_bytes()==b,name
    else:p.write_bytes(b)
def main():
    a=load(S/'data/coordinator-priority-acceptance.json') # external authority, path only
    c=load(S/a['frozen_contract']['path']);assert pin(S/a['frozen_contract']['path'])==a['frozen_contract']
    cache={a['frozen_contract']['path']:c}; checks=0
    for f in a['complete_source_companion_files']:
        p=S/f['path'];actual=pin(p);assert all(actual[k]==f[k] for k in actual)
        v=load(p);cache[f['path']]=v;assert sem(v)==f['full_semantic_sha256'];assert len(v)==f['complete_length'];checks+=3
        if p.suffix=='.gz':
            raw=gzip.decompress(p.read_bytes());assert len(raw)==f['complete_reconstructed_bytes'] and sha(raw)==f['complete_reconstructed_sha256'];checks+=2
        if 'complete_header' in f:assert v[0]==f['complete_header'];checks+=1
    for f in a['complete_root_field_semantics']:assert sem(pointer(c,f['pointer']))==f['full_recursive_semantic_sha256'];checks+=1
    for f in a['complete_source_object_references']:
        v=cache.setdefault(f['file'],None)
        if v is None:v=load(S/f['file']);cache[f['file']]=v
        o=v[f['JSONL_record']-1] if 'JSONL_record' in f else pointer(v,f['pointer'])
        assert sem(o)==f['full_recursive_semantic_sha256'];checks+=1
    assert (len(c),len(a['complete_source_companion_files']),len(a['complete_source_object_references']))==(42,42,16388)
    # Freeze all producer-sealed raw evidence by reference, including complete payloads.
    assets={}
    for seal in a['producer_seals']:
        p=S/seal['path'];assert pin(p)==seal;m=load(p)
        entries=m['owned']+m['shared_originals'] if 'owned'in m else m['assets']
        for e in entries:
            p=S/e['path'] if 'owned'in m else (S/'data/baselines'/e['path']).resolve()
            actual=pin(p);assert actual['bytes']==e['bytes'] and actual['sha256']==e['sha256'];assets[actual['path']]=actual;checks+=1
    write('frozen-references.json.gz',dict(external_authority_path='data/coordinator-priority-acceptance.json',contract=a['frozen_contract'],root_fields=a['complete_root_field_semantics'],complete_companions=a['complete_source_companion_files'],complete_objects=a['complete_source_object_references'],producer_seals=a['producer_seals'],full_asset_references=list(assets.values()),projection_allowed=False))
    # Snapshot exact already-frozen individual source receipts rather than news/manifest.json.
    sources=load(S/'data/turnout/extracts/source-references.json')
    write('historical-source-receipts.json',sources)
    write('historical-auxiliary-receipts.json',load(S/'data/baselines/source/shared-sources.json'))
    # Legacy producers mention mutable news manifest. We do not execute them; this explicit
    # override replaces its discovery function with frozen source-references/original-inputs.
    write('reconstruction-override.json',dict(run_producers=False,mutable_aggregate_used=False,discovery_override='historical-source-receipts.json plus complete pinned data/turnout/source/original-inputs.json and data/baselines/source/shared-sources.json',reason='Frozen individual full receipts/raw references make source reconstruction independent of mutable newsroom acquisition aggregate.',source_files=[pin(S/'data/turnout/extracts/source-references.json'),pin(S/'data/turnout/source/original-inputs.json'),pin(S/'data/baselines/source/shared-sources.json')]))
    write('launch-contract-validation.json',dict(status='pass',checks=checks,root_fields=42,complete_companions=42,complete_objects=16388,producer_assets=len(assets),external_acceptance='data/coordinator-priority-acceptance.json',frozen_false_flags_unchanged=True))
    print('PASS',checks,'complete contract/source reference checks;',len(assets),'producer assets')
if __name__=='__main__':main()
