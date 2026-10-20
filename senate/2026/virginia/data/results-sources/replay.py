"""Independent full frozen-authority replay, never invokes producer code.

Acceptance is external PATH ONLY. Expected input evidence is read from that
authority at runtime; no digest, body or reverse pin of acceptance is emitted.
"""
import argparse, collections, csv, gzip, hashlib, io, json, math, tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
STATE=ROOT.parent.parent
AUTHORITY=STATE/'data/coordinator-priority-acceptance.json'
def sha(b): return hashlib.sha256(b).hexdigest()
def strict(b):
    def pairs(items):
        d={}
        for k,v in items:
            if k in d:raise ValueError('duplicate key '+k)
            d[k]=v
        return d
    obj=json.loads(b,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))
    def finite(x):
        if isinstance(x,float) and not math.isfinite(x):raise ValueError('nonfinite number')
        if isinstance(x,dict):
            for v in x.values():finite(v)
        if isinstance(x,list):
            for v in x:finite(v)
    finite(obj);return obj
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def semantic(x):return sha(canonical(x))
def decoded(p,b): return gzip.decompress(b) if str(p).endswith('.gz') else b
def check_pin(p,b):
    assert len(b)==p['bytes'],('size',p['path'])
    assert sha(b)==p['sha256'],('hash',p['path'])
def pointer(obj,p):
    if not p:return obj
    for token in p.split('/')[1:]:
        token=token.replace('~1','/').replace('~0','~')
        obj=obj[int(token)] if isinstance(obj,list) else obj[token]
    return obj
def walk(x,p=''):
    if isinstance(x,(dict,list)):
        yield p,x
        items=x.items() if isinstance(x,dict) else enumerate(x)
        for k,v in items:
            yield from walk(v,p+'/'+str(k).replace('~','~0').replace('/','~1'))
def companion(f,b):
    raw=decoded(f['path'],b)
    if f['format']=='json':
        # A frozen negative fixture deliberately has duplicate fields. Its raw
        # complete bytes are verified above; authority's semantic view uses the
        # last field. This exception never applies to admitted source objects.
        if f['path']=='data/baselines/scenarios/fixtures/duplicate-json-field.input.json':return json.loads(raw)
        return strict(raw)
    if f['format']=='jsonl_full_ordered_array':return [strict(line) for line in raw.splitlines()]
    if f['format']=='csv_full_header_and_all_rows':return list(csv.reader(io.StringIO(raw.decode('utf-8-sig'),newline='')))
    raise ValueError(f['format'])
