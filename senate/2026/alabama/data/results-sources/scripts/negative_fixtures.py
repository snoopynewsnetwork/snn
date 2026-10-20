"""Actual corruptions, retained as exact patches against whole pinned inputs."""
import copy,gzip,json
from pathlib import Path
from replay_authority import STATE,OWN,CONTRACT,loadpin,parse,semantic,digest,verify
from build_data import validate,dump

def pointer_set(o,path,value):
    keys=path.strip('/').split('/');cur=o
    for k in keys[:-1]:cur=cur[int(k)] if isinstance(cur,list) else cur[k]
    k=int(keys[-1]) if isinstance(cur,list) else keys[-1]
    old=copy.deepcopy(cur[k]);cur[k]=value
    return cur,k,old

def test_contract(c):
    # Whole exact original root semantics reject changes even when arithmetic still balances.
    a=parse((STATE/'data/coordinator-priority-acceptance.json').read_bytes())
    for f in a['complete_root_field_semantics']:
        assert semantic(c[f['pointer'][1:]])==f['full_recursive_semantic_sha256']

def run(write=True):
    hraw=(OWN/'historical-hierarchy.json.gz').read_bytes();h=parse(gzip.decompress(hraw));validate(h)
    c=parse(loadpin(CONTRACT));test_contract(c)
    base={'path':'historical-hierarchy.json.gz','bytes':len(hraw),'sha256':digest(hraw),
          'reconstruct':'gzip.decompress whole body, parse strict JSON, apply exact JSON-pointer replacement'}
    fixtures=[]
    hcases=[('missing-native','/source_contexts',h['source_contexts'][:-1]),
      ('missing-parent','/parents',h['parents'][:-1]),
      ('county-substitute','/full_order',[p['parent_key'] for p in h['parents']]),
      ('reordered-priority','/ordered_priority',list(reversed(h['ordered_priority']))),
      ('reordered-remainder','/ordered_remainder',list(reversed(h['ordered_remainder']))),
      ('wrong80','/threshold_integer',1812071),('residual-allocation','/remainder_votes',452271),
      ('changed-count','/source_contexts/0/reported_candidate_votes',15692),
      ('wrong-rank','/source_contexts/0/rank',2),('wrong-mask','/source_contexts/0/priority',False),
      ('numeric-label-alias','/source_contexts/0/key','1'),
      ('wrong-source-column','/source_contexts/0/original_member/column_1based',6),
      ('wrong-original-member','/source_contexts/0/original_member/name','2024-General-Autauga.xls'),
      ('wrong-context-pointer','/source_contexts/0/full_own_source_context/pointer','/units/1'),
      ('truncated-source-context','/source_contexts/0/full_own_source_context',{'pointer':'/units/0'}),
      ('current-native-id','/source_contexts/0/current_native_id','0081'),
      ('current-choice-id','/source_contexts/0/current_choice_id','001'),
      ('current-match','/source_contexts/0/current_match','ABSENTEE'),
      ('unproved-CRS','/source_contexts/0/geometry_crs','EPSG:4326'),
      ('unproved-vintage','/source_contexts/0/geography_vintage','2026'),
      ('November-admission','/parents/0/November_votes_admitted',True),
      ('current-legal-admission','/approvals/current_legal',True),
      ('eligible-writein-admission','/approvals/eligible_named_writein',True),
      ('wrong-parent-array','/parents/0/full_source_rank_ordered_children',h['parents'][0]['full_source_rank_ordered_children'][:-1])]
    ccases=[('candidate-truncation','/units/0/candidate_votes',c['units'][0]['candidate_votes'][:-1]),
      ('party-change','/units/0/candidate_votes/0/party_literal','REP'),
      ('candidate-null-to-zero','/units/0/candidate_votes/0/raw_value',0),
      ('administrative-truncation','/units/0/administrative_fields',[]),
      ('raw-source-position','/units/0/candidate_votes/0/row_1based',11),
      ('method-change','/units/0/method_context','election_day'),
      ('native-header-alias','/units/0/native_label','1'),
      ('registration-null-inference','/units/0/registration_source',None),
      ('under-over-residual','/units/0/under_votes_source',49),
      ('duplicate-native-key','/units/1/key',c['units'][0]['key']),
      ('raw-context-truncation','/units/0/contest_other_fields',[]),
      ('actual-source-null-to-zero','/units/2084/administrative_fields/0/value',0)]
    assert c['units'][2084]['administrative_fields'][0]['value'] is None
    for scope,obj,cases,check,pin in [('hierarchy',h,hcases,validate,base),('contract',c,ccases,test_contract,CONTRACT)]:
        for name,path,val in cases:
            cur,key,old=pointer_set(obj,path,val)
            try:
                try:check(obj)
                except (AssertionError,ValueError,KeyError,IndexError,TypeError) as e:
                    result={'status':'REJECTED','exception':type(e).__name__,'reason':str(e)}
                else:raise AssertionError('negative fixture accepted: '+name)
            finally:cur[key]=old
            patch={'op':'replace','pointer':path,'value':val}
            if isinstance(old,list) and isinstance(val,list) and val==old[:-1]:
                patch={'op':'remove','pointer':path+'/'+str(len(old)-1)}
            fixture={'name':name,'scope':scope,'base':pin,'patch':patch,'actual_result':result}
            fixtures.append(fixture)
    # Real whole-byte truncation and complete companion replacement, not projected field samples.
    for name,pin,b in [('truncated-original-contract',CONTRACT,loadpin(CONTRACT)[:-1]),
                       ('whole-companion-replaced',next(x for x in parse((STATE/'data/coordinator-priority-acceptance.json').read_bytes())['complete_source_companion_files'] if x['path']=='data/turnout/candidate-universe.json'),b'[]')]:
        try:verify(b,pin)
        except AssertionError:pass
        else:raise AssertionError('byte corruption admitted')
        fixtures.append({'name':name,'base':pin,'byte_patch':{'op':'drop-last-byte'} if name.startswith('truncated') else {'op':'replace-whole','utf8':'[]'},'actual_result':{'status':'REJECTED','rule':'whole original size/SHA'}})
    raw=gzip.decompress(hraw); marker=b'"schema":';at=raw.index(marker)
    bad=raw[:at]+b'"schema":null,'+raw[at:]
    try:parse(bad)
    except ValueError:pass
    else:raise AssertionError('duplicate JSON fields admitted')
    fixtures.append({'name':'duplicate-JSON-key','base':base,'byte_patch':{'offset':at,'insert_utf8':'"schema":null,'},'actual_result':{'status':'REJECTED','rule':'strict duplicate JSON field parser'}})
    witness=parse((STATE/'data/turnout/source/original-first-witness.json').read_bytes())
    src=next(x for x in witness['sources'] if x.get('members'))
    rp=STATE/'data/turnout'/src['receipt'];rb=rp.read_bytes();r=parse(rb)
    from replay_originals import receipt_body
    original=receipt_body(r,STATE/'data/turnout')
    rawpin={'bytes':r['original_bytes'],'sha256':r['original_sha256']}
    try:verify(original[:-1],rawpin)
    except AssertionError:pass
    else:raise AssertionError('truncated original ZIP accepted')
    fixtures.append({'name':'truncated-original-ZIP-entity','scope':'original-entity',
        'base_receipt':{'path':str(rp.relative_to(STATE)),'bytes':len(rb),'sha256':digest(rb)},
        'whole_entity':rawpin,'byte_patch':{'op':'drop-last-byte'},'actual_result':{'status':'REJECTED','rule':'complete entity size/SHA before parsing'}})
    if write:
        out=OWN/'qa/fixtures';out.mkdir(exist_ok=True)
        for f in fixtures:(out/(f['name']+'.json')).write_bytes(dump(f))
        (OWN/'qa/negative-validation.json').write_bytes(dump({'status':'PASS','rejected':len(fixtures),'all_actual_inputs_reconstructable':True,
             'acceptance_path':'data/coordinator-priority-acceptance.json','current_admission':False}))
    return {'status':'PASS','rejected':len(fixtures)}

