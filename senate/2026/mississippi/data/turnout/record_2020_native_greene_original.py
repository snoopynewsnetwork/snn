"""Greene 2020 three-candidate native cells typed from complete PDFpages2–3."""
from record_2020_native_manual_original import build
E='Mike Espy';H='Cindy Hyde-Smith';J='Jimmy L. Edwards';B=[None]*8
LABELS={
 2:['Leakesville','North Leakesville','State Line','Mutual Rights','Wade','Jones','Piave','Maples','Vernal','Washington Neely','Leaf'],
 3:['McLain','Jonathan','TOTAL','','','','','','','',''],
}
GRIDS={
 2:{
 E:[134,177,353,16,42,8,13,86,93,19,46],
 H:[948,137,306,179,468,193,333,543,424,281,95],
 J:[35,7,5,7,15,4,5,16,9,8,4],
 },
 3:{
 E:[183,26,1196,*B],
 H:[128,360,4395,*B],
 J:[6,8,129,*B],
 },
}
if __name__=='__main__':build('greene','greene',GRIDS,LABELS,13)
