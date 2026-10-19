"""Original complete native Senate/header readings, including source code suffixes."""
import json
from acquire_sources import OUT
from record_native_review import record

def main():
 record('webster',[(2,['Bellefontaine','Big Black','Clarkson','Cumberland','Eupora No. 1','Eupora No. 2','Eupora No. 3','Grady','Maben','Mantee','Mathiston No. 3'],[34,10,24,44,367,63,22,43,116,26,51],[327,185,497,276,497,210,123,226,373,331,204],None),(3,['Mathiston No. 4','Tomnolen','Walthall','TOTAL']+['']*7,[21,17,16,854]+[None]*7,[295,338,321,4203]+[None]*7,4)])
 record('pontotoc',[(2,['Algoma Al','Bankhead Ba','Beckham Bec','Bethel/Endville Be','Buchanan Bu','Cherry Creek Cc','Ecru Ec','Friendship Fr','Hoyle Ho','Hurricane Hu','Judah Ju'],[67,224,81,65,38,78,130,34,235,39,21],[544,396,410,539,444,574,646,174,410,421,264],None),(3,['Longview Lo','Oakhill Oh','Pontotoc 1 P1','Pontotoc 2 P2','Pontotoc 3 P3','Pontotoc 4 P4','Pontotoc 5 P5','Randolph','Robbs Ro','Sherman Sh','Springville Sp'],[90,35,61,98,183,104,238,36,15,31,93],[167,286,286,367,649,388,820,709,53,280,647],None),(4,['Thaxton Th','Toccopola To','Troy Tr','Turnpike Tu','Woodland Wo','Zion Z','TOTAL']+['']*4,[54,38,79,29,15,93,2304]+[None]*4,[528,196,505,357,148,348,11556]+[None]*4,7)])
 record('winston',[(2,['American Legion','County Agent','East Winston','Fairground','Lovorn Tractor','Mars Hill','Mill Creek','Nanih Waiya','New National Guard','Noxapater','Shiloh'],[560,730,149,436,152,198,344,161,95,203,94],[148,168,394,952,188,361,722,890,263,517,264],None),(3,['Zion Ridge','TOTAL']+['']*9,[317,3439]+[None]*9,[70,4937]+[None]*9,2)])
 record('leake',[(2,['Conway','East Carthage','Edinburg','Freeny','Good Hope','HARMONY','Lena','Madden','North Carthage','Ofahoma','Renfroe'],[252,153,10,66,94,179,174,69,234,223,50],[137,492,377,374,420,177,183,379,351,80,317],None),(3,['Salem','Singleton','South Carthage','Sunrise','Thomastown','Walnut Grove','West Carthage','Wiggins','TOTAL','',''],[40,143,97,23,184,443,484,198,3116,None,None],[306,432,217,316,193,213,138,127,5229,None,None],9)])
 f=OUT/'native-reviewed-2024.json';d=json.loads(f.read_text())
 for p in d['sources']['sos-2024-county-pontotoc']['pages']:
  for c in p['columns']:
   if c['role']=='native_reporting_constituent' and c['label_literal']!='Randolph':c['printed_native_id']=c['label_literal'].rsplit(' ',1)[1];c['printed_id_scope']='Literal printed suffix code, county/year/source scope only; no crossyear/2026 equivalence.'
 f.write_text(json.dumps(d,indent=2)+'\n')
if __name__=='__main__':main()
