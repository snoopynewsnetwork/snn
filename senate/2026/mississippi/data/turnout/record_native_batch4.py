"""Independent original native labels, Senate vectors, TOTAL and unused roles."""
import gzip,json
from record_native_review import record
from acquire_sources import BASE
def main():
 record('benton',[(2,['Ashland Precinct District 3','Canaan Precinct District 1','Floyd Precinct Dist 4','Hickory Flat Prec Dist 5','Lamar Precinct District 2','TOTAL']+['']*5,[264,331,145,106,434,1280]+[None]*5,[495,398,611,766,252,2522]+[None]*5,6)])
 g=json.loads(gzip.decompress((BASE/'data/baselines/extracts/native-v4/sos-2024-county-calhoun/p0002.json.gz').read_bytes()))
 record('calhoun',[(2,['Banner #3','Bruce #3','Calhoun City #1','Calhoun City #4','Derma #4','Derma #5','Northeast Calhoun #2','Pittsboro #1','Pittsboro #2','Vardaman #5','TOTAL'],[43,177,353,169,67,84,93,260,105,161,1512],[344,746,316,649,287,370,621,80,426,563,4402],11)],physical_x_overrides={2:g['grid_x']})
 record('franklin',[(2,['Antioch','Bad Bayou','Bude','Cains','Eddiceton','Hamburg','Knoxville','Lucien','Mccall','Meadville','Pine Grove'],[102,13,329,40,24,158,51,22,47,86,10],[176,344,290,194,251,69,119,173,280,280,138],None),(3,['Roxie','Wesley Chapel','Whittington','TOTAL']+['']*7,[224,60,37,1203]+[None]*7,[175,111,252,2852]+[None]*7,4)])
 record('sharkey',[(2,['Anguilla Fifth District','Anguilla Fourth District','Cary Second District','Delta City Fifth District','Rolling Fork First District','Rolling Fork Fourth District','Rolling Fork Second District','Rolling Fork Third District','Spanish Fort First District','Straight Bayou Fourth District','TOTAL'],[128,166,194,117,229,76,33,255,3,28,1229],[33,104,70,88,167,1,2,27,21,43,556],11)])
if __name__=='__main__':main()
