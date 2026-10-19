"""Independent original numeric repairs for the20-source extension to60views.

Itawamba49/36 were not fully visible in the initial tight targeting crops.
Complete original candidate strips were separately read, so those cropped aids
are never used as accepted numeric authority. Raw hints/old aids stay unchanged.
"""
import json
from sources import OUT,save
VALUES=[108,54,40,76,519,1060,424,71,143,103,261,1106,145,1420,202,163,166,189,18,7,39,49,21,5,36,39,40,71,358,701,161,37,211,77,68,7]
ITAWAMBA_BOUNDS={21:[852,1162,972,1222],22:[1426,1162,1544,1222],23:[1538,1162,1658,1222],24:[968,1162,1089,1222],25:[1653,1162,1773,1222],26:[1768,1162,1886,1222]}
def main():
    p=json.loads((OUT/'source/replay-60views-original-disagreement-pointers.json').read_text());assert len(p)==len(VALUES);rows=[]
    for i,(r,v) in enumerate(zip(p,VALUES),1):
        row=r|dict(value=v,basis='Independent visual reading of complete unaltered original numeric cell; no control fitting or peer value used as transcription input.',evidence=f'qa/replay-60views-original-disagreements-{(i-1)//10+1}.png')
        if i in ITAWAMBA_BOUNDS:row.update(evidence='qa/itawamba-original-senate-full-rows-p3-4.png',accepted_reading_bounds=ITAWAMBA_BOUNDS[i],geometry_qualification='Original tight targeting box clips a glyph or includes adjacent-cell text. Expanded actual-source reading box retained separately; old target box/aid unchanged. Complete original p3/4 Senate rows independently read, includingClay49 andKirkville36.')
        rows.append(row)
    save(OUT/'replay-60views-manual-repairs.json',dict(readings=rows,qualification='All36 are native source candidate cells, noTOTAL differences. Itawamba targeting-box repairs are explicit and are not ordinal/geography normalization.'))
    save(OUT/'itawamba-original-row-readings.json',dict(source_id='sos-2024-county-itawamba',evidence='qa/itawamba-original-senate-full-rows-p3-4.png',scope='Entire two named Senate rows on both original p3/4 directly visually read to resolve clipped source targeting boxes; remaining Itawamba pages separate.',pages=[dict(page=3,Ty_Pinkins=[151,70,39,20,12,33,31,49,21,43,100],Roger_F_Wicker=[955,421,524,155,159,225,328,694,189,575,294]),dict(page=4,Ty_Pinkins=[14,26,15,5,2,5,106,128,3,36,39],Roger_F_Wicker=[120,421,124,87,95,84,278,477,178,629,590])],position_warning='Raw peer hints p3c8right1524 cuts actual49, printed rule~1540; p4c10right1753 cuts actual36, printed rule~1770. Neighbor boxes share that offset. Preserve both targeting and accepted original reading bounds, not exact box agreement.'))
    print('36native original readings retained;6Itawamba original reading boxes separately repaired')
if __name__=='__main__':main()
