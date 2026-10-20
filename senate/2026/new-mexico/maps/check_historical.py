"""Independently reopen original contest CSVs, preserving all literal fields and scopes."""
from common import *
import csv,io,collections

def run():
 ex=json.loads((S/'data/turnout/original-extract.json').read_bytes());receipts=json.loads((S/'data/turnout/acquisition.json').read_bytes());out=[];checks=0
 for contest,count in [('2020-senate',1959),('2024-senate',2201),('2024-president',2202),('2022-governor',2196)]:
  x=ex[contest];r=next(r for r in receipts if r['id']==x['source_id']);z=(S/r['asset']).read_bytes();assert sha(z)==r['stored_sha256'];b=gzip.decompress(z)if r.get('compression')=='gzip'else z;assert sha(b)==r['raw_sha256']==x['raw_sha256'];actual=list(csv.reader(io.StringIO(b.decode('utf-8-sig'))));assert actual[:2]==x['header_rows'];checks+=3
  for row in x['rows']:
   raw=actual[row['source_row_1based']-1];assert raw==row['raw_row'];checks+=1
   for f in row['fields']:
    literal=raw[f['column_1based']-1];assert f['literal']==literal and f['party_literal']==actual[1][f['column_1based']-1]and f['label']==actual[0][f['column_1based']-1]
    value=int(literal)if literal.isdigit()else None;assert f['value']==value;checks+=2
  natives=[r for r in x['rows']if r['level']=='Precinct'];counties=[r for r in x['rows']if r['level']=='County'];assert len(natives)==count and len(counties)==33 and sum(r['administrative']for r in natives)==33;checks+=3
  out.append({'contest':contest,'contest_id':x['contest_id'],'native_rows':count,'county_rows':33,'administrative':33,'complete_header_party_rows':actual[:2],'complete_source_rows':len(actual),'original_CSV_receipt':r,'full_extraction_reference':pin(S/'data/turnout/original-extract.json'),'all_fields_literal_roundtrip':True})
 sen={(r['county_literal'],r['native_label'])for r in ex['2024-senate']['rows']if r['level']=='Precinct'};pres={(r['county_literal'],r['native_label'])for r in ex['2024-president']['rows']if r['level']=='Precinct'};assert pres-sen=={('Otero','18')}and not sen-pres;checks+=1
 write(M/'historical-source-checks.json',{'status':'pass','checks':checks,'contests':out,'president_only_Otero18':'absent Senate, no Senate zero inferred','cross_year_or_geometry_join':None,'all_PDF_controls_and_originals':'whole immutable bodies retained through immutable-inputs; no new candidate/control allocation or numeric PDF certification claimed by maps'})
 print('Historical original CSV checks',checks)
if __name__=='__main__':run()
