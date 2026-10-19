"""Clay2018 Nov6 four-candidate special and Nov27 two-candidate runoff."""
from record_2018_native_manual_original import build

SPECIAL=['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel']
RUNOFF=['Mike Espy','Cindy Hyde-Smith']
HEADERS={
 2:['Cairo','Caradine','Cedar Bluff','Central-West Point','East-West Point',
    'North-West Point','Pheba','Pine Bluff','Siloam','South-West Point','Tibbee'],
 3:['Union Star','Vinton','West-West Point','TOTAL']+['']*7,
}
LABELS={sid:HEADERS for sid in ('sos-2018-county-clay','sos-2018-runoff-county-clay')}
STAGES=[
 dict(source_id='sos-2018-county-clay',date='2018-11-06',office='United States-Senate Special',candidate_order=SPECIAL,candidate_values={
  'Tobey Bernard Bartee':{2:[4,8,0,15,18,15,7,12,6,18,7],3:[8,12,18,148]+[None]*7},
  'Mike Espy':{2:[118,389,17,330,396,563,191,191,228,527,145],3:[209,212,707,4223]+[None]*7},
  'Cindy Hyde-Smith':{2:[115,65,89,214,616,368,143,40,307,183,71],3:[147,133,161,2652]+[None]*7},
  'Chris McDaniel':{2:[25,17,22,65,117,85,51,16,85,42,22],3:[43,34,50,674]+[None]*7},
 }),
 dict(source_id='sos-2018-runoff-county-clay',date='2018-11-27',office='United States-Senate Unexpired Term',candidate_order=RUNOFF,candidate_values={
  'Mike Espy':{2:[140,459,19,395,456,674,212,235,252,664,171],3:[254,245,789,4965]+[None]*7},
  'Cindy Hyde-Smith':{2:[135,69,111,245,689,402,165,46,370,203,82],3:[178,153,188,3036]+[None]*7},
 }),
]

if __name__=='__main__':build('Clay','28025',STAGES,LABELS,14,3,4)
