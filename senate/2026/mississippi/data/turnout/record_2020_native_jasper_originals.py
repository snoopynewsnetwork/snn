"""Separate complete original Jasper 2020 Senate grids, original and amended."""
from record_2020_native_manual_original import build,NAMES
def page(a,b,c):return dict(zip(NAMES,(a,b,c)))

ORIGINAL={
 2:page([41,483,423,294,11,856,261,326,164,149,179],
        [233,353,334,170,86,126,254,250,113,153,540],
        [7,7,7,10,1,4,6,10,2,5,13]),
 3:page([73,577,251,161,109,198,4556]+[None]*4,
        [11,251,64,204,945,15,4102]+[None]*4,
        [1,3,2,0,13,1,92]+[None]*4),
}
AMENDED={
 2:page([41,483,423,294,11,856,261,326,164,149,179],
        [233,353,334,170,86,126,254,250,113,153,540],
        [7,7,7,10,1,4,6,10,2,5,13]),
 3:page([73,577,251,161,109,198,4556]+[None]*4,
        [11,251,64,204,945,15,4102]+[None]*4,
        [1,3,2,0,13,1,92]+[None]*4),
}
ORIGINAL_LABELS={2:['Antioch','Bay Springs Beat 3','Bay Springs Beat 4','Claiborne','Fellowship','Heidelberg','Holders','Louin','Midway','Montrose','Moss'],3:['Palestine','Paulding','Philadelphia','Rose Hill','Stringer','Vossburg','TOTAL']+['']*4}
AMENDED_LABELS={2:['Antioch','Bay Springs Beat 3','Bay Springs Beat 4','Claiborne','Fellowship','Heidelberg','Holders','Louin','Midway','Montrose','Moss'],3:['Palestine','Paulding','Philadelphia','Rose Hill','Stringer','Vossburg','TOTAL']+['']*4}
def main():
    build('jasper','jasper-original',ORIGINAL,ORIGINAL_LABELS,17,hint_version='v3')
    build('jasper-amended','jasper-amended',AMENDED,AMENDED_LABELS,17,hint_version='v3')
if __name__=='__main__':main()
