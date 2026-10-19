"""Tunica and Stone 2020 three-candidate native grids from complete originals."""
from record_2020_native_manual_original import build
E='Mike Espy';H='Cindy Hyde-Smith';J='Jimmy L. Edwards'
TUNICA_LABELS={
 2:['Banks/Hambrick','Mhoon Landing','New Sub Park','Prichard','Robinsonville Community Center','Tunica','Tunica Auditorium','Tunica Co. Supt. of Educ.','Two Mile Lake','Westend Store','White Oak Rec. Center'],
 3:['Win Job Center','TOTAL','','','','','','','','',''],
}
TUNICA={
 2:{
 E:[202,16,273,281,331,251,351,170,320,40,306],
 H:[1,67,132,23,30,192,30,99,84,33,70],
 J:[0,2,4,2,4,11,6,7,3,0,2],
 },
 3:{
 E:[176,2717,None,None,None,None,None,None,None,None,None],
 H:[53,814,None,None,None,None,None,None,None,None,None],
 J:[1,42,None,None,None,None,None,None,None,None,None],
 },
}
STONE_LABELS={
 2:['Bond','National Guard','Old Health Department','Courthouse','American Legion','New Hope','Perkinston','Magnolia','Mchenry Library','Elarbee','Tuxechana'],
 3:['McHenry Community Center','Flint Creek','Big Level','Pleasant Hill','TOTAL','','','','','',''],
}
STONE={
 2:{
 E:[20,41,103,108,403,578,65,40,55,38,112],
 H:[105,267,379,353,264,220,251,350,356,352,949],
 J:[4,11,12,15,11,6,11,14,10,9,24],
 },
 3:{
 E:[178,166,111,33,2051,None,None,None,None,None,None],
 H:[428,620,528,187,5609,None,None,None,None,None,None],
 J:[23,15,22,11,198,None,None,None,None,None,None],
 },
}
if __name__=='__main__':
 build('tunica','tunica',TUNICA,TUNICA_LABELS,12,'v2')
 build('stone','stone',STONE,STONE_LABELS,15,'v2')
