"""Direct-original native Senate/header readings, explicit source-specific grids."""
from record_native_review import record
from own_page_geometry import geometry,evidence

def main():
 g={p:geometry('choctaw',p,635,1908,[220,443],{'Ty Pinkins':(1160,1222),'Roger F. Wicker':(1222,1278)},rotation_override=0,candidate_header_grid=True) for p in [2,3]}
 record('choctaw',[(2,['Bywy','Chester','District 5','East Weir','French Camp','Hebron','Kenego','Panhandle','Reform','Sherwood','Southwest Ackerman'],[39,133,131,157,29,18,8,75,73,14,188],[139,370,692,64,266,187,232,136,227,330,65],None),(3,['West Weir','TOTAL']+['']*9,[72,937]+[None]*9,[158,2866]+[None]*9,2)],page_overrides=g);evidence('choctaw',[2,3])
 record('claiborne',[(2,['County Precinct 1-A','County Precinct 1-B','County Precinct 2-A','County Precinct 2-B','County Precinct 3-A','County Precinct 3-B','County Precinct 3-C','County Precinct 4-A','County Precinct 4-B','County Precinct 4-D','County Precinct 5-A'],[430,184,323,166,371,14,130,273,273,22,329],[90,9,64,61,93,20,95,31,65,61,69],None),(3,['County Precinct 5-B','TOTAL']+['']*9,[328,2843]+[None]*9,[61,719]+[None]*9,2)])
 g={3:geometry('jasper',3,627,1892,[229,446],{'Ty Pinkins':(1164,1224),'Roger F. Wicker':(1224,1283)},rotation_override=0,candidate_header_grid=True)}
 record('jasper',[(2,['Antioch','Bay Springs Beat 3','Bay Springs Beat 4','Claiborne','Heidelberg','Holders','Louin','Montrose','Moss','Paulding','Rose Hill'],[80,429,293,230,906,215,268,117,168,616,268],[245,389,345,179,232,250,246,147,562,314,389],None),(3,['Stringer','TOTAL']+['']*9,[56,3646]+[None]*9,[891,4189]+[None]*9,2)],page_overrides=g);evidence('jasper',[3])
if __name__=='__main__':main()
