"""Independent complete original headers and both Senate rows; no count fitting."""
import json,gzip
from record_native_review import record
from acquire_sources import BASE
def main():
 record('holmes',[(2,['1 Acona','1 Durant St Anderson','Beat 1 Lexington','Beat 2 Durant','Beat 2 Sub Durant','Beat 2 West','Beat 3 Coxburg (A-Z)','Beat 3 Ebenezer','Beat 3 Goodman','Beat 3 Pickens','Beat 4 Lexington'],[372,150,626,296,318,223,40,162,353,484,807],[65,35,120,115,69,130,124,80,80,71,153],None),(3,['Beat 4 Thornton (A-Z)','Beat 4 Walden Chapel (A-Z','Beat 5 Cruger (A-Z)','Beat 5 Lexington (A-Z)','Beat 5 Tchula','TOTAL']+['']*5,[197,121,156,226,695,5226]+[None]*5,[41,17,67,163,126,1456]+[None]*5,6)],physical_pages=[2])
 record('issaquena',[(1,['Addie Voting Precinct','Grace Voting Precinct','Mayersville Courthouse','Tallula Community Center','Valley Park Community Center','TOTAL']+['']*5,[74,44,111,49,13,291]+[None]*5,[60,84,10,86,64,304]+[None]*5,6)])
 record('montgomery',[(5,['DUCK HILL','EAST WINONA','KILMICHAEL','Lodi','NORTH DUCK HILL','NORTH KILMICHAEL','NORTH MT PISGAH SWEETHOME','NORTH WINONA','Nations','Poplar Creek','SOUTH WINONA'],[148,268,174,108,100,54,35,139,18,10,451],[277,193,215,58,234,23,72,480,243,76,218],None),(6,['SOUTHEAST WINONA','Stewart','WEST WINONA','TOTAL']+['']*7,[75,10,88,1678]+[None]*7,[87,75,420,2671]+[None]*7,4)])
 gg={}
 for n in [2,3]:
  g=json.loads(gzip.decompress((BASE/f'data/baselines/extracts/native-v4/sos-2024-county-tallahatchie/p{n:04d}.json.gz').read_bytes()));gg[n]=g['grid_x'][1:-1]
 record('tallahatchie',[(2,['Blue Cane','Cascilla','Charleston Beat #1','Charleston Beat #2','Charleston Beat #3','Enid','Glendora','Murphreesboro','Paynes','Phillip','Rosebloom'],[187,66,232,466,217,79,188,16,18,87,9],[74,229,211,276,150,228,18,166,139,48,110],None),(3,['Springhill','Sumner Beat #2','Sumner Beat #5','Teasdale','Tippo','Tutwiler','Webb Beat #4','Webb Beat #5','TOTAL','',''],[16,68,78,55,80,358,67,259,2546,None,None],[135,146,46,233,122,66,19,62,2478,None,None],9)],physical_x_overrides=gg)
if __name__=='__main__':main()
