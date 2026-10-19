"""Independent direct-original review of larger 2024 native source views."""
import json,re
from record_native_review import record
from acquire_sources import OUT

def main():
 record('jackson',[(2,['Big Point','Carterville','East Central','Eastlawn','Escatawpa','Fair','Fontainebleau','Gautier North','Gautier South','Grace Baptist Church','Gulf Park Estates'],[116,20,327,348,486,1175,1037,576,888,776,589],[1454,414,3980,1318,1480,713,2714,816,1417,2002,1615],None),(3,['Hickory Hills','Hwy 57','Ingalls Avenue Baptist Church','Jefferson Street','Larue','Latimer','North Pascagoula','North Vancleave','OS Civic Ctr','OS Senior Center','Orange Grove'],[466,21,318,858,19,495,49,252,875,66,111],[1018,373,980,352,239,2308,287,1503,2101,161,686],None),(4,['Pelican Landing','Presbyterian','Ryan Youth Center','South Vancleave','St Martin','Sue Ellen','Villa Maria','West Jackson','YMBC-Dantzler','TOTAL',''],[681,153,483,200,620,1175,117,1025,610,14932,None],[154,726,1097,2167,1672,97,282,2512,421,37059,None],10)])
 record('pike-updated',[(2,['(01) New Hope Baptist Church','(02) S MCCOMB BAPTIST CHURCH','(03) Summit United Methodist Church','(04) Mlk Center','(05) North McComb Baptist Church','(06) Presley Event Center','(07) St Mary Free Will Bapt. Ch.','(08) Fernwood Baptist Church','(09) Magnolia Comm Ctr.','(10) Braswell Education Complex','(11) St. James Miss. Bapt. Church'],[460,172,234,438,271,198,401,431,438,448,194],[58,46,110,33,297,19,142,225,250,339,148],None),(3,['(12) Navilla Baptist Church Fellowship','(13) Holmesville Comm.','(14) Calvary Baptist Church','(15) Friendship Bapt. Church','(16) Summit City Hall','(17) SMCC Work Force Training Ctr','(18) Johnston Chapel Meth. Church','(19) Pisgah Methodist Church','(20) Pike Co. Nat. Bank','(21) Old Progress Volunteer Fire Station','(22) Church of Christ'],[366,241,178,105,209,290,133,206,261,401,453],[556,389,492,516,156,780,876,687,211,444,284],None),(4,['(23) West McComb Bapt. Church','(24) Our Lady of Hope','(25) Osyka City Hall','TOTAL']+['']*7,[219,295,88,7130]+[None]*7,[377,541,229,8205]+[None]*7,4)])
 path=OUT/'native-reviewed-2024.json';d=json.loads(path.read_text())
 for p in d['sources']['sos-2024-county-pike-updated']['pages']:
  for c in p['columns']:
   m=re.match(r'\((\d{2})\)',c['label_literal'])
   if m:c['printed_native_id']=m[1];c['printed_id_scope']='Printed parenthesized precinct code, scoped to this Pike Updated original and election only.'
 path.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')

if __name__=='__main__':main()
