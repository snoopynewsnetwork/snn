"""Record direct complete original-page 2020 Senate native readings.

Caller-supplied candidate vectors and literal headers are typed while viewing
full original SOS rasters. Peer and county numeric controls are consulted only
after every source cell has an explicit value or unprinted null.
"""
import csv,gzip,io,json
from acquire_sources import BASE,OUT,receipts,sha,savejson

NAMES=['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards']
def norm(s):return ' '.join(s.split())

def build(slug,tag,grids,labels,expected_native,hint_version='v1',allowed_peer_label_differences=None):
    sid='sos-2020-county-'+slug
    assert hint_version in ('v1','v2','v3','v4','v5','v6','v7')
    hintpath=OUT/f'source/2020-native-position-hints-{hint_version}.json'
    hint=next(s for s in json.loads(hintpath.read_text())['sources'] if s['source_id']==sid)
    rr=next(r for r in receipts if r['id']==sid)
    raw=gzip.decompress((BASE/rr['path']).read_bytes())
    assert sha(raw)==hint['source_raw_sha256']==rr['raw_sha256']
    assert set(grids)==set(labels)=={p['page'] for p in hint['pages']}
    pages=[];rows=[]
    for p in hint['pages']:
        page=p['page'];assert set(grids[page])==set(NAMES)
        raster=OUT/f'qa/2020-native-original-ocr/{sid}/p{page:04d}-original.png'
        assert raster.exists(),raster
        pages.append(dict(source_page=page,full_original_raster=str(raster.relative_to(BASE)),raster_sha256=sha(raster.read_bytes()),render_size=p['render_size'],rotation_ccw=p['rotation_ccw'],deskew_ccw=p['deskew_angle_ccw']))
        cols=p['columns'];assert len(cols)==len(labels[page])
        for name in NAMES:
            vals=grids[page][name];assert len(vals)==len(cols),(sid,page,name,len(vals),len(cols))
            for c,label,value in zip(cols,labels[page],vals):
                role=c['role'];col=c['source_column'];assert col==cols.index(c)+1
                assert (role=='unused_template_column' and value is None and label=='') or (role in ['source_native_reporting_constituent','source_TOTAL'] and isinstance(value,int) and value>=0 and label),(sid,page,col,name,role,value,label)
                rows.append(dict(source_id=sid,source_raw_sha256=rr['raw_sha256'],source_page=page,source_column=col,native_source_key=f'{sid}:p{page}:c{col}',literal_native_label=label,role=role,candidate=name,votes=value,reading_basis='direct_visual_complete_original_pdf_page' if value is not None else 'direct_visual_unprinted_template_position',header_position_hint=c['header_bounds'],candidate_row_band_hint=next(x['row_bounds'] for x in p['candidate_rows'] if x['candidate']==name),full_original_raster=str(raster.relative_to(BASE))))
    assert len(rows)==sum(3*len(p['columns']) for p in hint['pages'])
    counts={}
    for name in NAMES:
        s=sum(x['votes'] for x in rows if x['candidate']==name and x['role']=='source_native_reporting_constituent')
        ts=[x['votes'] for x in rows if x['candidate']==name and x['role']=='source_TOTAL']
        assert len(ts)==1
        counts[name]=dict(native_sum=s,printed_TOTAL=ts[0],passes=s==ts[0])
    assert all(x['passes'] for x in counts.values()),counts
    ownctl=json.loads((OUT/'2020-publication-original-total-readings.json').read_text())
    ctl=next(x for x in ownctl['sources'] if x['source_id']==sid)
    assert {n:counts[n]['native_sum'] for n in NAMES}==ctl['candidate_values']
    snapshot_version='104views-v1' if hint_version=='v7' else '95views-v1' if hint_version=='v6' else '85views-v1' if hint_version=='v5' else '70views-v1' if hint_version=='v4' else '65views-v1'
    snapshotpath=BASE/f'data/baselines/source/native-2020-{snapshot_version}/snapshot.json'
    snapshotbytes=snapshotpath.read_bytes();snapshot=json.loads(snapshotbytes)
    pin=next(x for x in snapshot['pins'] if x['original_path']=='data/baselines/native-2020-additional-candidate-votes.csv')
    frozen=(BASE/pin['stored_path']).read_bytes()
    assert len(frozen)==pin['stored_bytes'] and sha(frozen)==pin['stored_sha256']
    peerbytes=gzip.decompress(frozen)
    assert len(peerbytes)==pin['original_bytes'] and sha(peerbytes)==pin['original_sha256']
    peer={(int(x['source_page']),int(x['source_column']),x['candidate']):x for x in csv.DictReader(io.StringIO(peerbytes.decode())) if x['source_id']==sid}
    differences=[]
    for x in rows:
        q=peer[x['source_page'],x['source_column'],x['candidate']]
        if ('' if x['votes'] is None else str(x['votes']))!=q['votes'] or x['role']!=q['role'] or norm(x['literal_native_label'])!=norm(q['literal_native_label']):
            differences.append(dict(page=x['source_page'],column=x['source_column'],candidate=x['candidate'],own_value=x['votes'],peer_value=q['votes'],own_label=x['literal_native_label'],peer_label=q['literal_native_label'],own_role=x['role'],peer_role=q['role']))
    allowed_peer_label_differences=allowed_peer_label_differences or {}
    accepted_differences=[]
    for d in differences:
        expected=allowed_peer_label_differences.get((d['page'],d['column']))
        assert expected and (d['own_label'],d['peer_label'])==expected and d['own_value']==(None if d['peer_value']=='' else int(d['peer_value'])) and d['own_role']==d['peer_role'],d
        accepted_differences.append(d)
    assert set(allowed_peer_label_differences)=={(d['page'],d['column']) for d in accepted_differences},differences[:15]
    assert sum(x['role']=='source_native_reporting_constituent' for x in rows)==expected_native*3
    out=dict(scope=f'Direct whole original PDF-page 2020 Senate3-candidate native reading. Same-publication TOTAL and immutable {snapshot_version} peer compared only afterward; physical row bands from vote-free hints remain provisional numeric windows.',source_id=sid,source_raw_sha256=rr['raw_sha256'],source_original_path=rr['path'],position_hint_sha256=sha(hintpath.read_bytes()),peer_file_sha256=sha(peerbytes),peer_snapshot_sha256=sha(snapshotbytes),native_constituents=expected_native,source_positions=len(rows),candidate_checks=counts,peer_differences=differences,accepted_source_literal_label_differences=accepted_differences,pages=pages,rows=rows)
    savejson(OUT/f'{tag}-2020-native-original-readings.json',out)
    with (OUT/f'{tag}-2020-native-original-cells.csv').open('w',newline='') as f:
        fields=['source_id','source_raw_sha256','source_page','source_column','native_source_key','literal_native_label','role','candidate','votes','reading_basis','header_position_hint','candidate_row_band_hint','full_original_raster']
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:x[k] for k in fields} for x in rows)
    print(sid,len(rows),'positions',expected_native,'native; three source, county and peer vote vectors close;',len(differences),'literal peer-label differences')
