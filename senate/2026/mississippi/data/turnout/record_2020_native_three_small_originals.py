"""Wilkinson, Issaquena, Noxubee 2020 full original Senate grids."""
from record_2020_native_manual_original import build
E='Mike Espy';H='Cindy Hyde-Smith';J='Jimmy L. Edwards'
WILKINSON_LABELS={2:['Centreville 1st 1020','Centreville 3rd 3010','Cold Springs 4020','Fort Adams 2020','Longmire 5020','Woodville  5th 5010','Woodville  4th 4010','Woodville 1010','Woodville  2nd 2010','TOTAL','']}
WILKINSON={2:{
 E:[372,445,98,245,144,298,508,216,376,2702,None],
 H:[83,289,102,69,210,205,95,130,112,1295,None],
 J:[13,10,3,3,9,14,10,5,13,80,None],
}}
ISSAQUENA_LABELS={2:['Addie Voting Precinct','Grace Voting Precinct','Mayersville\nCourthouse','Tallula Community\nCenter','Valley Park\nCommunity Center','TOTAL','','','','','']}
ISSAQUENA={2:{
 E:[79,51,157,60,20,367,None,None,None,None,None],
 H:[63,84,12,83,67,309,None,None,None,None,None],
 J:[0,1,2,1,1,5,None,None,None,None,None],
}}
NOXUBEE_LABELS={2:['Brooksville','Cliftonville','District 3 Central','Mashulaville','Noxubee Human\nResource Bldg','Prairie Point','Shuqualak','Summerville','TOTAL','','']}
NOXUBEE={2:{
 E:[777,424,1047,157,799,355,542,37,4138,None,None],
 H:[259,27,153,192,186,138,123,100,1178,None,None],
 J:[6,1,6,1,1,1,5,0,21,None,None],
}}
if __name__=='__main__':
 build('wilkinson','wilkinson',WILKINSON,WILKINSON_LABELS,9)
 build('issaquena','issaquena',ISSAQUENA,ISSAQUENA_LABELS,5)
 build('noxubee','noxubee',NOXUBEE,NOXUBEE_LABELS,8)
