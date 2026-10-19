"""Separate direct-original amended 2020 Clay Senate page2–3 reading."""
from record_2020_native_manual_original import build,NAMES

def page(a,b,c): return dict(zip(NAMES,(a,b,c)))

ROWS={
    2:page([159,568,27,541,593,833,250,288,338,781,206],
           [176,102,145,327,846,531,208,64,506,252,113],
           [6,5,7,18,11,6,6,2,12,14,6]),
    3:page([309,305,973,6171,None,None,None,None,None,None,None],
           [254,220,262,4006,None,None,None,None,None,None,None],
           [6,4,6,109,None,None,None,None,None,None,None]),
}
LABELS={
    2:['Cairo','Caradine','Cedar Bluff','Central-West Point','East-West Point','North-West Point','Pheba','Pine Bluff','Siloam','South-West Point','Tibbee'],
    3:['Union Star','Vinton','West-West Point','TOTAL','','','','','','',''],
}

def main(): build('clay-amended','clay-amended',ROWS,LABELS,14,hint_version='v4')
if __name__=='__main__': main()
