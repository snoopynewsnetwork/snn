"""Three complete original 2020 Senate native grids, read page by page."""
from record_2020_native_manual_original import build
E='Mike Espy';H='Cindy Hyde-Smith';J='Jimmy L. Edwards'

CALHOUN_LABELS={2:['Banner','Bruce #3','Calhoun City #1','Calhoun City 4','Derma # 4','Derma #5','Northeast Calhoun','Pittsboro #1','Pittsboro #2','Vardaman','TOTAL']}
CALHOUN={2:{
 E:[59,255,436,272,77,117,125,394,160,243,2138],
 H:[374,715,290,716,290,359,629,95,390,483,4341],
 J:[8,16,11,16,3,6,19,3,16,14,112],
}}

TISH_LABELS={
 2:['Iuka','Belmont','Burnsville','Coles Mill','Cotton Springs','Dennis','East Iuka','Golden','Hubbard Salem','North Belmont','North Burnsville'],
 3:['Paden','Springhill','Tishomingo','TOTAL','','','','','','',''],
}
TISH={
 2:{
 E:[343,106,107,83,25,24,296,53,17,35,95],
 H:[1391,779,643,452,206,204,917,472,111,257,411],
 J:[55,19,25,8,2,4,43,13,5,12,8],
 },
 3:{
 E:[41,102,267,1594,None,None,None,None,None,None,None],
 H:[207,334,832,7216,None,None,None,None,None,None,None],
 J:[15,18,29,256,None,None,None,None,None,None,None],
 },
}

SMITH_LABELS={
 2:['Ag-Complex','Burns','Cedar Grove','Center Ridge','Clear Springs-\nPineville','Lorena - Spinola','Mize','North Raleigh','Polkville','Shady Grove','Summerland'],
 3:['Sylvarena','Taylorsville','Union-New Home','Warren Hill','West Raleigh','White Oak','Zion Hill - New Haven','TOTAL','','',''],
}
SMITH={
 2:{
 E:[77,90,56,31,23,66,53,264,35,21,435],
 H:[483,197,107,389,252,299,549,402,448,386,220],
 J:[12,2,0,10,5,3,11,18,7,5,0],
 },
 3:{
 E:[21,110,142,339,26,19,169,1977,None,None,None],
 H:[172,708,314,43,317,343,573,6202,None,None,None],
 J:[6,10,13,0,8,5,15,130,None,None,None],
 },
}
if __name__=='__main__':
 build('calhoun','calhoun',CALHOUN,CALHOUN_LABELS,10)
 build('tishomingo','tishomingo',TISH,TISH_LABELS,14)
 build('smith','smith',SMITH,SMITH_LABELS,18)
