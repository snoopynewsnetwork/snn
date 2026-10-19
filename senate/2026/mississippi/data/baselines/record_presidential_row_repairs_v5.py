"""Original field-label review repairs13 rotated/faint presidential page grids.

All nine candidate labels and their printed order were independently read on
each complete original label strip. Rules provide positions, never identities.
Winston uses expressly manual reading windows on the faint gray original.
"""
import json
from sources import OUT,save,sha
from extract_replay_president import NAMES
YS={('itawamba',3):[498.5,571,637,704,770.5,836.5,903.5,969.5,1036.5,1103.5],('itawamba',4):[495.5,568,634.5,701,767.5,833.5,900.5,966.5,1033.5,1100.5],('itawamba',5):[498.5,571,637,704,770.5,836.5,903,969.5,1036.5,1103.5],('scott',2):[360,413,461,509.5,557,605.5,654,702.5,751,800],('scott',3):[358,411,459,507.5,556,604.5,652.5,701,749.5,798],('scott',4):[360.5,413.5,462,510,558,606.5,655,703.5,752,801],('amite',2):[504.5,576,642.5,708.5,775,840.5,907,973.5,1040,1106.5],('amite',3):[504,576.5,642,708.5,774.5,840.5,907,973.5,1039.5,1106.5],('amite',4):[504.5,576.5,642.5,709,775.5,841.5,907.5,974.5,1040.5,1107.5],('webster',2):[550,601,648,694.5,741,787.5,834,881,928,975],('webster',3):[552,602,649,696,742.5,789.5,836,882,929,976],('winston',2):[500,570,638,705,770,837,904,970,1037,1103],('winston',3):[500,570,638,705,770,837,904,970,1037,1103]}
def main():
    pointers=json.loads((OUT/'source/presidential-original-row-review-pointers.json').read_text());rows=[]
    for p in pointers:
        county=p['source_id'].removeprefix('sos-2024-county-');ys=YS[(county,p['page'])];assert len(ys)==10;w,h=p['render_size'];evidence=OUT/'qa'/f'presidential-original-row-labels-{(p["card"]-1)//2+1}.png'
        for i,name in enumerate(NAMES):rows.append(dict(source_id=p['source_id'],raw_sha256=p['raw_sha256'],page=p['page'],candidate=name,source_row=i+1,row_bounds=[0,ys[i],w,ys[i+1]],render_size=p['render_size'],rotation_ccw=p['rotation_ccw'],deskew_angle_ccw=p['deskew_angle_ccw'],raster_path=p['raster_path'],raster_sha256=p['raster_sha256'],evidence_path=str(evidence.relative_to(OUT)),evidence_sha256=sha(evidence.read_bytes()),basis='All nine literal candidate labels and printed source order independently read on this original strip, not assumed from adjacent rows or peer counts',position_qualification='Manual complete-field reading windows estimated from original y ticks on faint gray page; not an exact printed-rule geometry claim' if county=='winston' else 'Actual original printed row dividers independently checked on original label strips; v2 rule proposal positions repaired where a token touched/straddled rule; no vote used'))
    assert len(rows)==117;save(OUT/'source/native-presidential-row-repairs-v5.json',dict(qualification='New versioned own-original label/position repairs only; earlier Jackson and v4 raw aids unchanged. No numeric vote/peer field enters these locators. Reading-window positions are not reporting-unit geometry.',readings=rows));print('13originalpages/117distinctprintedcandidate-rowlocators independentlyread;Winstonreadingwindows qualified')
if __name__=='__main__':main()
