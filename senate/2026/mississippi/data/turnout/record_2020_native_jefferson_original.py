"""Direct complete-original Jefferson 2020 Senate PDFpages2–3 transcription."""
from record_2020_native_manual_original import build,NAMES

def page(espy,hyde,edwards): return dict(zip(NAMES,(espy,hyde,edwards)))

ROWS={
 2:page([192,63,473,391,204,521,192,414,297,281,236],
        [17,101,13,46,12,13,46,39,6,42,7],
        [1,0,3,2,1,1,0,0,0,1,1]),
 3:page([164,3428,None,None,None,None,None,None,None,None,None],
        [134,476,None,None,None,None,None,None,None,None,None],
        [2,12,None,None,None,None,None,None,None,None,None]),
}
LABELS={
 2:['CANNONSBURG','CHURCH HILL','CITY HALL','COMMUNITY GARDEN CENTER','HARRISTON','LOCUST GROVE BAPTIST CHURCH','LORMAN','MT. ISREAL BAPTIST CHURCH','MULTIPURPOSE CENTER','RED LICK','STAMPLEY'],
 3:['UNION CHURCH','TOTAL','','','','','','','','',''],
}

def main(): build('jefferson','jefferson',ROWS,LABELS,12,hint_version='v5')
if __name__=='__main__': main()
