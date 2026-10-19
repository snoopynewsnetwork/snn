"""Bolivar original SEMS source pages 6–8: each physical column independently read."""
from record_native_review import record
from review_row_geometry import run

def main():
 record('bolivar',[(6,['Benoit','Beulah','Boyle','Choctaw','Cleveland Courthouse','District 3 Road Barn','Duncan-Alligator','East Central\nCleveland','East Cleveland','East Rosedale','Eastgate'],[133,105,210,101,77,261,93,242,588,322,442],[77,30,490,27,122,31,62,13,40,40,46],None),(7,['Gunnison','Longshot','Merigold','Morrison Chapel\nChurch','Mound Bayou','North Cleveland','North West Cleveland','Pace','Renova','Scott','Shaw'],[136,21,131,16,617,300,105,162,195,51,573],[68,48,125,180,82,98,696,49,10,69,116],None),(8,['Shelby','Skene','South Cleveland','Stringtown','West Central\nCleveland','West Cleveland','West Rosedale','Winstonville','TOTAL','',''],[286,8,443,2,146,145,147,142,6200,None,None],[34,147,35,28,499,782,48,9,4101,None,None],9)],physical_pages=[6,7,8]);run('bolivar',[6,7,8])
if __name__=='__main__':main()
