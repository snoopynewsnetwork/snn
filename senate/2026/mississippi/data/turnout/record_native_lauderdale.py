"""Independent original SEMS pages7-10; summary/method panels remain separate."""
import json,re
from record_native_review import record
from acquire_sources import OUT
def main():
 record('lauderdale',[(7,['101 - One','105 - Five','126 - The Landing on 39','127 - Bailey','146 - New Lauderdale','206 - Six','214 - Fourteen','235 - Daleville','237 - East Lauderdale','238 - Marion','240 - Kewanee'],[667,452,193,322,279,737,463,132,313,316,115],[906,847,545,1105,1076,170,93,65,728,378,106],None),(8,['254 - Russell','262 - Toomsuba','303 - Three','313 - Thirteen','329 - Center Hill','331 - Collinsville','343 - Martin','361 - Suqualena','407 - Seven','408 - Eight','409 - Nine'],[276,140,516,398,164,278,52,312,215,403,474],[440,166,138,343,1017,1224,779,1093,51,126,70],None),(9,['410 - Ten','411 - Eleven','412 - Twelve','415 - Fifteen','450 - Pickard','517 - Seventeen','528 - Causeyville','530 - Clarkdale','544 - Meehan','549 - Odom','560 - South Nellieburg'],[133,295,586,566,119,177,38,83,79,150,68],[39,42,58,258,380,269,334,1079,353,206,262],None),(10,['564 - Vimville','565 - Whynot','567 - Zero','583 - Mt Gilead','TOTAL']+['']*6,[290,70,119,149,10139]+[None]*6,[706,356,644,421,16873]+[None]*6,5)],physical_pages=[7,8,9,10])
 p=OUT/'native-reviewed-2024.json';d=json.loads(p.read_text())
 for pg in d['sources']['sos-2024-county-lauderdale']['pages']:
  for c in pg['columns']:
   m=re.match(r'(\d{3}) - ',c['label_literal'])
   if m:c['printed_native_id']=m[1];c['printed_id_scope']='Literal three-digit printed native code scoped to this Lauderdale original and election only.'
 p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
if __name__=='__main__':main()
