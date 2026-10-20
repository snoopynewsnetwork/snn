"""Independent whole frozen graph replay; acceptance is read by path only.
No producer code is imported or executed. All equality checks retain types/order.
"""
import json,gzip,csv,io,hashlib,tarfile,sys,collections
from pathlib import Path
HERE=Path(__file__).resolve().parent
STATE=HERE.parents[1]
def pairs(items):
    d={}
    for k,v in items:
        if k in d: raise ValueError('duplicate key '+k)
        d[k]=v
    return d
def loads(b): return json.loads(b,object_pairs_hook=pairs,parse_constant=lambda s:(_ for _ in ()).throw(ValueError(s)))
def digest(b): return hashlib.sha256(b).hexdigest()
def semantic(x):return digest(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode())
def checked(pin):
    b=(STATE/pin['path']).read_bytes()
    assert len(b)==pin['bytes'] and digest(b)==pin['sha256'],('whole file',pin['path'])
    return b
def decode(pin,b):
    if pin['path'].endswith('.gz'):b=gzip.decompress(b)
    if pin['format']=='csv_full_header_and_all_rows':return list(csv.reader(io.StringIO(b.decode())))
    if pin['format']=='jsonl_full_ordered_array':return [loads(line) for line in b.splitlines()]
    return loads(b)
def walk(x,p):
    if not isinstance(x,(list,dict)):return
    yield p,x
    if isinstance(x,dict):
        for k,v in x.items():yield from walk(v,p+'/'+k.replace('~','~0').replace('/','~1'))
    elif isinstance(x,list):
        for i,v in enumerate(x):yield from walk(v,p+'/'+str(i))
def main():
    a=loads((STATE/'data/coordinator-priority-acceptance.json').read_bytes())
    p=loads(checked(a['frozen_contract']));counts=collections.Counter()
    for pin in a['frozen_file_pins']:checked(pin);counts['fixed_whole_files']+=1
    for pin in a['producer_seals']:
        mf=loads(checked(pin));entries=mf[pin['owned_field']]
        assert len(entries)==pin['owned_entries']
        for entry in entries:
            checked(entry);counts['producer_members']+=1
    archives={}
    for pin in a['historical_full_body_resolvers']:
        st=pin['storage']
        if st['kind']=='tar_gzip_member':
            ap=st['archive'];key=ap['path']
            if key not in archives:
                archives[key]={}
                with tarfile.open(fileobj=io.BytesIO(checked(ap)),mode='r:gz') as tf:
                    for m in tf.getmembers():
                        if m.isfile():archives[key][m.name]=tf.extractfile(m).read()
            b=archives[key][st['member']]
        elif st['kind']=='immutable_original_reference':b=checked(st['file'])
        else:raise ValueError(st['kind'])
        assert len(b)==pin['bytes'] and digest(b)==pin['sha256'],('historical exact body',pin['path'])
        counts['historical_resolvers']+=1
    counts['complete_archives']=len(archives)
    for key,members in archives.items():
        declared={x['storage']['member'] for x in a['historical_full_body_resolvers'] if x['storage']['kind']=='tar_gzip_member' and x['storage']['archive']['path']==key}
        assert set(members)==declared,('archive full membership',key)
    roots=[]
    for root in a['complete_root_field_semantics']:
        v=p[root['pointer'][1:]];assert semantic(v)==root['full_recursive_semantic_sha256'];roots.append((root['pointer'],v));counts['complete_roots']+=1
    companions={}
    for pin in a['complete_source_companion_files']:
        value=decode(pin,checked(pin));assert len(value)==pin['complete_length'] and type(value).__name__==pin['semantic_type']
        assert semantic(value)==pin['full_semantic_sha256'],('companion semantics',pin['path'])
        companions[pin['path']]=value;counts['complete_companions']+=1
    def expected():
        for ptr,v in roots:
            yield {'file':a['frozen_contract']['path'],'pointer':ptr,'full_recursive_semantic_sha256':semantic(v)}
        for pin in a['complete_source_companion_files']:
            for pointer,value in walk(companions[pin['path']],''):yield {'file':pin['path'],'pointer':pointer,'full_recursive_semantic_sha256':semantic(value)}
    gen=expected();perfile=collections.Counter()
    for pin in a['complete_source_object_reference_bodies']:
        b=gzip.decompress(checked(pin));assert len(b)==pin['complete_reconstructed_bytes'] and digest(b)==pin['complete_reconstructed_sha256']
        n=0
        for line in b.splitlines():
            item=loads(line);assert item==next(gen),('ordered reference',counts['recursive_objects']);n+=1;perfile[item['file']]+=1;counts['recursive_objects']+=1
        assert n==pin['complete_object_count'];counts['whole_partitions']+=1
    assert next(gen,None) is None
    assert counts['recursive_objects']==a['complete_source_object_count']
    for k,v in a['source_objects_by_file'].items():assert perfile[k]==v
    for pin in a['complete_opaque_invalid_fixture_files']:checked(pin);counts['opaque_invalid_histories']+=1
    rows=p['full_order'];keys=[x['key'] for x in rows];assert keys==a['ordered_full_keys']
    assert keys==[x['key'] for x in sorted(rows,key=lambda r:(-r['votes'],r['key']))]
    assert len(keys)==len(set(keys))==2841 and sum(x['votes'] for x in rows)==1182676
    assert keys[:1056]==p['ordered_priority_keys']==a['ordered_priority_keys'];assert keys[1056:]==p['remainder_keys']==a['ordered_remainder_keys']
    assert sum(x['votes'] for x in rows[:15])==40031 and sum(x['votes'] for x in rows[:1055])==946007 and sum(x['votes'] for x in rows[:1056])==946377
    assert rows[1055]['county_name']=='CLEBURNE' and rows[1055]['native_name']=='GRASSEY OUTSIDE' and rows[1055]['votes']==370
    assert 5*946007<4*1182676<=5*946377
    for parent in p['all75parents']:
        fips=parent['county_fips'];v=a['all_parent_ordered_child_arrays'][parent['key']]
        assert semantic(parent)==v['complete_original_parent_semantic_sha256']
        for name,selection in [('full_source_rank_ordered_children',rows),('ordered_priority_children',rows[:1056]),('ordered_remainder_children',rows[1056:])]:
            assert v[name]==[r['key'] for r in selection if r['county_fips']==fips]
    counts.update(full_native=2841,priority_native=1056,remainder_native=1785,full_parents=75,priority_parents=68)
    return dict(counts)
if __name__=='__main__':print(json.dumps(main(),sort_keys=True))
