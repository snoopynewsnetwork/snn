"""Bounded coordinator check of all original Pike ES&S profile count fields."""
from pathlib import Path
import csv
import gzip
import hashlib
import io
import json
import re

DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
DEST=DATA/'coordinator-qa/pike-profile-review'
# Typed from the coordinator's own complete-original rendered panels, not from
# aggregate residuals. Original OCR and its failed/mismatched tokens stay intact.
MANUAL={
 (17,'Claudia De la Cruz'):0,(17,'Peter Sonski'):0,
 (19,'Randall Terry'):0,(19,'Shiva Ayyadurai'):0,(19,'Claudia De la Cruz'):0,
 (21,'president_generic_write_in'):2,(23,'Jill Stein'):0,
 (25,'Chase Oliver'):0,(25,'Peter Sonski'):0,(25,'ballots_blank'):0,
 (26,'Randall Terry'):0,(26,'Robert F. Kennedy Jr.'):0,(26,'Ty Pinkins'):338,(26,'ballots_blank'):0,
 (28,'Chase Oliver'):0,(28,'Randall Terry'):1,(28,'president_generic_write_in'):0,
 (29,'Randall Terry'):0,(32,'Claudia De la Cruz'):0,(32,'ballots_blank'):0,
 (36,'Claudia De la Cruz'):0,(36,'president_generic_write_in'):0,
 (43,'Randall Terry'):0,(44,'Kamala D. Harris'):103,(44,'Donald J. Trump'):773,
 (45,'Jill Stein'):1,(45,'Claudia De la Cruz'):0,
 (47,'Kamala D. Harris'):348,(47,'Donald J. Trump'):316,
 (47,'senate_generic_write_in'):2,(47,'voter_turnout_percent'):47.11,
 (49,'Donald J. Trump'):222,(49,'president_generic_write_in'):3,
 (49,'senate_total_votes_cast'):614,(49,'registration_total'):1164,
 (51,'Donald J. Trump'):288,(51,'Claudia De la Cruz'):0,(51,'ballots_blank'):0,
 (53,'Shiva Ayyadurai'):0,(53,'senate_generic_write_in'):0,(53,'ballots_blank'):0,
 (55,'Randall Terry'):0,
}
LABEL_MANUAL={21:'(04) Mlk Center',36:'(13) Holmesville Comm.'}
PRES=['Kamala D. Harris','Chase Oliver','Jill Stein','Randall Terry','Donald J. Trump',
      'Shiva Ayyadurai','Claudia De la Cruz','Robert F. Kennedy Jr.','Peter Sonski']
# Independently read full original PDF13 candidate panel and PDF12 statistics.
SUMMARY=dict(zip(PRES,[6091,17,15,11,6504,9,7,52,9]))|{
 'president_generic_write_in':31,'president_total_votes_cast':12746,'president_contest_total':12824,
 'Ty Pinkins':5898,'Roger F. Wicker':6719,'senate_generic_write_in':30,
 'senate_total_votes_cast':12647,'senate_contest_total':12824,
 'registration_total':24692,'ballots_cast_total':12824}

def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
    b=p.read_bytes()
    return {'path':str(p.relative_to(ROOT)),'bytes':len(b),'sha256':sha(b)}
def snapshot(p):
    dest=DEST/(p.name+'.gz')
    if not dest.exists():
        b=p.read_bytes();assert p.read_bytes()==b
        dest.write_bytes(gzip.compress(b,mtime=0))
    return gzip.decompress(dest.read_bytes()),pin(dest)

