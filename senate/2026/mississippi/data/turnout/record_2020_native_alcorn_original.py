"""Original-only Alcorn 2020 Senate native reading, with OCR exception history.

All labels below are typed from complete original PDF pages2–3. Eight
two-mode OCR disagreements are explicitly read on the enlarged original-card
atlas; the other numeric cells use independent original-pixel OCR. Peer values
and county controls enter only after the source transcript is complete.
"""
import csv,gzip,json,re
from acquire_sources import BASE,OUT,receipts,sha,savejson

SID='sos-2020-county-alcorn'
CANDIDATES=['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards']
LABELS={
 2:['2nd District Central\nPrecinct','Bethel','Biggersville','College Hill','East Corinth','Five Points  1st Dist','Glen','Jacinto','Kossuth','North Corinth','Pinecrest'],
 3:['Rienzi','Shady Grove','South Corinth','Union Center','Wenasoga','West Corinth','TOTAL','','','',''],
}
# Each entry was visually read from the enlarged ORIGINAL source card, not
# selected to close a residual or imported from an independent worker.
VISUAL={
 (2,2,'Mike Espy'):11,(2,3,'Mike Espy'):192,
 (2,1,'Cindy Hyde-Smith'):1089,
 (2,2,'Jimmy L. Edwards'):0,(2,11,'Jimmy L. Edwards'):11,
 (3,4,'Cindy Hyde-Smith'):889,
 (3,1,'Jimmy L. Edwards'):27,(3,3,'Jimmy L. Edwards'):15,
}

def norm(s):return ' '.join(s.split())
def main():
    src=OUT/f'2020-native-original-ocr/{SID}.json.gz'
    raw=gzip.decompress(src.read_bytes());aid=json.loads(raw)
    assert aid['source_id']==SID and len(aid['rows'])==66
    r=next(x for x in receipts if x['id']==SID)
    assert aid['source_raw_sha256']==r['raw_sha256']
    atlas=OUT/'qa/2020-native-original-ocr/alcorn-all-PSM-disagreements-atlas.png'
    assert atlas.exists()
    hint=json.loads((OUT/'source/2020-native-position-hints-v1.json').read_text())
    assert aid['position_hint_sha256']==sha((OUT/'source/2020-native-position-hints-v1.json').read_bytes())
    h=next(x for x in hint['sources'] if x['source_id']==SID)
    visual_positions={(x['source_page'],x['source_column'],x['candidate']) for x in aid['rows'] if x['role_hint']!='unused_template_column' and x['ocr_psm7']!=x['ocr_psm13']}
    assert visual_positions==set(VISUAL)
    rows=[]
    for x in aid['rows']:
        page=x['source_page'];col=x['source_column'];name=x['candidate'];role=x['role_hint']
        assert name in CANDIDATES and 1<=col<=11 and page in LABELS
        hp=next(p for p in h['pages'] if p['page']==page)
        assert hp['columns'][col-1]['role']==role
        if role=='unused_template_column':
            value=None;basis='direct_original_unprinted_template_cell'
            assert page==3 and col>=8 and x['ink_pixel_count']==0,(page,col,name,x['ink_pixel_count'])
        else:
            value=VISUAL.get((page,col,name),x['provisional_value'])
            basis='direct_visual_original_exception_atlas' if (page,col,name) in VISUAL else 'original_pixel_ocr_psm7_then_source_and_peer_reconciliation'
            assert isinstance(value,int) and value>=0,(page,col,name,value)
        rows.append(dict(source_id=SID,source_raw_sha256=r['raw_sha256'],source_page=page,source_column=col,native_source_key=f'{SID}:p{page}:c{col}',label_literal=LABELS[page][col-1],role=role,candidate=name,votes=value,reading_basis=basis,original_window=x['original_window'],ocr_psm7=x['ocr_psm7'],ocr_psm13=x['ocr_psm13'],original_full_page_raster=next(p['original_raster'] for p in aid['pages'] if p['source_page']==page)))
    assert len(rows)==66 and len({(x['source_page'],x['source_column'],x['candidate']) for x in rows})==66
    checks={}
    for name in CANDIDATES:
        a=sum(x['votes'] for x in rows if x['candidate']==name and x['role']=='source_native_reporting_constituent')
        t=[x['votes'] for x in rows if x['candidate']==name and x['role']=='source_TOTAL']
        assert len(t)==1
        checks[name]=dict(native_sum=a,original_printed_TOTAL=t[0],passes=a==t[0])
    assert all(x['passes'] for x in checks.values()),checks
    owncontrol=json.loads((OUT/'2020-publication-original-total-readings.json').read_text())
    ctl=next(x for x in owncontrol['sources'] if x['source_id']==SID)
    assert {n:checks[n]['native_sum'] for n in CANDIDATES}==ctl['candidate_values']
    peerpath=BASE/'data/baselines/native-2020-additional-candidate-votes.csv'
    peer={(int(x['source_page']),int(x['source_column']),x['candidate']):x for x in csv.DictReader(peerpath.open()) if x['source_id']==SID}
    diffs=[]
    for x in rows:
        q=peer[x['source_page'],x['source_column'],x['candidate']]
        if ('' if x['votes'] is None else str(x['votes']))!=q['votes'] or x['role']!=q['role'] or norm(x['label_literal'])!=norm(q['literal_native_label']):
            diffs.append(dict(page=x['source_page'],column=x['source_column'],candidate=x['candidate'],value=x['votes'],peer_value=q['votes'],label=x['label_literal'],peer_label=q['literal_native_label'],role=x['role'],peer_role=q['role']))
    assert not diffs,diffs
    qa=dict(source_id=SID,source_raw_sha256=r['raw_sha256'],source_original_path=r['path'],ocr_aid_path=str(src.relative_to(BASE)),ocr_aid_sha256=sha(src.read_bytes()),position_hint_sha256=aid['position_hint_sha256'],visual_exception_atlas=str(atlas.relative_to(BASE)),visual_exception_atlas_sha256=sha(atlas.read_bytes()),native_constituents=17,source_TOTAL_positions=3,unused_null_positions=12,candidate_checks=checks,peer_file_sha256=sha(peerpath.read_bytes()),peer_differences=diffs,pages=aid['pages'],rows=rows)
    savejson(OUT/'2020-native-alcorn-original-readings.json',qa)
    with (OUT/'2020-native-alcorn-original-candidate-votes.csv').open('w',newline='') as f:
        fields=['source_id','source_raw_sha256','source_page','source_column','native_source_key','label_literal','role','candidate','votes','reading_basis','original_window','ocr_psm7','ocr_psm13','original_full_page_raster']
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:x[k] for k in fields} for x in rows)
    print('2020 Alcorn original',len(rows),'positions',qa['native_constituents'],'native; source, county and peer controls close')
if __name__=='__main__':main()
