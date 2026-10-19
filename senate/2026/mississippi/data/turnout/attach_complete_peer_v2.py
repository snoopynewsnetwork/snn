"""Read-only, exact-byte V2 peer witness for the proposed 2024 native order.

The peer's frozen objects remain external dependencies. This adds no acceptance
of current geography and does not change any vote or rank in the owned contract.
"""
import gzip
import json

from acquire_sources import BASE, OUT, sha

SNAPSHOT='data/baselines/source/native-priority-v2/snapshot.json'
SNAPSHOT_SHA='a0432f1e47245c7b934a2328ebda95d3d96566c58cd3f71901406d060efc85ec'
COMPANION='data/baselines/source/native-priority-v2-field-evidence-v1/snapshot.json'
COMPANION_SHA='9bfe1e6f08f9e9b12e494302c58176e38a2a610adeb0497d1785379227e5c02a'


def frozen(path, expected, stored_key):
    body=(BASE/path).read_bytes()
    assert sha(body)==expected
    snapshot=json.loads(body)
    objects={}
    for pin in snapshot['pins']:
        packed=(BASE/pin[stored_key]).read_bytes()
        raw=gzip.decompress(packed)
        assert len(packed)==pin['stored_bytes'] and sha(packed)==pin['stored_sha256']
        assert len(raw)==pin['original_bytes'] and sha(raw)==pin['original_sha256']
        objects[pin['original_path']]=raw
    return snapshot,objects


def attach(contract):
    snapshot,objects=frozen(SNAPSHOT,SNAPSHOT_SHA,'frozen_path')
    companion,companion_objects=frozen(COMPANION,COMPANION_SHA,'stored_path')
    assert len(snapshot['pins'])==4 and len(companion['pins'])==17
    assert companion['proposal']==SNAPSHOT
    assert companion_objects[SNAPSHOT]==(BASE/SNAPSHOT).read_bytes()
    peer=json.loads(objects['data/baselines/native-priority-contract-v2.json'])
    proof=json.loads(objects['data/baselines/native-2024-all11-complete-peer-reconciliation.json'])
    assert snapshot['coordinator_accepted'] is False and snapshot['current2026_geography_approved'] is False
    assert peer['coordinator_accepted'] is False and peer['current2026_geography_approved'] is False
    assert snapshot['priority_native_units']==887 and snapshot['native_units']==1736
    assert snapshot['candidate_positions']==24926 and snapshot['priority_parent_authorities']==77
    assert snapshot['preceding886']==972157 and snapshot['priority887']==972656
    assert peer['ordered_native_keys']==[x['key'] for x in contract['all_unit_order']]
    assert peer['ordered_priority_native_keys']==contract['ordered_priority_keys']
    assert peer['ordered_nonpriority_native_keys']==contract['remainder']['ordered_keys']
    assert proof['source_columns']==2266 and proof['positions']==24926
    assert not proof['value_role_differences']
    own=json.loads(gzip.decompress((OUT/'source/2024-preferred-all11-source-fields-v1.json.gz').read_bytes()))
    own_fields={x['key']:x for x in own['columns']}
    peer_fields={x['source_position_key']:x for x in peer['all_preferred_source_columns']}
    assert len(own_fields)==len(peer_fields)==2266 and set(own_fields)==set(peer_fields)
    roles={'native_reporting_constituent':'native','source_TOTAL':'TOTAL',
           'unused_template_column':'unused','parallel_native_observation':'parallel'}
    literal_differences=[];wrapped_hyphen=[]
    for key,a in own_fields.items():
        b=peer_fields[key]
        assert (a['source_id'],a['source_page'],a['source_column'],a['parent_county_fips'],a['source_raw_sha256'])==(b['source_id'],b['PDFpage'],b['physical_source_column'],b['county_fips'],b['source_raw_sha256'])
        assert roles[a['role']]==b['role']
        assert a['Senate_candidate_votes']|a['president_candidate_votes']==b['candidate_votes']
        if a['label_literal']!=b['label_literal']:
            literal_differences.append(key)
            if ' '.join(a['label_literal'].split())!=' '.join(b['label_literal'].split()):
                assert a['label_literal'].replace('-\n','-')==b['label_literal'].replace('-\n','-')
                wrapped_hyphen.append(key)
    assert len(literal_differences)==165 and len(wrapped_hyphen)==2
    contract['peer_agreement']['complete_independent_native_priority_v2']={
        'snapshot_path':SNAPSHOT,'snapshot_sha256':SNAPSHOT_SHA,
        'field_evidence_companion_path':COMPANION,'field_evidence_companion_sha256':COMPANION_SHA,
        'lossless_frozen_proposal_bodies':4,'lossless_frozen_field_evidence_bodies':17,
        'ordered_native_keys':1736,'ordered_priority_keys':887,'all11_candidate_or_null_positions':24926,
        'source_columns':2266,'value_or_role_differences':0,
        'literal_label_line_wrap_representations':len(literal_differences),
        'hyphen_wrap_representations_unequal_under_whitespace_fold':len(wrapped_hyphen),
        'coordinator_accepted':False,'current_2026_geographic_approval':False,
        'qualification':'Exact read-only peer V2 order and all11 source field witness; historical original objects are separately pinned. Literal source wraps remain separate representations.'}
    return contract


if __name__=='__main__':
    path=OUT/'priority-set.json'
    from acquire_sources import savejson
    savejson(path,attach(json.loads(path.read_text())))
    print('Read-only V2 peer witness: 887 priority, 1736 source native, 24926 all11 positions')
