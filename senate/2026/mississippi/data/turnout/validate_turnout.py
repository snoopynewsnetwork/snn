"""Offline source/hash/geography/candidate/order/denominator/peer validation.

Native gates cannot pass merely because county totals agree. Run after builders.
"""
import csv,gzip,hashlib,io,json,re
from decimal import Decimal
from pathlib import Path
from acquire_sources import BASE,OUT,receipts,sha,savejson
def readcsv(p):return list(csv.DictReader(p.open()))
def main():
    checks={};errors=[]
    def check(name,ok,detail=None):
        checks[name]=dict(pass_=bool(ok),detail=detail)
        if not ok:errors.append(name)
    source_errors=[];verified=[]
    for r in receipts:
        p=BASE/r['path'];stored=p.read_bytes();raw=gzip.decompress(stored) if p.suffix=='.gz' else stored
        if sha(stored)!=r['stored_sha256'] or sha(raw)!=r['raw_sha256'] or len(stored)>=40_000_000:source_errors.append(r['id'])
        verified.append(dict(source_id=r['id'],path=r['path'],raw_sha256=sha(raw),stored_sha256=sha(stored),raw_bytes=len(raw),stored_bytes=len(stored)))
    check('all_original_and_stored_source_hashes',not source_errors,dict(source_count=len(verified),errors=source_errors))
    rows=readcsv(BASE/'data/county-turnout.csv');c=readcsv(OUT/'candidate-votes.csv');contract=json.loads((OUT/'priority-set.json').read_text())
    check('82_unique_county_fips',len(rows)==82 and len({r['fips'] for r in rows})==82 and all(re.fullmatch('28[0-9]{3}',r['fips']) for r in rows))
    check('complete_county_rank_sequence',[int(r['rank']) for r in rows]==list(range(1,83)))
    expected=sorted(rows,key=lambda r:(-int(r['2024_senate_candidate_votes']),r['fips']));check('descending_county_order',rows==expected)
    totals={}
    for r in c:
        key=(r['election_date'],r['office_literal'].strip(),r['candidate_literal'],r['party_literal']);totals[key]=totals.get(key,0)+int(r['votes'])
    controls={('2024-11-05','United States-Senate','Ty Pinkins','Democrat'):451981,('2024-11-05','United States-Senate','Roger F. Wicker','Republican'):763420,
      ('2020-11-03','United States-Senate','Mike Espy','Democrat'):578691,('2020-11-03','United States-Senate','Cindy Hyde-Smith','Republican'):709511,('2020-11-03','United States-Senate','Jimmy L. Edwards','Libertarian'):23152}
    balances=[dict(key=list(k),expected=v,actual=totals.get(k),difference=totals.get(k,0)-v) for k,v in controls.items()]
    check('2024_and_amended2020_Senate_primary_candidate_controls',all(x['difference']==0 for x in balances),balances)
    prescontrols={'Kamala D. Harris':466668,'Chase Oliver':2536,'Jill Stein':1873,'Randall Terry':1030,'Donald J. Trump':747744,'Shiva Ayyadurai':688,'Claudia De la Cruz':1075,'Robert F. Kennedy Jr.':5387,'Peter Sonski':1007}
    pres=[]
    for name,v in prescontrols.items():
        found=[(k,n) for k,n in totals.items() if k[0]=='2024-11-05' and k[1]=='United States-President' and k[2].startswith('Presidential Electors for '+name)];pres.append(dict(candidate=name,expected=v,actual=found[0][1] if len(found)==1 else None))
    check('all9_presidential_primary_controls',all(x['actual']==x['expected'] for x in pres),pres)
    key=lambda r:(r['election_date'],r['county'],r['office_literal'],r['candidate_literal'],r['party_literal'])
    check('no_silently_deduplicated_candidate_rows',len({key(r) for r in c})==len(c),dict(rows=len(c)))
    for r in rows:
        for date,col in [('2024-11-05','2024_senate_candidate_votes'),('2020-11-03','2020_senate_candidate_votes')]:
            assert sum(int(x['votes']) for x in c if x['county']==r['county'] and x['election_date']==date and x['office_literal'].strip()=='United States-Senate')==int(r[col])
    check('county_candidate_to_county_total_balances',True)
    state=sum(int(r['2024_senate_candidate_votes']) for r in rows);cum=0;cross=None
    for i,r in enumerate(rows,1):
        before=cum;cum+=int(r['2024_senate_candidate_votes']);assert cum==int(r['cumulative_votes'])
        if cross is None and 5*cum>=4*state:cross=(i,before,cum,r['fips'])
    check('minimum_integer80_crossing',cross==(41,970209,979428,'28101') and state==1215401 and 5*cross[1]<4*state<=5*cross[2],dict(state_total=state,crossing=cross))
    check('top15_exact',sum(int(r['2024_senate_candidate_votes']) for r in rows[:15])==653846)
    county_sensitivity=contract['county_parent_sensitivity']
    check('contract_county_parent_sensitivity_complete',county_sensitivity['ordered_priority_keys']==[r['fips'] for r in rows[:41]] and [r['fips'] for r in county_sensitivity['all_unit_order']]==[r['fips'] for r in rows] and county_sensitivity['remainder']['votes']==235973)
    check('all82_weights_total_one',abs(sum(Decimal(r['2024_senate_candidate_votes'])/Decimal(state) for r in rows)-1)<Decimal('1e-25'))
    part=readcsv(OUT/'participation-controls.csv');active=readcsv(OUT/'active-registration.csv')
    check('source_scoped_eac_82_county_coverage',all(len([r for r in part if r['year']==y and r['field']=='F1a'])==82 for y in ['2022','2024']))
    check('monthly_active_3x82_coverage',len(active)==246 and all(len({r['fips'] for r in active if r['source_id']==s})==82 for s in {r['source_id'] for r in active}))
    check('survey_missing_codes_not_numeric_zero',all(r['value']=='' for r in part if r['raw_value'].startswith('-')))
    hist=readcsv(OUT/'historical-county-candidate-votes.csv');hc={}
    for r in hist:
        k=(r['election_date'],r['candidate']);hc[k]=hc.get(k,0)+int(r['votes'])
    hcontrols={('2018-11-06','Tobey Bernard Bartee'):13852,('2018-11-06','Mike Espy'):386742,('2018-11-06','Cindy Hyde-Smith'):389995,('2018-11-06','Chris McDaniel'):154878,('2018-11-27','Mike Espy'):420819,('2018-11-27','Cindy Hyde-Smith'):486769}
    check('both2018_stages_all82_all492_primary_controls',len(hist)==492 and hc==hcontrols and all(len({r['fips'] for r in hist if r['election_date']==date})==82 for date in ['2018-11-06','2018-11-27']) and len({(r['election_date'],r['fips'],r['candidate']) for r in hist})==492,dict(actual={str(k):v for k,v in hc.items()}))
    issaquena=json.loads((OUT/'2018-issaquena-two-stage-native-original-readings.json').read_text());iss_errors=[]
    assert len(issaquena['sources'])==2
    for stage in issaquena['sources']:
        raster=BASE/stage['full_original_raster']
        if not raster.exists() or sha(raster.read_bytes())!=stage['full_original_raster_sha256']:iss_errors.append((stage['source_id'],'raster'))
        if stage['source_raw_sha256']!=next(r['raw_sha256'] for r in receipts if r['id']==stage['source_id']):iss_errors.append((stage['source_id'],'source_hash'))
        if len(stage['rows'])!=11*len(stage['candidate_checks']) or len({(x['physical_source_column'],x['candidate']) for x in stage['rows']})!=len(stage['rows']):iss_errors.append((stage['source_id'],'source_positions'))
        if not all(x['passes'] for x in stage['candidate_checks'].values()):iss_errors.append((stage['source_id'],'native_sum'))
        if stage['physical_TOTAL_column']!=6 or stage['native_constituents']!=5 or stage['unused_template_columns']!=[7,8,9,10,11]:iss_errors.append((stage['source_id'],'physical_roles'))
        if any(x['party_field_literal']!='' for x in stage['rows']):iss_errors.append((stage['source_id'],'party_scope'))
    check('2018_Issaquena_both_special_stages_complete_original_native_physical_grid',issaquena['total_candidate_positions']==66 and [(x['election_date'],x['prior_county_control_machine_TOTAL_ordinal']) for x in issaquena['sources']]==[('2018-11-06',4),('2018-11-27',6)] and not iss_errors,dict(source_stages=2,native_per_stage=5,numeric_positions=36,unused_null_positions=30,Nov6_machine_total_ordinal=4,actual_both_physical_TOTAL_column=6,errors=iss_errors))
    benton=json.loads((OUT/'2018-benton-two-stage-native-original-readings.json').read_text());benton_errors=[]
    for stage in benton['sources']:
        raster=BASE/stage['full_original_raster']
        if not raster.exists() or sha(raster.read_bytes())!=stage['full_original_raster_sha256']:benton_errors.append((stage['source_id'],'raster'))
        if stage['source_raw_sha256']!=next(r['raw_sha256'] for r in receipts if r['id']==stage['source_id']):benton_errors.append((stage['source_id'],'source_hash'))
        if len(stage['rows'])!=11*len(stage['candidate_checks']) or len({(x['physical_source_column'],x['candidate']) for x in stage['rows']})!=len(stage['rows']):benton_errors.append((stage['source_id'],'source_positions'))
        if not all(x['passes'] for x in stage['candidate_checks'].values()):benton_errors.append((stage['source_id'],'native_sum'))
        if stage['physical_TOTAL_column']!=6 or stage['native_constituents']!=5 or stage['unused_template_columns']!=[7,8,9,10,11]:benton_errors.append((stage['source_id'],'physical_roles'))
        if any(x['party_field_literal']!='' for x in stage['rows']):benton_errors.append((stage['source_id'],'party_scope'))
    check('2018_Benton_both_special_stages_complete_original_native_physical_grid',benton['total_candidate_positions']==66 and {x['election_date'] for x in benton['sources']}=={'2018-11-06','2018-11-27'} and not benton_errors,dict(source_stages=2,native_per_stage=5,numeric_positions=36,unused_null_positions=30,errors=benton_errors))
    franklin2018=json.loads((OUT/'2018-franklin-two-stage-native-original-readings.json').read_text());franklin2018_errors=[]
    for stage in franklin2018['sources']:
        if stage['source_raw_sha256']!=next(r['raw_sha256'] for r in receipts if r['id']==stage['source_id']):franklin2018_errors.append((stage['source_id'],'source_hash'))
        for page in stage['pages']:
            raster=BASE/page['original_raster']
            if not raster.exists() or sha(raster.read_bytes())!=page['raster_sha256']:franklin2018_errors.append((stage['source_id'],page['source_pdf_page'],'raster'))
        if len(stage['rows'])!=22*len(stage['candidate_checks']) or len({(x['source_pdf_page'],x['physical_source_column'],x['candidate']) for x in stage['rows']})!=len(stage['rows']):franklin2018_errors.append((stage['source_id'],'source_positions'))
        if not all(x['passes'] for x in stage['candidate_checks'].values()):franklin2018_errors.append((stage['source_id'],'native_sum'))
        if stage['physical_TOTAL_page']!=3 or stage['physical_TOTAL_column']!=4 or stage['native_constituents']!=14 or stage['unused_template_columns_page3']!=[5,6,7,8,9,10,11]:franklin2018_errors.append((stage['source_id'],'physical_roles'))
        if any(x['party_field_literal']!='' for x in stage['rows']):franklin2018_errors.append((stage['source_id'],'party_scope'))
    check('2018_Franklin_both_special_stages_complete_original_native_physical_grid',franklin2018['total_candidate_positions']==132 and {x['election_date'] for x in franklin2018['sources']}=={'2018-11-06','2018-11-27'} and not franklin2018_errors,dict(source_stages=2,native_per_stage=14,numeric_positions=6*15,unused_null_positions=4*7+2*7,errors=franklin2018_errors))
    franklin_case=json.loads((OUT/'2018-franklin-header-case-correction-history.json').read_text())
    case_pin=BASE/franklin_case['prior_pin'];case_errors=[]
    if sha(case_pin.read_bytes())!=franklin_case['prior_pin_sha256']:case_errors.append('prior_pin')
    for p in json.loads(case_pin.read_text())['pins']:
        stored=(BASE/p['stored_path']).read_bytes();original=gzip.decompress(stored)
        if sha(stored)!=p['stored_sha256'] or len(stored)!=p['stored_bytes'] or sha(original)!=p['original_sha256'] or len(original)!=p['original_bytes']:case_errors.append(p['stored_path'])
    for crop_rec in franklin_case['crops']:
        if not (BASE/crop_rec['rendered_crop']).exists() or sha((BASE/crop_rec['rendered_crop']).read_bytes())!=crop_rec['rendered_crop_sha256'] or sha((BASE/crop_rec['original_raster']).read_bytes())!=crop_rec['original_raster_sha256']:case_errors.append(crop_rec['source_id'])
    if sha((BASE/franklin_case['new_readings_path']).read_bytes())!=franklin_case['new_readings_sha256'] or sha((BASE/franklin_case['new_flat_path']).read_bytes())!=franklin_case['new_flat_sha256']:case_errors.append('current_readings')
    if any(case_rec['earlier_literal']!='McCall' or case_rec['corrected_source_literal']!='Mccall' or case_rec['source_pdf_page']!=2 or case_rec['physical_column']!=9 for case_rec in franklin_case['changes']):case_errors.append('literal_position')
    check('2018_Franklin_original_literal_Mccall_prior_case_history',franklin_case['changed_position_count']==6 and len(franklin_case['crops'])==2 and not case_errors,dict(changed_literal_positions=6,earlier='McCall',printed='Mccall',vote_change=False,errors=case_errors))
    clay2018=json.loads((OUT/'2018-clay-two-stage-native-original-readings.json').read_text());clay_errors=[]
    for stage in clay2018['sources']:
        if stage['source_raw_sha256']!=next(r['raw_sha256'] for r in receipts if r['id']==stage['source_id']):clay_errors.append((stage['source_id'],'source_hash'))
        for page in stage['pages']:
            raster=BASE/page['original_raster']
            if not raster.exists() or sha(raster.read_bytes())!=page['raster_sha256']:clay_errors.append((stage['source_id'],page['source_pdf_page'],'raster'))
        if stage['physical_TOTAL_page']!=3 or stage['physical_TOTAL_column']!=4 or stage['native_constituents']!=14 or not all(z['passes'] for z in stage['candidate_checks'].values()):clay_errors.append((stage['source_id'],'physical_or_candidate'))
        if len({(z['source_pdf_page'],z['physical_source_column'],z['candidate']) for z in stage['rows']})!=len(stage['rows']) or any(z['party_field_literal'] is not None for z in stage['rows']):clay_errors.append((stage['source_id'],'unique_or_party_scope'))
    clay_peer=json.loads((OUT/'2018-clay-native-peer-reconciliation.json').read_text())
    check('2018_Clay_both_special_stages_direct_original_native_and_frozen_peer',clay2018['total_candidate_positions']==132 and clay2018['native_constituents_per_stage']==14 and {s['election_date'] for s in clay2018['sources']}=={'2018-11-06','2018-11-27'} and not clay_errors and clay_peer['source_position_count']==132 and not clay_peer['disagreements'] and clay_peer['own_sha256']==sha((OUT/'2018-clay-two-stage-native-original-readings.json').read_bytes()),dict(native_per_stage=14,source_positions=132,runoff_physical_TOTAL_column=4,old_runoff_locator_hint=3,errors=clay_errors,qualification='Original-specific Clay special/runoff stages; no regular ClassI union or current identity join.'))
    smith2018=json.loads((OUT/'2018-smith-two-stage-native-original-readings.json').read_text());smith_errors=[]
    for stage in smith2018['sources']:
        if stage['source_raw_sha256']!=next(r['raw_sha256'] for r in receipts if r['id']==stage['source_id']):smith_errors.append((stage['source_id'],'source_hash'))
        for page in stage['pages']:
            raster=BASE/page['original_raster']
            if not raster.exists() or sha(raster.read_bytes())!=page['raster_sha256']:smith_errors.append((stage['source_id'],page['source_pdf_page'],'raster'))
        if stage['physical_TOTAL_page']!=3 or stage['physical_TOTAL_column']!=8 or stage['native_constituents']!=18 or not all(z['passes'] for z in stage['candidate_checks'].values()):smith_errors.append((stage['source_id'],'physical_or_candidate'))
        if len({(z['source_pdf_page'],z['physical_source_column'],z['candidate']) for z in stage['rows']})!=len(stage['rows']) or any(z['party_field_literal'] is not None for z in stage['rows']):smith_errors.append((stage['source_id'],'unique_or_party_scope'))
    smith_peer=json.loads((OUT/'2018-smith-native-peer-reconciliation.json').read_text())
    check('2018_Smith_both_special_stages_direct_original_native_and_frozen_peer',smith2018['total_candidate_positions']==132 and smith2018['native_constituents_per_stage']==18 and {s['election_date'] for s in smith2018['sources']}=={'2018-11-06','2018-11-27'} and not smith_errors and smith_peer['source_position_count']==132 and not smith_peer['disagreements'] and smith_peer['own_sha256']==sha((OUT/'2018-smith-two-stage-native-original-readings.json').read_bytes()),dict(native_per_stage=18,source_positions=132,physical_TOTAL_page=3,physical_TOTAL_column=8,errors=smith_errors,qualification='Distinct original special and runoff grids; printed source headers and two party-unprinted candidate pools only. No cross-stage/current-geography join.'))
    montgomery2018=json.loads((OUT/'2018-montgomery-two-stage-native-original-readings.json').read_text());montgomery_errors=[]
    for stage in montgomery2018['sources']:
        if stage['source_raw_sha256']!=next(r['raw_sha256'] for r in receipts if r['id']==stage['source_id']):montgomery_errors.append((stage['source_id'],'source_hash'))
        for page in stage['pages']:
            raster=BASE/page['original_raster']
            if not raster.exists() or sha(raster.read_bytes())!=page['raster_sha256']:montgomery_errors.append((stage['source_id'],page['source_pdf_page'],'raster'))
        if stage['physical_TOTAL_page']!=3 or stage['physical_TOTAL_column']!=5 or stage['native_constituents']!=15 or not all(z['passes'] for z in stage['candidate_checks'].values()):montgomery_errors.append((stage['source_id'],'physical_or_candidate'))
        if len({(z['source_pdf_page'],z['physical_source_column'],z['candidate']) for z in stage['rows']})!=len(stage['rows']) or any(z['party_field_literal'] is not None for z in stage['rows']):montgomery_errors.append((stage['source_id'],'unique_or_party_scope'))
    montgomery_peer=json.loads((OUT/'2018-montgomery-native-peer-reconciliation.json').read_text())
    check('2018_Montgomery_both_special_stages_direct_original_native_and_frozen_peer',montgomery2018['total_candidate_positions']==132 and montgomery2018['native_constituents_per_stage']==15 and {s['election_date'] for s in montgomery2018['sources']}=={'2018-11-06','2018-11-27'} and not montgomery_errors and montgomery_peer['source_position_count']==132 and not montgomery_peer['disagreements'] and montgomery_peer['own_sha256']==sha((OUT/'2018-montgomery-two-stage-native-original-readings.json').read_bytes()),dict(native_per_stage=15,source_positions=132,physical_TOTAL_page=3,physical_TOTAL_column=5,errors=montgomery_errors,qualification='Source-specific Nov6 and Nov27 native columns and literal headers, no cross-stage/current-geography join.'))
    quitman2018=json.loads((OUT/'2018-quitman-two-stage-native-original-readings.json').read_text());quitman_errors=[]
    for stage in quitman2018['sources']:
        if stage['source_raw_sha256']!=next(r['raw_sha256'] for r in receipts if r['id']==stage['source_id']):quitman_errors.append((stage['source_id'],'source_hash'))
        for page in stage['pages']:
            raster=BASE/page['original_raster']
            if not raster.exists() or sha(raster.read_bytes())!=page['raster_sha256']:quitman_errors.append((stage['source_id'],page['source_pdf_page'],'raster'))
        if stage['physical_TOTAL_page']!=2 or stage['physical_TOTAL_column']!=11 or stage['native_constituents']!=10 or not all(z['passes'] for z in stage['candidate_checks'].values()):quitman_errors.append((stage['source_id'],'physical_or_candidate'))
        if len({(z['source_pdf_page'],z['physical_source_column'],z['candidate']) for z in stage['rows']})!=len(stage['rows']) or any(z['party_field_literal'] is not None for z in stage['rows']):quitman_errors.append((stage['source_id'],'unique_or_party_scope'))
    quitman_peer=json.loads((OUT/'2018-quitman-native-peer-reconciliation.json').read_text())
    check('2018_Quitman_both_special_stages_direct_original_native_and_frozen_peer',quitman2018['total_candidate_positions']==66 and quitman2018['native_constituents_per_stage']==10 and {s['election_date'] for s in quitman2018['sources']}=={'2018-11-06','2018-11-27'} and not quitman_errors and quitman_peer['source_position_count']==66 and not quitman_peer['disagreements'] and quitman_peer['own_sha256']==sha((OUT/'2018-quitman-two-stage-native-original-readings.json').read_bytes()),dict(native_per_stage=10,source_positions=66,physical_TOTAL_page=2,physical_TOTAL_column=11,errors=quitman_errors,qualification='Separate original single-page Senate special/runoff columns, no regular ClassI or same-name current-unit join.'))
    noxubee2018=json.loads((OUT/'2018-noxubee-two-stage-native-original-readings.json').read_text());noxubee_errors=[]
    for stage in noxubee2018['sources']:
        if stage['source_raw_sha256']!=next(r['raw_sha256'] for r in receipts if r['id']==stage['source_id']):noxubee_errors.append((stage['source_id'],'source_hash'))
        for page in stage['pages']:
            raster=BASE/page['original_raster']
            if not raster.exists() or sha(raster.read_bytes())!=page['raster_sha256']:noxubee_errors.append((stage['source_id'],page['source_pdf_page'],'raster'))
        if stage['physical_TOTAL_page']!=2 or stage['physical_TOTAL_column']!=9 or stage['native_constituents']!=8 or not all(z['passes'] for z in stage['candidate_checks'].values()):noxubee_errors.append((stage['source_id'],'physical_or_candidate'))
        if len({(z['source_pdf_page'],z['physical_source_column'],z['candidate']) for z in stage['rows']})!=len(stage['rows']) or any(z['party_field_literal'] is not None for z in stage['rows']):noxubee_errors.append((stage['source_id'],'unique_or_party_scope'))
    noxubee_peer=json.loads((OUT/'2018-noxubee-native-peer-reconciliation.json').read_text())
    check('2018_Noxubee_both_special_stages_direct_original_native_and_frozen_peer',noxubee2018['total_candidate_positions']==66 and noxubee2018['native_constituents_per_stage']==8 and {s['election_date'] for s in noxubee2018['sources']}=={'2018-11-06','2018-11-27'} and not noxubee_errors and noxubee_peer['source_position_count']==66 and not noxubee_peer['disagreements'] and noxubee_peer['own_sha256']==sha((OUT/'2018-noxubee-two-stage-native-original-readings.json').read_bytes()),dict(native_per_stage=8,source_positions=66,physical_TOTAL_page=2,physical_TOTAL_column=9,errors=noxubee_errors,qualification='Separate original stage columns and printed labels; unprinted party unknown, no current-geographic join.'))
    yalobusha2018=json.loads((OUT/'2018-yalobusha-two-stage-native-original-readings.json').read_text());yalobusha_errors=[]
    for stage in yalobusha2018['sources']:
        if stage['source_raw_sha256']!=next(r['raw_sha256'] for r in receipts if r['id']==stage['source_id']):yalobusha_errors.append((stage['source_id'],'source_hash'))
        for page in stage['pages']:
            raster=BASE/page['original_raster']
            if not raster.exists() or sha(raster.read_bytes())!=page['raster_sha256']:yalobusha_errors.append((stage['source_id'],page['source_pdf_page'],'raster'))
        if stage['physical_TOTAL_page']!=3 or stage['physical_TOTAL_column']!=1 or stage['native_constituents']!=11 or not all(z['passes'] for z in stage['candidate_checks'].values()):yalobusha_errors.append((stage['source_id'],'physical_or_candidate'))
        if len({(z['source_pdf_page'],z['physical_source_column'],z['candidate']) for z in stage['rows']})!=len(stage['rows']) or any(z['party_field_literal'] is not None for z in stage['rows']):yalobusha_errors.append((stage['source_id'],'unique_or_party_scope'))
    yalobusha_peer=json.loads((OUT/'2018-yalobusha-native-peer-reconciliation.json').read_text())
    check('2018_Yalobusha_both_special_stages_direct_original_native_and_frozen_peer',yalobusha2018['total_candidate_positions']==132 and yalobusha2018['native_constituents_per_stage']==11 and {s['election_date'] for s in yalobusha2018['sources']}=={'2018-11-06','2018-11-27'} and not yalobusha_errors and yalobusha_peer['source_position_count']==132 and not yalobusha_peer['disagreements'] and yalobusha_peer['own_sha256']==sha((OUT/'2018-yalobusha-two-stage-native-original-readings.json').read_bytes()),dict(native_per_stage=11,source_positions=132,physical_TOTAL_page=3,physical_TOTAL_column=1,errors=yalobusha_errors,qualification='Separate stage original pages and printed source-only headers. Nov6 regular ClassI office remains distinct; no same-name current unit join.'))
    greene2018=json.loads((OUT/'2018-greene-two-stage-native-original-readings.json').read_text());greene_peer=json.loads((OUT/'2018-greene-native-peer-reconciliation.json').read_text());greene_errors=[]
    for stage in greene2018['sources']:
        if stage['source_raw_sha256']!=next(r['raw_sha256'] for r in receipts if r['id']==stage['source_id']):greene_errors.append((stage['source_id'],'source_hash'))
        if stage['physical_TOTAL_page']!=3 or stage['physical_TOTAL_column']!=3 or stage['native_constituents']!=13 or not all(c['passes'] for c in stage['candidate_checks'].values()):greene_errors.append((stage['source_id'],'physical_or_candidate'))
        if len({(r['source_pdf_page'],r['physical_source_column'],r['candidate']) for r in stage['rows']})!=len(stage['rows']) or any(r['party_field_literal'] is not None for r in stage['rows']):greene_errors.append((stage['source_id'],'unique_or_party_scope'))
        for page in stage['pages']:
            p=BASE/page['original_raster']
            if not p.exists() or sha(p.read_bytes())!=page['raster_sha256']:greene_errors.append((stage['source_id'],page['source_pdf_page'],'raster'))
    for crop in greene_peer['original_crop_evidence']:
        p=BASE/crop['path']
        if not p.exists() or sha(p.read_bytes())!=crop['sha256'] or crop['direct_visual_original_read']!='Mclain':greene_errors.append((crop['source_id'],'literal_crop'))
    history=greene_peer['initial_disagreement_archive'];history_path=BASE/history['path']
    if not history_path.exists() or sha(history_path.read_bytes())!=history['stored_sha256'] or sha(gzip.decompress(history_path.read_bytes()))!=history['original_sha256']:greene_errors.append('initial_peer_literal_history')
    check('2018_Greene_both_special_stages_original_votes_peer_with_six_literal_case_exceptions',greene2018['total_candidate_positions']==132 and greene2018['native_constituents_per_stage']==13 and greene_peer['source_position_count']==132 and not greene_peer['disagreements'] and len(greene_peer['accepted_literal_differences'])==6 and {(x['own_original_literal'],x['peer_derivative_literal'],x['page'],x['physical_column']) for x in greene_peer['accepted_literal_differences']}=={('Mclain','McLain',3,1)} and greene_peer['own_sha256']==sha((OUT/'2018-greene-two-stage-native-original-readings.json').read_bytes()) and not greene_errors,dict(native_per_stage=13,positions=132,printed_original_literal='Mclain',peer_derivative_literal='McLain',candidate_value_differences=0,errors=greene_errors,qualification='Six stage/candidate literal capitalization exceptions are preserved, not normalized into source identity; source votes/roles/parent FIPS agree.'))
    hp=json.loads((OUT/'historical-county-peer-reconciliation.json').read_text());check('independent_peer_164_originals492_historical_fields_with_Issaquena_ordinal_vintage',hp['compared_candidate_values']==492 and not hp['candidate_differences'] and hp['accepted_TOTAL_ordinal_differences']==[dict(source_id='sos-2018-county-issaquena',own=4,peer=6)] and hp['qualified_machine_vs_physical_ordinal'],dict(pins=hp['input_pins'],ordinal_vintages=hp['accepted_TOTAL_ordinal_differences']))
    pub=json.loads((OUT/'2020-publication-original-peer-reconciliation.json').read_text())
    check('original_2020_104_county_publications_312_candidate_totals_peer_and_state',pub['source_count']==104 and pub['county_count']==82 and pub['amended_publication_count']==22 and pub['compared_candidate_fields']==312 and not pub['source_value_page_hash_differences'] and not pub['selected_county_CSV_differences'] and pub['all_original_publications_minus_original_state_certificate']=={'Mike Espy':-474,'Cindy Hyde-Smith':-48,'Jimmy L. Edwards':-2} and pub['selected_minus_amended_state_certificate']=={'Mike Espy':0,'Cindy Hyde-Smith':0,'Jimmy L. Edwards':0} and pub['changed_amendment_count']==3,dict(source_count=pub['source_count'],candidate_fields=pub['compared_candidate_fields'],changed_counties=[x['county'] for x in pub['amendment_comparisons'] if x['any_change']],qualification=pub['qualification']))
    h2020=json.loads((OUT/'2020-native-alcorn-original-readings.json').read_text())
    h2020aid=OUT/h2020['ocr_aid_path'].removeprefix('data/turnout/')
    h2020visual=BASE/h2020['visual_exception_atlas']
    h2020bad=[]
    for p in h2020['pages']:
        raster=BASE/p['original_raster']
        if not raster.exists() or sha(raster.read_bytes())!=p['raster_sha256']:h2020bad.append(('original_raster',p['source_page']))
    if sha(h2020aid.read_bytes())!=h2020['ocr_aid_sha256']:h2020bad.append('ocr_aid_hash')
    if sha(h2020visual.read_bytes())!=h2020['visual_exception_atlas_sha256']:h2020bad.append('visual_exception_hash')
    if len({(x['source_page'],x['source_column'],x['candidate']) for x in h2020['rows']})!=66:h2020bad.append('duplicate_or_missing_position')
    check('2020_Alcorn_17_native_3candidate_original_page_OCR_visual_peer',h2020['native_constituents']==17 and h2020['source_TOTAL_positions']==3 and h2020['unused_null_positions']==12 and len(h2020['rows'])==66 and all(c['passes'] for c in h2020['candidate_checks'].values()) and not h2020['peer_differences'] and not h2020bad,dict(native=17,positions=66,manual_original_exception_fields=8,source_candidate_sums={k:v['native_sum'] for k,v in h2020['candidate_checks'].items()},errors=h2020bad,qualification='One actual 2020 publication; all other historical native sources remain open.'))
    historic_tags=['benton','benton-amended','greene','wilkinson','issaquena','noxubee','sharkey-original','sharkey-amended','calhoun','tishomingo','smith','tunica','stone','attala','amite','clarke','kemper','winston','newton','jasper-original','jasper-amended','george','washington-original','washington-amended','carroll','clay','clay-amended','yalobusha-original','yalobusha-amended','choctaw-original','choctaw-amended','quitman','grenada','jefferson','claiborne','franklin','perry','webster','prentiss-original','prentiss-amended']
    historic_direct=[json.loads((OUT/f'{tag}-2020-native-original-readings.json').read_text()) for tag in historic_tags]
    historical_native_errors=[]
    for d in historic_direct:
        if d['source_raw_sha256']!=next((r['raw_sha256'] for r in receipts if r['id']==d['source_id']),None):historical_native_errors.append((d['source_id'],'raw_hash'))
        expected_label_differences=d['accepted_source_literal_label_differences'] if d['source_id']=='sos-2020-county-kemper' else []
        if not all(x['passes'] for x in d['candidate_checks'].values()) or d['peer_differences']!=expected_label_differences:historical_native_errors.append((d['source_id'],'source_or_peer'))
        if len({(x['source_page'],x['source_column'],x['candidate']) for x in d['rows']})!=len(d['rows']):historical_native_errors.append((d['source_id'],'duplicate_position'))
        for p in d['pages']:
            path=BASE/p['full_original_raster']
            if not path.exists() or sha(path.read_bytes())!=p['raster_sha256']:historical_native_errors.append((d['source_id'],p['source_page'],'original_raster'))
    check('fortyone_2020_native_source_publications_565_constituents_complete_original_controls_peer',len(historic_direct)==40 and len({d['source_id'] for d in historic_direct}|{h2020['source_id']})==41 and sum(d['native_constituents'] for d in historic_direct)+h2020['native_constituents']==565 and sum(d['source_positions'] for d in historic_direct)+len(h2020['rows'])==2475 and not historical_native_errors,dict(source_publications=41,native_across_vintages=565,candidate_positions=2475,errors=historical_native_errors,qualification='Thirty-three counties; Prentiss original and amended publications each retain15 distinct source columns and literal publication values. Earlier 23-publication prose native count correction retained; no source/candidate change. Frozen65 Kemper one-n literal source header differs from two-n frozen peer; all votes agree. Remaining63 publications and statewide2018 native stages open.'))
    coahoma_native=json.loads((OUT/'2020-coahoma-two-publication-native-original-readings.json').read_text())
    coahoma_peer=json.loads((OUT/'2020-coahoma-two-publication-native-peer-reconciliation.json').read_text())
    coahoma_errors=[]
    coahoma_ids={s['source_id'] for s in coahoma_native['sources']}
    if coahoma_ids!={'sos-2020-county-coahoma','sos-2020-county-coahoma-amended'}:coahoma_errors.append('publication_ids')
    for s in coahoma_native['sources']:
        if s['source_raw_sha256']!=next((r['raw_sha256'] for r in receipts if r['id']==s['source_id']),None):coahoma_errors.append((s['source_id'],'raw_hash'))
        if len({(r['source_pdf_page'],r['physical_source_column'],r['candidate']) for r in s['rows']})!=66:coahoma_errors.append((s['source_id'],'source_positions'))
        if s['native_constituents']!=18 or s['physical_TOTAL_page']!=3 or s['physical_TOTAL_column']!=8 or not all(c['passes'] for c in s['candidate_checks'].values()):coahoma_errors.append((s['source_id'],'controls'))
        for p in s['pages']:
            path=BASE/p['original_raster']
            if not path.exists() or sha(path.read_bytes())!=p['raster_sha256']:coahoma_errors.append((s['source_id'],p['source_pdf_page'],'original_raster'))
    if coahoma_peer['own_original_reading_sha256']!=sha((OUT/'2020-coahoma-two-publication-native-original-readings.json').read_bytes()) or coahoma_peer['compared_candidate_positions']!=132 or coahoma_peer['differences']:coahoma_errors.append('post_original_peer_reconciliation')
    check('Coahoma_2020_two_publications_36_native_132_source_positions_original_peer',len(coahoma_native['sources'])==2 and coahoma_native['total_candidate_positions']==132 and coahoma_peer['native_source_observations']==36 and not coahoma_errors,dict(source_publications=2,source_native_observations=36,positions=132,original_candidate_vectors=[s['candidate_checks'] for s in coahoma_native['sources']],errors=coahoma_errors,qualification='Added after the earlier immutable 41-publication set; 43 distinct publication views across34 counties, with amended Coahoma selected only once.'))
    union2020=json.loads((OUT/'union-2020-native-original-readings.json').read_text());union2020_errors=[]
    if union2020['source_id']!='sos-2020-county-union' or union2020['source_raw_sha256']!=next(r['raw_sha256'] for r in receipts if r['id']=='sos-2020-county-union'):union2020_errors.append('source_hash')
    if len({(r['source_page'],r['source_column'],r['candidate']) for r in union2020['rows']})!=66 or union2020['peer_differences']:union2020_errors.append('source_positions_or_peer')
    for page in union2020['pages']:
        raster=BASE/page['full_original_raster']
        if not raster.exists() or sha(raster.read_bytes())!=page['raster_sha256']:union2020_errors.append(('original_raster',page['source_page']))
    check('Union_2020_full_original_20_native_three_candidate_source_and_peer',union2020['native_constituents']==20 and union2020['source_positions']==66 and {k:v['native_sum'] for k,v in union2020['candidate_checks'].items()}=={'Mike Espy':2660,'Cindy Hyde-Smith':9572,'Jimmy L. Edwards':424} and all(v['passes'] for v in union2020['candidate_checks'].values()) and not union2020_errors,dict(publication='original',native=20,source_positions=66,printed_TOTAL_page=3,printed_TOTAL_physical_column=10,errors=union2020_errors,qualification='Complete actual original 2020 Senate grid; no cross-year or current precinct identity inferred.'))
    peer2020=json.loads((OUT/'2020-full-peer-native-scope-audit.json').read_text());peer2020_errors=[]
    if peer2020['own_original_publication_control_sha256']!=sha((OUT/'2020-publication-original-total-readings.json').read_bytes()):peer2020_errors.append('own_publication_controls_hash')
    if len(peer2020['flat102_source_checks'])!=306 or len(peer2020['separate_coahoma_source_checks'])!=6 or any(r['peer_native_sum']!=r['peer_printed_TOTAL'] or r['peer_printed_TOTAL']!=r['own_original_county_TOTAL'] for r in peer2020['flat102_source_checks']+peer2020['separate_coahoma_source_checks']):peer2020_errors.append('source_candidate_controls')
    if len(peer2020['flat102_original_render_sha256_by_page'])!=248 or any(not (BASE/r['path']).exists() or sha((BASE/r['path']).read_bytes())!=r['sha256'] for r in peer2020['flat102_original_render_sha256_by_page']):peer2020_errors.append('peer_original_renders')
    check('peer_complete_2020_104_publication_native_scope_against_own_original_controls',peer2020['publication_views']==104 and peer2020['selected_amended_where_linked_views']==82 and peer2020['candidate_source_controls']==312 and peer2020['native_observations_across_distinct_publications']==2131 and peer2020['combined104_candidate_or_null_positions']==8316 and peer2020['flat102_roles_by_candidate_position']=={'source_native_reporting_constituent':6285,'source_TOTAL':306,'unused_template_column':1590,'source_administrative_reporting_column':3} and peer2020['selected82_native_candidate_state_controls']=={'Mike Espy':578691,'Cindy Hyde-Smith':709511,'Jimmy L. Edwards':23152} and peer2020['accepted_new_own_original_native_cells_from_this_audit']==0 and not peer2020_errors,dict(source_views=104,selected_views=82,native_across_versions=2131,source_candidate_controls=312,errors=peer2020_errors,qualification='Read-only complete peer original-native witness reconciled to independent county publication controls; own direct-original subset remains separately bounded, no cross-vintage ID or source chronology inference.'))
    aid2018=json.loads((OUT/'2018-original-numeric-aid-validation.json').read_text())
    aid2018_errors=[]
    if sha((OUT/'source/2018-vote-free-targets-v1.json').read_bytes())!=aid2018['target_sha256']:aid2018_errors.append('target_hash')
    for pin in aid2018['assets']:
        p=BASE/pin['path']
        if not p.exists() or p.stat().st_size!=pin['bytes'] or sha(p.read_bytes())!=pin['sha256']:aid2018_errors.append(pin['path'])
    check('all164_2018_original_pixel_numeric_aids_are_pinned_diagnostic_only',aid2018['source_views']==164 and aid2018['targeted_original_pages']==381 and aid2018['asset_count']==545 and aid2018['counts']==dict(targeted_cells=12476,single_numeric_token=7004,no_token=4430,ambiguous_or_noninteger=1042) and len(aid2018['empty_target_views'])==8 and not aid2018_errors,dict(source_views=164,raw_pages=381,tentative_target_cells=12476,empty_machine_views=8,errors=aid2018_errors,qualification='Provenance/position inventory only; OCR values, absences and target boxes cannot become accepted native votes or zeros.'))
    frozen78_validation_raw=(OUT/'2018-frozen78-original-pixels-validation.json').read_bytes()
    frozen78=json.loads(frozen78_validation_raw)
    frozen78_compare=json.loads((OUT/'2018-frozen78-original-ocr-peer-diagnostic.json').read_text())
    frozen78_errors=[]
    if sha((OUT/'source/2018-frozen78-vote-free-position-hints-v1.json').read_bytes())!=frozen78['hint_sha256']:frozen78_errors.append('vote_free_hint')
    if frozen78_compare['original_OCR_validation_sha256']!=sha(frozen78_validation_raw):frozen78_errors.append('post_extraction_validation_pin')
    for pin in frozen78['assets']:
        p=BASE/pin['path']
        if not p.exists() or p.stat().st_size!=pin['bytes'] or sha(p.read_bytes())!=pin['sha256']:frozen78_errors.append(pin['path'])
    expected78=dict(expected_printed_numeric=3614,exact_numeric_OCR=3184,
                    numeric_OCR_disagree=430,expected_source_X=4,exact_X_OCR=3,
                    source_X_OCR_disagree=1,expected_unprinted_null=1134,
                    blank_OCR_on_unprinted=1122,nonblank_OCR_on_unprinted=12,
                    original_header_positions=1584,header_OCR_fold_match=817,
                    header_OCR_disagree=767,geometry_mismatch_pages=0)
    check('frozen78_2018_value_free_original_pixel_OCR_pinned_diagnostic_only',frozen78['source_views']==78 and frozen78['original_pages']==144 and frozen78['asset_count']==222 and frozen78['original_pixel_crop_hashes_verified']==dict(headers=1584,cells=4752) and frozen78['counts']['candidate_cell_targets']==4752 and frozen78_compare['counts']==expected78 and frozen78_compare['accepted_native_field_count_from_this_comparison']==0 and len(frozen78_compare['numerical_or_source_mark_OCR_exceptions'])==443 and len(frozen78_compare['header_OCR_exceptions'])==767 and not frozen78_errors,dict(source_views=78,original_pages=144,targeted_cells=4752,exact_numeric_OCR=3184,numeric_disagreements=430,unresolved_source_X=1,nonblank_OCR_on_unprinted=12,header_OCR_disagreements=767,errors=frozen78_errors,qualification='Fresh OCR only from exact original PDF pixels using a strictly value-free frozen layout; comparison after extraction. No accepted vote, blank, header, numeric polygon or unit identity follows from an OCR match.'))
    leflore=json.loads((OUT/'2018-leflore-Nov6-native-original-readings.json').read_text())
    leflore_errors=[];leflore_rows=leflore['rows']
    if len(leflore_rows)!=88 or len({(r['source_pdf_page'],r['physical_source_column'],r['candidate']) for r in leflore_rows})!=88:leflore_errors.append('source_position_coverage')
    if leflore['source_raw_sha256']!=next((r['raw_sha256'] for r in receipts if r['id']==leflore['source_id']),None):leflore_errors.append('source_raw_hash')
    for p in leflore['pages']:
        path=BASE/p['original_raster']
        if not path.exists() or sha(path.read_bytes())!=p['raster_sha256']:leflore_errors.append((p['source_pdf_page'],'original_page'))
    strip=leflore['Espy_full_original_row_strips'];strip_path=BASE/strip['path']
    if not strip_path.exists() or sha(strip_path.read_bytes())!=strip['sha256']:leflore_errors.append('original_Espy_row_strips')
    lf_checks=leflore['candidate_checks']
    for candidate,item in lf_checks.items():
        native=sum(r['votes'] for r in leflore_rows if r['candidate']==candidate and r['role']=='source_native_reporting_constituent')
        printed=[r['votes'] for r in leflore_rows if r['candidate']==candidate and r['role']=='source_TOTAL']
        if len(printed)!=1 or native!=item['native_sum'] or printed[0]!=item['printed_TOTAL'] or native-printed[0]!=item['native_minus_printed_TOTAL'] or item['county_control']!=printed[0]:leflore_errors.append((candidate,'source_arithmetic'))
    check('Leflore_2018_Nov6_original_native_Espy_10_source_discrepancy_unallocated',leflore['native_constituents']==18 and leflore['physical_TOTAL_page']==3 and leflore['physical_TOTAL_column']==8 and len(lf_checks)==4 and lf_checks['Mike Espy']['native_sum']==5853 and lf_checks['Mike Espy']['printed_TOTAL']==5863 and lf_checks['Mike Espy']['native_minus_printed_TOTAL']==-10 and all(item['native_minus_printed_TOTAL']==0 for n,item in lf_checks.items() if n!='Mike Espy') and not leflore_errors,dict(original_native_Espy=5853,printed_TOTAL_Espy=5863,unallocated_difference=-10,other_three_candidate_vectors_closed=True,errors=leflore_errors,qualification='One Nov6 source-stage original PDF only. County/state printed TOTAL remains separate; no fitted precinct, no regular ClassI pooling or current ID join.'))
    perry=json.loads((OUT/'2018-perry-two-stage-native-original-readings.json').read_text())
    perry_peer=json.loads((OUT/'2018-perry-native-peer-reconciliation.json').read_text())
    perry_history=json.loads((OUT/'2018-perry-header-wrap-correction-history.json').read_text())
    perry_errors=[]
    for stage in perry['sources']:
        if stage['source_raw_sha256']!=next((r['raw_sha256'] for r in receipts if r['id']==stage['source_id']),None):perry_errors.append((stage['source_id'],'raw_hash'))
        if stage['native_constituents']!=15 or stage['physical_TOTAL_page']!=3 or stage['physical_TOTAL_column']!=5 or not all(x['passes'] for x in stage['candidate_checks'].values()):perry_errors.append((stage['source_id'],'source_controls'))
        for p in stage['pages']:
            image_path=BASE/p['original_raster']
            if not image_path.exists() or sha(image_path.read_bytes())!=p['raster_sha256']:perry_errors.append((stage['source_id'],p['source_pdf_page'],'original_raster'))
    for pin in perry_history['initial_byte_pins']:
        archive_path=OUT/pin['archive_path']
        if not archive_path.exists() or sha(archive_path.read_bytes())!=pin['stored_sha256'] or sha(gzip.decompress(archive_path.read_bytes()))!=pin['raw_sha256']:perry_errors.append((pin['archive_path'],'initial_history'))
    if perry_history['current_reading_sha256']!=sha((OUT/'2018-perry-two-stage-native-original-readings.json').read_bytes()):perry_errors.append('wrap_history_current_pin')
    check('Perry_2018_both_original_stage_grids_and_36_literal_wrap_history',len(perry['sources'])==2 and perry['total_candidate_positions']==132 and perry['native_constituents_per_stage']==15 and perry_peer['source_position_count']==132 and not perry_peer['disagreements'] and perry_peer['own_sha256']==perry_history['current_reading_sha256'] and perry_history['changed_candidate_label_positions']==36 and perry_history['changed_physical_header_positions']==12 and not perry_errors,dict(stage_grids=2,native_per_stage=15,positions=132,header_wrap_only_candidate_positions=36,errors=perry_errors,qualification='Nov6 four-candidate special and Nov27 two-candidate runoff independently original-read, post-read peer exact across numeric/null/role/source/printed header; initial vote fields preserved byte-for-byte with source line-break repair. No cross-stage/current ID join.'))
    for county,native,total_column in [('coahoma',18,8),('kemper',14,4),('winston',12,2)]:
        ledger=json.loads((OUT/f'2018-{county}-two-stage-native-original-readings.json').read_text())
        peer=json.loads((OUT/f'2018-{county}-native-peer-reconciliation.json').read_text())
        flat=readcsv(OUT/f'2018-{county}-two-stage-native-original-cells.csv')
        stage_errors=[]
        for stage in ledger['sources']:
            original=next((r for r in receipts if r['id']==stage['source_id']),None)
            if original is None or stage['source_raw_sha256']!=original['raw_sha256']:stage_errors.append((stage['source_id'],'original_source_hash'))
            if stage['native_constituents']!=native or stage['physical_TOTAL_page']!=3 or stage['physical_TOTAL_column']!=total_column:stage_errors.append((stage['source_id'],'physical_grid'))
            if not all(c['passes'] and c['native_sum']==c['printed_TOTAL']==int(c['county_control']) for c in stage['candidate_checks'].values()):stage_errors.append((stage['source_id'],'candidate_source_control'))
            for page in stage['pages']:
                raster=BASE/page['original_raster']
                if not raster.exists() or sha(raster.read_bytes())!=page['raster_sha256']:stage_errors.append((stage['source_id'],page['source_pdf_page'],'original_page'))
        if len(flat)!=132 or len({(r['source_id'],r['source_pdf_page'],r['physical_source_column'],r['candidate']) for r in flat})!=132:stage_errors.append('flat_source_position_coverage')
        if peer['source_position_count']!=132 or peer['disagreements']:stage_errors.append('independent_peer_post_reading')
        check(f'{county}_2018_both_original_special_stage_grids_reciprocal',len(ledger['sources'])==2 and ledger['native_constituents_per_stage']==native and ledger['total_candidate_positions']==132 and not stage_errors,dict(stage_grids=2,native_per_stage=native,positions=132,physical_TOTAL_page=3,physical_TOTAL_column=total_column,errors=stage_errors,qualification='Separate Nov6 special and Nov27 runoff direct complete-original source grids; no cross-stage/current geometry join or party union.'))
    winston_history=json.loads((OUT/'2018-winston-header-original-correction-history.json').read_text())
    winston_prior=OUT/'source/2018-winston-header-correction-v1/prior-ledger-pins.json'
    winston_errors=[]
    if sha(winston_prior.read_bytes())!=winston_history['prior_manifest_sha256']:winston_errors.append('prior_manifest')
    for pin in json.loads(winston_prior.read_text())['pins']:
        stored=(BASE/pin['archive_path']).read_bytes()
        if sha(stored)!=pin['stored_sha256'] or sha(gzip.decompress(stored))!=pin['raw_sha256']:winston_errors.append(pin['archive_path'])
    for crop in winston_history['original_crops']:
        original=BASE/crop['full_original_raster'];raster=BASE/crop['crop_path']
        if not original.exists() or not raster.exists() or sha(original.read_bytes())!=crop['full_original_raster_sha256'] or sha(raster.read_bytes())!=crop['crop_sha256']:winston_errors.append(crop['source_id'])
    check('Winston_2018_original_Nanih_Waiya_six_literal_only_correction_history',len(winston_history['derivative_comparisons'])==2 and all(x['changed_candidate_label_positions']==6 for x in winston_history['derivative_comparisons']) and len(winston_history['original_crops'])==2 and not winston_errors,dict(stage_headers=2,corrected_candidate_label_positions=6,errors=winston_errors,qualification='Initial Nann Waiya literal reading archived losslessly; complete original pages visibly print Nanih Waiya. Candidate votes, physical columns and roles unchanged; peer comparison followed correction.'))
    tunica=json.loads((OUT/'2018-tunica-two-stage-native-original-readings.json').read_text())
    tunica_peer=json.loads((OUT/'2018-tunica-native-peer-reconciliation.json').read_text())
    tunica_errors=[]
    if len(tunica['sources'])!=2 or tunica['native_constituents_per_stage']!=12 or tunica['total_candidate_positions']!=132:tunica_errors.append('source_grid_count')
    for stage in tunica['sources']:
        receipt=next((r for r in receipts if r['id']==stage['source_id']),None)
        if receipt is None or receipt['raw_sha256']!=stage['source_raw_sha256']:tunica_errors.append((stage['source_id'],'source_hash'))
        if stage['physical_TOTAL_page']!=3 or stage['physical_TOTAL_column']!=2 or not all(x['passes'] for x in stage['candidate_checks'].values()):tunica_errors.append((stage['source_id'],'candidate_source_controls'))
        for p in stage['pages']:
            raster=BASE/p['original_raster']
            if not raster.exists() or sha(raster.read_bytes())!=p['raster_sha256']:tunica_errors.append((stage['source_id'],p['source_pdf_page'],'original_raster'))
    tunica_archive=tunica_peer['initial_disagreement_archive'];stored=(BASE/tunica_archive['path']).read_bytes()
    if sha(stored)!=tunica_archive['stored_sha256'] or sha(gzip.decompress(stored))!=tunica_archive['raw_sha256']:tunica_errors.append('lossless_initial_peer_disagreement')
    for x in tunica_peer['original_crop_evidence']:
        full=BASE/x['original_full_raster'];crop=BASE/x['exact_original_pixel_crop']
        if not full.exists() or not crop.exists() or sha(full.read_bytes())!=x['original_full_raster_sha256'] or sha(crop.read_bytes())!=x['crop_sha256']:tunica_errors.append((x['source_id'],'original_crop'))
    if tunica_peer['own_sha256']!=sha((OUT/'2018-tunica-two-stage-native-original-readings.json').read_bytes()):tunica_errors.append('current_reading_pin')
    check('Tunica_2018_both_original_stage_grids_Mhoon_peer_literal_disagreement',tunica_peer['source_position_count']==132 and not tunica_peer['disagreements'] and len(tunica_peer['accepted_literal_differences'])==6 and all(x['original_literal']=='Mhoon Landing' and x['peer_derivative_literal']=='Moon Landing' and x['source_pdf_page']==2 and x['physical_source_column']==2 for x in tunica_peer['accepted_literal_differences']) and not tunica_errors,dict(stage_grids=2,native_per_stage=12,positions=132,explicit_source_literal_differences=6,errors=tunica_errors,qualification='All numeric/null/role/source-hash/FIPS fields agree peer after original reading. Both actual p2c2 original crops print Mhoon Landing; frozen peer says Moon Landing. No normalization/current precinct join.'))
    for county in ('calhoun','sharkey'):
        ledger=json.loads((OUT/f'2018-{county}-two-stage-native-original-readings.json').read_text())
        peer=json.loads((OUT/f'2018-{county}-native-peer-reconciliation.json').read_text())
        source_errors=[]
        for stage in ledger['sources']:
            original=next((r for r in receipts if r['id']==stage['source_id']),None)
            if original is None or original['raw_sha256']!=stage['source_raw_sha256']:source_errors.append((stage['source_id'],'source_hash'))
            if stage['native_constituents']!=10 or stage['physical_TOTAL_page']!=2 or stage['physical_TOTAL_column']!=11 or not all(x['passes'] for x in stage['candidate_checks'].values()):source_errors.append((stage['source_id'],'physical_source_controls'))
            for page in stage['pages']:
                raster=BASE/page['original_raster']
                if not raster.exists() or sha(raster.read_bytes())!=page['raster_sha256']:source_errors.append((stage['source_id'],page['source_pdf_page'],'original_raster'))
        check(f'{county}_2018_both_original_single_page_stage_grids_and_peer',len(ledger['sources'])==2 and ledger['native_constituents_per_stage']==10 and ledger['total_candidate_positions']==66 and peer['source_position_count']==66 and not peer['disagreements'] and not source_errors,dict(stage_grids=2,native_per_stage=10,positions=66,original_page=2,physical_TOTAL_column=11,errors=source_errors,qualification='Four-candidate Nov6 special and two-candidate Nov27 runoff independently original-read; all fields peer agreement post-reading, no cross-stage/current ID join.'))
    neshoba=json.loads((OUT/'2018-neshoba-original-validation.json').read_text())
    neshoba_peer=json.loads((OUT/'2018-neshoba-native-peer-reconciliation.json').read_text())
    check('Neshoba_2018_two_complete_original_stage_grids_header_history_and_peer',neshoba['status']=='pass_bounded_complete_original_two_stages' and neshoba['source_position_count']==198 and neshoba['native_constituents_per_stage']==27 and neshoba['numeric_positions']==168 and neshoba['unprinted_null_positions']==30 and neshoba['initial_header_difference_count']==36 and neshoba['current_reading_sha256']==sha((OUT/'2018-neshoba-two-stage-native-original-readings.json').read_bytes()) and neshoba_peer['source_position_count']==198 and not neshoba_peer['disagreements'],dict(stage_grids=2,native_per_stage=27,positions=198,source_literal_glyph_correction='Arlington in both original PDFpage2 column1 headers',qualification='Originals, source controls and exact correction-history pins independently checked by validate_2018_neshoba_original.py; no current identity join.'))
    george=json.loads((OUT/'2018-george-two-stage-native-original-readings.json').read_text())
    george_peer=json.loads((OUT/'2018-george-native-peer-reconciliation.json').read_text())
    george_errors=[]
    for stage in george['sources']:
        original=next((r for r in receipts if r['id']==stage['source_id']),None)
        if original is None or original['raw_sha256']!=stage['source_raw_sha256']:george_errors.append((stage['source_id'],'source_hash'))
        if stage['native_constituents']!=22 or stage['physical_TOTAL_page']!=4 or stage['physical_TOTAL_column']!=1 or not all(x['passes'] for x in stage['candidate_checks'].values()):george_errors.append((stage['source_id'],'physical_source_controls'))
        for page in stage['pages']:
            raster=BASE/page['original_raster']
            if not raster.exists() or sha(raster.read_bytes())!=page['raster_sha256']:george_errors.append((stage['source_id'],page['source_pdf_page'],'original_raster'))
    check('George_2018_two_complete_original_stage_grids_and_peer',len(george['sources'])==2 and george['native_constituents_per_stage']==22 and george['total_candidate_positions']==198 and george_peer['source_position_count']==198 and not george_peer['disagreements'] and george_peer['own_sha256']==sha((OUT/'2018-george-two-stage-native-original-readings.json').read_bytes()) and not george_errors,dict(stage_grids=2,native_per_stage=22,numeric_positions=138,unused_null_positions=60,physical_TOTAL_page=4,physical_TOTAL_column=1,errors=george_errors,qualification='Separate Nov6 special and Nov27 runoff, six original candidate vectors, no ClassI/current-geography join.'))
    union2018=json.loads((OUT/'2018-union-two-stage-native-original-readings.json').read_text())
    union_peer=json.loads((OUT/'2018-union-native-peer-reconciliation.json').read_text())
    union_errors=[]
    for stage in union2018['sources']:
        original=next((r for r in receipts if r['id']==stage['source_id']),None)
        if original is None or original['raw_sha256']!=stage['source_raw_sha256']:union_errors.append((stage['source_id'],'source_hash'))
        if stage['native_constituents']!=20 or stage['physical_TOTAL_page']!=3 or stage['physical_TOTAL_column']!=10 or not all(x['passes'] for x in stage['candidate_checks'].values()):union_errors.append((stage['source_id'],'physical_source_controls'))
        for page in stage['pages']:
            raster=BASE/page['original_raster']
            if not raster.exists() or sha(raster.read_bytes())!=page['raster_sha256']:union_errors.append((stage['source_id'],page['source_pdf_page'],'original_raster'))
    check('Union_2018_two_complete_original_stage_grids_and_peer',len(union2018['sources'])==2 and union2018['native_constituents_per_stage']==20 and union2018['total_candidate_positions']==132 and union_peer['source_position_count']==132 and not union_peer['disagreements'] and union_peer['own_sha256']==sha((OUT/'2018-union-two-stage-native-original-readings.json').read_bytes()) and not union_errors,dict(stage_grids=2,native_per_stage=20,numeric_positions=126,unused_null_positions=6,physical_TOTAL_page=3,physical_TOTAL_column=10,errors=union_errors,qualification='Nov6 four special candidates and Nov27 two runoff candidates are separate original grids; no current identity or 2024 vendor-profile join.'))
    sunflower=json.loads((OUT/'2018-sunflower-two-stage-native-original-readings.json').read_text())
    sunflower_peer=json.loads((OUT/'2018-sunflower-native-peer-reconciliation.json').read_text())
    sunflower_errors=[]
    for stage in sunflower['sources']:
        original=next((r for r in receipts if r['id']==stage['source_id']),None)
        if original is None or original['raw_sha256']!=stage['source_raw_sha256']:sunflower_errors.append((stage['source_id'],'source_hash'))
        if stage['native_constituents']!=17 or stage['physical_TOTAL_page']!=3 or stage['physical_TOTAL_column']!=7 or not all(v['passes'] for v in stage['candidate_checks'].values()):sunflower_errors.append((stage['source_id'],'source_controls'))
        for page in stage['pages']:
            raster=BASE/page['original_raster']
            if not raster.exists() or sha(raster.read_bytes())!=page['raster_sha256']:sunflower_errors.append((stage['source_id'],page['source_pdf_page'],'original_raster'))
    check('Sunflower_2018_two_complete_original_stage_grids_and_peer',len(sunflower['sources'])==2 and sunflower['native_constituents_per_stage']==17 and sunflower['total_candidate_positions']==132 and sunflower_peer['source_position_count']==132 and not sunflower_peer['disagreements'] and sunflower_peer['own_sha256']==sha((OUT/'2018-sunflower-two-stage-native-original-readings.json').read_bytes()) and not sunflower_errors,dict(stage_grids=2,native_per_stage=17,printed_TOTAL_page=3,printed_TOTAL_physical_column=7,source_vectors=[s['candidate_checks'] for s in sunflower['sources']],errors=sunflower_errors,qualification='Four special candidates and two runoff candidates are distinct; regular Class I rows excluded; no cross-stage/current identity join.'))
    peer164=json.loads((OUT/'2018-full-peer-native-scope-audit.json').read_text())
    peer164_errors=[]
    if peer164['own_independent_county_controls_sha256']!=sha((OUT/'historical-county-candidate-votes.csv').read_bytes()):peer164_errors.append('county_controls_hash')
    if len(peer164['source_checks'])!=492 or any(r['printed_TOTAL']!=r['own_county_control'] for r in peer164['source_checks']):peer164_errors.append('source_controls')
    if len(peer164['exceptions'])!=5 or {(r['source_id'],r['candidate'],r['known_native_sum_minus_printed_TOTAL']) for r in peer164['exceptions'] if r['known_native_sum_minus_printed_TOTAL']}!={('sos-2018-county-leflore','Mike Espy',-10)} or sum(len(r['literal_X_source_keys']) for r in peer164['exceptions'])!=6:peer164_errors.append('native_exceptions')
    if len(peer164['source_render_sha256_by_page'])!=414 or any(not (BASE/r['path']).exists() or sha((BASE/r['path']).read_bytes())!=r['sha256'] for r in peer164['source_render_sha256_by_page']):peer164_errors.append('peer_original_renders')
    check('peer_complete_2018_native_source_scope_against_own_164_county_controls',peer164['source_views']==164 and peer164['counties']==82 and peer164['native_observations_across_distinct_stages']==3545 and peer164['source_columns_across_distinct_stages']==4554 and peer164['candidate_or_null_positions']==13662 and peer164['roles_by_candidate_position']=={'native':10632,'TOTAL':492,'unused':2530,'administrative':8} and peer164['literal_source_marks']=={'X':6} and peer164['accepted_new_own_original_native_cells_from_this_audit']==0 and not peer164_errors,dict(stage_views=164,native_observations=3545,candidate_controls=492,leflore_Espy_native_minus_printed_TOTAL=-10,literal_X_native_cells=6,errors=peer164_errors,qualification='Read-only peer full-native original witness reconciled to independently read county TOTALs. This does not expand own direct-original native coverage beyond the separately listed stages, fill X or −10, or establish current geography.'))
    three=json.loads((OUT/'2018-peer142-three-original-aids-diagnostic.json').read_text())
    three_count=three['counts']
    check('2018_peer142_new64_three_original_OCR_aids_diagnostic_only',three['source_views']==64 and three['field_positions']==5544 and three_count['numeric']==4416 and three_count['some_original_OCR_agrees']==3941 and three_count['all_OCR_unresolved_or_disagrees']==475 and three_count['unprinted_null']==1128 and three_count['all_OCR_blank']==1053 and three_count['OCR_nonblank_at_source_null']==75 and len(three['exceptions'])==550 and three['accepted_native_fields_from_this_diagnostic']==0,dict(original_source_stage_views=64,source_candidate_positions=5544,numeric_agreements_diagnostic_only=3941,still_requires_direct_original_numeric_review=475,OCR_nonblank_on_source_null=75,qualification='All OCR saved from original pages/crops before source-value comparison; no source vote, blank, physical digit box or reporting ID accepted from this diagnostic.'))
    hmeta=json.loads((OUT/'2020-native-peer-metadata-update-history.json').read_text())
    hmeta_errors=[];metadata_fields=set(hmeta['permitted_metadata_fields'])
    hmeta_pin=OUT/'source/2020-native-peer-metadata-history-inputs-v1.json'
    if sha(hmeta_pin.read_bytes())!='02b3c394af61b9e5ecc05a4217bc27fdfc42d5b61a1b4405c75ff99e8731ebec':hmeta_errors.append('immutable_39_archive_input_pin')
    for r in hmeta['records']:
        try:
            stored=(BASE/r['archive_path']).read_bytes();earlier=gzip.decompress(stored);later=(BASE/r['current_path']).read_bytes()
            old=json.loads(earlier);new=json.loads(later)
            core=lambda d:{k:v for k,v in d.items() if k not in metadata_fields}
            changed={k:dict(earlier_present=k in old,earlier_value=old.get(k),later_present=k in new,later_value=new.get(k)) for k in sorted(set(old)|set(new)) if old.get(k)!=new.get(k) or (k in old)!=(k in new)}
            if sha(stored)!=r['archive_stored_sha256'] or len(stored)!=r['archive_stored_bytes'] or sha(earlier)!=r['earlier_raw_sha256'] or sha(later)!=r['later_raw_sha256'] or core(old)!=core(new) or changed!=r['comparison_metadata_changes'] or not set(changed)<=metadata_fields or len(old['rows'])!=r['source_positions']:hmeta_errors.append(r['source_id'])
        except Exception as exc:hmeta_errors.append((r['source_id'],str(exc)))
    check('2020_native_original_witness_later_peer_metadata_history',hmeta['archived_reading_count']==39 and hmeta['metadata_changed_count']==17 and hmeta['unchanged_count']==22 and hmeta['candidate_or_null_positions']==2343 and len(hmeta['records'])==39 and not hmeta_errors,dict(archived_readings=39,later_metadata_changes=17,source_positions=2343,errors=hmeta_errors,qualification='Earlier original-reading peer hashes and exact archive bytes preserved separately from later repeat comparisons; no source rows or votes changed.'))
    perry_revision=json.loads((OUT/'2020-native-perry-correction-history.json').read_text())
    check('2020_Perry_source_header_original_crop_correction_preserved',perry_revision['initial_direct_fullpage_read']=='Beaumont Senior Citizens 1120' and perry_revision['corrected_direct_original_crop_read']=='Beaumont Senior Citizens 5120' and not perry_revision['count_change'] and all((BASE/perry_revision[k]).exists() and sha((BASE/perry_revision[k]).read_bytes())==perry_revision[k+'_sha256'] for k in ('original_raster','source_crop')),perry_revision)
    webster_revision=json.loads((OUT/'2020-native-webster-correction-history.json').read_text())
    check('2020_Webster_source_TOTAL_original_crop_correction_preserved',webster_revision['initial_direct_fullpage_read']==4057 and webster_revision['corrected_direct_original_crop_read']==4067 and webster_revision['source_page']==3 and webster_revision['physical_column']==7 and all((BASE/webster_revision[k]).exists() and sha((BASE/webster_revision[k]).read_bytes())==webster_revision[k+'_sha256'] for k in ('original_raster','source_crop')),webster_revision)
    native_count_correction=json.loads((OUT/'source/2020-native-count-correction.json').read_text())
    check('2020_23_publication_native_count_arithmetic_correction_retained',native_count_correction['earlier_draft_23_publication_native_count']==279 and native_count_correction['corrected_23_publication_native_count']==313 and native_count_correction['arithmetic_difference']==34 and sorted(x['native_constituents'] for x in native_count_correction['new_publication_native_counts'].values())==[16,17,17,22],native_count_correction)
    native_hints={v:OUT/f'source/2020-native-position-hints-{v}.json' for v in ('v1','v2','v3','v4','v5','v6','v7')}
    expected_hints={'v1':('06f6964a02ec5fa6d54a642b23fa2fe30200e6c9be5b19d9af5ad3caeb0a8c02',38),'v2':('86dc96083e52a5df84e12c90201d73e6428f42ae76fbb4745e5f3e25e6aa18ef',48),'v3':('8722697ff80ef80d9d757fbe9c017155e2f693c0f4d57fad10063ae13edae4ca',63),'v4':('034b4e4bae4ea7571bb100e058383aa1fb725286398ecf698870b5bfc82ade00',68),'v5':('213e5f09e0c8f905802ff2bf6a5479bdfe761dca8cb54e34389838068001f184',83),'v6':('6b7cfe90d06c231d415342829715552865e8566b6a3a282d5e791e67e3be7d4c',93),'v7':('a3b7ea9287f0e2ab7261f515b7aa9f1a882a9c0230c0073bc8fe9f0340517ff1',102)}
    hint_errors=[]
    for v,path in native_hints.items():
        h=json.loads(path.read_text());expected_digest,expected_count=expected_hints[v]
        if sha(path.read_bytes())!=expected_digest or len(h['sources'])!=expected_count or any('votes' in str(s) or 'literal_native_label' in str(s) for s in h['sources']):hint_errors.append(v)
    check('2020_vote_free_position_hints_exact_immutable40_through104_sources',not hint_errors,dict(hint_hashes={v:sha(p.read_bytes()) for v,p in native_hints.items()},errors=hint_errors))
    kemper_review=json.loads((OUT/'2020-native-kemper-header-review.json').read_text());kemper_errors=[]
    for field,digest in [('full_original_raster','full_original_raster_sha256'),('expanded_original_crop','expanded_original_crop_sha256')]:
        path=BASE/kemper_review[field]
        if not path.exists() or sha(path.read_bytes())!=kemper_review[digest]:kemper_errors.append(field)
    kemper_rows=next(d for d in historic_direct if d['source_id']=='sos-2020-county-kemper')['peer_differences']
    check('2020_Kemper_original_literal_Lynville_frozen65_peer_Lynnville_exception',kemper_review['accepted_original_read']=='Lynville' and kemper_review['frozen65_peer_derivative_label']=='Lynnville' and len(kemper_rows)==3 and {(x['page'],x['column'],x['own_label'],x['peer_label']) for x in kemper_rows}=={(2,9,'Lynville','Lynnville')} and not kemper_errors,dict(original_header='Lynville',frozen65_peer_label='Lynnville',candidate_positions=3,errors=kemper_errors))
    amite_history=json.loads((OUT/'2020-native-amite-correction-history.json').read_text());amite_errors=[]
    for correction in amite_history['corrections']:
        if correction['initial_visual_read']==correction['accepted_visual_reread']:amite_errors.append(('unchanged',correction['source_page']))
        for field,digest in [('full_original_raster','full_original_raster_sha256'),('expanded_original_crop','expanded_original_crop_sha256')]:
            path=BASE/correction[field]
            if not path.exists() or sha(path.read_bytes())!=correction[digest]:amite_errors.append((field,correction['source_page']))
    check('2020_Amite_two_original_glyph_corrections_retained',len(amite_history['corrections'])==2 and not amite_errors,dict(corrections=amite_history['corrections'],errors=amite_errors))
    cp=json.loads((OUT/'canvass-peer-reconciliation.json').read_text());check('independent_canvass_panels_peer_agreement_with_Lincoln_clock_scope',cp.get('status')=='agree_numeric_clock_scope_qualified' and cp.get('checks')==390 and len(cp.get('accepted_source_clock_scope_differences',[]))==1 and not cp.get('unexpected_differences'),dict(status=cp.get('status'),comparison=cp))
    lincoln=json.loads((OUT/'2024-lincoln-original-panel-readings.json').read_text());lincoln_errors=[]
    if lincoln['source_raw_sha256']!=next(r['raw_sha256'] for r in receipts if r['id']=='sos-2024-county-lincoln'):lincoln_errors.append('original_pdf_hash')
    for page in lincoln['pages']:
        path=BASE/page['render_path']
        if not path.exists() or sha(path.read_bytes())!=page['render_sha256']:lincoln_errors.append(('render',page['page']))
    crop=BASE/lincoln['candidate_crop_path']
    if not crop.exists() or sha(crop.read_bytes())!=lincoln['candidate_crop_sha256']:lincoln_errors.append('original_candidate_crop')
    prior_pins=json.loads((OUT/'source/canvass-pre-lincoln-v1/pins.json').read_text())
    for label,pin in prior_pins.items():
        stored=(BASE/pin['path']).read_bytes();raw=gzip.decompress(stored)
        if len(stored)!=pin['stored_bytes'] or sha(stored)!=pin['stored_sha256'] or len(raw)!=pin['raw_bytes'] or sha(raw)!=pin['raw_sha256']:lincoln_errors.append(('prior_panel_pin',label))
    summaries=json.loads((OUT/'canvass-summary-readings.json').read_text())['sources'];statistics=json.loads((OUT/'canvass-statistics-readings.json').read_text())
    if len(summaries)!=15 or len(statistics)!=14 or len([s for s in summaries if s['source_id']=='sos-2024-county-lincoln'])!=1 or len([s for s in statistics if s['source_id']=='sos-2024-county-lincoln'])!=1:lincoln_errors.append('panel_coverage')
    if lincoln['summary'] not in summaries or lincoln['statistics'] not in statistics:lincoln_errors.append('original_panel_transcript_not_in_controls')
    summary_rows=[r for r in readcsv(OUT/'canvass-summary-controls.csv') if r['source_id']=='sos-2024-county-lincoln']
    if len(summary_rows)!=17:lincoln_errors.append(('flat_method_fields',len(summary_rows)))
    if lincoln['source_arithmetic']!={'senate_named':15679,'president_named':15802,'senate_generic':47,'president_generic':27,'both_printed_contest_totals':15898,'Senate_unallocated_after_named_and_generic':172,'president_unallocated_after_named_and_generic':69,'statistics_ballots_cast':15898,'statistics_ballots_minus_contest_total':0}:lincoln_errors.append('source_arithmetic')
    if lincoln['statistics']['registered_voters_total']!=0 or lincoln['statistics']['source_turnout_percent_literal']!='0.00%' or lincoln['statistics']['report_status_literal']!='Unofficial':lincoln_errors.append('printed_zero_registration_status')
    check('Lincoln_unofficial_primary_panels_ballot_generic_registration_and_unallocated_residuals',not lincoln_errors,dict(source='sos-2024-county-lincoln',summary_rows=len(summary_rows),registration_printed_zero_unusable=True,errors=lincoln_errors))
    lincoln_history=json.loads((OUT/'source/2024-lincoln-ballots-original-correction-v1/correction-history.json').read_text())
    history_errors=[]
    for name,pin in lincoln_history['frozen_initial_artifacts'].items():
        try:
            if 'stored_path' in pin:
                stored=(BASE/pin['stored_path']).read_bytes();raw=gzip.decompress(stored)
                if len(stored)!=pin['stored_bytes'] or sha(stored)!=pin['stored_sha256'] or len(raw)!=pin['raw_bytes'] or sha(raw)!=pin['raw_sha256']:history_errors.append((name,'lossless_pin'))
            else:
                raw=(BASE/pin['original_path']).read_bytes()
                if len(raw)!=pin['raw_bytes'] or sha(raw)!=pin['raw_sha256']:history_errors.append((name,'original_image_pin'))
        except Exception as exc:history_errors.append((name,str(exc)))
    frozen_first=json.loads(gzip.decompress((BASE/lincoln_history['frozen_initial_artifacts']['initial_reading']['stored_path']).read_bytes()))
    check('Lincoln_ballots_original_glyph_correction_lossless_prior_15909_to_15898',frozen_first['statistics']['ballots_cast_total']==15909 and frozen_first['source_arithmetic']['statistics_ballots_minus_contest_total']==11 and lincoln['statistics']['ballots_cast_total']==15898 and lincoln['source_arithmetic']['statistics_ballots_minus_contest_total']==0 and lincoln_history['correction']['initial_reading']==15909 and lincoln_history['correction']['direct_original_glyph_reading']==15898 and not history_errors,dict(original_page=9,initial=15909,corrected=15898,contest_total_unchanged=15898,history_errors=history_errors,qualification='Direct original enlarged glyph reread. No Senate/President votes changed or residual assigned.'))
    montgomery=json.loads((OUT/'2024-montgomery-original-statistics-reading.json').read_text());montgomery_errors=[]
    if montgomery['source_raw_sha256']!=next(r['raw_sha256'] for r in receipts if r['id']=='sos-2024-county-montgomery'):montgomery_errors.append('original_pdf_hash')
    for page in montgomery['source_pages']:
        path=BASE/page['render_path']
        if not path.exists() or sha(path.read_bytes())!=page['render_sha256']:montgomery_errors.append(('render',page['pdf_page']))
    prior=montgomery['prior_statistics_ledger_pin'];stored=(BASE/prior['path']).read_bytes();raw=gzip.decompress(stored)
    if len(stored)!=prior['stored_bytes'] or sha(stored)!=prior['stored_sha256'] or len(raw)!=prior['raw_bytes'] or sha(raw)!=prior['raw_sha256'] or len(json.loads(raw))!=13:montgomery_errors.append('prior_13_panel_pin')
    mstats=[s for s in statistics if s['source_id']=='sos-2024-county-montgomery']
    if len(mstats)!=1 or mstats[0]!=montgomery['statistics']:montgomery_errors.append('working_statistics_transcript')
    msummaries=[s for s in summaries if s['source_id']=='sos-2024-county-montgomery']
    if len(msummaries)!=1 or msummaries[0]['source_clock_literal']!='11/15/2024 10:25 AM':montgomery_errors.append('separate_summary_clock')
    ma=montgomery['source_arithmetic']
    check('Montgomery_original_statistics_885_incompatible_with_named_candidate_votes',not montgomery_errors and montgomery['statistics']['registered_voters_total']==6291 and montgomery['statistics']['ballots_cast_total']==885 and montgomery['statistics']['ballots_cast_blank']==1 and montgomery['statistics']['source_turnout_percent_literal']=='14.07%' and montgomery['statistics']['source_clock_literal']=='11/15/2024 10:24 AM' and ma['named_senate_votes']==4349 and ma['named_president_votes']==4424 and ma['senate_named_exceeds_statistics_ballots_by']==3464 and ma['president_named_exceeds_statistics_ballots_by']==3539 and ma['status']=='incompatible_source_panel_no_denominator_substitution',dict(source='sos-2024-county-montgomery',original_page=3,source_arithmetic=ma,errors=montgomery_errors,qualification='Printed stats preserved as incompatible source panel, not a candidate-ballot denominator or allocation.'))
    locator=json.loads((OUT/'2024-county-panel-locator-controls.json').read_text());stored=(BASE/locator['stored_path']).read_bytes();raw=gzip.decompress(stored);full_locator=json.loads(raw)
    locator_ok=(len(stored)==locator['stored_bytes'] and sha(stored)==locator['stored_sha256'] and len(raw)==locator['raw_bytes'] and sha(raw)==locator['raw_sha256'] and full_locator['source_views']==82 and full_locator['total_pdf_pages']==locator['total_pdf_pages']==803 and all(len(s['pages'])==s['page_count'] and [p['pdf_page'] for p in s['pages']]==list(range(1,s['page_count']+1)) for s in full_locator['sources']))
    check('all82_original_county_pdf_page_locator_hashes_and_scope',locator_ok,dict(source_views=82,pages=locator['total_pdf_pages'],qualification='OCR locator only; keyword absence does not establish source-field unavailability.'))
    availability=json.loads((OUT/'2024-field-availability.json').read_text());availability_errors=[]
    available_stored=(BASE/availability['fullpage_OCR_locator_stored_path']).read_bytes();available_raw=gzip.decompress(available_stored)
    if len(available_stored)!=availability['fullpage_OCR_locator_stored_bytes'] or sha(available_stored)!=availability['fullpage_OCR_locator_stored_sha256'] or len(available_raw)!=availability['fullpage_OCR_locator_raw_bytes'] or sha(available_raw)!=availability['fullpage_OCR_locator_raw_sha256']:availability_errors.append('allpage_locator_bytes')
    for field,digest in [('direct_original_summary_reading_path','direct_original_summary_reading_sha256'),('direct_original_statistics_reading_path','direct_original_statistics_reading_sha256'),('direct_original_E013_reading_path','direct_original_E013_reading_sha256')]:
        if sha((BASE/availability[field]).read_bytes())!=availability[digest]:availability_errors.append(field)
    preferred_availability=availability['preferred_sources'];available_ids=set()
    for rec in preferred_availability:
        sid=rec['source_id'];available_ids.add(sid)
        original=next((r for r in receipts if r['id']==sid),None)
        if original is None or original['raw_sha256']!=rec['source_raw_sha256'] or original['path']!=rec['source_original_path']:availability_errors.append((sid,'original_pdf'))
        if rec['field_availability_status']=='not_located_by_allpage_original_OCR_no_numeric_field_accepted' and (rec['direct_original_summary_page'] is not None or rec['direct_original_statistics_page'] is not None or rec['direct_original_E013_named_candidate_summary_page'] is not None):availability_errors.append((sid,'absence_with_panel'))
    if len(available_ids)!=82 or len(preferred_availability)!=82:availability_errors.append('preferred_identity_coverage')
    if len(availability['nonadditive_alternative_sources'])!=2 or {r['source_id'] for r in availability['nonadditive_alternative_sources']}!={'sos-2024-county-coahoma','sos-2024-county-pike'}:availability_errors.append('alternative_publication_scope')
    check('all82_preferred_original_method_ballot_registration_field_availability_source_scoped',availability['preferred_source_views']==82 and availability['preferred_source_pdf_pages_allpage_OCR_located']==803 and availability['preferred_direct_original_summary_panels']==14 and availability['preferred_direct_original_statistics_panels']==13 and availability['summary_panel_source_count_all_versions']==15 and availability['statistics_panel_source_count_all_versions']==14 and availability['separate_preferred_E013_candidate_only_summary_pages']==3 and sum(r['field_availability_status'].startswith('not_located') for r in preferred_availability)==66 and sum(r['field_availability_status']=='direct_original_E013_named_candidate_only' for r in preferred_availability)==2 and sum(r['direct_original_E013_named_candidate_summary_page'] is not None for r in preferred_availability)==3 and sum(r['statistics_registered_voters_field_printed'] for r in preferred_availability)==13 and sum(r['statistics_ballots_cast_field_printed'] for r in preferred_availability)==13 and sum(r['statistics_blank_field_printed'] for r in preferred_availability)==7 and sum(r['senate_generic_write_in_row_printed'] for r in preferred_availability)==13 and sum(r['senate_overvote_row_printed'] for r in preferred_availability)==3 and sum(r['senate_undervote_row_printed'] for r in preferred_availability)==3 and not availability_errors,dict(preferred_source_views=82,direct_original_summary_panels=14,direct_original_statistics_panels=13,E013_candidate_only_pages=3,other_source_views_with_no_reviewed_panel=66,errors=availability_errors,qualification='All-page OCR is only a locator; Grenada E-013 coexists with a reviewed standard panel, while Bolivar and Itawamba have E-013 only. Unreviewed fields are unavailable, not zero; Montgomery ballot scope is incompatible with candidate totals.'))
    native=json.loads(gzip.decompress((OUT/'native-constituents-reviewed.json.gz').read_bytes()));nativeerrors=[]
    for u in native:
        w,h=u['render_size']
        for b in [u['header_bounds']]+list(u['candidate_bounds'].values()):
            if not (0<=b[0]<b[2]<=w+2 and 0<=b[1]<b[3]<=h+2):nativeerrors.append(dict(key=u['key'],bounds=b))
        if not (BASE/u['evidence']).exists():nativeerrors.append(dict(key=u['key'],missing_evidence=u['evidence']))
        if u['role']=='unused_template_column' and any(v is not None for v in u['candidate_votes'].values()):nativeerrors.append(dict(key=u['key'],unused_not_null=True))
    check('reviewed_native_unique_keys_bounds_unused_and_evidence',len({u['key'] for u in native})==len(native) and not nativeerrors,dict(source_columns=len(native),errors=nativeerrors))
    nc=json.loads((OUT/'native-reviewed-controls.json').read_text());check('reviewed_native_source_candidate_balances',all(r['all_candidate_balances'] for r in nc['source_view_checks']),dict(source_views=nc['source_views'],native_constituents=nc['native_constituents'],qualification='Bounded reviewed scope only; not full-state gate'))
    orders=json.loads((OUT/'native-source-orders.json').read_text());preferred=orders['preferred82_view'];unit_order=preferred['full_descending_order'];crossing=preferred['minimum80'];source_tot=preferred['named_candidate_total']
    check('native_preferred82_complete_order_exact_integer80_and_Tunica_discrepancy',len(orders['source_views'])==84 and preferred['count']==1736 and len(unit_order)==1736 and source_tot==1215400 and preferred['candidate_sums']=={'Ty Pinkins':451980,'Roger F. Wicker':763420} and preferred['top15']['votes']==60019 and crossing==dict(count=887,votes=972656,preceding_count=886,preceding_votes=972157,crossing_key='28075:sos-2024-county-lauderdale:p9:c5',crossing_votes=499) and 5*crossing['preceding_votes']<4*source_tot<=5*crossing['votes'] and len({u['key'] for u in unit_order})==1736 and len({u['parent_county_fips'] for u in unit_order})==82 and sum(u['named_candidate_votes'] for u in unit_order)==source_tot and all(unit_order[i]['named_candidate_votes']>=unit_order[i+1]['named_candidate_votes'] for i in range(1735)) and orders['preferred_native_minus_primary']=={'Ty Pinkins':-1,'Roger F. Wicker':0},dict(source_native_total=source_tot,certified_county_total=state,minimum80=crossing,source_minus_primary=orders['preferred_native_minus_primary']))
    check('contract_dispatch_native_keys_allunit_order_parent_sensitivity_and_unassigned_case',contract['ordered_priority_keys']==[u['key'] for u in unit_order[:887]] and [u['key'] for u in contract['all_unit_order']]==[u['key'] for u in unit_order] and contract['priority_count']==887 and contract['remainder']['ordered_keys']==[u['key'] for u in unit_order[887:]] and contract['remainder']['votes']==242744 and len(contract['source_native_constituents'])==2321 and len(contract['source_native_unavailable_cases'])==1 and contract['source_native_unavailable_cases'][0]['parent_county_fips']=='28143' and contract['source_native_unavailable_cases'][0]['difference']==1 and sum(len(v) for v in contract['native_priority_by_parent'].values())==887,dict(dispatch_units=len(contract['all_unit_order']),retained_source_columns=len(contract['source_native_constituents']),priority_units=contract['priority_count'],unavailable_cases=contract['source_native_unavailable_cases']))
    ordercsv=readcsv(OUT/'native-source-order.csv')
    check('full_native_order_csv_1736_values_and_887_flags',len(ordercsv)==1736 and [r['key'] for r in ordercsv]==[u['key'] for u in unit_order] and [int(r['cumulative_votes']) for r in ordercsv]==[u['cumulative_votes'] for u in unit_order] and sum(int(r['Ty Pinkins'])+int(r['Roger F. Wicker']) for r in ordercsv)==1215400 and sum(r['priority_native80']=='True' for r in ordercsv)==887 and len({r['parent_county_fips'] for r in ordercsv if r['priority_native80']=='True'})==77,dict(rows=len(ordercsv),priority_count=887,priority_parent_count=77))
    metadata=json.loads((OUT/'native-84-working-metadata-differences.json').read_text());additions=metadata['literal_printed_ID_additions']
    check('frozen84_to_working_43_literal_printed_ID_additions_separate',metadata['frozen_84_ledger_sha256']=='bcc0237da3b31fda688c533b1d64eb994ddb9657f78f568973e4a1e5fcfea715' and metadata['compared_source_columns']==2321 and len(additions)==43 and not metadata['other_printed_ID_changes'] and all(x['frozen84_printed_ID'] is None and x['working_printed_ID'] in x['label_literal'] for x in additions),dict(additions=len(additions),source_ids=sorted({x['source_id'] for x in additions}),frozen84=metadata['frozen_84_ledger_sha256']))
    nf=json.loads((OUT/'native-allfield-peer-reconciliation.json').read_text());check('reviewed_fullfield_native_peer_scope',all(r['status']=='agree_all_fields_in_reviewed_scope' and not r['differences'] for r in nf['results']),nf['results'])
    nfc=json.loads((OUT/'native-allfield-controls.json').read_text());check('reviewed_all11_native_primary_controls',all(r['all11_candidates_reconcile'] and r['native_sums']==r['printed_TOTAL_values']==r['county_primary_controls'] for r in nfc['checks']),dict(source_views=nfc['source_views'],qualification='Bounded original-read complete-candidate scope only; statewide coverage still separate.'))
    nr=json.loads((OUT/'native-reviewed-peer-reconciliation-40views.json').read_text());check('independent_peer40_native_fields_labels_IDs_and_bounds',nr['status']=='agree_reviewed_native_Senate_scope' and nr['compared_candidate_positions']==2442 and not nr['differences'] and not nr['physical_target_bound_differences'] and not nr['printed_native_id_comparison'],dict(own_pin=nr['own_pin'],peer_pin=nr['peer_pin'],source_scope='Frozen40views; not complete statewide coverage'))
    n84=json.loads((OUT/'native-reviewed-peer-reconciliation-84views.json').read_text());check('independent_peer84_all4642_Senate_positions_with_explicit_box_ID_qualifications',n84['compared_candidate_positions']==4642 and not n84['differences'] and not n84['printed_native_id_value_differences'] and n84['accepted_reading_box_difference_count']==58 and all(d['source_id']=='sos-2024-county-itawamba' for d in n84['accepted_reading_box_differences']) and n84['blank_versus_null_ID_unit_count']==2075,dict(frozen_own=n84['own_frozen_ledger'],frozen_peer=n84['peer_csv'],box_differences=n84['accepted_reading_box_difference_count'],null_blank_ID_units=n84['blank_versus_null_ID_unit_count']))
    profiles=json.loads((OUT/'native-profile-controls.json').read_text());pc=contract['source_native_alternative_vendor_profiles'];check('two_complete_nonadditive_original_vendor_profile_views',profiles['source_views']==2 and profiles['profile_count']==45 and len(pc)==2 and sorted((v['source_id'],len(v['profiles'])) for v in pc)==[('sos-2024-county-pike',25),('sos-2024-county-union',20)] and len(readcsv(OUT/'native-profile-fields.csv'))==905 and all(x['all_printed_aggregate_controls_match'] and all(c['match'] is True for c in x['source_field_comparisons'] if c['county_panel_availability']=='reported') for x in profiles['checks']) and any(c['field']=='ballots_blank' and c['county_panel_availability']=='not_printed' for x in profiles['checks'] if x['source_id']=='sos-2024-county-pike' for c in x['source_field_comparisons']),dict(source_views=profiles['source_views'],profile_count=profiles['profile_count'],Pike_county_blank_scope='not_printed_in_county_statistics_but_1_in_profiles'))
    styles=json.loads((OUT/'2024-union-ballot-styles-original-reading.json').read_text());style_peer=json.loads((OUT/'2024-union-ballot-styles-peer-reconciliation.json').read_text());embedded=contract['source_native_nonadditive_ballot_style_report'];style_errors=[]
    if styles['source_raw_sha256']!=next(r['raw_sha256'] for r in receipts if r['id']=='sos-2024-county-union'):style_errors.append('original_source_hash')
    for page in styles['pages']:
        raster=BASE/page['render_path']
        if not raster.exists() or sha(raster.read_bytes())!=page['render_sha256']:style_errors.append(('raster',page['pdf_page']))
    style_parents={(r['pdf_page'],r['printed_precinct_code']):r for r in styles['parent_TOTAL_rows']};style_groups={}
    for row in styles['split_rows']:
        style_groups.setdefault((row['pdf_page'],row['printed_precinct_code']),[]).append(row)
    if len(style_parents)!=20 or len(styles['split_rows'])!=58 or len({r['key'] for r in styles['split_rows']+styles['parent_TOTAL_rows']})!=78:style_errors.append('source_row_coverage')
    for style_key,parent in style_parents.items():
        if sum(r['printed_total_voters'] for r in style_groups.get(style_key,[]))!=parent['printed_TOTAL_voters']:style_errors.append(('parent_total',style_key))
    if sum(r['printed_TOTAL_voters'] for r in style_parents.values())!=17058:style_errors.append('grand_total')
    if style_peer['status']!='agree_all_original_source_rows' or style_peer['differences'] or style_peer['own_sha256']!=sha((OUT/'2024-union-ballot-styles-original-reading.json').read_bytes()):style_errors.append('independent_peer')
    if embedded['source_raw_sha256']!=styles['source_raw_sha256'] or embedded['original_reading_sha256']!=sha((OUT/'2024-union-ballot-styles-original-reading.json').read_bytes()) or embedded['independent_peer_comparison_sha256']!=sha((OUT/'2024-union-ballot-styles-peer-reconciliation.json').read_bytes()) or len(embedded['split_rows'])!=58 or len(embedded['printed_parent_TOTAL_rows'])!=20:style_errors.append('working_contract_payload')
    if any(r['senate_candidate_votes'] is not None or r['presidential_candidate_votes'] is not None or r['additive_with_preferred_native'] for r in embedded['split_rows']):style_errors.append('false_candidate_assignment')
    check('Union_original_BP009_58_split_style_rows_20_parent_totals_nonadditive',not style_errors and embedded['printed_grand_total_voters']==17058 and embedded['separate_vendor_profile_registration']==17084 and contract['coverage']['nonadditive_source_native_ballot_style_split_rows']==58,dict(source='sos-2024-county-union',split_rows=58,parent_totals=20,printed_grand_total=17058,profile_registration_separate=17084,errors=style_errors,qualification='No candidate votes printed in split report; values are not allocated to native Senate cells or current geography.'))
    e013_path=OUT/'2024-extra-e013-original-summary-readings.json';e013=json.loads(e013_path.read_text());e013_contract=contract['source_native_nonadditive_E013_county_summaries'];e013_errors=[]
    if e013_contract['original_reading_sha256']!=sha(e013_path.read_bytes()) or e013_contract['county_aggregate_views']!=e013['sources']:e013_errors.append('working_contract_payload')
    county_lookup={r['county'].lower():r for r in rows}
    for page in e013['sources']:
        original=next((r for r in receipts if r['id']==page['source_id']),None)
        if original is None or original['raw_sha256']!=page['source_raw_sha256']:e013_errors.append((page['source_id'],'original_source_hash'))
        raster=BASE/page['original_render_path']
        if not raster.exists() or sha(raster.read_bytes())!=page['original_render_sha256']:e013_errors.append((page['source_id'],'original_render'))
        pres=[r['reported_votes'] for r in page['candidate_rows'] if r['office_literal']=='United States, President']
        senate=[r['reported_votes'] for r in page['candidate_rows'] if r['office_literal']=='United States, Senate']
        county=county_lookup[page['source_id'].removeprefix('sos-2024-county-')]
        if len(pres)!=9 or len(senate)!=2 or sum(pres)!=page['printed_president_TOTAL'] or sum(senate)!=page['printed_senate_TOTAL'] or sum(pres)!=int(county['2024_president_candidate_votes']) or senate!=[int(county['2024_senate_pinkins']),int(county['2024_senate_wicker'])]:e013_errors.append((page['source_id'],'candidate_totals'))
        if page['generic_write_in_available'] or page['ballots_cast_available'] or page['registered_voters_available'] or page['voting_method_available']:e013_errors.append((page['source_id'],'false_extra_field_availability'))
    check('three_original_E013_county_summaries_33_named_rows_nonadditive',e013['source_views']==3 and e013['named_candidate_rows']==33 and len(e013['sources'])==3 and contract['coverage']['nonadditive_E013_county_summary_views']==3 and not e013_errors,dict(source_views=3,named_candidate_rows=33,errors=e013_errors,qualification='County aggregate source pages agree named controls only; no native assignment, generic, ballot, registration or method data inferred.'))
    historical_ref=contract['historical_source_native_dependencies'];hist_path=OUT/historical_ref['path'];historical=json.loads(hist_path.read_text());historical_errors=[]
    if hist_path.stat().st_size!=historical_ref['bytes'] or sha(hist_path.read_bytes())!=historical_ref['sha256']:historical_errors.append('dependency_body_pin')
    for year in ('2020','2018'):
        dep=historical[year];snapshot_path=BASE/dep['canonical_snapshot_path'];snapshot_raw=snapshot_path.read_bytes();snapshot=json.loads(snapshot_raw)
        if len(snapshot_raw)!=dep['canonical_snapshot_bytes'] or sha(snapshot_raw)!=dep['canonical_snapshot_sha256']:historical_errors.append((year,'snapshot_pin'))
        frozen={}
        for pin in dep['canonical_lossless_component_pins']:
            stored=(BASE/pin['stored_path']).read_bytes();raw=gzip.decompress(stored)
            if len(stored)!=pin['stored_bytes'] or sha(stored)!=pin['stored_sha256'] or len(raw)!=pin['original_bytes'] or sha(raw)!=pin['original_sha256']:historical_errors.append((year,pin['stored_path'],'lossless_pin'))
            frozen[pin['original_path'].split('/')[-1]]=raw
        if len(frozen)!=len(snapshot['pins']):historical_errors.append((year,'component_count'))
        if year=='2020':
            old=json.loads(frozen['native-2020-additional-readings.json'])['sources']+json.loads(frozen['coahoma-2020-amendment-readings.json'])['sources']
            parts=dep['ordered_source_partitions']
            if len(parts['all104_in_coverage_index_order'])!=104 or len(parts['selected82_amended_where_explicit_in_index_order'])!=82 or len(parts['nonadditive_alternative22_in_index_order'])!=22 or set(parts['selected82_amended_where_explicit_in_index_order'])|set(parts['nonadditive_alternative22_in_index_order'])!={s['source_id'] for s in old}:historical_errors.append((year,'source_partitions'))
            if dep['full_flat_candidate_or_null_positions']!=8316 or len(list(csv.DictReader(io.StringIO(frozen['native-2020-additional-candidate-votes.csv'].decode()))))!=8184:historical_errors.append((year,'flat_candidate_scope'))
        else:
            old=json.loads(frozen['native-2018-original-readings.json'])['sources'];parts=dep['ordered_source_partitions']
            if len(parts['all164_in_original_ledger_order'])!=164 or parts['all164_in_original_ledger_order']!=[s['source_id'] for s in old] or len(parts['Nov6_special82_in_ledger_order'])!=82 or len(parts['Nov27_runoff82_in_ledger_order'])!=82:historical_errors.append((year,'source_partitions'))
            if dep['full_flat_candidate_or_null_positions']!=13662 or len(list(csv.DictReader(io.StringIO(frozen['native-2018-original-candidate-votes.csv'].decode()))))!=13662 or dep['literal_source_marks']!={'X':6}:historical_errors.append((year,'flat_candidate_scope_or_marks'))
        descriptors=dep['complete_source_objects_in_ledger_order']
        if len(descriptors)!=len(old):historical_errors.append((year,'source_object_count'))
        for obj,descriptor in zip(old,descriptors):
            digest=sha(json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode())
            if descriptor['source_id']!=obj['source_id'] or descriptor['source_raw_sha256']!=obj['raw_sha256'] or descriptor['complete_source_object_sha256']!=digest:historical_errors.append((year,obj['source_id'],'full_object_digest'))
        audit_path=BASE/dep['independent_worker_read_only_full_scope_audit_path']
        if sha(audit_path.read_bytes())!=dep['independent_worker_read_only_full_scope_audit_sha256']:historical_errors.append((year,'independent_audit_pin'))
    check('complete_2020_104_and_2018_164_historical_source_native_immutable_dependencies',not historical_errors and historical_ref['full_peer_source_objects_canonical'] and historical_ref['own_direct_original_native_replay_scope']=={'2020_publications':44,'2018_stage_views':43} and historical_ref['own_direct_original_native_replay_complete'] is False,dict(years=['2020','2018'],source_views={'2020':104,'2018':164},own_bounded_direct_replay={'2020':44,'2018':43},errors=historical_errors,qualification='Lossless immutable peer source objects are canonical dependencies; this worker’s direct original native replay remains bounded.'))
    pa=json.loads((OUT/'presidential-original-aid-controls.json').read_text());pv=json.loads((OUT/'presidential-unresolved-original-readings.json').read_text());pa_rows=readcsv(OUT/'presidential-original-aid-cells.csv')
    check('presidential_original_aid_provenance_and_open_row_errors',pa['source_views']==84 and pa['position_rows']==18980 and len(pa_rows)==18980 and len(pa['unresolved_native_positions'])==32 and pv['count']==922 and pv['numeric_readings']==890 and pv['row_target_mismatch_count']==32 and len(pa['manual_two_view_differences'])==15 and all((BASE/path).exists() and sha((BASE/path).read_bytes())==digest for path,digest in pv['atlas_sha256'].items()),dict(source_views=84,provisional_candidate_positions=18980,original_visual_cards=922,explicit_row_target_errors=32,qualification='OCR/atlas source-position evidence only; statewide nine-candidate native field acceptance remains open.'))
    bounded=json.loads((OUT/'direct-presidential-two-source-reconciliation.json').read_text());winston=json.loads((OUT/'winston-original-peer-reconciliation.json').read_text())
    direct_ledgers=[json.loads((OUT/f'{county}-presidential-original-readings.json').read_text()) for county in ['tunica','perry']]+[json.loads((OUT/'winston-allfield-original-readings.json').read_text())]
    receipt_hashes={r['id']:r['raw_sha256'] for r in receipts};direct_errors=[]
    for d in direct_ledgers:
        if d['source_raw_sha256']!=receipt_hashes[d['source_id']]:direct_errors.append((d['source_id'],'raw_hash'))
        if len({(r['source_page'],r['source_column'],r['candidate']) for r in d['rows']})!=len(d['rows']):direct_errors.append((d['source_id'],'duplicate_position'))
        for p in d['pages']:
            path=BASE/p['render_path']
            if not path.exists() or sha(path.read_bytes())!=p['render_sha256']:direct_errors.append((d['source_id'],p['page'],'render_hash'))
        for r in d['rows']:
            page=next(p for p in d['pages'] if p['page']==r['source_page']);w,h=page['render_size'];b=r.get('original_cell_bounds',r.get('source_cell_bounds'))
            if not (0<=b[0]<b[2]<=w and 0<=b[1]<b[3]<=h):direct_errors.append((d['source_id'],r['source_page'],r['source_column'],r['candidate'],'bounds'))
            if r['role']=='unused_template_column' and r['direct_original_visual_value'] is not None:direct_errors.append((d['source_id'],r['source_page'],r['source_column'],r['candidate'],'unused_value'))
        if not all(c['passes'] for c in d['candidate_checks'].values()):direct_errors.append((d['source_id'],'candidate_sum'))
    bounded_ok=len(bounded['sources'])==2 and sum(x['native_constituents'] for x in bounded['sources'])==28 and sum(x['candidate_positions'] for x in bounded['sources'])==270 and bounded['sources'][0]['peer_position_count']==117 and [(x['candidate'],x['source_to_CSV_difference']) for x in bounded['sources'][0]['source_to_CSV_disagreements']]==[('Kamala D. Harris',1)] and not bounded['sources'][1]['source_to_CSV_disagreements']
    winston_ok=winston['position_count']==242 and winston['numeric_positions']==143 and winston['unused_null_positions']==99 and winston['all_position_values_and_labels_match'] and len(winston['county_candidate_controls'])==11
    check('three_bounded_direct_original_allfield_sources_positions_controls_and_peer',not direct_errors and bounded_ok and winston_ok,dict(source_views=3,native_constituents=40,direct_positions=512,Tunica_Harris_CSV_minus_SEMS=1,Winston_peer_positions=242,errors=direct_errors,qualification='Bounded source views; statewide native presidential and method gates remain open.'))
    hinds=json.loads((OUT/'hinds-presidential-original-readings.json').read_text());small=json.loads((OUT/'small-presidential-original-readings.json').read_text());batch2=json.loads((OUT/'batch2-presidential-original-readings.json').read_text());batch3=json.loads((OUT/'batch3-presidential-original-readings.json').read_text());batch4=json.loads((OUT/'batch4-presidential-original-readings.json').read_text());batch5=json.loads((OUT/'batch5-presidential-original-readings.json').read_text());batch6=json.loads((OUT/'batch6-presidential-original-readings.json').read_text());batch7=json.loads((OUT/'batch7-presidential-original-readings.json').read_text());batch8=json.loads((OUT/'batch8-presidential-original-readings.json').read_text());batch9=json.loads((OUT/'batch9-presidential-original-readings.json').read_text());batch10=json.loads((OUT/'batch10-presidential-original-readings.json').read_text());batch11=json.loads((OUT/'batch11-presidential-original-readings.json').read_text());batch12=json.loads((OUT/'batch12-presidential-original-readings.json').read_text());batch13=json.loads((OUT/'batch13-presidential-original-readings.json').read_text());batch14=json.loads((OUT/'batch14-presidential-original-readings.json').read_text());batch15=json.loads((OUT/'batch15-presidential-original-readings.json').read_text());batch16=json.loads((OUT/'batch16-presidential-original-readings.json').read_text());batch17=json.loads((OUT/'batch17-presidential-original-readings.json').read_text());batch18=json.loads((OUT/'batch18-presidential-original-readings.json').read_text());batch19=json.loads((OUT/'batch19-presidential-original-readings.json').read_text());batch20=json.loads((OUT/'batch20-presidential-original-readings.json').read_text());batch21=json.loads((OUT/'batch21-presidential-original-readings.json').read_text())
    batch22=json.loads((OUT/'batch22-presidential-original-readings.json').read_text())
    batch23=json.loads((OUT/'batch23-presidential-original-readings.json').read_text())
    batch24=json.loads((OUT/'batch24-presidential-original-readings.json').read_text())
    batch25=json.loads((OUT/'batch25-presidential-original-readings.json').read_text())
    batch26=json.loads((OUT/'batch26-presidential-original-readings.json').read_text())
    batch27=json.loads((OUT/'batch27-presidential-original-readings.json').read_text())
    batch28=json.loads((OUT/'batch28-presidential-original-readings.json').read_text())
    final_batches=[json.loads((OUT/f'batch{n}-presidential-original-readings.json').read_text()) for n in range(29,34)]
    extra_errors=[]
    complete_original_sources=[hinds]+small['sources']+batch2['sources']+batch3['sources']+batch4['sources']+batch5['sources']+batch6['sources']+batch7['sources']+batch8['sources']+batch9['sources']+batch10['sources']+batch11['sources']+batch12['sources']+batch13['sources']+batch14['sources']+batch15['sources']+batch16['sources']+batch17['sources']+batch18['sources']+batch19['sources']+batch20['sources']+batch21['sources']+batch22['sources']+batch23['sources']+batch24['sources']+batch25['sources']+batch26['sources']+batch27['sources']+batch28['sources']+sum((x['sources'] for x in final_batches),[])
    for d in complete_original_sources:
        if d['source_raw_sha256']!=receipt_hashes[d['source_id']]:extra_errors.append((d['source_id'],'raw_hash'))
        if not all(x['passes'] for x in d['candidate_checks'].values()):extra_errors.append((d['source_id'],'candidate_sums'))
        if d.get('independent_peer_value_role_label_differences',d.get('independent_peer_position_differences')):extra_errors.append((d['source_id'],'peer_fields'))
        for p in d['pages']:
            path=BASE/p.get('render_path',p.get('full_original_raster'))
            if not path.exists() or sha(path.read_bytes())!=p.get('render_sha256',p.get('raster_sha256')):extra_errors.append((d['source_id'],p['source_page'],'original_render'))
    check('six_more_original_presidential_source_views_148_native_all9_controls_and_peer',hinds['source_position_rows']==990 and hinds['native_constituents']==108 and hinds['original_OCR_visual_correction_count']==8 and small['source_view_count']==5 and small['native_constituent_count']==40 and small['source_position_count']==594 and small['visual_correction_count']==20 and not extra_errors,dict(source_views=6,native_constituents=148,Hinds_positions=990,small_positions=594,errors=extra_errors,qualification='Bounded source views; original OCR polygons provisional, no whole-state acceptance.'))
    check('seven_batch2_original_presidential_views_96_native_all9_controls_and_peer',batch2['source_view_count']==7 and batch2['native_constituent_count']==96 and batch2['source_position_count']==1188 and batch2['visual_correction_count']==37 and len({x['source_id'] for x in batch2['sources']})==7 and not extra_errors,dict(source_views=7,native_constituents=96,positions=1188,visual_corrections=37,errors=extra_errors,qualification='Bounded source views; full-state native and method gates remain open.'))
    check('four_batch3_original_presidential_views_53_native_all9_controls_and_peer',batch3['source_view_count']==4 and batch3['native_constituent_count']==53 and batch3['source_position_count']==693 and batch3['visual_correction_count']==60 and len({x['source_id'] for x in batch3['sources']})==4 and not extra_errors,dict(source_views=4,native_constituents=53,positions=693,visual_corrections=60,errors=extra_errors,qualification='Bounded source views; full-state native and method gates remain open.'))
    check('eight_batch4_original_presidential_views_155_native_all9_controls_and_peer',batch4['source_view_count']==8 and batch4['native_constituent_count']==155 and batch4['source_position_count']==1683 and batch4['visual_correction_count']==36 and len({x['source_id'] for x in batch4['sources']})==8 and not extra_errors,dict(source_views=8,native_constituents=155,positions=1683,visual_corrections=36,errors=extra_errors,qualification='Bounded source views; full-state native and method gates remain open.'))
    check('four_batch5_original_presidential_views_63_native_all9_controls_and_peer',batch5['source_view_count']==4 and batch5['native_constituent_count']==63 and batch5['source_position_count']==792 and batch5['visual_correction_count']==21 and len({x['source_id'] for x in batch5['sources']})==4 and not extra_errors,dict(source_views=4,native_constituents=63,positions=792,visual_corrections=21,errors=extra_errors,qualification='Bounded source views; full-state native and method gates remain open.'))
    check('four_batch6_original_presidential_views_64_native_all9_controls_and_peer',batch6['source_view_count']==4 and batch6['native_constituent_count']==64 and batch6['source_position_count']==792 and batch6['visual_correction_count']==49 and len({x['source_id'] for x in batch6['sources']})==4 and not extra_errors,dict(source_views=4,native_constituents=64,positions=792,visual_corrections=49,errors=extra_errors,qualification='Bounded source views; full-state native and method gates remain open.'))
    check('four_batch7_original_presidential_views_176_native_all9_controls_and_peer',batch7['source_view_count']==4 and batch7['native_constituent_count']==176 and batch7['source_position_count']==1881 and batch7['visual_correction_count']==46 and len({x['source_id'] for x in batch7['sources']})==4 and not extra_errors,dict(source_views=4,native_constituents=176,positions=1881,visual_corrections=46,errors=extra_errors,qualification='Bounded source views; full-state native and method gates remain open.'))
    check('two_batch8_original_presidential_views_77_native_all9_controls_and_peer',batch8['source_view_count']==2 and batch8['native_constituent_count']==77 and batch8['source_position_count']==891 and batch8['visual_correction_count']==34 and len({x['source_id'] for x in batch8['sources']})==2 and not extra_errors,dict(source_views=2,native_constituents=77,positions=891,visual_corrections=34,errors=extra_errors,qualification='Bounded source views; full-state native and method gates remain open.'))
    check('three_batch9_original_presidential_views_54_native_all9_controls_and_peer',batch9['source_view_count']==3 and batch9['native_constituent_count']==54 and batch9['source_position_count']==594 and batch9['visual_correction_count']==56 and len({x['source_id'] for x in batch9['sources']})==3 and not extra_errors,dict(source_views=3,native_constituents=54,positions=594,visual_corrections=56,errors=extra_errors,qualification='Bounded source views; full-state native and method gates remain open.'))
    check('four_batch10_original_presidential_views_102_native_all9_controls_and_peer',batch10['source_view_count']==4 and batch10['native_constituent_count']==102 and batch10['source_position_count']==1188 and batch10['visual_correction_count']==20 and len({x['source_id'] for x in batch10['sources']})==4 and not extra_errors,dict(source_views=4,native_constituents=102,positions=1188,visual_corrections=20,errors=extra_errors,qualification='Bounded source views; full-state native and method gates remain open.'))
    check('three_batch11_original_presidential_views_67_native_all9_controls_and_peer',batch11['source_view_count']==3 and batch11['native_constituent_count']==67 and batch11['source_position_count']==792 and batch11['visual_correction_count']==17 and len({x['source_id'] for x in batch11['sources']})==3 and not extra_errors,dict(source_views=3,native_constituents=67,positions=792,visual_corrections=17,errors=extra_errors,qualification='Bounded source views; full-state native and method gates remain open.'))
    check('three_batch12_original_presidential_views_71_native_all9_controls_and_peer',batch12['source_view_count']==3 and batch12['native_constituent_count']==71 and batch12['source_position_count']==891 and batch12['visual_correction_count']==30 and len({x['source_id'] for x in batch12['sources']})==3 and not extra_errors,dict(source_views=3,native_constituents=71,positions=891,visual_corrections=30,errors=extra_errors,qualification='Bounded source views; full-state native and method gates remain open.'))
    check('three_batch13_original_presidential_views_71_native_all9_controls_and_peer',batch13['source_view_count']==3 and batch13['native_constituent_count']==71 and batch13['source_position_count']==891 and batch13['visual_correction_count']==38 and len({x['source_id'] for x in batch13['sources']})==3 and not extra_errors,dict(source_views=3,native_constituents=71,positions=891,visual_corrections=38,errors=extra_errors,qualification='Bounded source views; Pike Updated publication is distinct from Pike original; full-state native and method gates remain open.'))
    check('three_batch14_original_presidential_views_60_native_all9_controls_and_peer',batch14['source_view_count']==3 and batch14['native_constituent_count']==60 and batch14['source_position_count']==693 and batch14['visual_correction_count']==53 and len({x['source_id'] for x in batch14['sources']})==3 and not extra_errors,dict(source_views=3,native_constituents=60,positions=693,visual_corrections=53,errors=extra_errors,qualification='Bounded source views; full-state native and method gates remain open.'))
    check('one_batch15_Yazoo_original_presidential_view_23_native_all9_controls_and_peer',batch15['source_view_count']==1 and batch15['native_constituent_count']==23 and batch15['source_position_count']==297 and batch15['visual_correction_count']==23 and not extra_errors,dict(source_views=1,native_constituents=23,positions=297,visual_corrections=23,errors=extra_errors,qualification='Bounded source view; full-state native and method gates remain open.'))
    check('one_batch16_Lafayette_original_presidential_view_18_native_all9_controls_and_peer',batch16['source_view_count']==1 and batch16['native_constituent_count']==18 and batch16['source_position_count']==198 and batch16['visual_correction_count']==26 and not extra_errors,dict(source_views=1,native_constituents=18,positions=198,visual_corrections=26,errors=extra_errors,qualification='Bounded source view; full-state native and method gates remain open.'))
    check('one_batch17_Clarke_original_presidential_view_23_native_all9_controls_and_peer',batch17['source_view_count']==1 and batch17['native_constituent_count']==23 and batch17['source_position_count']==297 and batch17['visual_correction_count']==61 and not extra_errors,dict(source_views=1,native_constituents=23,positions=297,visual_corrections=61,errors=extra_errors,qualification='Bounded source view; full-state native and method gates remain open.'))
    check('one_batch18_Bolivar_original_presidential_view_30_native_all9_controls_and_peer',batch18['source_view_count']==1 and batch18['native_constituent_count']==30 and batch18['source_position_count']==297 and batch18['visual_correction_count']==23 and not extra_errors,dict(source_views=1,native_constituents=30,positions=297,visual_corrections=23,errors=extra_errors,qualification='Bounded source view; full-state native and method gates remain open.'))
    check('one_batch19_Lincoln_original_presidential_view_30_native_all9_controls_and_peer',batch19['source_view_count']==1 and batch19['native_constituent_count']==30 and batch19['source_position_count']==297 and batch19['visual_correction_count']==49 and not extra_errors,dict(source_views=1,native_constituents=30,positions=297,visual_corrections=49,errors=extra_errors,qualification='Bounded source view; full-state native and method gates remain open.'))
    check('one_batch20_Lauderdale_original_presidential_view_37_native_all9_controls_and_peer',batch20['source_view_count']==1 and batch20['native_constituent_count']==37 and batch20['source_position_count']==396 and batch20['visual_correction_count']==61 and not extra_errors,dict(source_views=1,native_constituents=37,positions=396,visual_corrections=61,errors=extra_errors,qualification='Bounded source view; full-state native and method gates remain open.'))
    check('one_batch21_Grenada_original_presidential_view_13_native_all9_controls_and_peer',batch21['source_view_count']==1 and batch21['native_constituent_count']==13 and batch21['source_position_count']==198 and batch21['visual_correction_count']==30 and not extra_errors,dict(source_views=1,native_constituents=13,positions=198,visual_corrections=30,errors=extra_errors,qualification='Original scanned page4 presidential aid raster full-size vs downsampled Senate/native geometry explicitly distinct; full-state native and method gates remain open.'))
    tip_index=json.loads((OUT/'batch22-presidential-original-review-index.json').read_text())['sources'][0]
    tip_missing=tip_index['original_aid_missing_positions']
    tip_rows=batch22['sources'][0]['rows']
    tip_direct=[x for x in tip_rows if x['original_reading_basis']=='direct_visual_full_original_page_missing_aid_position']
    check('one_batch22_Tippah_original_presidential_view_21_native_nine_missing_totals_and_peer',batch22['source_view_count']==1 and batch22['native_constituent_count']==21 and batch22['source_position_count']==198 and batch22['visual_correction_count']==13 and len(tip_missing)==9 and len(tip_direct)==9 and all(x['role']=='source_TOTAL' and x['original_aid_cell_bounds'] is None for x in tip_direct) and not extra_errors,dict(source_views=1,native_constituents=21,positions=198,aid_missing_printed_TOTALs=9,original_visual_readings=13,errors=extra_errors,qualification='Nine printed TOTALs read on original page4; no OCR-gap zero or residual fill. Full-state native and method gates remain open.'))
    lef=batch23['sources'][0]
    lef_rows=lef['rows']
    check('one_batch23_Leflore_complete_original_grid_18_native_and_peer',batch23['source_view_count']==1 and batch23['native_constituent_count']==18 and batch23['source_position_count']==198 and lef['original_OCR_visual_correction_count']==106 and lef['original_aid_missing_position_count']==18 and all(x['original_reading_basis'].startswith('direct_visual_') for x in lef_rows) and len([x for x in lef_rows if x['role']=='unused_template_column' and x['direct_original_value'] is None])==27 and not extra_errors,dict(source_views=1,native_constituents=18,positions=198,OCR_disagreements=106,aid_missing_positions=18,unused_nulls=27,errors=extra_errors,qualification='Every printed glyph read on full original PDFpages5–6, including Schlater c11 and 3 unused p6 columns; numeric aid polygons provisional. Full-state native and method gates remain open.'))
    web=batch24['sources'][0]
    web_rows=web['rows']
    check('one_batch24_Webster_complete_original_grid_14_native_no_OCR_aid_and_peer',batch24['source_view_count']==1 and batch24['native_constituent_count']==14 and batch24['source_position_count']==198 and web['original_aid_missing_position_count']==198 and all(x['original_reading_basis'].startswith('direct_visual_') and x['original_aid_cell_bounds'] is None for x in web_rows) and len([x for x in web_rows if x['role']=='unused_template_column' and x['direct_original_value'] is None])==63 and not extra_errors,dict(source_views=1,native_constituents=14,positions=198,aid_missing_positions=198,unused_nulls=63,errors=extra_errors,qualification='All nine printed vectors and unused blanks directly read from original PDFpages2–3; no OCR aid or peer values used for transcription. Full-state native and method gates remain open.'))
    jd=batch25['sources'][0]
    fr=batch26['sources'][0]
    check('two_batch25_26_Jeff_Davis_Franklin_complete_original_grids_31_native_peer',batch25['source_view_count']==batch26['source_view_count']==1 and batch25['native_constituent_count']==17 and batch26['native_constituent_count']==14 and batch25['source_position_count']==batch26['source_position_count']==198 and jd['original_OCR_visual_correction_count']==19 and jd['original_aid_missing_position_count']==30 and fr['original_OCR_visual_correction_count']==1 and fr['original_aid_missing_position_count']==99 and all(x['original_reading_basis'].startswith('direct_visual_') for x in jd['rows']+fr['rows']) and not extra_errors,dict(source_views=2,native_constituents=31,positions=396,Jeff_Davis_OCR_disagreements=19,Franklin_OCR_disagreements=1,Jeff_Davis_missing_aid=30,Franklin_missing_aid=99,errors=extra_errors,qualification='Both two-page original grids fully transcribed and source/peer checked; full-state native and method gates remain open.'))
    ho=batch27['sources'][0]
    ch=batch28['sources'][0]
    check('two_batch27_28_Holmes_Choctaw_complete_original_grids_28_native_peer',batch27['source_view_count']==batch28['source_view_count']==1 and batch27['native_constituent_count']==16 and batch28['native_constituent_count']==12 and batch27['source_position_count']==batch28['source_position_count']==198 and ho['original_OCR_visual_correction_count']==49 and ho['original_aid_missing_position_count']==99 and ch['original_OCR_visual_correction_count']==24 and ch['original_aid_missing_position_count']==143 and all(x['original_reading_basis'].startswith('direct_visual_') for x in ho['rows']+ch['rows']) and not extra_errors,dict(source_views=2,native_constituents=28,positions=396,Holmes_OCR_disagreements=49,Choctaw_OCR_disagreements=24,Holmes_missing_aid=99,Choctaw_missing_aid=143,errors=extra_errors,qualification='Both two-page original grids fully transcribed; Holmes A-Z source-wrap representation only folded for comparison, literal strings retained; full-state native and method gates remain open.'))
    final_expected=[('amite',22,297),('scott',23,297),('itawamba',28,297),('jackson',31,297),('kemper',14,297)]
    final_ok=all(b['source_view_count']==1 and b['native_constituent_count']==n and b['source_position_count']==positions and b['sources'][0]['source_id']=='sos-2024-county-'+slug and all(c['passes'] for c in b['sources'][0]['candidate_checks'].values()) and not b['sources'][0]['independent_peer_position_differences'] for b,(slug,n,positions) in zip(final_batches,final_expected))
    kemper=final_batches[-1]['sources'][0]
    kemper_parallel=[r for r in kemper['rows'] if r['role']=='parallel_native_observation']
    check('five_final_preferred_2024_original_presidential_views_118_native_and_Kemper_parallel',final_ok and len(kemper_parallel)==99 and all(r['source_page']==6 and isinstance(r['direct_original_value'],int) for r in kemper_parallel) and not extra_errors,dict(source_views=5,native_constituents=118,source_positions=1485,Kemper_nonadditive_parallel_positions=99,errors=extra_errors,qualification='Kemper PDF6 unofficial 11 columns retained nonadditively; PDF7–8 official14 native close source TOTAL. All five complete original grids post-read peer agree.'))
    original_ids={d['source_id'] for d in complete_original_sources}|{d['source_id'] for d in direct_ledgers}|{'sos-2024-county-alcorn','sos-2024-county-coahoma-updated'}
    preferred_ids={u['source_id'] for u in json.loads(gzip.decompress((OUT/'native-constituents-reviewed.json.gz').read_bytes())) if u['role']=='native_reporting_constituent'}-{'sos-2024-county-pike','sos-2024-county-coahoma'}
    check('all82_preferred_2024_presidential_native_original_source_coverage',len(original_ids)==len(preferred_ids)==82 and original_ids==preferred_ids and sum(d['native_constituents'] for d in complete_original_sources)+75==1736 and not extra_errors,dict(source_views=len(original_ids),native_constituents=1736,source_ids_missing=sorted(preferred_ids-original_ids),source_ids_unexpected=sorted(original_ids-preferred_ids),qualification='Alcorn and Coahoma Updated all11 original ledgers and Tunica/Perry/Winston separate direct original ledgers complete this 82-view coverage. Old Pike/Coahoma are nonadditive alternatives; historical and broad method gates remain open.'))
    conflicts=[];f1={r['fips']:int(r['value']) for r in part if r['year']=='2024' and r['field']=='F1a'}
    for r in rows:
        if int(r['2024_senate_candidate_votes'])>f1[r['fips']]:conflicts.append(dict(county=r['county'],senate=int(r['2024_senate_candidate_votes']),eac_F1a=f1[r['fips']]))
    check('ballot_survey_disagreements_preserved',len(conflicts)==8,conflicts)
    peerpath=BASE/'data/baselines/candidate-votes.csv';peer=[];diff=[]
    if peerpath.exists():
        peerall=readcsv(peerpath);peer=[r for r in peerall if r['election_date'] in ['2024-11-05','2020-11-03']];our={key(r):r for r in c};assert len(our)==len(c)
        for r in peer:
            k=key(r)
            if k not in our or int(r['votes'])!=int(our[k]['votes']) or r['fips']!=our[k]['fips']:diff.append(dict(key=k,peer=r.get('votes'),own=our.get(k,{}).get('votes')))
        peercontract=json.loads((BASE/'data/baselines/county-contract.json').read_text());order=[r['fips'] for r in rows]
        check('independent_peer_shared_county_candidate_fields',len(peer)==1148 and not diff,dict(compared_rows=len(peer),peer_total_rows=len(peerall),other_stage_scope='2018 November6/November27 fields independently checked in historical-county-peer-reconciliation.json; not silently dropped from state arithmetic',differences=diff,peer_csv_sha256=sha(peerpath.read_bytes())))
        check('independent_peer_all82_order_minimum80',order==peercontract['ordered_keys'] and county_sensitivity['ordered_priority_keys']==peercontract['ordered_priority_keys'] and peercontract['minimum80_count']==41,dict(peer_contract_sha256=sha((BASE/'data/baselines/county-contract.json').read_bytes())))
    else:check('independent_peer_shared_county_candidate_fields',False,'No independent peer artifact yet')
    link_errors=[]
    for p in [BASE/'turnout.md',OUT/'source/SCHEMA.md']:
        if not p.exists():link_errors.append(str(p.relative_to(BASE)));continue
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if target.startswith(('http:','https:','#')):continue
            if not (p.parent/target.split('#')[0]).exists():link_errors.append(dict(file=str(p.relative_to(BASE)),target=target))
    check('all_report_and_schema_relative_links',not link_errors,link_errors)
    oversized=[str(p.relative_to(BASE)) for p in OUT.rglob('*') if p.is_file() and p.stat().st_size>=40_000_000]
    check('all_owned_assets_strictly_under40M',not oversized,oversized)
    named_audit=json.loads((OUT/'2024-named-contract-coverage-audit.json').read_text())
    named_errors=[]
    for sid,pin in named_audit['all11_original_source_reading_pins'].items():
        path=OUT/pin['path']
        if not path.exists() or sha(path.read_bytes())!=pin['sha256']:named_errors.append((sid,'original_reading_pin'))
    if sha((OUT/'priority-set.json').read_bytes())!=named_audit['priority_contract_sha256']:named_errors.append('working_priority_contract_pin')
    if sha((OUT/'native-reviewed-peer-reconciliation-84views.json').read_bytes())!=named_audit['senate_peer_reconciliation_sha256']:named_errors.append('independent_Senate_peer_pin')
    if sha((OUT/'native-allfield-peer-reconciliation.json').read_bytes())!=named_audit['two_view_allfield_peer_reconciliation_sha256']:named_errors.append('independent_two_view_allfield_peer_pin')
    dependency=contract.get('preferred_2024_all11_source_fields_dependency',{})
    dep_path=BASE/dependency.get('path','data/turnout/source/2024-preferred-all11-source-fields-v1.json.gz')
    if not dep_path.exists():
        named_errors.append('missing_all11_source_field_dependency')
    else:
        stored=dep_path.read_bytes()
        if sha(stored)!=dependency.get('stored_sha256') or len(stored)!=dependency.get('stored_bytes'):
            named_errors.append('all11_source_field_stored_pin')
        raw=gzip.decompress(stored)
        if sha(raw)!=dependency.get('raw_sha256') or len(raw)!=dependency.get('raw_bytes'):
            named_errors.append('all11_source_field_raw_pin')
        dep=json.loads(raw)
        cols=dep['columns']
        preferred_contract=[u for u in contract['source_native_constituents'] if u['source_id'] not in ('sos-2024-county-coahoma','sos-2024-county-pike')]
        dep_errors=[]
        if len(cols)!=len(preferred_contract)!=2266 or len(dep['original_reading_pins'])!=82:
            dep_errors.append('coverage')
        if len({c['key'] for c in cols})!=len(cols):dep_errors.append('duplicate_source_key')
        for col,u in zip(cols,preferred_contract):
            if (col['key']!=u['key'] or col['source_raw_sha256']!=u['source_raw_sha256'] or
                col['source_page']!=u['source_page'] or col['source_column']!=u['source_column'] or
                col['role']!=u['role'] or col['label_literal']!=u['label_literal'] or
                col['Senate_candidate_votes']!=u['candidate_votes'] or
                col['president_candidate_votes']!=u.get('separately_scoped_contests',{}).get('2024-president',{}).get('candidate_votes')):
                dep_errors.append(col['key'])
        for sid,pin in dep['original_reading_pins'].items():
            original=BASE/pin['path']
            if not original.exists() or sha(original.read_bytes())!=pin['sha256']:
                dep_errors.append((sid,'original_reading_pin'))
        if (dep['source_views']!=82 or dep['source_columns']!=2266 or dep['native_constituents']!=1736 or
            dep['Senate_candidate_fields']!=4532 or dep['presidential_candidate_fields']!=20394 or
            dep['explicit_unprinted_template_positions_absent_from_two_older_direct_ledgers']!=126 or
            dep['presidential_native_named_vote_sum']!=1228007 or not all(c['all_nine_native_sums_equal_printed_TOTAL_and_original_control'] for c in dep['source_checks'])):
            dep_errors.append('source_controls')
        if dep_errors:named_errors.append(dict(all11_source_field_dependency=dep_errors))
    if named_audit.get('preferred_all11_dependency')!=dependency:named_errors.append('all11_dependency_audit_mismatch')
    from attach_complete_peer_v2 import attach as verify_complete_peer_v2
    peer_v2_verification=verify_complete_peer_v2(json.loads(json.dumps(contract)))
    check('independent_complete_peer_v2_order_all11_fields_and_printed_field_pins',
          peer_v2_verification['peer_agreement']['complete_independent_native_priority_v2']==
          contract['peer_agreement'].get('complete_independent_native_priority_v2'),
          dict(source_columns=2266,native_constituents=1736,priority_native_constituents=887,
               all11_candidate_or_null_positions=24926,peer_source_or_role_vote_differences=0,
               qualification='Read-only frozen independent V2; 165 line-wrap label representations, including two hyphen wraps, remain literal variants. No coordinator or 2026 geographic acceptance.'))
    peer_agreement=contract.get('peer_agreement',{})
    peer_snapshot_path=BASE/peer_agreement.get('complete_preferred82_all11_peer_snapshot_path','data/baselines/source/2024-all11-complete-peer-v1/snapshot.json')
    peer_proof_path=BASE/peer_agreement.get('complete_preferred82_all11_peer_reconciliation_path','data/baselines/source/2024-all11-complete-peer-v1/reconciliation.json')
    if not peer_snapshot_path.exists() or not peer_proof_path.exists():
        named_errors.append('complete_all11_peer_witness_missing')
    else:
        peer_snapshot_raw=peer_snapshot_path.read_bytes();peer_proof_raw=peer_proof_path.read_bytes()
        if sha(peer_snapshot_raw)!=peer_agreement.get('complete_preferred82_all11_peer_snapshot_sha256') or sha(peer_proof_raw)!=peer_agreement.get('complete_preferred82_all11_peer_reconciliation_sha256'):
            named_errors.append('complete_all11_peer_witness_pin')
        peer_snapshot=json.loads(peer_snapshot_raw);peer_proof=json.loads(peer_proof_raw)
        peer_pin=peer_snapshot['peer_body'];stored=(BASE/peer_pin['path']).read_bytes();raw=gzip.decompress(stored)
        if (peer_pin!=peer_agreement.get('complete_preferred82_all11_peer_body_exact_pin') or
            len(stored)!=peer_pin['stored_bytes'] or sha(stored)!=peer_pin['stored_sha256'] or
            len(raw)!=peer_pin['original_bytes'] or sha(raw)!=peer_pin['original_sha256'] or
            peer_proof['status']!='pass_post_original_complete_preferred82_all11_source_position_replay' or
            peer_proof['positions']!=24926 or peer_proof['source_columns']!=2266 or
            peer_proof['native_units']!=1736 or peer_proof['value_role_differences'] or
            len(peer_proof['literal_label_representation_aliases'])!=22):
            named_errors.append('complete_all11_peer_witness_content')
    check('working_priority_contract_2024_all11_named_source_coverage_currently_accurate',named_audit['preferred_source_views']==82 and named_audit['preferred_native_constituents']==1736 and len(named_audit['all11_original_source_reading_pins'])==82 and contract['coverage']['reviewed_all11_candidate_source_views']==82 and contract['coverage']['complete_preferred82_original_named_candidate_fields_2024_Senate_and_president'] is True and contract['peer_agreement']['native_fields_complete'] is False and contract['current_2026_geographic_approval'] is False and not named_errors,dict(preferred_source_views=82,native_constituents=1736,errors=named_errors,qualification='2024 preferred named candidate source field coverage only; generic/method/historical/current identity and coordinator acceptance remain outside this check.'))
    check('all82_preferred_2024_named_native_fields_and_complete_peer_gate',
          contract['coverage']['complete_preferred82_original_named_candidate_fields_2024_Senate_and_president'] is True and
          peer_agreement.get('named_2024_Senate_and_president_source_fields_complete') is True and
          peer_agreement.get('complete_preferred82_all11_source_positions')==24926 and not named_errors,
          dict(native_constituents=1736,all11_candidate_or_null_positions=24926,
               qualification='Complete named Senate/presidential original field and peer agreement only; generic, method, ballot, registration and current identity stay source-scoped.'))
    check('unavailable_broad_native_fields_and_current_geometry_explicitly_qualified',
          peer_agreement.get('native_fields_complete') is False and
          contract['coverage'].get('native_unit_extraction')=='complete_2024_preferred_named_candidates_other_fields_in_progress' and
          contract['current_2026_geographic_approval'] is False and
          historical_ref['own_direct_original_native_replay_complete'] is False,
          dict(broad_native_fields_complete=False,current_2026_geographic_approval=False,
               own_historical_native_direct_replay_complete=False))
    result=dict(status='pass_offline_qa_qualified_pending_coordinator_acceptance' if not errors else 'failed_offline_qa',checks=checks,failed_or_pending_checks=errors,verified_sources=verified,scope='All named 2024 priority candidate fields and full historical canonical dependencies checked. Ballot/registration/method are source-scoped; no current-geographic or coordinator acceptance; no source discrepancy repair.')
    savejson(OUT/'validation.json',result)
    from build_asset_manifest import main as build_manifest
    build_manifest()
    print(json.dumps(dict(status=result['status'],checks=len(checks),failed_or_pending_checks=errors)))
if __name__=='__main__':main()
