"""Direct complete-original Franklin 2020 Senate PDFpages2–3 transcription."""
from record_2020_native_manual_original import build,NAMES

def page(espy,hyde,edwards): return dict(zip(NAMES,(espy,hyde,edwards)))

ROWS={
 2:page([206,19,407,55,41,204,61,25,60,78,11],
        [198,375,254,191,317,65,108,143,276,318,117],
        [5,2,10,3,5,3,4,2,7,3,1]),
 3:page([292,71,40,1570,None,None,None,None,None,None,None],
        [166,43,262,2833,None,None,None,None,None,None,None],
        [2,2,5,54,None,None,None,None,None,None,None]),
}
LABELS={
 2:['Antioch','Bad Bayou','Bude','Cains','Eddiceton','Hamburg','Knoxville','Lucien','McCall','Meadville','Pine Grove'],
 3:['Roxie','Wesley Chapel','Whittington','TOTAL','','','','','','',''],
}

def main(): build('franklin','franklin',ROWS,LABELS,14,hint_version='v5')
if __name__=='__main__': main()
