"""Actual complete packets with corruption; no source/producer repair."""
import json,gzip,copy,base64,sys
from pathlib import Path
from replay import loads,digest,checked,STATE,HERE,semantic
from original_replay import originals,workbook
def packet():
    a=loads((STATE/'data/coordinator-priority-acceptance.json').read_bytes());p=loads(checked(a['frozen_contract']))
    bodies,pins,n=originals();w,witness=workbook(bodies['sos-2024-general-precinct-original'],p)
    source=next(x for x in pins if x['receipt']['id']=='2024-federal-05001')
    return {'historical_context':p,'whole_original_body_base64':base64.b64encode(bodies['2024-federal-05001']).decode(),'original_receipt':source['receipt'],'complete_companion':loads((STATE/'data/turnout/source/original-pins.json').read_bytes()),'complete_header_candidate_row':witness[0], 'qualifications':{'CRS':None,'vintage':'historical2024 source only','current_matches':None,'native80_legal':False,'current_admission':False,'county_substitution':False,'residual_allocation':False}}
def validate_bytes(b,expected):
    value=loads(b)
    # Whole recursive equality, without projecting away unknown/native/admin fields.
    # JSON's bool/int equality is deliberately avoided by typed canonical encoding.
    if semantic(value)!=semantic(expected):raise ValueError('complete source/context/qualification packet differs')
    raw=base64.b64decode(value['whole_original_body_base64'],validate=True)
    assert digest(raw)==digest(base64.b64decode(expected['whole_original_body_base64']))
    p=value['historical_context'];rows=p['full_order'];total=sum(x['votes'] for x in rows)
    assert len(rows)==2841 and total==1182676 and len(p['ordered_priority_keys'])==1056
    assert len(p['all75parents'])==75 and sum(x['votes'] for x in rows[:1055])*5<4*total<=sum(x['votes'] for x in rows[:1056])*5
    return True
def cases(expected):
    def leaf(x):return x['historical_context']['full_order'][0]
    yield 'truncated-whole-original',lambda x:x.update(whole_original_body_base64=base64.b64encode(base64.b64decode(x['whole_original_body_base64'])[:-1]).decode())
    yield 'truncated-whole-companion',lambda x:x['complete_companion'].pop()
    yield 'missing-native',lambda x:x['historical_context']['full_order'].pop()
    yield 'missing-administrative-context',lambda x:leaf(x).pop('unit_type')
    yield 'changed-raw-position',lambda x:leaf(x)['source_rows'].__setitem__(0,leaf(x)['source_rows'][0]+1)
    yield 'missing-method-mask',lambda x:leaf(x)['methods'].pop('Provisional')
    yield 'numeric-native-id-alias',lambda x:leaf(x).update(matched_api_native_id=12)
    yield 'changed-native-count',lambda x:leaf(x).update(votes=leaf(x)['votes']+1)
    yield 'invented-CRS',lambda x:x['qualifications'].update(CRS='EPSG:4326')
    yield 'current-vintage-substitution',lambda x:x['qualifications'].update(vintage='2026 approved')
    yield 'changed-full-order',lambda x:x['historical_context']['full_order'].__setitem__(slice(0,2),list(reversed(x['historical_context']['full_order'][:2])))
    yield 'wrong-80-crossing',lambda x:x['historical_context']['ordered_priority_keys'].pop()
    yield 'county-substitute',lambda x:x['historical_context'].update(full_order=x['historical_context']['all75parents'])
    yield 'residual-allocation',lambda x:x['qualifications'].update(residual_allocation=True)
    yield 'null-to-zero',lambda x:leaf(x).update(ballots_cast=0)
    yield 'party-relabel',lambda x:leaf(x)['party_literals'].update({'Jill Stein/Rudolph Ware':'Democratic'})
    yield 'missing-candidate',lambda x:leaf(x)['candidates'].pop('Michael Wood/John G. Pietrowski')
    yield 'truncated-header',lambda x:x['complete_header_candidate_row']['header'].pop()
    yield 'changed-original-cell',lambda x:x['complete_header_candidate_row']['cells'][0]['attributes'].update(r='Z999')
    yield 'missing-source-receipt-field',lambda x:x['original_receipt'].pop('url')
    yield 'changed-parent-child-array',lambda x:x['historical_context']['all75parents'][0]['source_native_constituents']['2024-api'].pop()
    yield 'current-match-invented',lambda x:x['qualifications'].update(current_matches={'old':'current'})
    yield 'current-admission',lambda x:x['qualifications'].update(current_admission=True)
    yield 'native80-legal-admission',lambda x:x['qualifications'].update(native80_legal=True)
def run(write=False):
    expected=packet();base=json.dumps(expected,ensure_ascii=False,separators=(',',':')).encode();validate_bytes(base,expected)
    root=HERE/'fixtures';results=[]
    if write:root.mkdir(exist_ok=True);(root/'complete-positive.json.gz').write_bytes(gzip.compress(base,mtime=0))
    for name,modify in cases(expected):
        if write:
            bad=copy.deepcopy(expected);modify(bad);b=json.dumps(bad,ensure_ascii=False,separators=(',',':')).encode();(root/(name+'.json.gz')).write_bytes(gzip.compress(b,mtime=0))
        else:b=gzip.decompress((root/(name+'.json.gz')).read_bytes())
        rejected=False
        try:validate_bytes(b,expected)
        except (ValueError,AssertionError,KeyError,TypeError):rejected=True
        assert rejected,name
        results.append({'fixture':name+'.json.gz','raw_bytes':len(b),'raw_sha256':digest(b),'expected':'reject','actual':'reject'})
    name='duplicate-json-keys';b=b'{"qualifications":null,"qualifications":{}}'
    if write:(root/(name+'.json.gz')).write_bytes(gzip.compress(b,mtime=0))
    else:b=gzip.decompress((root/(name+'.json.gz')).read_bytes())
    try:validate_bytes(b,expected)
    except ValueError:results.append({'fixture':name+'.json.gz','raw_bytes':len(b),'raw_sha256':digest(b),'expected':'reject','actual':'reject'})
    else:raise AssertionError(name)
    return {'positive_complete_packet':'pass','negative_count':len(results),'cases':results,'full_packet_scope':'entire historical contract, complete original county body, full original receipt/companion, exact typed workbook/header/candidate cells and qualifications'}
if __name__=='__main__':
    write='--write' in sys.argv;result=run(write)
    if write:(HERE/'negative-proof.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'negative_count':result['negative_count'],'status':'pass'}))
