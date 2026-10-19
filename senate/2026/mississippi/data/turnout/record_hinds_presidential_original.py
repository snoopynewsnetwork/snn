"""Independent Hinds nine-candidate source columns from original PDF pixels.

The original-pixel OCR aid precedes any peer comparison. Eight exception cells
below were reread directly from full original pages2,3,11; the peer's votes are
never extraction inputs. Source OCR crop boxes remain provisional locators.
"""
import csv,gzip,json
from acquire_sources import BASE,OUT,receipts,sha,savejson

SID='sos-2024-county-hinds'
NAMES=['Kamala D. Harris','Chase Oliver','Jill Stein','Randall Terry','Donald J. Trump','Shiva Ayyadurai','Claudia De la Cruz','Robert F. Kennedy Jr.','Peter Sonski']
MANUAL={(2,5,'Claudia De la Cruz'):1,(2,5,'Peter Sonski'):1,(2,6,'Jill Stein'):1,(3,2,'Kamala D. Harris'):709,(3,4,'Kamala D. Harris'):336,(3,4,'Peter Sonski'):0,(11,2,'Peter Sonski'):1,(11,5,'Peter Sonski'):1}
def main():
    r=next(x for x in receipts if x['id']==SID)
    original=gzip.decompress((BASE/r['path']).read_bytes());assert sha(original)==r['raw_sha256']
    review=json.loads((OUT/'hinds-presidential-original-review-index.json').read_text());assert review['source_raw_sha256']==r['raw_sha256']
    assert len(review['pages'])==10 and all(sha((BASE/p['render_path']).read_bytes())==p['render_sha256'] for p in review['pages'])
    assert len(review['cards'])==8 and {(x['source_page'],x['source_column'],x['candidate']) for x in review['cards']}==set(MANUAL)
    for x in review['cards']:assert sha((BASE/x['card_path']).read_bytes())==x['card_sha256']
    aidpath=OUT/'presidential-original-aid-cells.csv'
    aid=[x for x in csv.DictReader(aidpath.open()) if x['source_id']==SID]
    assert len(aid)==990 and len({(int(x['source_page']),int(x['source_column']),x['candidate']) for x in aid})==990
    native=json.loads(gzip.decompress((OUT/'native-constituents-reviewed.json.gz').read_bytes()))
    units={x['key']:x for x in native if x['source_id']==SID}
    assert len(units)==110
    rows=[]
    for x in aid:
        page=int(x['source_page']);col=int(x['source_column']);name=x['candidate'];key=(page,col,name)
        unit=units[x['source_native_key']];assert unit['role']==x['role'] and unit['source_raw_sha256']==r['raw_sha256']
        if x['role']=='unused_template_column':value=None;basis='unprinted_unused_template_position_not_numeric_zero'
        elif key in MANUAL:value=MANUAL[key];basis='direct_visual_full_original_page_after_OCR_error'
        else:
            assert x['compiled_provisional_value'].isdigit(),key
            value=int(x['compiled_provisional_value']);basis=x['compiled_basis'].replace('_unaccepted','_source_read_pending_reciprocal')
        rows.append(dict(source_id=SID,source_raw_sha256=r['raw_sha256'],source_page=page,source_column=col,source_native_key=x['source_native_key'],role=x['role'],label_literal=unit['label_literal'],printed_native_id=unit['printed_native_id'],source_header_bounds=unit['header_bounds'],candidate=name,direct_original_value=value,original_reading_basis=basis,provisional_original_OCR_value=int(x['compiled_provisional_value']) if x['compiled_provisional_value'].isdigit() else None,original_aid_cell_bounds=json.loads(x['original_cell_bounds']),original_aid_bounds_status='provisional_OCR_target_not_accepted_numeric_polygon',original_full_page_raster=next(p['render_path'] for p in review['pages'] if p['source_page']==page)))
    checks={}
    csvvotes={x['candidate_literal'].split(' for President')[0].removeprefix('Presidential Electors for '):int(x['votes']) for x in csv.DictReader((OUT/'candidate-votes.csv').open()) if x['county']=='Hinds' and x['election_date']=='2024-11-05' and x['office_literal'].strip()=='United States-President'}
    for name in NAMES:
        rr=[x for x in rows if x['candidate']==name];native_sum=sum(x['direct_original_value'] for x in rr if x['role']=='native_reporting_constituent');tot=[x['direct_original_value'] for x in rr if x['role']=='source_TOTAL'];assert len(tot)==1
        checks[name]=dict(native_sum=native_sum,printed_TOTAL=tot[0],official_county_CSV=csvvotes[name],passes=native_sum==tot[0]==csvvotes[name])
    assert all(x['passes'] for x in checks.values())
    peerpath=BASE/'data/baselines/native-allfield-additional-candidate-votes.csv';peer={(int(x['source_page']),int(x['source_column']),x['candidate']):x for x in csv.DictReader(peerpath.open()) if x['source_id']==SID and x['candidate'] in NAMES}
    assert len(peer)==990
    diffs=[]
    for x in rows:
        p=peer[x['source_page'],x['source_column'],x['candidate']]
        peer_role='source_native_reporting_constituent' if x['role']=='native_reporting_constituent' else x['role']
        if (str(x['direct_original_value']) if x['direct_original_value'] is not None else '')!=p['value'] or peer_role!=p['role'] or x['label_literal']!=p['literal_native_label']:
            diffs.append(dict(source_page=x['source_page'],source_column=x['source_column'],candidate=x['candidate'],own=x['direct_original_value'],peer=p['value'],own_role=x['role'],peer_role=p['role'],own_label=x['label_literal'],peer_label=p['literal_native_label']))
    assert not diffs,diffs[:10]
    output=dict(scope='Complete Hinds PDF pages2–11 nine presidential candidate rows from independent original-pixel OCR plus eight direct full-original visual corrections; source TOTAL and unused positions separate. All values compared to peer only after own original extraction. Original aid crop boxes remain provisional, and c11 on final page is an unprinted template slot.',source_id=SID,source_raw_sha256=r['raw_sha256'],source_original_path=r['path'],source_original_bytes=len(original),source_page_count=31,source_position_rows=990,native_constituents=108,source_TOTAL_columns=1,unprinted_unused_template_columns=1,original_OCR_visual_correction_count=len(MANUAL),candidate_checks=checks,original_aid_sha256=sha(aidpath.read_bytes()),independent_peer_file_sha256=sha(peerpath.read_bytes()),independent_peer_value_role_label_differences=diffs,review_index_sha256=sha((OUT/'hinds-presidential-original-review-index.json').read_bytes()),pages=review['pages'],rows=rows)
    savejson(OUT/'hinds-presidential-original-readings.json',output)
    with (OUT/'hinds-presidential-original-cells.csv').open('w',newline='') as f:
        fields=['source_id','source_raw_sha256','source_page','source_column','source_native_key','role','label_literal','printed_native_id','candidate','direct_original_value','original_reading_basis','provisional_original_OCR_value','original_aid_bounds_status','original_full_page_raster']
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:x[k] for k in fields} for x in rows)
    print('Hinds original presidential',len(rows),'positions',sum(x['role']=='native_reporting_constituent' for x in rows),'native candidate cells',len(MANUAL),'direct visual corrections; all9 sums/peer positions match')
if __name__=='__main__':main()
