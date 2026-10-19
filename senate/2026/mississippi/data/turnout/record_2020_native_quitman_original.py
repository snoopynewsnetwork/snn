"""Direct complete-original 2020 Quitman Senate PDFpage2 reading."""
from record_2020_native_manual_original import build,NAMES

ROWS={2:dict(zip(NAMES,(
    [110,57,134,230,191,296,414,347,259,269,2307],
    [3,189,33,160,175,48,91,41,75,68,883],
    [1,2,5,2,6,7,8,7,6,4,48],
)))}
LABELS={2:['Crenshaw','Crowder','Darling','District 3 North','District 3 South','Lambert','North West Marks','Sledge','South West Marks','West Lambert','TOTAL']}

def main(): build('quitman','quitman',ROWS,LABELS,10,hint_version='v4')
if __name__=='__main__': main()
