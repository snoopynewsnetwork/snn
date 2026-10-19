#!/usr/bin/env python3
"""Verify external dispatch, frozen reviews and recursive original references.

Authority is the external acceptance PATH. It is not a reverse dependency in
the immutable contract. No mutable news/coordinator aggregate is a build input.
"""
import gzip, hashlib, json, pathlib, sys
sys.dont_write_bytecode=True
D=pathlib.Path(__file__).resolve().parent; S=D.parent.parent
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_bytes())
def leaves(v):
    if isinstance(v,dict):
        yield v
        for x in v.values():yield from leaves(x)
    elif isinstance(v,list):
        for x in v:yield from leaves(x)
def main():
    a=load(S/'data/coordinator-priority-acceptance.json')
    c=load(S/a['frozen_contract']['path']); verified={}; pending=[];reconstructed={}
    def pin(r):
        if r['path']=='data/news/manifest.json':
            # A frozen producer reference points at this subsequently appendable
            # ledger. Preserve its exact former bytes from complete individually
            # pinned receipt objects; never require the mutable aggregate file.
            old=load(S/'data/turnout/source/shared-news-ledger.json')
            extra=load(D/'optional-news-receipts.json')['append6_observations']
            b=(json.dumps(old+extra,indent=2)+'\n').encode()
            assert len(b)==r['bytes']and sha(b)==r['sha256']
            reconstructed[r['path']]=dict(source_path=r['path'],bytes=r['bytes'],sha256=r['sha256'],reconstruction='json.dumps(frozen233receiptobjects + six exact individual optional receipt objects, indent=2) + newline; UTF8, ensure_ascii=True',mutable_aggregate_file_dependency=False)
            return
        p=S/r['path'];b=p.read_bytes()
        assert len(b)==r['bytes'] and sha(b)==r['sha256'],r['path']
        if r['path'] not in verified:
            verified[r['path']]={k:r[k] for k in ['path','bytes','sha256']}
            if p.suffix=='.json': pending.append(p)
    for v in leaves(a):
        if {'path','bytes','sha256'}<=v.keys():pin(v)
    # Full reads of every frozen review/manifest/proof, not just its outer hash.
    while pending:
        p=pending.pop();j=load(p)
        for v in leaves(j):
            if {'path','bytes','sha256'}<=v.keys() and (v['path']=='data/news/manifest.json' or (S/v['path']).is_file()):pin(v)
            if {'asset','stored_sha256','raw_sha256','bytes'}<=v.keys():
                q=S/'data/news'/v['asset']
                if q.is_file():
                    z=q.read_bytes();raw=gzip.decompress(z)
                    assert sha(z)==v['stored_sha256'] and len(raw)==v['bytes'] and sha(raw)==v['raw_sha256'],v['asset']
                    pin(dict(path=str(q.relative_to(S)),bytes=len(z),sha256=sha(z)))
    assert len(c['constituents'])==1326 and len(c['all93_parents'])==93
    assert c['ordered_priority_keys']==a['ordered_priority_keys']
    assert c['ordered_full_keys']==a['ordered_full_keys']
    assert c['ordered_remainder_keys']==a['ordered_remainder_keys']
    assert c['all93_parents']==a['all93_parent_objects']
    for k in ['parent_full_child_map','parent_priority_child_map','child_parent_map']:assert c[k]==a[k]
    assert not c['coordinator_acceptance'] and not c['current_geography_approval']
    assert [len(c[k]) for k in ['administrative_and_partial_alternates','additional_native_source_contexts','unavailable_cases','additional_administrative_contexts']]==[329,14,2,2]
    out=dict(schema='NE-official-frozen-input-graph-v1',authority_path='data/coordinator-priority-acceptance.json',contract=a['frozen_contract'],verified_inputs=sorted(verified.values(),key=lambda r:r['path']),exact_reconstructed_legacy_aggregate_pins=list(reconstructed.values()),complete_contract_reference=dict(path=a['frozen_contract']['path'],json_pointer='',recursive_all_fields=True),preserved_arrays=['constituents','administrative_and_partial_alternates','additional_native_source_contexts','unavailable_cases','additional_administrative_contexts'],qualification='All complete frozen objects/fields/nulls and source graphs are transitively retained by exact original bytes. Producer legacy mutable-ledger reference is reconstructed exactly from complete individual receipts; never read as runtime aggregate dependency. No projection, eligible vote allocation, current geography approval or mutable aggregate dependency.')
    p=D/'frozen-inputs.json';p.write_text(json.dumps(out,indent=2)+'\n');print('Verified frozen input files',len(verified),'exact reconstructed legacy aggregate pins',len(reconstructed),'full contract fields',len(c),'complete objects',1326+329+14+2+2)
if __name__=='__main__':main()
