"""Preserve literal unofficial/official pages and a primary source discrepancy."""
import json
from acquire_sources import OUT
from record_native_review import record

def main():
 labels=['Courthouse','Damascus','Farmers Market','Fort Stephens','Kellis Store','Kemper Springs','Library','Little Rock Comm Ctr','Lynville','Mount Nebo','Porterville'];a=[348,74,24,42,119,89,234,259,74,130,321];b=[153,228,36,183,57,17,126,208,182,73,123]
 record('kemper',[(6,labels,a,b,None),(7,labels,a,b,None),(8,['Preston','Scooba A-L','Scooba M-Z','TOTAL']+['']*7,[164,208,148,2234]+[None]*7,[176,134,128,1824]+[None]*7,4)],physical_pages=[6,7,8])
 f=OUT/'native-reviewed-2024.json';d=json.loads(f.read_text());s=d['sources']['sos-2024-county-kemper'];p=next(p for p in s['pages'] if p['page']==6)
 p['source_presentation']='Original PDF p6 prints Unofficial Recapitulation, footer Page1; PDF p7 prints Official Recapitulation, footer Page2; same eleven headers and two Senate vectors independently directly read. Both retained; p6 is non-additive parallel observation, no chronology or crossyear identity inference.'
 for c in p['columns']:c['role']='parallel_native_observation';c['source_view_qualification']=p['source_presentation']
 f.write_text(json.dumps(d,indent=2)+'\n')
 record('tunica',[(7,['Austin Park','Dundee Community\nCenter','Hambrick','Mhoon Landing','New Sub Park','Robinsonville\nCommunity Center','Tunica','Tunica Auditorium','Tunica Economic\nComplex','Verner Park','White Oak Rec.\nCenter'],[30,226,202,7,225,168,129,212,126,169,195],[38,95,10,60,47,27,265,44,111,34,50],None),(8,['Workforce Center','TOTAL']+['']*9,[108,1797]+[None]*9,[46,827]+[None]*9,2)],physical_pages=[7])
 d=json.loads(f.read_text());d['sources']['sos-2024-county-tunica']['county_control_qualification']=dict(source_minus_county_primary={'Ty Pinkins':-1,'Roger F. Wicker':0},basis='Native SEMS PDF pp7–8 directly sum and print1797/827; county CSV and original ES&S summary PDFp3 print1798/827. Explicit primary presentation disagreement; one Pinkins vote is not allocated to any native unit or repaired. Source release chronology/cause unknown.',other_primary_evidence='data/turnout/canvass-summary-readings.json')
 f.write_text(json.dumps(d,indent=2)+'\n')
if __name__=='__main__':main()
