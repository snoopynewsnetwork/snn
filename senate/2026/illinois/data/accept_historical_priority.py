"""External full-field historical dispatch seal; never change producer flags.

The complete object-reference ledger is lossless JSONL gzip so every stored
object remains below40MB. It is a complete ledger, not a sampled projection.
"""
from pathlib import Path
from collections import Counter
import csv
import gzip
import hashlib
import io
import json

D=Path(__file__).resolve().parent
S=D.parent
T=D/'turnout'
B=D/'baselines'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def canonical(v):
    return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()


def sem(v):
    return sha(canonical(v))


def pin(p):
    raw=p.read_bytes()
    assert len(raw)<40_000_000
    return dict(path=str(p.relative_to(S)),bytes=len(raw),sha256=sha(raw))


def pointer(key):
    return '/'+str(key).replace('~','~0').replace('/','~1')


def main():
    cp=T/'priority-set.json'
    assert sha(cp.read_bytes())=='50a21c166dbe14339d3cfa103443c75d7141bf6554f40f5cc96dddf8dfecb78e'
    c=json.loads(cp.read_bytes())
    assert c['coordinator_acceptance'] is False and c['current_geometry_approved'] is False
    assert (len(c['full_order']),len(c['ordered_priority_keys']),len(c['remainder_keys']))==(10062,5540,4522)
    p=c['primary_priority']
    assert (p['denominator'],p['top15_votes'],p['preceding_votes'],p['crossing_votes'],p['cumulative80_votes'])==(5592368,29572,4473789,523,4474312)
    review_paths=[D/x for x in ['coordinator-native-category-review.json','coordinator-county-original-review.json',
                                'coordinator-turnout-final-review.json','coordinator-baseline-final-review.json',
                                'coordinator-first-pair-math-review.json',
                                'coordinator-live-input-review-v1/final-repair-review.json']]
    for path in review_paths:
        assert json.loads(path.read_bytes())['status'].startswith('pass')
    assert json.loads((D/'coordinator-first-pair-math-review.json').read_bytes())['complete_state_scenarios']==99
    producer_seals=[]
    for root,owned_field in [(T,'assets'),(B,'owned_assets')]:
        mfpath=root/'asset-manifest.json';mf=json.loads(mfpath.read_bytes())
        expected={r['path'] for r in mf[owned_field]}
        actual={str(x.relative_to(S)) for x in root.rglob('*') if x.is_file() and x.name!='asset-manifest.json'}
        actual|={'turnout.md','data/county-turnout.csv'} if root==T else {'county-partisanship.md','data/county-baselines.csv'}
        assert actual==expected
        for row in mf[owned_field]:
            assert pin(S/row['path'])==row
        if root==T:
            for row in mf['external_originals']:
                assert pin(S/row['path'])==row
        else:
            for row in mf['source_references']:
                z=(root/row['path']).read_bytes();raw=gzip.decompress(z)
                assert len(z)==row['bytes']<40_000_000 and sha(z)==row['sha256']
                assert len(raw)==row['raw_bytes'] and sha(raw)==row['raw_sha256']
        producer_seals.append(dict(**pin(mfpath),owned_field=owned_field,
                                   owned_entries=len(expected),owned_path_resolution='state-relative',
                                   original_reference_field='external_originals' if root==T else 'source_references',
                                   original_reference_path_resolution='state-relative' if root==T else 'baseline-directory-relative',
                                   every_complete_listed_body_required=True))
    buffer=io.BytesIO()
    raw_hash=hashlib.sha256();raw_size=0;object_count=0;by_file=Counter()
    with gzip.GzipFile(fileobj=buffer,mode='wb',mtime=0,filename='') as compressed:
        def emit(file,locator,obj):
            nonlocal raw_size,object_count
            row=dict(file=file,**locator,full_recursive_semantic_sha256=sem(obj))
            line=canonical(row)+b'\n'
            compressed.write(line);raw_hash.update(line);raw_size+=len(line);object_count+=1;by_file[file]+=1
        for key,value in c.items():
            emit('data/turnout/priority-set.json',dict(pointer=pointer(key)),value)
        for field in ['native_constituents','authority_inventory','unavailable_cases','primary_scope_missing_cells']:
            for index,value in enumerate(c[field]):
                emit('data/turnout/priority-set.json',dict(pointer=pointer(field)+'/'+str(index)),value)
        for key,value in c['native_to_authority_parent_map'].items():
            emit('data/turnout/priority-set.json',dict(pointer='/native_to_authority_parent_map'+pointer(key)),value)
        paths=sorted([x for folder in [T/'extract',B/'extract'] for x in folder.iterdir() if x.is_file()])
        paths += [T/'source/shared-originals.json',T/'source/external-originals.json',
                  T/'source/provider-parent-receipts.json',B/'source/registry.json.gz',B/'schema-inventory.json',
                  B/'priority/contracts.json',B/'scenario-settings.json',B/'authority-state-scenarios.json']
        companions=[]
        for path in paths:
            descriptor=pin(path);raw=path.read_bytes()
            if path.suffix=='.gz':
                raw=gzip.decompress(raw)
                descriptor.update(complete_reconstructed_bytes=len(raw),complete_reconstructed_sha256=sha(raw))
            basename=path.name.removesuffix('.gz');file=str(path.relative_to(S))
            if basename.endswith('.jsonl'):
                ordered=hashlib.sha256();ordered.update(b'[');length=0
                for index,line in enumerate(raw.splitlines(),1):
                    if not line:continue
                    value=json.loads(line)
                    if length:ordered.update(b',')
                    ordered.update(canonical(value));length+=1
                    emit(file,dict(JSONL_record_1based=index),value)
                ordered.update(b']')
                descriptor.update(full_semantic_sha256=ordered.hexdigest(),complete_length=length,semantic_type='ordered_JSONL_object_list')
            elif basename.endswith('.json'):
                value=json.loads(raw)
                descriptor.update(full_semantic_sha256=sem(value),complete_length=len(value),semantic_type=type(value).__name__)
                entries=enumerate(value) if isinstance(value,list) else value.items()
                for key,item in entries:
                    emit(file,dict(pointer=pointer(key)),item)
            elif basename.endswith('.csv'):
                value=list(csv.reader(io.StringIO(raw.decode('utf-8-sig'))))
                descriptor.update(full_semantic_sha256=sem(value),complete_length=len(value),
                                  semantic_type='ordered_CSV_rows_including_complete_header',complete_header=value[0])
                for index,item in enumerate(value,1):
                    emit(file,dict(CSV_row_1based_including_header=index),item)
            descriptor.update(complete_body_required=True,projection_or_subset_substitution=False)
            companions.append(descriptor)
    stored=buffer.getvalue();assert len(stored)<40_000_000
    ledger=D/'coordinator-full-source-object-refs-v1.jsonl.gz'
    if ledger.exists():assert ledger.read_bytes()==stored
    else:ledger.write_bytes(stored)
    ledger_pin=dict(**pin(ledger),complete_reconstructed_bytes=raw_size,
                    complete_reconstructed_sha256=raw_hash.hexdigest(),complete_object_count=object_count,
                    format='Complete ordered JSONL ledger; stream every line and verify its full source object, not a sample.',
                    source_objects_by_file=dict(by_file))
    priorities=set(c['ordered_priority_keys']);remainder=set(c['remainder_keys'])
    assert not priorities.intersection(remainder)
    mapping=c['native_to_authority_parent_map'];parent_keys=[]
    for key in c['ordered_priority_keys']:
        if mapping[key] not in parent_keys:parent_keys.append(mapping[key])
    assert len(parent_keys)==97
    parents={}
    for authority in c['authority_inventory']:
        key=authority['key'];source_children=authority['native_constituent_keys']
        assert all(mapping[x]==key for x in source_children)
        ranked=[x for x in c['full_order'] if mapping[x]==key]
        assert set(ranked)==set(source_children)
        parents[key]=dict(original_source_ordered_children=source_children,
                          canonical_rank_ordered_children=ranked,
                          ordered_priority_children=[x for x in ranked if x in priorities],
                          ordered_remainder_children=[x for x in ranked if x in remainder])
    fixed=['turnout.md','county-partisanship.md','data/county-turnout.csv','data/county-baselines.csv',
           'data/turnout/validation.json','data/baselines/validation.json','data/turnout/peer-reconciliation.json',
           'data/baselines/peer-reconciliation.json','data/baselines/peer-native-priority-reconciliation.json',
           'data/baselines/peer-final-availability-reconciliation.json','data/turnout/source/SCHEMA.md',
           'data/baselines/source/SCHEMA.md','data/baselines/negative-fixture-results.json']
    result=dict(schema='IL-external-complete-historical-source-dispatch-v1',
                status='accepted_complete_historical_known_printed_source_research_dispatch_only',
                coordinator_agent_id='d0fc3534-1613-4883-b48b-21a233fcfd9e',state='IL',
                authority='External acceptance PATH ONLY in later worker packages. Never copy/reverse-pin this authority or change frozen producer false flags.',
                frozen_contract=pin(cp),producer_seals=producer_seals,
                frozen_first_pair_assets=[pin(S/x) for x in fixed],
                independent_coordinator_reviews=[pin(x) for x in review_paths],
                primary_scope=c['primary_scope'],source_candidate_denominator=5592368,top15_votes=29572,
                minimum80=dict(count=5540,votes=4474312,preceding_count=5539,preceding_votes=4473789,
                               crossing_key=p['crossing_key'],crossing_votes=523),
                remainder=dict(count=4522,votes=1118056,unavailable_named_pool_contexts=4),
                full_native_source_groups=10062,full_source_presentations=11535,
                all_source_authorities=108,priority_source_authorities=97,geographic_counties=102,
                ordered_full_keys=c['full_order'],ordered_priority_keys=c['ordered_priority_keys'],
                ordered_remainder_keys=c['remainder_keys'],ordered_priority_parent_literals=parent_keys,
                derived_ordered_child_arrays_by_parent=parents,
                complete_root_field_semantics=[dict(pointer=pointer(k),full_recursive_semantic_sha256=sem(v)) for k,v in c.items()],
                complete_source_companion_files=companions,
                complete_source_object_reference_bodies=[ledger_pin],complete_source_object_count=object_count,
                full_field_rule='Every complete contract/root/companion/object/producer-sealed original remains recursively reconstructable. The gzip ledger is complete, not a projection; verify every row, original schema and null/admin/category/source position. No current ID or geographic join follows.',
                source_partitions=dict(original_CSV_rows=146370,original_columns_per_row=12,
                                       full_literal_field_positions=1756440,
                                       native_source_groups_by_year={'2024':10062,'2022':9478,'2020':10106},
                                       complete_combined_county_views=306,county_candidate_rows=1462,
                                       observed_zero_pair_contexts=745,unknown_named_pools=4,other_absent_Kennedy_cells=15),
                source_qualifications=[
                    'No2024 Senate:2024president primary,2022otherClassIII Senate midterm,2020sameClassII Senate. Candidate parties/literal labels remain source-specific.',
                    'Known printed candidate-record scope is not all eligible/native valid votes. State27literal rows5633310, finer printed5592368 and generic57411 leave16469 scope difference unallocated;27rows are not27legal tickets. Genericcase variants/absence stay explicit.',
                    '108disjoint source authority IDs differ from102combined county selector pages. County pages include six city commission slices; never add combined counties/cities. No108current authority/legal-boundary assumption.',
                    'All11535presentations/raw12fields preserved. Four administrative-only named pools staynull and sort after observed numeric zeros;745A=B=0 are observed zero pools with undefined preference. Missing Kennedy source rows remain absent/null, not0.',
                    'Registration repeats on raw candidate/category rows and differs from historical Total Voters; current A/I letters remain literal without definition expansion. No exact outstanding ballot pool is registration minus counts.',
                    'Native all-category2024 tally5702776 differs from independent ballots5705246 by2470, unallocated. Historical generic/blank/under/over/method availability differs; no residual allocation or label-derived methods.',
                    'Source-only printed threshold5540 is accepted for bounded historical research dispatch. Eligible-writein robustness/current physical or legal geography/November roster/feed IDs/cadence/remainder/collector/probability remain unapproved.'
                ],
                dispatch_requirements=[
                    'Inventory current state/allactual county and city authorities; preserve108 historical source-parent records separately. Deeply investigate all97priority source-parent chains with actual public evidence and5540ordered shared-parent records plus4522remainder/all10062/full108 hierarchy.',
                    'Acquire actual official/linked map assets and qualified full-state historical fallback. Every priority observation gets specific shared-resource/access/vintage/finer/current gaps; no invented5540leaf/current/legal matches or spatial vote allocation.',
                    'Independently replay complete contract/root fields, every complete companion, every full gzip-ledger source object and every producer-sealed immutable file reference. No mutable newsroom aggregate, unfinished peer/coordinator proof, producer edit or reverse acceptance dependency.'
                ],current_geography_approved=False,current_November_returns_admitted=False,
                current_choice_or_reporting_IDs_approved=False,legal_native_80_robustness_approved=False,
                live_cadence_or_exact_remainder_approved=False,collector_or_probability_approval=False)
    path=D/'coordinator-priority-acceptance.json'
    encoded=(json.dumps(result,indent=2,ensure_ascii=False)+'\n').encode()
    assert len(encoded)<40_000_000
    if path.exists():assert path.read_bytes()==encoded
    else:path.write_bytes(encoded)
    print(json.dumps(dict(**pin(path),root_fields=len(c),complete_companions=len(companions),
                          complete_objects=object_count,object_ledger_stored_bytes=len(stored))))


if __name__=='__main__':
    main()
