"""Record complete original-page presidential grids without numeric OCR inputs.

The caller supplies literal rows independently read on original PDF rasters.
County and peer controls are consulted only after the complete reading exists.
Missing OCR aids are represented explicitly, including unprinted template cells.
"""
import csv,gzip,json
from acquire_sources import BASE,OUT,receipts,sha,savejson
from record_small_presidential_original import NAMES,label_ws

def build(slug,tag,grids,expected_native,expected_positions):
    sid='sos-2024-county-'+slug
    reviewpath=OUT/f'{tag}-presidential-original-review-index.json'
    review=json.loads(reviewpath.read_text())['sources'][0]
    assert review['source_id']==sid
    rr={x['id']:x for x in receipts};r=rr[sid]
    raw=gzip.decompress((BASE/r['path']).read_bytes())
    assert sha(raw)==r['raw_sha256']==review['source_raw_sha256']
    pages={p['source_page']:p for p in review['pages']}
    for p in pages.values():assert sha((BASE/p['full_original_raster']).read_bytes())==p['raster_sha256']
    native=json.loads(gzip.decompress((OUT/'native-constituents-reviewed.json.gz').read_bytes()))
    own={(u['source_page'],u['source_column']):u for u in native if u['source_id']==sid}
    assert len(own)==expected_positions//9 and len(grids)==len(pages)
    aidpath=OUT/'presidential-original-aid-cells.csv'
    aid={(int(a['source_page']),int(a['source_column']),a['candidate']):a for a in csv.DictReader(aidpath.open()) if a['source_id']==sid}
    rows=[]
    for page,byname in grids.items():
        assert page in pages and set(byname)==set(NAMES)
        columns=sorted(col for p,col in own if p==page)
        for name in NAMES:
            values=byname[name]
            assert len(values)==len(columns),(sid,page,name,len(values),len(columns))
            for col,value in zip(columns,values):
                u=own[page,col]
                assert (u['role']=='unused_template_column' and value is None) or (u['role'] in ('native_reporting_constituent','parallel_native_observation','source_TOTAL') and isinstance(value,int)),(sid,page,col,name,u['role'],value)
                a=aid.get((page,col,name))
                rows.append(dict(source_id=sid,source_raw_sha256=r['raw_sha256'],source_page=page,source_column=col,source_native_key=u['key'],role=u['role'],label_literal=u['label_literal'],printed_native_id=u['printed_native_id'],source_header_bounds=u['header_bounds'],candidate=name,direct_original_value=value,original_reading_basis='direct_visual_complete_original_page_grid' if value is not None else 'direct_visual_unprinted_unused_template_position',provisional_original_OCR_value=int(a['compiled_provisional_value']) if a and a['compiled_provisional_value'].isdigit() else None,original_aid_cell_bounds=json.loads(a['original_cell_bounds']) if a else None,original_aid_bounds_status='provisional_OCR_target_not_accepted_numeric_polygon' if a else 'no_original_aid_crop_full_page_direct_read',original_full_page_raster=pages[page]['full_original_raster']))
    assert len(rows)==expected_positions and len({(x['source_page'],x['source_column'],x['candidate']) for x in rows})==len(rows)
    county={'pearl-river':'Pearl River','pike-updated':'Pike','jeff-davis':'Jeff Davis'}.get(slug,slug)
    votes=list(csv.DictReader((OUT/'candidate-votes.csv').open()))
    csvvotes={x['candidate_literal'].split(' for President')[0].removeprefix('Presidential Electors for '):int(x['votes']) for x in votes if x['county'].lower()==county.lower() and x['election_date']=='2024-11-05' and x['office_literal'].strip()=='United States-President'}
    checks={}
    for name in NAMES:
        selected=[x for x in rows if x['candidate']==name]
        s=sum(x['direct_original_value'] for x in selected if x['role']=='native_reporting_constituent')
        totals=[x['direct_original_value'] for x in selected if x['role']=='source_TOTAL']
        assert len(totals)==1
        checks[name]=dict(native_sum=s,printed_TOTAL=totals[0],county_CSV=csvvotes[name],passes=s==totals[0]==csvvotes[name])
    assert all(x['passes'] for x in checks.values()),(sid,checks)
    if slug=='kemper':
        peerpath=BASE/'data/baselines/native-source-exception-readings.json'
        peer={}
        ps=next(s for s in json.loads(peerpath.read_text())['sources'] if s['source_id']==sid)
        for pg in ps['pages']:
            for field in pg['fields']:
                if field['candidate'] not in NAMES:continue
                for col,value in enumerate(field['values'],1):
                    role=pg['roles'][col-1]
                    label=pg['labels_literal'][col-1] if col<=len(pg['labels_literal']) else ''
                    peer[sid,pg['page'],col,field['candidate']]=dict(value='' if value is None else str(value),role=role,literal_native_label=label)
    else:
        peerpath=BASE/'data/baselines/native-allfield-additional-candidate-votes.csv'
        peer={(x['source_id'],int(x['source_page']),int(x['source_column']),x['candidate']):x for x in csv.DictReader(peerpath.open()) if x['candidate'] in NAMES}
    differences=[]
    for x in rows:
        p=peer[sid,x['source_page'],x['source_column'],x['candidate']]
        role='source_native_reporting_constituent' if x['role']=='native_reporting_constituent' else x['role']
        # Preserve both literal labels; for agreement only, fold the source's
        # explicitly printed Holmes A-\nZ line wrap without inserting a space.
        peer_label_compare=label_ws(p['literal_native_label'].replace('-\n','-'))
        if (str(x['direct_original_value']) if x['direct_original_value'] is not None else '')!=p['value'] or role!=p['role'] or label_ws(x['label_literal'])!=peer_label_compare:
            differences.append(dict(page=x['source_page'],column=x['source_column'],candidate=x['candidate'],own=x['direct_original_value'],peer=p['value'],own_role=x['role'],peer_role=p['role'],own_label=x['label_literal'],peer_label=p['literal_native_label']))
    assert not differences,(sid,differences[:15])
    aid_disagreements=sum(aid[x['source_page'],x['source_column'],x['candidate']]['compiled_provisional_value']!=(str(x['direct_original_value']) if x['direct_original_value'] is not None else '') for x in rows if (x['source_page'],x['source_column'],x['candidate']) in aid)
    source=dict(source_id=sid,source_raw_sha256=r['raw_sha256'],source_original_path=r['path'],source_original_bytes=len(raw),source_position_rows=len(rows),native_constituents=len({x['source_native_key'] for x in rows if x['role']=='native_reporting_constituent'}),original_OCR_visual_correction_count=aid_disagreements,original_aid_missing_position_count=len(rows)-len(aid),candidate_checks=checks,independent_peer_position_differences=differences,pages=list(pages.values()),rows=rows)
    assert source['native_constituents']==expected_native
    savejson(OUT/f'{tag}-presidential-original-readings.json',dict(scope='Complete original PDF grid manually read across all nine candidate rows and every printed source column; original OCR aids and peer compared only afterward. No numeric crop box acceptance.',source_view_count=1,native_constituent_count=expected_native,source_position_count=expected_positions,original_aid_missing_position_count=source['original_aid_missing_position_count'],original_aid_SHA256=sha(aidpath.read_bytes()),independent_peer_file_sha256=sha(peerpath.read_bytes()),review_index_sha256=sha(reviewpath.read_bytes()),sources=[source]))
    with (OUT/f'{tag}-presidential-original-cells.csv').open('w',newline='') as f:
        fields=['source_id','source_raw_sha256','source_page','source_column','source_native_key','role','label_literal','printed_native_id','candidate','direct_original_value','original_reading_basis','provisional_original_OCR_value','original_aid_bounds_status','original_full_page_raster']
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:x[k] for k in fields} for x in rows)
    print(sid,len(rows),expected_native,source['original_OCR_visual_correction_count'],'OCR disagreements',source['original_aid_missing_position_count'],'missing aid; all9 source/county/peer controls pass')
