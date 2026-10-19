"""Offline bounded original native 2018 stage/physical-column validation."""
import csv,gzip,json,re
from collections import Counter
from sources import OUT,BASE,original,sha,save
from record_2018_native_original import NAMES
from record_2018_greene_header_case import same_or_original_case_correction,readpin,SOURCES
from record_2018_tunica_header import same_or_documented_header_correction,SOURCES as TUNICA_SOURCES

def frozen_body(pin):
    stored=(BASE/pin['stored_path']).read_bytes();assert len(stored)==pin['stored_bytes']<40000000 and sha(stored)==pin['stored_sha256'];body=gzip.decompress(stored);assert len(body)==pin['original_bytes'] and sha(body)==pin['original_sha256'];return body

def source_exception(source,sums,totals):
    controls=source['controls'];pin=controls.get('unallocated_source_disagreement')
    assert dict(sums)==controls['native_candidate_sums'] and totals==controls['printed_TOTAL']
    if not pin:
        assert dict(sums)==totals and controls['all_vectors_close'];return None
    path=BASE/pin['path'];assert path.stat().st_size==pin['bytes'] and sha(path.read_bytes())==pin['sha256'];exception=json.loads(path.read_text())
    delta={candidate:sums[candidate]-total for candidate,total in totals.items()}
    assert source['source_id']==exception['source_id']=='sos-2018-county-leflore' and source['raw_sha256']==exception['raw_sha256']=='47d8b6e8606b617d690430c0bf927f3b9aaf0542e25f046ee83d27aa400d6b87'
    assert exception['native_candidate_sums']==dict(sums) and exception['printed_TOTAL']==totals and exception['native_minus_printed_TOTAL']==controls['native_minus_printed_TOTAL']==delta=={'Tobey Bernard Bartee':0,'Mike Espy':-10,'Cindy Hyde-Smith':0,'Chris McDaniel':0}
    assert not controls['all_vectors_close'] and not exception['all_vectors_close']
    initial=exception['initial_reading'];p=BASE/initial['path'];assert p.stat().st_size==initial['bytes'] and sha(p.read_bytes())==initial['sha256']
    for evidence in exception['complete_original_row_evidence']:
        crop=BASE/evidence['crop_path'];assert crop.stat().st_size==evidence['bytes'] and sha(crop.read_bytes())==evidence['sha256'];assert sha((BASE/evidence['full_original_render_path']).read_bytes())==evidence['render_sha256']
    return dict(source_id=source['source_id'],raw_sha256=source['raw_sha256'],native_candidate_sums=dict(sums),printed_TOTAL=totals,native_minus_printed_TOTAL=delta,evidence=pin,unallocated=True)

