"""Five small complete original-PDF presidential source views, independently read.

The original-pixel provisional aid predates peer use. Twenty OCR disagreements
are transcribed below from full original PDF pages shown in original-only QA.
Peer values are consulted only after the resulting source ledger is built.
"""
import csv,gzip,json
from acquire_sources import BASE,OUT,receipts,sha,savejson
NAMES=['Kamala D. Harris','Chase Oliver','Jill Stein','Randall Terry','Donald J. Trump','Shiva Ayyadurai','Claudia De la Cruz','Robert F. Kennedy Jr.','Peter Sonski']
def label_ws(x):return ' '.join(x.split())
MANUAL={
 'benton':{(2,2,'Robert F. Kennedy Jr.'):1},
 'greene':{(2,1,'Kamala D. Harris'):90,(2,3,'Kamala D. Harris'):275,(3,1,'Kamala D. Harris'):138,(3,3,'Kamala D. Harris'):835},
 'wilkinson':{(2,2,'Jill Stein'):1,(2,9,'Kamala D. Harris'):0,(2,10,'Peter Sonski'):0,(2,10,'Shiva Ayyadurai'):1},
 'noxubee':{(2,1,'Claudia De la Cruz'):0,(2,1,'Kamala D. Harris'):621,(2,4,'Chase Oliver'):2,(2,7,'Kamala D. Harris'):454,(2,8,'Kamala D. Harris'):29},
 'issaquena':{(1,1,'Kamala D. Harris'):13,(1,3,'Randall Terry'):1,(1,4,'Donald J. Trump'):58,(1,5,'Kamala D. Harris'):41,(1,6,'Donald J. Trump'):296,(1,6,'Shiva Ayyadurai'):5},
}
def build(manual_by_slug=MANUAL,tag='small',expected_native=40,expected_positions=594,expected_visual=20):
    reviewpath=OUT/f'{tag}-presidential-original-review-index.json';review=json.loads(reviewpath.read_text())
    aidpath=OUT/'presidential-original-aid-cells.csv';aid=list(csv.DictReader(aidpath.open()))
    nativelist=json.loads(gzip.decompress((OUT/'native-constituents-reviewed.json.gz').read_bytes()))
    native={x['key']:x for x in nativelist}
    c=list(csv.DictReader((OUT/'candidate-votes.csv').open()))
    peerpath=BASE/'data/baselines/native-allfield-additional-candidate-votes.csv'
    peer={(x['source_id'],int(x['source_page']),int(x['source_column']),x['candidate']):x for x in csv.DictReader(peerpath.open()) if x['candidate'] in NAMES}
    rr={x['id']:x for x in receipts};sources=[];flat=[]
    for slug,manual in manual_by_slug.items():
        sid='sos-2024-county-'+slug;r=rr[sid];rview=next(x for x in review['sources'] if x['source_id']==sid)
        raw=gzip.decompress((BASE/r['path']).read_bytes());assert sha(raw)==r['raw_sha256']==rview['source_raw_sha256']
        for p in rview['pages']:assert sha((BASE/p['full_original_raster']).read_bytes())==p['raster_sha256']
        for x in rview['cards']:assert sha((BASE/x['original_card']).read_bytes())==x['card_sha256']
        card_keys={(x['source_page'],x['source_column'],x['candidate']) for x in rview['cards']}
        missing_keys={(x['source_page'],x['source_column'],x['candidate']) for x in rview.get('original_aid_missing_positions',[])}
        assert len(manual)==len(card_keys|missing_keys) and set(manual)==card_keys|missing_keys
        rows=[]
        for x in (z for z in aid if z['source_id']==sid):
            n=int(x['source_page']);col=int(x['source_column']);name=x['candidate'];k=(n,col,name);u=native[x['source_native_key']]
            assert u['role']==x['role'] and u['source_raw_sha256']==r['raw_sha256']
            if x['role']=='unused_template_column':value=None;basis='unprinted_unused_template_position_not_numeric_zero'
            elif k in manual:value=manual[k];basis='direct_visual_full_original_page_after_OCR_error'
            else:
                assert x['compiled_provisional_value'].isdigit(),(sid,k)
                value=int(x['compiled_provisional_value']);basis=x['compiled_basis'].replace('_unaccepted','_source_read_pending_reciprocal')
            rows.append(dict(source_id=sid,source_raw_sha256=r['raw_sha256'],source_page=n,source_column=col,source_native_key=x['source_native_key'],role=x['role'],label_literal=u['label_literal'],printed_native_id=u['printed_native_id'],source_header_bounds=u['header_bounds'],candidate=name,direct_original_value=value,original_reading_basis=basis,provisional_original_OCR_value=int(x['compiled_provisional_value']) if x['compiled_provisional_value'].isdigit() else None,original_aid_cell_bounds=json.loads(x['original_cell_bounds']),original_aid_bounds_status='provisional_OCR_target_not_accepted_numeric_polygon',original_full_page_raster=next(p['full_original_raster'] for p in rview['pages'] if p['source_page']==n)))
        # A missing machine aid is not a zero or a fitted residual. These
        # printed positions were read directly on the retained whole PDF page.
        for n,col,name in sorted(missing_keys):
            matches=[u for u in nativelist if u['source_id']==sid and u['source_page']==n and u['source_column']==col]
            assert len(matches)==1,(sid,n,col,name)
            u=matches[0];value=manual[n,col,name]
            assert (u['role']=='unused_template_column' and value is None) or (u['role'] in ('source_TOTAL','native_reporting_constituent') and isinstance(value,int)),(sid,n,col,name,u['role'],value)
            basis='direct_visual_full_original_page_missing_aid_position' if value is not None else 'direct_visual_full_original_page_unprinted_unused_position'
            rows.append(dict(source_id=sid,source_raw_sha256=r['raw_sha256'],source_page=n,source_column=col,source_native_key=u['key'],role=u['role'],label_literal=u['label_literal'],printed_native_id=u['printed_native_id'],source_header_bounds=u['header_bounds'],candidate=name,direct_original_value=value,original_reading_basis=basis,provisional_original_OCR_value=None,original_aid_cell_bounds=None,original_aid_bounds_status='no_original_aid_crop_full_page_direct_read',original_full_page_raster=next(p['full_original_raster'] for p in rview['pages'] if p['source_page']==n)))
        assert len(rows)==rview['position_count']+len(missing_keys) and len({(x['source_page'],x['source_column'],x['candidate']) for x in rows})==len(rows)
        csv_county_name={'pearl-river':'Pearl River','pike-updated':'Pike'}.get(slug,slug)
        csvvotes={x['candidate_literal'].split(' for President')[0].removeprefix('Presidential Electors for '):int(x['votes']) for x in c if x['county'].lower()==csv_county_name.lower() and x['election_date']=='2024-11-05' and x['office_literal'].strip()=='United States-President'}
        checks={}
        for name in NAMES:
            selected=[x for x in rows if x['candidate']==name];v=sum(x['direct_original_value'] for x in selected if x['role']=='native_reporting_constituent');t=[x['direct_original_value'] for x in selected if x['role']=='source_TOTAL'];assert len(t)==1
            checks[name]=dict(native_sum=v,printed_TOTAL=t[0],county_CSV=csvvotes[name],passes=v==t[0]==csvvotes[name])
        assert all(x['passes'] for x in checks.values()),(slug,checks)
        differences=[]
        for x in rows:
            p=peer[sid,x['source_page'],x['source_column'],x['candidate']]
            peer_role='source_native_reporting_constituent' if x['role']=='native_reporting_constituent' else x['role']
            if (str(x['direct_original_value']) if x['direct_original_value'] is not None else '')!=p['value'] or peer_role!=p['role'] or label_ws(x['label_literal'])!=label_ws(p['literal_native_label']):
                differences.append(dict(page=x['source_page'],column=x['source_column'],candidate=x['candidate'],own=x['direct_original_value'],peer=p['value'],own_role=x['role'],peer_role=p['role'],own_label=x['label_literal'],peer_label=p['literal_native_label']))
        assert not differences,(sid,differences[:10])
        sources.append(dict(source_id=sid,source_raw_sha256=r['raw_sha256'],source_original_path=r['path'],source_original_bytes=len(raw),source_position_rows=len(rows),native_constituents=len({x['source_native_key'] for x in rows if x['role']=='native_reporting_constituent'}),original_OCR_visual_correction_count=len(manual),candidate_checks=checks,independent_peer_position_differences=differences,pages=rview['pages'],rows=rows))
        flat.extend(rows)
    assert sum(x['native_constituents'] for x in sources)==expected_native and len(flat)==expected_positions and sum(x['original_OCR_visual_correction_count'] for x in sources)==expected_visual
    savejson(OUT/f'{tag}-presidential-original-readings.json',dict(scope=f'{len(sources)} complete original-PDF nine-candidate source views; first original-pixel OCR preceded peer, {expected_visual} full-original visual corrections, post-extraction all-position peer comparison. Aid crop polygons are provisional. Printed TOTAL and unprinted template slots separate.',source_view_count=len(sources),native_constituent_count=expected_native,source_position_count=expected_positions,visual_correction_count=expected_visual,original_aid_sha256=sha(aidpath.read_bytes()),independent_peer_file_sha256=sha(peerpath.read_bytes()),review_index_sha256=sha(reviewpath.read_bytes()),sources=sources))
    with (OUT/f'{tag}-presidential-original-cells.csv').open('w',newline='') as f:
        fields=['source_id','source_raw_sha256','source_page','source_column','source_native_key','role','label_literal','printed_native_id','candidate','direct_original_value','original_reading_basis','provisional_original_OCR_value','original_aid_bounds_status','original_full_page_raster']
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:x[k] for k in fields} for x in flat)
    print(len(sources),'original presidential source views,',len(flat),'positions,',expected_native,'native constituents,',expected_visual,'original visual corrections; all9 candidate sums and peer fields match')
def main():build()
if __name__=='__main__':main()
