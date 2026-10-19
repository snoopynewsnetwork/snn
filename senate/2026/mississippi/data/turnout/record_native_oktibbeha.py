"""Oktibbeha original native Senate rows; p3 Wicker wrong-row aid superseded."""
from record_native_review import record
from own_page_geometry import geometry,evidence

def main():
 g={3:geometry('oktibbeha',3,634,1906,[222,444],{'Ty Pinkins':(1158,1221),'Roger F. Wicker':(1221,1277)},rotation_override=-90,candidate_header_grid=True)}
 record('oktibbeha',[(2,['Bell Schoolhouse','Central Starkville','Craig Springs','Double Springs','East Starkville','Hickory Grove','Maben','Needmore','North Adaton','North Longview','North Starkville\nDistrict 2'],[170,579,18,59,177,849,94,636,253,209,281],[124,198,181,401,189,835,104,293,313,513,132],None),(3,['North Starkville\nDistrict 3','Oktibbeha Co Storm\nShelter','Oktoc','Osborn','Sessums','South Adaton','South Longview','South Starkville','Sturgis','TOTAL',''],[840,1276,389,520,515,158,49,1092,161,8325,None],[660,1152,367,307,373,245,95,2456,560,9498,None],10)],page_overrides=g);evidence('oktibbeha',[3])
if __name__=='__main__':main()
