"""Independent original-PDF Senate TOTAL values for all104 2020 publications.

Fifty values are a strict two-PSM original-pixel OCR agreement; the other54
vectors below are transcribed from the original-only visual atlases/expanded
strips.  No peer candidate numbers enter this file.  The peer's source ID,
page and proposed physical locator are used only as a source-position hint.
Accepted TOTAL-column ordinals require distinct header review; locator status
is kept explicit rather than inferred from candidate agreement.
"""
import csv,json
from acquire_sources import BASE,OUT,receipts,sha,savejson

MANUAL={
 'alcorn':(3641,11616,378),'amite':(2750,4347,74),
 'attala':(3824,4888,108),'claiborne':(3907,555,26),
 'clay-amended':(6171,4006,109),'coahoma':(6452,2161,46),
 'copiah':(6730,6062,118),'covington':(3637,5604,131),
 'desoto':(31115,43171,1768),'franklin':(1570,2833,54),
 'george':(1844,8811,260),'greene':(1196,4395,129),
 'hancock':(5651,14537,573),'hinds':(75467,23661,910),
 'humphreys':(3135,1023,29),'issaquena':(367,309,5),
 'itawamba':(1680,8818,251),'jasper':(4556,4102,92),
 'jasper-amended':(4556,4102,92),'jefferson-amended':(3428,476,12),
 'jefferson-davis':(3758,2400,44),'jefferson-davis-amended':(3758,2400,44),
 'kemper':(2965,1720,40),'lamar':(8157,19588,693),
 'lawrence':(2318,4222,57),'lawrence-amended':(2318,4222,57),
 'lowndes':(13843,13010,369),'madison':(25374,30038,823),
 'marshall':(8590,6904,212),'marshall-amended':(8590,6904,212),
 'montgomery':(2264,2738,86),'neshoba':(3602,7797,234),
 'newton':(3290,6659,176),'noxubee':(4138,1178,21),
 'panola':(7953,7425,220),'pike':(9048,8044,257),
 'pontotoc':(3164,10803,337),'quitman':(2307,883,48),
 'rankin':(20315,48502,1664),'scott':(4649,5933,151),
 'sharkey':(1511,663,7),'sharkey-amended':(1511,663,7),
 'sunflower':(7020,2623,42),'sunflower-amended':(7020,2623,42),
 'tallahatchie':(3316,2309,64),'union':(2660,9572,424),
 'walthall':(2993,4005,86),'warren':(10853,9912,246),
 'warren-amended':(10853,9912,246),
 'washington-amended':(13155,4891,109),'wayne':(3954,5984,144),
 'webster':(1198,4067,113),'yalobusha-amended':(3005,3415,88),
 'yazoo':(5804,4551,79),
}
# The first number is the literal source physical ordinal observed on the
# complete original page.  The second is the preceding position-only proposal.
ORIGINAL_ORDINAL_CORRECTIONS={
 'attala':(10,4),'lamar':(2,1),'lowndes':(10,9),
 'neshoba':(6,5),'newton':(6,5),'noxubee':(9,8),
 'rankin':(5,4),'walthall':(10,9),
 'washington-amended':(9,7),'yalobusha-amended':(2,1),
}
NAMES=['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards']

def main():
    assert len(MANUAL)==54
    idx=json.loads((OUT/'qa/2020-county-total-originals/index.json').read_text())
    aid=json.loads((OUT/'2020-publication-original-total-ocr-aid.json').read_text())
    strips=json.loads((OUT/'2020-total-original-broad-exception-strips.json').read_text())
    si={x['source_id']:x for x in strips['entries']}
    ai={x['source_id']:x for x in aid['readings']}
    rs={x['id']:x for x in receipts}
    rows=[];sources=[]
    for e in idx['entries']:
        sid=e['source_id'];suffix=sid.removeprefix('sos-2020-county-');a=ai[sid]
        assert a['source_raw_sha256']==rs[sid]['raw_sha256']==e['source_raw_sha256']
        if suffix in MANUAL:
            values=MANUAL[suffix];basis='direct_visual_full_original_candidate_band'
            evidence=si[sid]['strip_path'] if sid in si else e['full_original_candidate_band']
            if suffix=='jefferson-davis-amended':evidence='data/turnout/qa/2020-county-total-originals/broad-exception-strips/sos-2020-county-jefferson-davis-amended-complete-Senate.png'
        else:
            assert a['provisional_three_values'] is not None,(sid,'unresolved original OCR')
            values=a['provisional_three_values'];basis='two_independent_PSM_readings_of_original_total_cell'
            evidence=e['original_card']
        assert all(isinstance(v,int) and v>=0 for v in values) and len(values)==3
        accepted_c,old_c=ORIGINAL_ORDINAL_CORRECTIONS.get(suffix,(None,None))
        if accepted_c is not None:assert e['source_column_hint']==old_c
        p=BASE/evidence;assert p.exists()
        sources.append(dict(source_id=sid,source_raw_sha256=e['source_raw_sha256'],source_page=e['source_page'],candidate_values=dict(zip(NAMES,values)),original_reading_basis=basis,source_column_position_hint=e['source_column_hint'],source_column_hint_status=e['column_hint_status'],direct_original_corrected_column=accepted_c,position_hint_column_before_correction=old_c,source_column_ordinal_status='direct_original_header_numeric_count_verified' if accepted_c else 'peer_locator_hint_not_asserted_as_final_ordinal',original_evidence=evidence,original_evidence_sha256=sha(p.read_bytes()),original_card=e['original_card'],original_card_sha256=e['card_sha256']))
        for name,value in zip(NAMES,values):rows.append(dict(source_id=sid,source_raw_sha256=e['source_raw_sha256'],source_page=e['source_page'],candidate=name,votes=value,reading_basis=basis,original_evidence=evidence,source_column_ordinal=accepted_c or '',source_column_position_hint=e['source_column_hint'],source_column_ordinal_status='direct_original_header_numeric_count_verified' if accepted_c else 'peer_locator_hint_not_asserted_as_final_ordinal'))
    assert len(sources)==104 and len(rows)==312 and sum(x['original_reading_basis'].startswith('direct') for x in sources)==54
    savejson(OUT/'2020-publication-original-total-readings.json',dict(scope='All104 actual index-linked 2020 original/amended county publication Senate named TOTAL vectors; independent original OCR or direct original visual; source column locator qualifications explicit. No common-vintage state certificate inferred.',source_count=104,candidate_field_count=312,direct_visual_source_count=54,dual_PSM_original_OCR_source_count=50,manual_corrected_ordinal_count=len(ORIGINAL_ORDINAL_CORRECTIONS),candidates=NAMES,sources=sources))
    with (OUT/'2020-publication-original-total-candidate-votes.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print('2020 original county publications',len(sources),'candidate TOTAL fields',len(rows),'manual originals',54,'dual PSM originals',50,'manual ordinal corrections',len(ORIGINAL_ORDINAL_CORRECTIONS))

if __name__=='__main__':main()