def main(write=False):
    a=strict(AUTHORITY.read_bytes())
    # Entire external root has been read. Its own bytes/hash are never recorded.
    fixed={}
    for f in a['frozen_file_pins']:
        b=(STATE/f['path']).read_bytes();check_pin(f,b);fixed[f['path']]=b
    contract=strict(fixed[a['frozen_contract']['path']])
    check_pin(a['frozen_contract'],fixed[a['frozen_contract']['path']])
    for f in a['complete_root_field_semantics']:
        assert semantic(pointer(contract,f['pointer']))==f['full_recursive_semantic_sha256'],f['pointer']
    assert len(contract)==len(a['complete_root_field_semantics'])==25
    archive_cache={}; member_sets=collections.defaultdict(set); historical=0
    for f in a['historical_full_body_resolvers']:
        st=f['storage']
        if st['kind']=='tar_gzip_member':
            ar=st['archive'];name=ar['path']
            if name not in archive_cache:
                b=(STATE/name).read_bytes();check_pin(ar,b)
                with tarfile.open(fileobj=io.BytesIO(b),mode='r:gz') as t:
                    members=[m for m in t.getmembers() if m.isfile()]
                    assert len({m.name for m in members})==len(members)
                    archive_cache[name]={m.name:t.extractfile(m).read() for m in members}
            b=archive_cache[name][st['member']];member_sets[name].add(st['member'])
        elif st['kind']=='immutable_original_reference':
            ref=st['file'];b=(STATE/ref['path']).read_bytes();check_pin(ref,b)
        else:raise ValueError(st['kind'])
        check_pin(f,b);historical+=1
    for name,members in archive_cache.items():assert member_sets[name]==set(members),('incomplete archive',name)
    objects={'data/turnout/priority-set.json':contract};companions=0
    for f in a['complete_source_companion_files']:
        b=fixed.get(f['path'])
        if b is None:b=(STATE/f['path']).read_bytes()
        check_pin(f,b);x=companion(f,b)
        assert semantic(x)==f['full_semantic_sha256'],('companion semantic',f['path'])
        assert type(x).__name__==f['semantic_type'] and len(x)==f['complete_length']
        objects[f['path']]=x;companions+=1
    for f in a['complete_opaque_invalid_fixture_files']:
        b=(STATE/f['path']).read_bytes();check_pin(f,b)
        try:strict(decoded(f['path'],b))
        except (ValueError,UnicodeDecodeError):pass
        else:raise AssertionError(('fixture unexpectedly valid',f['path']))
    # Compare every complete dict/list, including all scalar descendants in each
    # canonical body, and independently require exact traversal order/membership.
    def expected_stream():
        for f in a['complete_root_field_semantics']:
            yield a['frozen_contract']['path'],f['pointer'],pointer(contract,f['pointer'])
        for f in a['complete_source_companion_files']:
            for p,x in walk(objects[f['path']]):yield f['path'],p,x
    iterator=iter(expected_stream())
    counts=collections.Counter();ledger_count=0;partition_counts=[]
    for f in a['complete_source_object_reference_bodies']:
        b=(STATE/f['path']).read_bytes();check_pin(f,b);raw=gzip.decompress(b)
        assert len(raw)==f['complete_reconstructed_bytes'] and sha(raw)==f['complete_reconstructed_sha256']
        n=0
        for line in raw.splitlines():
            ref=strict(line);name=ref['file']
            expected_name,p,x=next(iterator)
            assert name==expected_name,('file order',name,expected_name)
            assert p==ref['pointer'],('order/pointer',name,p,ref['pointer'])
            assert semantic(x)==ref['full_recursive_semantic_sha256'],('object full semantics',name,p)
            counts[name]+=1;n+=1;ledger_count+=1
        assert n==f['complete_object_count'];partition_counts.append(n)
    assert next(iterator,None) is None
    assert dict(counts)==a['source_objects_by_file'] and ledger_count==a['complete_source_object_count']
    seals=[]
    for f in a['producer_seals']:
        b=(STATE/f['path']).read_bytes();check_pin(f,b);m=strict(b);entries=m[f['owned_field']]
        assert len(entries)==f['owned_entries']
        for entry in entries:check_pin(entry,(STATE/entry['path']).read_bytes())
        seals.append({'path':f['path'],'targets':len(entries),'self_excluded':f['path'] not in [e['path'] for e in entries]})
    pins=strict(fixed['data/baselines/source/input-pins.json']);original_entities=set()
    for r in pins['sources']:
        rb=(STATE/r['receipt_path']).read_bytes()
        assert sha(rb)==r['receipt_sha256'] and len(rb)==r['receipt_bytes'] and strict(rb)==r['receipt']
        for e in r['entities']:
            b=(STATE/e['path']).read_bytes();check_pin(e,b);raw=decoded(e['path'],b)
            assert len(raw)==e['raw_bytes'] and sha(raw)==e['raw_sha256'];original_entities.add(e['raw_sha256'])
    add=strict(fixed['data/baselines/source/additional-pins.json']);rb=(STATE/add['receipt_path']).read_bytes()
    assert sha(rb)==add['receipt_sha256'] and strict(rb)==add['receipt']
    e=add['entity'];b=(STATE/e['path']).read_bytes();check_pin(e,b);raw=decoded(e['path'],b)
    assert sha(raw)==e['raw_sha256'] and len(raw)==e['raw_bytes']
    shared=strict(fixed['data/turnout/source/pinned-originals.json']);shared_raw={};csv_reconstruction=[]
    for pin in shared:
        rb=(STATE/'data/turnout'/pin['receipt_path']).read_bytes();assert sha(rb)==pin['receipt_sha256'];strict(rb)
        b=(STATE/pin['body_path']).read_bytes()
        assert len(b)==pin['stored_bytes'] and sha(b)==pin['stored_sha256']
        raw=gzip.decompress(b)
        assert len(raw)==pin['raw_bytes'] and sha(raw)==pin['raw_sha256']
        shared_raw.setdefault(pin['raw_sha256'],raw)
        if pin['id'].endswith('senate-linked-csv'):
            year=pin['id'].split('-')[1]
            records=list(csv.reader(io.StringIO(raw.decode('utf-8-sig'),newline='')))
            own=strict(b'[]')
            ref='data/turnout/'+contract['full_historical_source_records'][year]
            own=[strict(line) for line in gzip.decompress((STATE/ref).read_bytes()).splitlines()]
            assert len(own)==len(records),(year,'complete original record count')
            for i,(record,extracted) in enumerate(zip(records,own),1):
                assert extracted['source_record']==i and extracted['cells']==record,(year,i)
                span=raw[extracted['byte_start']:extracted['byte_end_exclusive']]
                # The retained literal full byte span must decode to the exact
                # cells, including headers, controls, administrative rows/blanks.
                assert list(csv.reader(io.StringIO(span.decode('utf-8-sig'),newline='')))==[record],(year,i,'byte span')
            csv_reconstruction.append({'year':year,'complete_logical_records':len(records),'all_header_control_parent_native_cells_and_positions_verified':True})
    assert len(shared)==9
    units=contract['ordered_units'];bykey={u['key']:u for u in units}
    order=sorted(units,key=lambda u:(-u['reported_candidate_writein_votes'],u['source_record']))
    assert [u['key'] for u in order]==a['ordered_full_keys']==contract['full_all_unit_order']
    assert len(bykey)==2669 and sum(u['reported_candidate_writein_votes'] for u in units)==4445535
    total=4445535;threshold=(4*total+4)//5;acc=0;n=0
    while acc<threshold:acc+=order[n]['reported_candidate_writein_votes'];n+=1
    assert n==1538 and acc==3557034 and acc-order[n-1]['reported_candidate_writein_votes']==3555604
    assert [u['key'] for u in order[:n]]==a['ordered_priority_keys']==contract['ordered_priority_keys']
    assert [u['key'] for u in order[n:]]==a['ordered_remainder_keys']==contract['ordered_remainder_keys']
    assert len(contract['parent_inventory'])==133 and len(a['ordered_priority_parent_keys'])==108
    for p,arrays in a['all_parent_ordered_child_arrays'].items():
        children=[u['key'] for u in order if u['parent_key']==p]
        assert children==arrays['full_source_rank_ordered_children']
        assert [k for k in children if k in set(a['ordered_priority_keys'])]==arrays['ordered_priority_children']
        assert [k for k in children if k in set(a['ordered_remainder_keys'])]==arrays['ordered_remainder_children']
        assert pointer(contract,arrays['complete_parent_contract_pointer'])['historical_parent_key']==p
    result={'status':'pass','external_acceptance_authority_path':str(AUTHORITY.relative_to(STATE)),
      'complete_contract_root_fields':len(contract),'fixed_bodies':len(fixed),'companions':companions,
      'full_recursive_objects':ledger_count,'ordered_partition_object_counts':partition_counts,
      'complete_archives':len(archive_cache),'historical_exact_body_resolvers':historical,
      'opaque_invalid_fixtures':len(a['complete_opaque_invalid_fixture_files']), 'producer_seals':seals,
      'original_receipts':len(pins['sources']),'original_distinct_raw_entities':len(original_entities),
      'shared_original_bodies':len(shared),'independent_complete_original_csv_reconstruction':csv_reconstruction,
      'final_candidate_workbook_verified':True,'native_records':len(units),'parents':133,
      'priority':n,'priority_parents':108,'remainder':len(units)-n,'threshold_integer':threshold,
      'producer_code_executed':False,'network_requests':0,'scenario_or_outcome_equality_claim':False}
    if write:(ROOT/'historical-replay.json').write_bytes(json.dumps(result,indent=2).encode()+b'\n')
    print(json.dumps(result))
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args();main(args.write)