def audit_stored():
    """Apply every retained input patch to the entire pinned base and rerun it."""
    files=sorted((OWN/'qa/fixtures').glob('*.json'));count=0
    for p in files:
        f=parse(p.read_bytes());scope=f.get('scope');pin=f.get('base')
        try:
            if scope=='original-entity':
                from replay_originals import receipt_body
                r=parse(loadpin(f['base_receipt']));b=receipt_body(r,STATE/'data/turnout')
                verify(b[:-1],f['whole_entity'])
            elif 'patch' in f:
                b=loadpin(pin) if scope=='contract' else verify((OWN/pin['path']).read_bytes(),pin)
                o=parse(gzip.decompress(b) if scope=='hierarchy' else b)
                patch=f['patch']
                if patch['op']=='replace':pointer_set(o,patch['pointer'],patch['value'])
                else:
                    keys=patch['pointer'].strip('/').split('/');cur=o
                    for k in keys[:-1]:cur=cur[int(k)] if isinstance(cur,list) else cur[k]
                    del cur[int(keys[-1]) if isinstance(cur,list) else keys[-1]]
                (validate if scope=='hierarchy' else test_contract)(o)
            elif f['name']=='duplicate-JSON-key':
                b=gzip.decompress(verify((OWN/pin['path']).read_bytes(),pin));patch=f['byte_patch'];i=patch['offset']
                parse(b[:i]+patch['insert_utf8'].encode()+b[i:])
            else:
                b=loadpin(pin);patch=f['byte_patch']
                verify(b[:-1] if patch['op']=='drop-last-byte' else patch['utf8'].encode(),pin)
        except (AssertionError,ValueError,KeyError,IndexError,TypeError):count+=1
        else:raise AssertionError('stored negative accepted: '+p.name)
    assert count==40 and len(files)==40
    return {'status':'PASS','stored_whole_inputs_replayed_and_rejected':count}
if __name__=='__main__':
    import sys
    print(json.dumps(audit_stored() if '--audit' in sys.argv else run()))
