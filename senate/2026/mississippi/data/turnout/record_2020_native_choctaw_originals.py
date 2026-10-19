"""Separate full-original 2020 Choctaw original/amended Senate readings."""
from record_2020_native_manual_original import build,NAMES

def page(a,b,c): return dict(zip(NAMES,(a,b,c)))

ORIGINAL={
    2:page([66,71,203,219,81,61,36,24,102,98,20],
           [141,186,736,73,187,256,174,224,126,194,291],
           [2,0,22,4,5,7,6,6,5,2,10]),
    3:page([248,91,1320,None,None,None,None,None,None,None,None],
           [47,176,2811,None,None,None,None,None,None,None,None],
           [5,4,78,None,None,None,None,None,None,None,None]),
}
AMENDED={
    2:page([66,71,203,219,81,61,36,24,102,98,20],
           [141,186,736,73,187,256,174,224,126,194,291],
           [2,0,22,4,5,7,6,6,5,2,10]),
    3:page([248,91,1320,None,None,None,None,None,None,None,None],
           [47,176,2811,None,None,None,None,None,None,None,None],
           [5,4,78,None,None,None,None,None,None,None,None]),
}
ORIGINAL_LABELS={
    2:['Bywy','Chester','District 5','East Weir','Fentress','French Camp','Hebron','Kenego','Panhandle','Reform','Sherwood'],
    3:['Southwest Ackerman','West Weir','TOTAL','','','','','','','',''],
}
AMENDED_LABELS={
    2:['Bywy','Chester','District 5','East Weir','Fentress','French Camp','Hebron','Kenego','Panhandle','Reform','Sherwood'],
    3:['Southwest Ackerman','West Weir','TOTAL','','','','','','','',''],
}

def main():
    build('choctaw','choctaw-original',ORIGINAL,ORIGINAL_LABELS,13,hint_version='v4')
    build('choctaw-amended','choctaw-amended',AMENDED,AMENDED_LABELS,13,hint_version='v4')
if __name__=='__main__': main()
