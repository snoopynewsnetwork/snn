"""Direct full-page Prentiss original and amended 2020 Senate readings."""
from record_2020_native_manual_original import build, NAMES

def page(espy, hyde, edwards):
    return dict(zip(NAMES, (espy, hyde, edwards)))

ORIGINAL = {
    2: page([483,59,204,51,117,249,102,28,88,72,472],
            [484,313,839,292,421,518,727,202,512,487,202],
            [14,8,19,4,18,19,26,7,19,15,7]),
    3: page([146,120,345,158,2694,None,None,None,None,None,None],
            [316,478,1249,563,7603,None,None,None,None,None,None],
            [13,17,26,15,227,None,None,None,None,None,None]),
}
AMENDED = {
    2: page([489,59,204,51,117,253,102,28,89,72,476],
            [486,313,839,293,421,524,739,202,521,487,207],
            [14,8,19,4,18,20,26,7,19,15,7]),
    3: page([146,120,348,160,2714,None,None,None,None,None,None],
            [316,478,1257,568,7651,None,None,None,None,None,None],
            [13,17,27,15,229,None,None,None,None,None,None]),
}
LABELS = {
    2: ['Baldwyn','Blackland','Booneville/Ag-Ctr','Cairo','Cross Roads',
        'East Booneville','Hills Chapel- New Hope','Ingram','Marietta',
        'New Site','North Booneville/Sunflower'],
    3: ['Thrasher','Tuscumbia-New Candler','West Booneville','Wheeler',
        'TOTAL','','','','','',''],
}

def main():
    build('prentiss','prentiss-original',ORIGINAL,LABELS,15,hint_version='v5')
    build('prentiss-amended','prentiss-amended',AMENDED,LABELS,15,hint_version='v5')

if __name__ == '__main__': main()
