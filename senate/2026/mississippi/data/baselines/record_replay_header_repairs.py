"""Independent readings of 74 expanded original header crops (four atlases)."""
import json
from sources import OUT,save
LABELS=[
'Glen','5 Willis','Clear Springs-\nPineville','Summerland','TOTAL','Bond','32-Indianola 3\nSouthwest','51-Ruleville North',
'Centreville 1st 1020','Centreville 3rd 3010','Cold Springs 4020','Fort Adams 2020','Longmire 5020','Woodville 5th 5010','Woodville 4th 4010','Woodville 1010','Woodville 2nd 2010','TOTAL','430 School','Cedar Bluff',
'Pine Bluff','Tibbee','Union Star','','','','','','','',
'GUMPOND/HICKORY\nGROVE 3','PIC/HAWL/NH 5','TOTAL','Oak Grove','','','','','North\nBooneville/Sunflower','','',
'Noxubee Alliance\nBldg','Summerville','Decatur #5','Newton #1','Iuka','(04) Mlk Center','(05) North McComb\nBaptist Church','(12) Navilla Baptist\nChurch Fellowship','(14) Calvary Baptist\nChurch','(15) Friendship Bapt.\nChurch','(16) Summit City\nHall','(17) SMCC Work\nForce Training Ctr','(18) Johnston Chapel\nMeth. Church','(19) Pisgah\nMethodist Church','(20) Pike Co. Nat.\nBank','(21) Old Progress\nVolunteer Fire Station','(22) Church of Christ','','','','',
'Fontainebleau','Gautier North','Gautier South','Hickory Hills','Hwy 57','Larue','OS Civic Ctr','OS Senior Center','Orange Grove','West Jackson','TOTAL','']
def main():
    rows=json.loads((OUT/'reviewed-replay-label-comparison.json').read_text())['disagreements'];assert len(rows)==len(LABELS),(len(rows),len(LABELS));out=[]
    for i,(r,label) in enumerate(zip(rows,LABELS),1):
        out.append({k:r[k] for k in ['source_id','page','source_column','header_bounds']}|dict(label_literal=label,prior_own_ocr=r['own_ocr'],basis='Independent visual reading of expanded original header crop; wraps retained; blank template headers remain empty strings, not invented reporting identities.',evidence=f'qa/replay-original-headers-{(i-1)//20+1}.png',review_card=i))
    save(OUT/'reviewed-replay-header-repairs.json',dict(readings=out))
if __name__=='__main__':main()
