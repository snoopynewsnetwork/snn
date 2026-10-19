"""Complete original native rows: Clarke, Perry and Lawrence."""
import gzip,json
from acquire_sources import BASE,OUT
from record_native_review import record
from own_page_geometry import geometry,evidence

def main():
 record('clarke',[(2,['Beaverdam','Carmichael','Desoto','East Quitman','Energy','Enterprise','HOPEWELL','Harmony  Dist. 1','Harmony  Dist. 2','Langsdale','Manassa'],[110,55,112,136,6,193,66,40,96,29,8],[69,159,101,960,159,947,76,88,198,14,115],None),(3,['North Quitman','Oakgrove','Pachuta','Rolling Creek','Shubuta','Snell','Souinlovie','South Quitman','Springs','Stonewall  Dist. 3','Stonewall Dist. 1'],[73,204,149,23,328,9,17,353,63,66,183],[220,42,114,183,99,146,94,265,57,307,102],None),(4,['Union','TOTAL']+['']*9,[31,2350]+[None]*9,[636,5151]+[None]*9,2)],physical_x_overrides={3:[687,812,936,1062,1187,1312,1438,1562,1687,1811,1935,2058]})
 gg={}
 for p in [2,3]:
  g=json.loads(gzip.decompress((BASE/f'data/baselines/extracts/native-v4/sos-2024-county-perry/p{p:04d}.json.gz').read_bytes()));gg[p]=g['grid_x'][1:-1]
 record('perry',[(2,['Arlington 4100','Beaumont District 1\n1030','Beaumont Voting\nPrecinct 5120','Buck Creek 4110','Courthouse 5110','Deep Creek 5150','Hintonville 4090','Indian Springs 1010','Janice 5140','McSwain Community\nCenter','New Augusta\nCommunity Center'],[64,294,27,5,35,14,75,123,50,74,66],[406,100,108,118,180,68,200,238,471,39,90],None),(3,['Prospect 2050','Richton Holly Street\n3060','Richton Multi Purpose\n4080','Runnelstown 2040','Thompson Hill 5130','TOTAL']+['']*5,[13,108,80,58,3,1089]+[None]*5,[151,1071,211,900,61,4412]+[None]*5,6)],physical_x_overrides=gg)
 record('lawrence',[(2,['Arm','Coopers Creek (A-Z)','Courthouse A-Z','Jayess','New Hebron','Oma','S District 4','Silver Creek','Sontag','Stringer/N Pleasant\nHill','Topeka'],[220,68,175,34,121,191,74,224,166,213,14],[256,522,956,454,445,77,192,165,336,159,202],None),(3,['West District 5','West Monticello (A-Z)','TOTAL']+['']*8,[207,160,1867]+[None]*8,[92,281,4137]+[None]*8,3)],physical_pages=[2])
if __name__=='__main__':main()
