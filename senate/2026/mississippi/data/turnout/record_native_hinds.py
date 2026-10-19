"""Full independent original Hinds p2-11 labels and both Senate rows."""
import json,re
from record_native_review import record
from acquire_sources import OUT
def precincts(ns):return ['Precinct '+str(n).zfill(2) for n in ns]
def main():
 record('hinds',[
 (2,['Bolton','Brownsville','Byram 1','Byram 2','Byram 3','Cayuga','Chapel Hill','Clinton 1','Clinton 2','Clinton 3','Clinton 4'],[636,177,1571,966,1037,165,300,479,867,853,540],[310,222,370,755,260,95,313,654,1232,787,339],None),
 (3,['Clinton 5','Clinton 6','Clinton 7','Cynthia','Dry Grove','Edwards','Learned','Old Byram','Pinehaven','Pocahontas','Precinct 01'],[313,693,623,328,257,945,160,820,1060,278,421],[499,446,815,67,462,433,324,577,1197,186,112],None),
 (4,precincts([2,4,6,8,9,10,11,13,14,16,18]),[97,245,257,253,384,156,229,556,301,748,218],[16,18,62,228,385,16,16,47,363,368,20],None),
 (5,precincts([19,20,21,22,23,25,26,27,28,29,30]),[218,239,512,739,460,579,772,663,531,310,249],[16,22,44,53,39,53,99,48,49,25,19],None),
 (6,precincts(list(range(31,42))),[408,215,165,291,304,503,433,424,500,634,907],[31,420,660,933,828,166,132,47,41,55,80],None),
 (7,precincts([42,43,44,45,46,47,49,51,54,55,56]),[590,840,870,665,1387,228,523,680,192,298,131],[70,77,286,545,597,43,18,54,13,33,19],None),
 (8,precincts([57,58,59,60,61,62,63,64,68,69,70]),[320,609,459,161,224,649,197,188,1022,503,195],[26,37,47,17,29,65,18,24,94,59,29],None),
 (9,precincts([71,72,73,74,76,77,78,79,80,81,82]),[324,243,276,306,262,486,524,917,886,1183,710],[48,23,44,48,49,111,358,146,73,82,42],None),
 (10,precincts([83,84,85,86,88,90,91,92,93,94,96]),[1522,138,1209,623,686,1150,1186,1027,533,1551,894],[86,8,87,44,66,119,147,134,57,180,219],None),
 (11,['Raymond 1','Raymond 2','Springridge','St Thomas','Terry 1','Terry 2','Tinnin','Utica 1','Utica 2','TOTAL',''],[557,677,1525,264,962,1132,279,268,405,60625,None],[892,947,816,39,316,1525,731,289,121,25901,None],10)])
 f=OUT/'native-reviewed-2024.json';d=json.loads(f.read_text())
 for p in d['sources']['sos-2024-county-hinds']['pages']:
  for c in p['columns']:
   m=re.fullmatch(r'Precinct (\d{2})',c['label_literal'])
   if m:c['printed_native_id']=m[1];c['printed_id_scope']='Printed two-digit Precinct code scoped to this Hinds original/election; municipal names remain literal distinct source constituents.'
 f.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
if __name__=='__main__':main()