def main():
    ledger=json.loads(gzip.decompress((DEST/'turnout-ledger-snapshot.json.gz').read_bytes()))
    parsed=json.loads((DEST/'independent-parsed-fields.json').read_bytes())
    initial=json.loads((DEST/'initial-OCR-comparison.json').read_bytes())
    assert {(r['page'],r['field']) for r in initial}==set(MANUAL) and len(MANUAL)==42
    assert sum(r['value'] is not None for r in initial)==1
    original=json.loads(gzip.decompress((DEST/'independent-original-ocr.json.gz').read_bytes()))
    meta=original['source_metadata']
    raw=gzip.decompress((ROOT/meta['path']).read_bytes())
    assert sha(raw)==ledger['raw_sha256']==meta['raw_sha256']
    own_values={};comparisons=[];direct=0;label_rows=[]
    for p,q in zip(parsed,ledger['profiles']):
        page=p['source_page'];assert page==q['source_page']
        assert q['source_raw_sha256']==meta['raw_sha256']
        label=LABEL_MANUAL.get(page,p['literal_label_OCR'])
        assert label==q['native_label_literal']
        assert re.match(r'\((\d\d)\)',label)[1]==q['printed_native_id']
        label_rows.append({'page':page,'own_raw_OCR':p['literal_label_OCR'],
                           'accepted_original_label':label,'separate_visual_reading':page in LABEL_MANUAL})
        own_values[page]={}
        assert len(p['fields'])==21 and set(p['fields'])==set(q['fields'])
        for field,item in p['fields'].items():
            manual=(page,field) in MANUAL
            value=MANUAL[page,field] if manual else item['value']
            assert value is not None and value==q['fields'][field]['value'],(page,field,value)
            direct+=not manual
            own_values[page][field]=value
            comparisons.append({'page':page,'field':field,**item,'accepted_value':value,
                                'direct_original_visual_reading':manual})
        assert q['unprinted_fields']=={'under':None,'over':None,'method_breakdown':None}
        for office,names in [('president',PRES),('senate',['Ty Pinkins','Roger F. Wicker'])]:
            values=own_values[page]
            assert sum(values[n] for n in names)+values[office+'_generic_write_in']==values[office+'_total_votes_cast']
    assert direct==483 and len(comparisons)==525
    assert own_values[49]['Peter Sonski']==1 and own_values[49]['ballots_blank']==1
    sums={k:sum(v[k] for v in own_values.values()) for k in ledger['field_sums']}
    assert sums==ledger['field_sums']
    assert {k:sums[k] for k in SUMMARY}==SUMMARY and len(SUMMARY)==19
    assert sums['ballots_blank']==1
    # Complete42-page inventory independently reads the printed source profile
    # code in each actual header. It does not infer a separate unit per page.
    inventory=json.loads((DEST/'independent-42page-inventory.json').read_bytes())
    assert len(inventory['pages'])==42
    groups=[]
    for page in inventory['pages']:
        hits=[re.match(r'^[| ]*\(?([0-2]\d)\)',l) for l in page['raw_header_OCR'].splitlines()]
        code=next(m[1] for m in hits if m)
        assert pin(ROOT/page['whole_original_render'])['sha256']==page['render_sha256']
        if not groups or code!=groups[-1]['printed_profile_code']:
            groups.append({'printed_profile_code':code,'source_pages':[]})
        groups[-1]['source_pages'].append(page['source_page'])
    assert [g['printed_profile_code'] for g in groups]==[f'{i:02}' for i in range(1,26)]
    assert [g['source_pages'][0] for g in groups]==[p['source_page'] for p in parsed]
    csv_raw,csv_pin=snapshot(DATA/'turnout/native-profile-fields.csv')
    rows=[r for r in csv.DictReader(io.StringIO(csv_raw.decode(),newline='')) if r['source_id']==ledger['source_id']]
    assert len(rows)==525
    seen=set()
    for r in rows:
        key=(int(r['source_page']),r['source_field']);assert key not in seen;seen.add(key)
        assert float(r['value'])==own_values[key[0]][key[1]]
        assert r['source_raw_sha256']==sha(raw) and r['source_method_literal']=='TOTAL'
        profile=next(p for p in ledger['profiles'] if p['source_page']==key[0])
        assert r['label_literal']==profile['native_label_literal'] and r['printed_native_id']==profile['printed_native_id']
    controls_raw,controls_pin=snapshot(DATA/'turnout/native-profile-controls.json')
    control=next(c for c in json.loads(controls_raw)['checks'] if c['source_id']==ledger['source_id'])
    for c in control['source_field_comparisons']:
        assert c['profile_sum']==sums[c['field']]
        if c['field']=='ballots_blank':
            assert c['county_panel_availability']=='not_printed' and c['source_county_panel_value'] is None
        else:assert c['source_county_panel_value']==SUMMARY[c['field']]
    evidence=[pin(p) for p in sorted(DEST.glob('independent-required-panels-*.png'))]
    evidence += [pin(DEST/f'independent-summary-{p}.png') for p in [12,13]]
    result={
      'status':'pass_25_original_Pike_profiles_525_fields_with_explicit_OCR_repairs_and_source_scope',
      'source':meta,'frozen_ledger':pin(DEST/'turnout-ledger-snapshot.json.gz'),
      'frozen_aggregate_CSV':csv_pin,'frozen_aggregate_controls':controls_pin,
      'independent_original_OCR':pin(DEST/'independent-original-ocr.json.gz'),
      'independent_complete_page_inventory':pin(DEST/'independent-42page-inventory.json'),
      'original_profile_count':25,'profile_section_pages':42,'profile_page_groups':groups,
      'fields_compared':525,'strict_independent_OCR_values_agree':483,
      'original_visual_numeric_readings':42,'OCR_numeric_disagreement_resolved_from_original':
          {'page':28,'field':'Randall Terry','raw_OCR_value':4,'original_value':1},
      'printed_label_checks':label_rows,'field_comparisons':comparisons,
      'original_profile_count_sums':sums,'summary_reported_count_fields_agree':19,
      'original_summary_control_readings':SUMMARY,'blank_profile_sum':1,
      'county_statistics_blank_field':None,'county_statistics_blank_availability':'not_printed',
      'arithmetic_residual_only':{'president':78,'senate':177},
      'Sonski_original_PDF49':1,'source_summary_clock':'11/15/2024 3:05 PM',
      'profile_clock_context':'11/15/2024 3:07 PM','source_timezone':None,
      'visual_evidence':evidence,
      'scope':'Complete original Pike ES&S source view, nonadditive to preferred SEMS and updated Pike. All525 required numeric fields are independently extracted from exact original scans:483 agree by strict fresh OCR and42 are separately read on complete original profile blocks. The coordinator has not freshly visually read every agreeing glyph. Profile labels use23 exact OCR agreements and2 original visual readings. All42 section pages are independently inventoried, yielding25 variable-length profiles. Nineteen additive count sums match fresh original summary/statistics readings; one profile blank is not upgraded to an unprinted county blank control. Total Votes Cast is distinct from Contest Totals; generic marks and unprinted under/over remain unadjudicated. No cross-source, historical/current, polling-geography or reporting-ID join is approved. This bounded review does not close statewide presidential/historical-native/method gates or authorize dispatch.'}
    (DATA/'coordinator-pike-profile-review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','original_profile_count','profile_section_pages',
          'fields_compared','strict_independent_OCR_values_agree','original_visual_numeric_readings',
          'summary_reported_count_fields_agree','arithmetic_residual_only']}))

if __name__=='__main__':main()
