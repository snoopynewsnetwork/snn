"""Independent original Pike vendor-profile glyph transcription, source-vintage scoped."""
import json
from collections import Counter
from sources import OUT,BASE,save,sha,original
from build_counties import writecsv
from extract_pike_vendor_fields import FIELDS
LABELS=['New Hope Baptist Church','S MCCOMB BAPTIST CHURCH','Summit United Methodist Church','Mlk Center','North McComb Baptist Church','Presley Event Center','St Mary Free Will Bapt. Ch.','Fernwood Baptist Church','Magnolia Comm Ctr.','Braswell Education Complex','St. James Miss. Bapt. Church','Navilla Baptist Church Fellowship Hall','Holmesville Comm.','Calvary Baptist Church','Friendship Bapt. Church','Summit City Hall','SMCC Work Force Training Ctr','Johnston Chapel Meth. Church','Pisgah Methodist Church','Pike Co. Nat. Bank','Old Progress Volunteer Fire Station','Church of Christ','West McComb Bapt. Church','Our Lady of Hope','Osyka City Hall']
# Original-only row cards; None denotes a still-unreviewed ambiguous field,
# NEVER zero or a value fitted to a contest/county residual.
VALUES={
'01':['1,053',456,0,'43.30%',420,0,0,1,28,1,0,2,0,0,452,456,394,45,1,440,456],
'02':[551,203,0,'36.84%',165,0,1,0,34,0,0,1,0,0,201,203,160,40,0,200,203],
'03':[580,307,0,'52.93%',216,0,1,0,85,0,0,0,0,1,303,307,214,87,2,303,307],
'04':[982,433,0,'44.09%',402,0,2,0,21,0,1,2,0,2,430,433,383,28,1,412,433],
'05':[876,463,0,'52.85%',219,2,0,0,227,2,1,5,1,6,463,463,216,236,1,453,463],
'06':[493,194,0,'39.35%',178,0,0,0,14,0,0,0,0,1,193,194,173,17,1,191,194],
'07':[942,458,0,'48.62%',358,0,0,0,94,1,0,0,0,1,454,458,338,103,0,441,458],
'08':['1,134',533,0,'47.00%',360,0,0,1,166,0,0,4,1,0,532,533,345,184,1,530,533],
'09':['1,175',521,0,'44.34%',356,1,0,0,151,0,0,2,1,1,512,521,348,164,3,515,521],
'10':['1,381',633,0,'45.84%',346,1,1,1,264,0,1,2,0,2,618,633,347,270,4,621,633],
'11':[633,278,0,'43.92%',165,0,0,0,108,0,0,1,0,0,274,278,162,111,0,273,278],
'12':['1,465',760,0,'51.88%',307,1,1,1,439,1,0,6,1,0,757,760,308,445,2,755,760],
'13':[975,533,0,'54.67%',212,1,1,0,314,0,0,2,2,0,532,533,203,328,1,532,533],
'14':[958,606,0,'63.26%',158,1,0,2,440,1,0,0,0,2,604,606,154,446,1,601,606],
'15':[896,541,0,'60.38%',93,1,2,1,435,1,0,5,0,1,539,541,91,447,1,539,541],
'16':[531,304,0,'57.25%',178,1,0,0,119,0,0,2,0,0,300,304,167,124,1,292,304],
'17':['1,465',920,0,'62.80%',258,1,0,0,654,0,0,4,0,2,919,920,242,671,2,915,920],
'18':['1,336',884,0,'66.17%',103,3,2,1,773,1,0,0,0,1,884,884,112,766,0,878,884],
'19':['1,163',705,0,'60.62%',150,1,1,0,549,0,0,1,0,1,703,705,138,561,0,699,705],
'20':[810,407,0,'50.25%',241,0,1,0,160,1,0,2,0,1,406,407,227,171,3,401,407],
'21':['1,435',676,0,'47.11%',348,1,1,1,316,0,2,3,0,2,674,676,332,334,2,668,676],
'22':['1,164',621,1,'53.35%',384,0,1,1,222,0,1,3,1,3,616,621,376,236,2,614,621],
'23':[915,467,0,'51.04%',174,0,0,1,288,0,0,1,0,1,465,467,171,292,1,464,467],
'24':['1,277',629,0,'49.26%',216,2,0,0,402,0,0,4,1,3,628,629,218,405,0,623,629],
'25':[502,292,0,'58.17%',84,0,0,0,201,0,1,0,1,0,287,292,79,208,0,287,292]}
def main():
    pending=[];readings=[]
    for code,vs in VALUES.items():
        assert len(vs)==21
        for field,value in zip(FIELDS,vs):
            if value is None:pending.append(dict(profile_code=code,field=field,reason='Original-only initial card had missing/ambiguous source-label targeting, full original reread needed'))
            else:readings.append(dict(profile_code=code,field=field,accepted_printed_literal=str(value),value=float(str(value)[:-1]) if field=='printed_turnout' else int(str(value).replace(',','')),basis='Independent original numeric glyph read from row card with printed field label; printed thousands punctuation typed from original, never OCR punctuation normalization'))
    save(OUT/'pike-vendor-manual-reading-progress.json',dict(qualification='Own-original visual readings; pending values remain unknown, never zeros. Complete original42pages retained. No county residual used.',readings=readings,pending_field_rereads=pending,unreviewed_profiles=[f'{i:02d}' for i in range(1,26) if f'{i:02d}' not in VALUES]))
    if pending or len(VALUES)!=25:return
    path=OUT/'pike-vendor-field-extract.json';raw=json.loads(path.read_text());assert sha(original(raw['source_id']))==raw['raw_sha256'];assert not raw['unassigned_pages'] and not raw['missing_or_duplicate_field_labels'];profiles=[];flat=[];sums=Counter();differences=[]
    for i,(code,p) in enumerate(raw['profiles'].items()):
        assert code==f'{i+1:02d}';label=f'({code}) {LABELS[i]}';index={f['field']:f for f in p['fields']};assert len(index)==21
        evidence=OUT/'qa'/f'pike-vendor-original-field-cards-{i//4+1}.png';fields=[]
        for field,v in zip(FIELDS,VALUES[code]):
            f=index[field];assert sha((BASE/f['full_original_render_path']).read_bytes())==f['render_sha256'];lit=str(v);value=float(lit[:-1]) if field=='printed_turnout' else int(lit.replace(',',''));rec=f|dict(printed_literal=lit,value=value,basis='Independent original printed glyph review, with explicit zero/thousands punctuation. Own label/office/TOTAL-column positions precede peer comparison; no value inferred from county or contest sums.',evidence_path=str(evidence.relative_to(BASE)),evidence_sha256=sha(evidence.read_bytes()));fields.append(rec)
            if field!='printed_turnout':sums[field]+=value
            if f['source_value_literal']!=lit:differences.append(dict(profile_code=code,source_page=f['source_page'],field=field,raw_OCR_literal=f['source_value_literal'],accepted_printed_literal=lit,accepted_value=value,source_value_candidates=f['source_value_candidates']))
            flat.append(dict(source_id=raw['source_id'],raw_sha256=raw['raw_sha256'],source_page=f['source_page'],vendor_profile_code=code,native_label_literal=label,native_view='Pike original ES&S Precinct Summary profile; separate from original/updated SEMS and current geography',field=field,value=value,printed_literal=lit,source_label_literal=f['source_label_literal'],raw_OCR_value_literal=f['source_value_literal'],original_reading_box_pixels=json.dumps(f['complete_original_row_reading_box']),original_value_box_pixels=json.dumps(f['source_value_box']),render_size=json.dumps(f['render_size']),full_original_render_path=f['full_original_render_path'],render_sha256=f['render_sha256'],evidence_path=rec['evidence_path'],evidence_sha256=rec['evidence_sha256']))
        d={f['field']:f['value'] for f in fields};assert sum(d[k] for k in FIELDS[4:14])==d['pres_total_votes_cast'];assert sum(d[k] for k in ['sen_Pinkins','sen_Wicker','sen_generic_write_in'])==d['sen_total_votes_cast'];assert d['ballots_cast']==d['pres_contest_total']==d['sen_contest_total']
        profiles.append(dict(printed_profile_code=code,native_label_literal=label,source_pages=p['pages'],raw_header_observations=p['headers'],fields=fields,registration_scope='Printed Registered Voters - Total; active/inactive/status date unspecified',status_literal='Certified Results',clock_literal='Precinct Summary - 11/15/2024 3:07 PM',timezone=None,unprinted_undervotes=None,unprinted_overvotes=None,arithmetic_unallocated_contest_residuals=dict(president=d['pres_contest_total']-d['pres_total_votes_cast'],senate=d['sen_contest_total']-d['sen_total_votes_cast'])))
    summary=next(r for r in json.loads((OUT/'canvass-readings.json').read_text())['readings'] if r['source_id']==raw['source_id']);stats=next(r for r in json.loads((OUT/'canvass-statistics-readings.json').read_text())['readings'] if r['source_id']==raw['source_id']);expected=dict(zip(FIELDS[4:13],[v[0] for v in summary['president']['candidates']]));expected.update(registration=stats['registered_voters_total'],ballots_cast=stats['ballots_cast_total'][0])
    for office,prefix in [('president','pres'),('senate','sen')]:
        s=summary[office];expected.update({prefix+'_generic_write_in':s['generic_write_in_marks'][0],prefix+'_total_votes_cast':s['total_votes_cast'][0],prefix+'_contest_total':s['contest_opportunities'][0]})
    expected.update(sen_Pinkins=summary['senate']['candidates'][0][0],sen_Wicker=summary['senate']['candidates'][1][0]);assert len(expected)==19;assert {k:sums[k] for k in expected}==expected,(sums,expected);assert sums['blank_ballots']==1 and stats['ballots_cast_blank'] is None
    header_evidence=OUT/'qa/pike-vendor-original-profile-headers.png';save(OUT/'pike-native-profile-readings.json',dict(source_id=raw['source_id'],raw_sha256=raw['raw_sha256'],county_fips='28113',qualification='All25 original vendor profiles across all42 actual PDF15–56 pages: 525 required numeric fields and25 printed headers independently read from original rasters before peer comparison. Twenty additive COUNT vectors; 25 turnout percentages nonadditive. Nineteen count vectors close original county panels; profile blank sum1 has no printed county blank control. Generic marks are separate from certified valid/named write-ins. No vendor/SEMS/current unit equivalence, updated-vintage splicing, release chronology or residual vote allocation.',original_extract_path=str(path.relative_to(BASE)),original_extract_sha256=sha(path.read_bytes()),header_original_evidence_path=str(header_evidence.relative_to(BASE)),header_original_evidence_sha256=sha(header_evidence.read_bytes()),profiles=profiles,raw_OCR_original_literal_differences=differences,source_label_repair_history=[dict(profile_code='06',source_page=25,field='sen_generic_write_in',raw_OCR_label='Write-in Totais',original_printed_label='Write-In Totals',accepted_value=1,basis='Full original page25 independently reread, explicit printed1; initial missing-target aid retained at source/pike-vendor-initial-label-extract.json.gz and qa/pike-vendor-initial-profile06-label-gap-card.png')],controls=dict(profiles=25,actual_profile_pages=42,required_numeric_fields=525,additive_count_vectors=20,independent_county_vectors=19,printed_turnout_fields_nonadditive=25,field_sums=dict(sums),independent_original_county_controls=expected,all19_available_count_vectors_match_original_county=True,profile_blank_sum=1,county_blank_control=None,contest_unallocated_arithmetic_residuals=dict(president=sums['pres_contest_total']-sums['pres_total_votes_cast'],senate=sums['sen_contest_total']-sums['sen_total_votes_cast']),profile_clock='11/15/2024 3:07 PM',county_clock=summary['clock_literal'],no_release_chronology_inferred=True,no_SEMS_or_current_crosswalk_claim=True)))
    writecsv(OUT/'pike-native-profile-fields.csv',flat);print('25 profiles,42 original pages,525 original glyph fields;19 county count controls agree; blank1 county-unprinted; raw OCR literal differences',len(differences))
if __name__=='__main__':main()
