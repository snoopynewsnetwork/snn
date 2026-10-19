"""Direct complete-original 2020 Carroll Senate page2–3 transcription."""
from record_2020_native_manual_original import build,NAMES

def page(a,b,c): return dict(zip(NAMES,(a,b,c)))

ROWS={
    2:page([183,92,10,69,289,461,59,31,163,81,93],
           [89,192,158,299,288,219,373,149,269,347,716],
           [2,3,5,6,6,11,3,1,5,11,20]),
    3:page([163,42,187,1923,None,None,None,None,None,None,None],
           [67,356,194,3716,None,None,None,None,None,None,None],
           [1,5,5,84,None,None,None,None,None,None,None]),
}
LABELS={
    2:['430 School','Black Hawk','Calvary','Carrollton','East Vaiden','Fire Tower','Gravel Hill','Jefferson','McCarley','North Carrollton','Rays Shop'],
    3:['Salem','West Carroll','West Vaiden','TOTAL','','','','','','',''],
}

def main(): build('carroll','carroll',ROWS,LABELS,14,hint_version='v4')
if __name__=='__main__': main()
