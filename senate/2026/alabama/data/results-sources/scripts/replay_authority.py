"""Independent complete source-authority replay; never imports a producer.

Acceptance is read by path only and is never copied, hashed or reverse-pinned.
Historical resolver members are opened from their exact archives, never from
newer paths with matching names. No producer scripts execute here.
"""
import csv
import gzip
import hashlib
import io
import json
import tarfile
from collections import Counter, defaultdict
from pathlib import Path

STATE = Path(__file__).resolve().parents[3]
OWN = Path(__file__).resolve().parents[1]
ACCEPTANCE = 'data/coordinator-priority-acceptance.json'
CONTRACT = {'path':'data/turnout/priority-set.json','bytes':15257023,
            'sha256':'a3d53415e3379a512b88a1f5f81506ac337a92f45870dd616038b9e23bf71850'}

def strict_pairs(pairs):
    out={}
    for k,v in pairs:
        if k in out: raise ValueError('duplicate JSON key: '+k)
        out[k]=v
    return out

def parse(b):
    return json.loads(b,object_pairs_hook=strict_pairs,
                      parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))

def digest(b): return hashlib.sha256(b).hexdigest()
def canonical(o): return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def semantic(o): return digest(canonical(o))

def verify(b,p):
    assert len(b)==p['bytes'], ('size',p.get('path'))
    assert digest(b)==p['sha256'], ('hash',p.get('path'))
    return b

def loadpin(p): return verify((STATE/p['path']).read_bytes(),p)

def nodes(o,p=''):
    if not isinstance(o,(list,dict)): return
    yield p,o
    children = enumerate(o) if isinstance(o,list) else o.items()
    for k,v in children:
        yield from nodes(v,p+'/'+str(k).replace('~','~0').replace('/','~1'))

def replay():
    a=parse((STATE/ACCEPTANCE).read_bytes())
    p=parse(loadpin(CONTRACT))
    assert a['frozen_contract']==CONTRACT
    counts=Counter()
    for pin in a['frozen_file_pins']:
        loadpin(pin); counts['fixed_files']+=1
    for f in a['complete_root_field_semantics']:
        assert semantic(p[f['pointer'][1:]])==f['full_recursive_semantic_sha256']
        counts['roots']+=1
    archives={}
    for r in a['historical_full_body_resolvers']:
        st=r['storage']
        if st['kind']=='tar_gzip_member':
            ap=st['archive']['path']
            if ap not in archives:
                raw=loadpin(st['archive'])
                with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as tf:
                    members=tf.getmembers()
                    assert len({m.name for m in members})==len(members)
                    archives[ap]={m.name:tf.extractfile(m).read() for m in members if m.isfile()}
            b=archives[ap][st['member']]
        elif st['kind']=='immutable_original_reference': b=loadpin(st['file'])
        else: raise ValueError(st['kind'])
        verify(b,r);counts['historical_bodies']+=1
    for ap, bodies in archives.items():
        expected=[r['storage']['member'] for r in a['historical_full_body_resolvers']
                  if r['storage'].get('archive',{}).get('path')==ap]
        assert set(expected)==set(bodies),(ap,'incomplete archive')
    counts['complete_archives']=len(archives)
    def expected_refs():
        for f in a['complete_root_field_semantics']:
            yield CONTRACT['path'], f['pointer'], semantic(p[f['pointer'][1:]])
        for c in a['complete_source_companion_files']:
            b=loadpin(c)
            if c['path'].endswith('.gz'): b=gzip.decompress(b)
            o=list(csv.reader(io.StringIO(b.decode()))) if c['format']=='csv_full_header_and_all_rows' else parse(b)
            assert type(o).__name__==c['semantic_type'] and len(o)==c['complete_length']
            assert semantic(o)==c['full_semantic_sha256'],('whole companion',c['path'])
            counts['whole_companions']+=1
            for pointer,obj in nodes(o):
                yield c['path'],pointer,semantic(obj)
    expected=iter(expected_refs()); byfile=Counter()
    for partition in a['complete_source_object_reference_bodies']:
        raw=gzip.decompress(loadpin(partition))
        assert len(raw)==partition['complete_reconstructed_bytes']
        assert digest(raw)==partition['complete_reconstructed_sha256']
        n=0
        for line in raw.splitlines():
            r=parse(line); actual=(r['file'],r['pointer'],r['full_recursive_semantic_sha256'])
            assert actual==next(expected),('recursive order/body',r['file'],r['pointer'])
            n+=1;byfile[r['file']]+=1
        assert n==partition['complete_object_count']
        counts['recursive_objects']+=n;counts['ordered_partitions']+=1
        print('partition',counts['ordered_partitions'],'PASS',n,flush=True)
    assert next(expected,None) is None
    assert byfile==Counter(a['source_objects_by_file'])
    assert counts['recursive_objects']==a['complete_source_object_count']
    units=p['units'];keys=[u['key'] for u in units]
    assert len(set(keys))==len(keys)==2085
    assert units==sorted(units,key=lambda u:(-u['reported_candidate_votes'],u['key']))
    total=0
    for i,u in enumerate(units):
        assert u['rank']==i+1
        assert sum(c['value'] for c in u['candidate_votes'])==u['reported_candidate_votes']
        total+=u['reported_candidate_votes']; assert u['cumulative_votes']==total
        assert u['current_2026_crosswalk'] is None and u['named_valid_writein_allocation'] is None
    assert total==2265090
    assert keys==p['full_order']==a['ordered_full_keys']
    assert keys[:887]==p['ordered_priority_keys']==p['priority_keys']==a['ordered_priority_keys']
    assert keys[887:]==p['remainder_keys']==a['ordered_remainder_keys']
    before=sum(u['reported_candidate_votes'] for u in units[:886])
    crossing=before+units[886]['reported_candidate_votes']
    assert before==1811981 and crossing==1812818 and 5*before<4*total<=5*crossing
    assert sum(u['reported_candidate_votes'] for u in units[:15])==115428
    assert units[886]['native_label']=='OAK GROVE BAPT' and units[886]['reported_candidate_votes']==837
    priority=set(keys[:887]);parents=p['parents']; assert len(parents)==67
    for i,parent in enumerate(parents):
        pk=parent['parent_key']; ar=a['all_parent_ordered_child_arrays'][pk]
        full=[u['key'] for u in units if u['county_fips']==parent['county_fips']]
        assert ar['full_source_rank_ordered_children']==full
        assert ar['ordered_priority_children']==[k for k in full if k in priority]
        assert ar['ordered_remainder_children']==[k for k in full if k not in priority]
        assert semantic(parent)==ar['complete_original_parent_semantic_sha256']
        assert ar['complete_parent_contract_pointer']==f'/parents/{i}'
        assert len(parent['constituent_keys'])==len(full) and set(parent['constituent_keys'])==set(full)
        assert parent['priority_constituent_keys']==[k for k in parent['constituent_keys'] if k in priority]
        assert parent['remainder_constituent_keys']==[k for k in parent['constituent_keys'] if k not in priority]
    assert len({u['county_fips'] for u in units[:887]})==63
    return {'status':'PASS','acceptance_path':ACCEPTANCE,'contract':CONTRACT,'checks':dict(counts),
            'scope':'Whole source authority and historical hierarchy only; no scenarios or current admission',
            'native_contexts':2085,'priority':887,'remainder':1198,'parents':67,'priority_parents':63}

if __name__=='__main__':
    import sys
    result=replay()
    if '--audit' not in sys.argv:
        (OWN/'qa/authority-replay.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
