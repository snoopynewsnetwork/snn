"""Direct complete-original Claiborne 2020 Senate PDFpages2–3 transcription."""
from record_2020_native_manual_original import build,NAMES

def page(espy,hyde,edwards): return dict(zip(NAMES,(espy,hyde,edwards)))

ROWS={
 2:page([588,326,398,219,682,17,351,388,28,497,413],
        [78,3,74,30,135,17,26,43,70,19,60],
        [1,4,3,1,8,0,3,2,2,0,2]),
 3:page([3907,None,None,None,None,None,None,None,None,None,None],
        [555,None,None,None,None,None,None,None,None,None,None],
        [26,None,None,None,None,None,None,None,None,None,None]),
}
LABELS={
 2:[f'County Precinct {code}' for code in ['1-A','1-B','2-A','2-B','3-A','3-B','4-A','4-B','4-D','5-A','5-B']],
 3:['TOTAL','','','','','','','','','',''],
}

def main(): build('claiborne','claiborne',ROWS,LABELS,11,hint_version='v5')
if __name__=='__main__': main()
