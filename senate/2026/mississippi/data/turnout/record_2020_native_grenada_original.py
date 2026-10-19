"""Direct complete-original 2020 Grenada Senate PDFpages2–3 reading."""
from record_2020_native_manual_original import build,NAMES

def page(a,b,c): return dict(zip(NAMES,(a,b,c)))

ROWS={
 2:page([637,122,102,284,96,194,1180,17,324,1374,148],
        [1049,371,254,260,433,567,351,98,82,106,533],
        [18,10,5,6,12,10,18,1,2,11,11]),
 3:page([204,438,5120,None,None,None,None,None,None,None,None],
        [532,1018,5654,None,None,None,None,None,None,None,None],
        [20,33,157,None,None,None,None,None,None,None,None]),
}
LABELS={
 2:['Box 1 Southside Church of Christ','Elliott Vol Fire Station','Sweethome Holt#2 Fire Stat','Box 2 Grenada Co Office','Gore Springs Comm Center','Futheyville 1st Pentecost','Box 3 City Auditorium',"Mt. Nebo Young's Landing",'Pleasant Grove Commun Cen','Box 4 Taylor Hall','Geeslin Friendship Bapt Church'],
 3:['Holcomb Community Center','Box 5 EOC Building','TOTAL','','','','','','','',''],
}

def main():build('grenada','grenada',ROWS,LABELS,13,hint_version='v5')
if __name__=='__main__':main()
