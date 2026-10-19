"""Independent source-specific native SEMS views in mixed summary packets."""
import gzip,json
from record_native_review import record
from acquire_sources import BASE
def main():
 record('leflore',[(5,['Central Gwd','East Gwd','Minter City','Money','Morgan City','Mvsu','Ne Gwd','North Gwd','North Itta Bena','Rising Sun','Schlater'],[199,896,57,19,69,129,536,586,731,343,92],[52,51,88,89,53,26,121,1852,114,20,117],None),(6,['Sidon','South Gwd','South Itta Bena','Southeast Gwd','Southwest Gwd','Swiftown','West Gwd','TOTAL']+['']*3,[129,199,204,980,243,17,802,6231]+[None]*3,[66,13,59,169,16,20,185,3111]+[None]*3,8)],physical_pages=[6])
 record('attala',[(3,['Berea','Carmack','East','Ethel','Hesterville','Liberty Chapel','Mcadams','Mccool','Newport','North Central','North East'],[13,8,148,83,12,47,124,83,94,40,634],[85,183,506,198,185,180,132,172,154,246,247],None),(4,['North West','Possumneck','Providence','Sallis','South Central','South West','Thompson','Williamsville','Zama','TOTAL',''],[238,66,25,460,255,188,8,292,76,2894,None],[418,126,222,271,368,77,116,706,161,4753,None],10)])
 g=json.loads(gzip.decompress((BASE/'data/baselines/extracts/native-v4/sos-2024-county-grenada/p0003.json.gz').read_bytes()))
 record('grenada',[(3,['Box 1 Southside Church of Christ','Elliott Vol Fire Station','Sweethome Hol#2 Fire Stat','Box 2 Grenada Co Office','Gore Springs Comm Center','Futheyville 1st Pentecost','Box 3 City Auditorium','Mt. Nebo Young Water and Sewer','Pleasant Grove Commun Cen','Box 4 Taylor Hall','Geeslin Friendship Bapt Church'],[519,89,80,238,71,143,856,3,261,1106,108],[1060,424,257,234,458,570,322,103,79,145,582],None),(4,['Holcomb Community Center','Box 5 EOC Building','TOTAL']+['']*8,[155,360,3989]+[None]*8,[517,938,5689]+[None]*8,3)],physical_x_overrides={3:g['grid_x'][1:-1]})
if __name__=='__main__':main()
