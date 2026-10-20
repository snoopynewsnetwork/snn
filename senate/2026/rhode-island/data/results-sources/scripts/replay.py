"""Replay ENTIRE external authority in memory. Never store its body or digest."""
from common import *
from collections import Counter,defaultdict
import tarfile

def walk(file,value,pointer=''):
    if isinstance(value,(dict,list)):
        yield file,pointer,value
        for k,v in value.items() if isinstance(value,dict) else enumerate(value):
            if isinstance(v,(dict,list)):
                yield from walk(file,v,pointer+'/'+str(k).replace('~','~0').replace('/','~1'))

def run():
    a=parsed(S/AUTHORITY)  # Whole body, not a sampled projection.
    c=parsed(S/a['frozen_contract']['path'])
    verify((S/a['frozen_contract']['path']).read_bytes(),a['frozen_contract'])
    counts=Counter()
    for p in a['frozen_file_pins']:
        verify((S/p['path']).read_bytes(),p);counts['current_file_pins']+=1
    for k,p in zip(c,a['complete_root_field_semantics'],strict=True):
        assert p['pointer']=='/'+k and sem(c[k])==p['full_recursive_semantic_sha256']
        counts['whole_contract_roots']+=1
    def ledger():
        for p in a['complete_source_object_reference_bodies']:
            b=(S/p['path']).read_bytes();verify(b,p)
            raw=gzip.decompress(b)
            assert len(raw)==p['complete_reconstructed_bytes'] and sha(raw)==p['complete_reconstructed_sha256']
            lines=raw.splitlines();assert len(lines)==p['complete_object_count']
            counts['ordered_ledger_partitions']+=1
            for line in lines:yield json.loads(line)
    entries=iter(ledger());byfile=Counter()
    def compare(file,pointer,value):
        e=next(entries)
        assert e==dict(file=file,pointer=pointer,full_recursive_semantic_sha256=sem(value)),(file,pointer)
        counts['recursive_objects']+=1;byfile[file]+=1
    for k,v in c.items():compare(a['frozen_contract']['path'],'/'+k,v)
    for p in a['complete_source_companion_files']:
        b=(S/p['path']).read_bytes();verify(b,p);v=parsed(S/p['path'])
        assert sem(v)==p['full_semantic_sha256'] and type(v).__name__==p['semantic_type']
        assert (len(v) if isinstance(v,(dict,list)) else None)==p['complete_length']
        for file,ptr,obj in walk(p['path'],v):compare(file,ptr,obj)
        counts['whole_companions']+=1
    assert next(entries,None) is None
    assert dict(byfile)==a['source_objects_by_file'] and counts['recursive_objects']==a['complete_source_object_count']
    # Resolve historical path+SHA against exact immutable storage, never current-path fallback.
    archives=defaultdict(list)
    for p in a['historical_full_body_resolvers']:
        st=p['storage'];kind=st['kind']
        if kind=='immutable_original_reference':
            b=(S/st['file']['path']).read_bytes();verify(b,st['file']);verify(b,p)
            counts['historical_full_bodies']+=1
        else:
            key=canon(st['archive'] if kind=='tar_gzip_member' else st['parts'])
            archives[(kind,key)].append(p)
    for (kind,_),rows in archives.items():
        st=rows[0]['storage']
        if kind=='tar_gzip_member':
            p=st['archive'];compressed=(S/p['path']).read_bytes();verify(compressed,p)
        else:
            chunks=[]
            for p in st['parts']:
                b=(S/p['path']).read_bytes();verify(b,p);chunks.append(b)
            compressed=b''.join(chunks);assert sha(compressed)==st['gzip_sha256']
        raw=gzip.decompress(compressed)
        if kind=='ordered_tar_gzip_member':assert sha(raw)==st['tar_sha256']
        with tarfile.open(fileobj=io.BytesIO(raw),mode='r:') as tf:
            for p in rows:
                b=tf.extractfile(p['storage']['member']).read();verify(b,p)
                counts['historical_full_bodies']+=1
        counts['whole_historical_archives']+=1
    # Verify whole original entities once by stored hash, preserving all full receipt objects by references.
    seen=set()
    for mf in ['data/turnout/asset-manifest.json','data/baselines/asset-manifest.json']:
        for p in parsed(S/mf)['external_original_references']:
            key=(p['path'],p['stored_sha256'])
            b=(S/p['path']).read_bytes()
            assert len(b)==p['stored_bytes'] and sha(b)==p['stored_sha256']
            raw=gzip.decompress(b) if p.get('compression')=='gzip' else b
            assert len(raw)==p['raw_bytes'] and sha(raw)==p['raw_sha256']
            seen.add(key)
    counts['unique_external_original_entities']=len(seen)
    full=c['complete_descending_order'];inv=c['all_source_native_constituents'];priority=c['ordered_priority_keys']
    assert [x['key'] for x in full]==a['ordered_full_keys']
    assert priority==a['ordered_priority_keys']==[x['key'] for x in full[:242]]
    assert [x['key'] for x in full[242:]]==a['ordered_remainder_keys']
    assert full==sorted(full,key=lambda x:(-x['votes'],int(x['source_anchor']['byte_offset'])))
    assert len(inv)==497 and len(full)==458 and sum(x['votes'] for x in full)==491948
    assert sum(x['votes'] for x in full[:241])==393066 and sum(x['votes'] for x in full[:242])==394072
    assert sum(x['votes'] for x in full[242:])==97876 and sum(x['votes']==0 for x in full)==15
    assert full[241]['native_code']=='0804' and full[241]['source_anchor']['byte_offset']==1075900
    assert full[241]['source_anchor']['line']==4061 and full[241]['votes']==1006
    assert sum(x['contests']['Senator in Congress']['total'] is None for x in inv)==39
    parents=c['municipal_and_administrative_parent_sensitivity']['full_inventory']
    for i,p in enumerate(parents):
        rows=[x for x in full if x['parent_key']==p['key']]
        assert a['all_parent_ordered_child_arrays'][p['key']]==dict(
            original_ordered_native_inventory_keys=p['native_keys'],
            full_source_rank_ordered_children=[x['key'] for x in rows],
            ordered_priority_children=[x['key'] for x in rows if x['key'] in priority],
            ordered_remainder_children=[x['key'] for x in rows if x['key'] not in priority],
            complete_parent_contract_pointer='/municipal_and_administrative_parent_sensitivity/full_inventory/'+str(i))
    counts['complete_parent_arrays']=len(parents)
    return dict(status='pass',authority_path=AUTHORITY,counts=dict(counts),
        scope='Complete root/companion/ordered recursive ledger/current pin/historical body/original entity replay; no producer import or writer. Historical path+SHA resolves exact stored member.',
        current_approval=False,collector_approval=False,probability_approval=False)
if __name__=='__main__':
    import sys
    result=run()
    if '--write' in sys.argv:write(R/'qa/authority-replay.json',dump(result))
    print(json.dumps(result))