def main():
    q=json.loads((OUT/'native-2018-original-readings.json').read_text());flat=list(csv.DictReader((OUT/'native-2018-original-candidate-votes.csv').open()));rows={(r['source_id'],int(r['source_page']),int(r['source_column']),r['candidate']):r for r in flat};assert len(rows)==len(flat)
    hp=q['literal_header_correction_history'];historypath=BASE/hp['path'];assert historypath.stat().st_size==hp['bytes'] and sha(historypath.read_bytes())==hp['sha256'];headerhistory=json.loads(historypath.read_text());assert headerhistory['status']=='confirmed_original_literal_header_case_correction' and headerhistory['changed_source_header_objects']==2 and len(headerhistory['changed_candidate_header_fields'])==6
    priorwitness=headerhistory['prior_witness'];assert sha((BASE/priorwitness['path']).read_bytes())==priorwitness['sha256'];priorfields=None;priorobjects=None
    for pin in headerhistory['prior_pins']:
        body=readpin(pin)
        if pin['original_path'].endswith('/native-2018-original-readings.json'):priorobjects={s['source_id']:s for s in json.loads(body)['sources']}
        if pin['original_path'].endswith('/native-2018-original-candidate-votes.csv'):priorfields={(r['source_id'],int(r['source_page']),int(r['source_column']),r['candidate']):r for r in csv.DictReader(__import__('io').StringIO(body.decode()))}
    currentobjects={s['source_id']:s for s in q['sources']};assert all(same_or_documented_header_correction(s,currentobjects[sid]) for sid,s in priorobjects.items());assert set(sid for sid,s in priorobjects.items() if s!=currentobjects[sid])==set(SOURCES+TUNICA_SOURCES)
    for change in headerhistory['changed_candidate_header_fields']:
        key=(change['source_id'],change['PDFpage'],change['physical_column'],change['candidate']);before=priorfields[key];after=rows[key];assert before['literal_native_label']=='McLain' and after['literal_native_label']=='Mclain';expected=dict(before,literal_native_label='Mclain');assert expected==after and int(after['votes'])==change['votes']
    for entry in headerhistory['original_readings']:
        assert sha(original(entry['source_id']))==entry['raw_sha256'] and sha((BASE/entry['full_original_render_path']).read_bytes())==entry['render_sha256'];pin=entry['crop'];p=BASE/pin['path'];assert p.stat().st_size==pin['bytes'] and sha(p.read_bytes())==pin['sha256']
    counts=Counter();seen=set();exceptions=[]
    for source in q['sources']:
        sid=source['source_id'];assert sid not in seen;seen.add(sid);assert sha(original(sid))==source['raw_sha256'];sums=Counter();totals={}
        for page in source['pages']:
            pg=page['page'];path=BASE/page['full_original_render_path'];assert sha(path.read_bytes())==page['render_sha256'];receipt=json.loads(path.with_name(f'p{pg:04d}-render.json').read_text());assert receipt['raw_sha256']==source['raw_sha256'] and receipt['render_sha256']==page['render_sha256'];w,h=page['render_size'];cols=page['columns'];assert [c['source_column'] for c in cols]==list(range(1,len(cols)+1));assert [f['candidate'] for f in page['fields']]==NAMES[source['stage']]
            for col in cols:
                role=col['role'];assert role in ['native','TOTAL','unused','administrative']
                if role=='native':counts['native_constituents_across_separate_stages']+=1;assert col['label_literal']
                elif role=='TOTAL':counts['TOTAL_columns']+=1;assert col['label_literal']=='TOTAL'
                elif role=='unused':counts['unused_columns']+=1;assert col['label_literal']=='' and col['literal_printed_id'] is None
                else:counts['administrative_columns']+=1;assert col['label_literal']

            for field in page['fields']:
                assert field['party_literal'] is None and len(field['values'])==len(cols);l,t,r,b=field['row_bounds'];assert 0<=l<r<=w and 0<=t<b<=h
                for col,v in zip(cols,field['values']):
                    l1,t1,r1,b1=col['header_bounds'];assert 0<=l1<r1<=w and 0<=t1<b1<=h;row=rows.pop((sid,pg,col['source_column'],field['candidate']));assert row['source_raw_sha256']==source['raw_sha256'] and row['literal_native_label']==col['label_literal'] and row['role']==col['role'] and row['stage']==source['stage'];assert row['party_literal']=='' and row['literal_printed_id']==(col['literal_printed_id'] or '');assert row['county_fips']==source.get('county_fips','28055') and row['source_key']==f'{sid}:p{pg}:c{col["source_column"]}';assert json.loads(row['header_bounds_pixels'])==col['header_bounds'] and json.loads(row['candidate_reading_window_pixels'])==[l1,t,r1,b];assert row['render_sha256']==page['render_sha256'] and row['full_original_render_path']==page['full_original_render_path']
                    if col['role']=='unused':assert v is None and row['votes']=='' and row.get('raw_source_mark','')=='';counts['unused_null_positions']+=1
                    elif str(col['source_column']) in field.get('source_marks',{}):
                        assert col['role']=='native' and v is None and row['votes']=='' and row['raw_source_mark']==field['source_marks'][str(col['source_column'])]=='X';counts['marked_native_positions']+=1
                    else:
                        assert type(v) is int and v>=0 and int(row['votes'])==v and row.get('raw_source_mark','')=='';counts['numeric_positions']+=1
                        if col['role'] in ['native','administrative']:sums[field['candidate']]+=v
                        else:totals[field['candidate']]=v
            if page.get('header_rule_probe'):
                pin=page['header_rule_probe'];probe=BASE/pin['path'];assert probe.stat().st_size==pin['bytes'] and sha(probe.read_bytes())==pin['sha256'];a=json.loads(probe.read_text());assert a['source_id']==sid and a['PDFpage']==pg and a['raw_sha256']==source['raw_sha256'] and a['render_sha256']==page['render_sha256'];assert a['accepted_physical_rule_x']==[cols[0]['header_bounds'][0]]+[c['header_bounds'][2] for c in cols]
            if page.get('manual_reading_correction_history'):
                history=json.loads((BASE/page['manual_reading_correction_history']).read_text());assert history['source_id']==sid and history['source_raw_sha256']==source['raw_sha256'] and history['PDFpage']==pg and history['render_sha256']==page['render_sha256'];assert (history['initial_manual_value'],history['accepted_original_glyph']) in [(98,96),(226,228),(158,168),(152,182),(590,690)]
                field=next(f for f in page['fields'] if f['candidate']==history['candidate']);assert field['values'][history['physical_column']-1]==history['accepted_original_glyph']
                for pin in history['evidence']:
                    p=BASE/pin['path'];assert p.stat().st_size==pin['bytes'] and sha(p.read_bytes())==pin['sha256']
            if page.get('manual_header_evidence'):
                evidence=json.loads((BASE/page['manual_header_evidence']).read_text());entry=next(r for r in evidence['readings'] if r['source_id']==sid and r['PDFpage']==pg);assert entry['raw_sha256']==source['raw_sha256'] and entry['render_sha256']==page['render_sha256'] and cols[entry['physical_column']-1]['label_literal']==entry['literal_header']
                for pin in entry['evidence']:
                    p=BASE/pin['path'];assert p.stat().st_size==pin['bytes'] and sha(p.read_bytes())==pin['sha256']
        exception=source_exception(source,sums,totals)
        if exception:exceptions.append(exception)
        counts['source_views']+=1
    assert not rows and dict(counts)==q['counts'] and len(q['all164_source_status'])==164
    for status in q['all164_source_status']:
        if status['source_id'] in seen:
            source=next(s for s in q['sources'] if s['source_id']==status['source_id']);assert status['reviewed_native_count']==sum(c['role']=='native' for p in source['pages'] for c in p['columns'])
        else:assert status['reviewed_native_count'] is None
    pinpath=OUT/'source/2018-physical-column-corrections-v1/prior-ledger-pin.json';pin=json.loads(pinpath.read_text());stored=(BASE/pin['stored_path']).read_bytes();assert sha(stored)==pin['stored']['sha256'] and len(stored)==pin['stored']['bytes'];raw=gzip.decompress(stored);assert sha(raw)==pin['original']['sha256'] and len(raw)==pin['original']['bytes'];prior={r['source_id']:r for r in json.loads(raw)['readings']};current={r['source_id']:r for r in json.loads((OUT/'county-2018-readings.json').read_text())['readings']};sid='sos-2018-county-issaquena';old=prior[sid];new=current[sid];assert old['source_positions']['source_column']==4 and new['source_positions']['source_column']==6 and old['candidate_values']==new['candidate_values'];assert new['physical_column_correction_history']['prior_source_positions']==old['source_positions'];assert all(current[k]==v for k,v in prior.items() if k!=sid)
    assert all(s['controls']['printed_TOTAL']==prior[s['source_id']]['candidate_values'] for s in q['sources'])
    rejectionpath=OUT/'source/native-2018-witness-rejections.json';rejections=json.loads(rejectionpath.read_text())['rejected_witnesses'];rejected={r['snapshot']['path']:r for r in rejections};assert len(rejected)==len(rejections)==1;rejected_verified=[]
    witnesses=[];earlier={}
    for sp in sorted((p for p in (OUT/'source').glob('native-2018-*views-v*/snapshot.json') if re.fullmatch(r'native-2018-[0-9]+views-v[0-9]+',p.parent.name)),key=lambda p:(int(p.parent.name.split('-')[2].split('views')[0]),int(p.parent.name.rsplit('-v',1)[1]))):
        snap=json.loads(sp.read_text());frozen=None;relative=str(sp.relative_to(BASE))
        for pin in snap['pins']:
            body=frozen_body(pin)
            if pin['original_path'].endswith('/native-2018-original-readings.json'):frozen=json.loads(body)
        assert snap['counts']==frozen['counts']
        declared=int(re.fullmatch(r'native-2018-([0-9]+)views-v[0-9]+',sp.parent.name).group(1));assert snap['version']==sp.parent.name.removeprefix('native-2018-')
        if relative in rejected:
            r=rejected[relative];assert r['snapshot']['bytes']==sp.stat().st_size and r['snapshot']['sha256']==sha(sp.read_bytes());assert r['declared_version']==snap['version']=='98views-v1' and r['actual_source_views']==snap['counts']['source_views']==94 and declared==98;assert len(frozen['sources'])==94 and r['reason'];rejected_verified.append(dict(**r,all_pins_verified=True,excluded_from_accepted_witness_chain=True));continue
        assert declared==snap['counts']['source_views']==len(frozen['sources'])
        ss={r['source_id']:r for r in frozen['sources']}
        assert all(same_or_documented_header_correction(v,ss[k]) for k,v in earlier.items());case_changes=[k for k,v in earlier.items() if ss[k]!=v];earlier=ss;witnesses.append(dict(path=str(sp.relative_to(BASE)),bytes=sp.stat().st_size,sha256=sha(sp.read_bytes()),counts=snap['counts'],all_pins_verified=True,prior_source_objects_unchanged=not case_changes,explicit_original_header_case_corrections=case_changes))
    current_sources={r['source_id']:r for r in q['sources']};assert all(same_or_documented_header_correction(v,current_sources[k]) for k,v in earlier.items())
    th=q['literal_header_spelling_correction_history'];tp=BASE/th['path'];assert tp.stat().st_size==th['bytes'] and sha(tp.read_bytes())==th['sha256'];tunica=json.loads(tp.read_text());assert tunica['changed_source_header_objects']==2 and len(tunica['changed_candidate_header_fields'])==6;old_sources={};old_rows={}
    for pin in tunica['prior_pins']:
        body=readpin(pin)
        if pin['original_path'].endswith('/native-2018-original-readings.json'):old_sources={s['source_id']:s for s in json.loads(body)['sources']}
        if pin['original_path'].endswith('/native-2018-original-candidate-votes.csv'):old_rows={(r['source_id'],int(r['source_page']),int(r['source_column']),r['candidate']):r for r in csv.DictReader(__import__('io').StringIO(body.decode()))}
    assert {sid for sid,s in old_sources.items() if s!=current_sources[sid]}==set(TUNICA_SOURCES) and all(same_or_documented_header_correction(s,current_sources[sid]) for sid,s in old_sources.items())
    current_rows={(r['source_id'],int(r['source_page']),int(r['source_column']),r['candidate']):r for r in flat};changed=[]
    for key,before in old_rows.items():
        after=current_rows[key]
        if before!=after:assert key[0] in TUNICA_SOURCES and key[1:3]==(2,2) and before['literal_native_label']=='Moon Landing' and after==dict(before,literal_native_label='Mhoon Landing');changed.append(key)
    assert len(changed)==6
    for entry in tunica['original_readings']:
        assert sha(original(entry['source_id']))==entry['raw_sha256'] and sha((BASE/entry['full_original_render_path']).read_bytes())==entry['render_sha256'];pin=entry['crop'];p=BASE/pin['path'];assert p.stat().st_size==pin['bytes'] and sha(p.read_bytes())==pin['sha256']
    header_evidence=json.loads((OUT/'source/2018-native-header-evidence.json').read_text())
    for entry in header_evidence['readings']:
        s=current_sources[entry['source_id']];p=next(p for p in s['pages'] if p['page']==entry['PDFpage']);assert entry['raw_sha256']==s['raw_sha256'] and entry['render_sha256']==p['render_sha256'] and p['columns'][entry['physical_column']-1]['label_literal']==entry['literal_header']
        for pin in entry['evidence']:
            path=BASE/pin['path'];assert path.stat().st_size==pin['bytes'] and sha(path.read_bytes())==pin['sha256']
    assert len(rejected_verified)==len(rejected)
    save(OUT/'native-2018-validation.json',dict(status='pass_bounded_original_stage_and_physical_column_scopes',counts=dict(counts),flat_positions=len(flat),immutable_witnesses=witnesses,rejected_witnesses=rejected_verified,literal_header_correction_history=hp,literal_header_spelling_correction_history=th,source_native_TOTAL_disagreements=exceptions,all_reviewed_candidate_vectors_close_earlier_county_controls=not exceptions,prior_ledger_pin=dict(path=str(pinpath.relative_to(BASE)),bytes=pinpath.stat().st_size,sha256=sha(pinpath.read_bytes())),physical_column_correction=dict(source_id=sid,prior_merged_machine_ordinal=4,accepted_physical_TOTAL_column=6,candidate_values_unchanged=True,other163_county_readings_unchanged=True),complete2018_named_candidate_native_source_review=counts["source_views"]==164,complete2018_native=False,current2026_geography_approved=False,exact_numeric_polygons_approved=False));print('PASS bounded original2018native',dict(counts),'unallocated source disagreements',len(exceptions))
if __name__=='__main__':main()
