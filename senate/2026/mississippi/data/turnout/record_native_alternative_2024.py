"""Independently read alternative county originals; no cross-vintage native join."""
import json,re
from acquire_sources import OUT
from record_native_review import record
from own_page_geometry import geometry,evidence

def main():
 g={p:geometry('coahoma',p,690,1960,[226,446],{'Ty Pinkins':(1158,1221),'Roger F. Wicker':(1221,1277)},candidate_header_grid=True) for p in [2,3]}
 record('coahoma',[(2,['Bobo','Cagle Crossing','Clarksdale\nCourthouse','Clarksdale #2','Clarksdale #3','Clarksdale #4','Clarksdale #4 North','Clarksdale #5','Coahoma','Dublin','Farrell'],[61,18,299,515,284,838,76,743,138,55,88],[41,29,188,438,67,73,50,166,30,66,39],None),(3,['Friars Point','Jonestown','Lula','Lyon','Rena Lara','Roundaway','Sasse Street Fire\nStation','TOTAL','','',''],[277,389,96,254,32,26,344,4533,None,None,None],[49,33,112,574,143,29,19,2146,None,None,None],8)],page_overrides=g);evidence('coahoma',[2,3])
 record('pike',[(2,['(01) New Hope\nBaptist Church','(02) S MCCOMB\nBAPTIST CHURCH','(03) Summit United\nMethodist Church','(04) Mlk Center','(05) North McComb\nBaptist Church','(06) Presley Event\nCenter','(07) St Mary Free\nWill Bapt. Ch.','(08) Fernwood\nBaptist Church','(09) Magnolia Comm\nCtr.','(10) Braswell\nEducation Complex','(11) St. James Miss.\nBapt. Church'],[394,160,214,383,216,173,338,345,348,347,162],[45,40,87,28,236,17,103,184,164,270,111],None),(3,['(12) Navilla Baptist\nChurch Fellowship','(13) Holmesville\nComm.','(14) Calvary Baptist\nChurch','(15) Friendship Bapt.\nChurch','(16) Summit City\nHall','(17) SMCC Work\nForce Training Ctr','(18) Johnston Chapel\nMeth. Church','(19) Pisgah\nMethodist Church','(20) Pike Co. Nat.\nBank','(21) Old Progress\nVolunteer Fire Station','(22) Church of Christ'],[308,203,154,91,167,242,112,138,227,332,376],[445,328,446,447,124,671,766,561,171,334,236],None),(4,['(23) West McComb\nBapt. Church','(24) Our Lady of\nHope','(25) Osyka City Hall','TOTAL']+['']*7,[171,218,79,5898]+[None]*7,[292,405,208,6719]+[None]*7,4)])
 f=OUT/'native-reviewed-2024.json';d=json.loads(f.read_text());s=d['sources']['sos-2024-county-pike'];s['county_control_qualification']=dict(source_minus_county_primary={'Ty Pinkins':-1232,'Roger F. Wicker':-1486},basis='This retained ORIGINAL packet prints/sums5898/6719, also original ES&S summaryp13 and old statewideCSV. Explicit UPDATED packet nativep2–4/printedTOTALp4 gives7130/8205 and matches signed statewide certificate replacement. Parallel vintages not additive; no chronology/reason or native-ID equivalence inferred.',other_primary_evidence='data/turnout/canvass-summary-readings.json')
 for pg in s['pages']:
  for c in pg['columns']:
   if c['role']=='native_reporting_constituent':c['printed_native_id']=re.match(r'\((\d{2})\)',c['label_literal'])[1];c['printed_id_scope']='Literal printed parenthesized source code; original packet only; no cross-vintage/current geometry equivalence.'
 f.write_text(json.dumps(d,indent=2)+'\n')
if __name__=='__main__':main()
