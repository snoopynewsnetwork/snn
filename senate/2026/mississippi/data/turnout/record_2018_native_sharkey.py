"""Direct complete original Sharkey 2018 distinct Senate special stages."""
from record_2018_native_manual_original import build

HEADERS={2:['Anguilla Fifth District','Anguilla Fourth\nDistrict',
            'Cary Second District','Delta City Fifth\nDistrict',
            'Rolling Fork First\nDistrict','Rolling Fork Fourth\nDistrict',
            'Rolling Fork Second\nDistrict','Rolling Fork Third\nDistrict',
            'Spanish Fort First\nDistrict','Straight Bayou\nFourth District','TOTAL']}
STAGES=[
 dict(source_id='sos-2018-county-sharkey',date='2018-11-06',
      office='United States-Senate Special',
      candidate_order=['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel'],
      candidate_values={
       'Tobey Bernard Bartee':{2:[3,2,2,1,3,4,0,3,0,1,19]},
       'Mike Espy':{2:[154,140,166,118,196,66,43,255,3,30,1171]},
       'Cindy Hyde-Smith':{2:[18,98,54,61,206,1,1,17,19,40,515]},
       'Chris McDaniel':{2:[6,12,13,10,10,1,0,3,5,8,68]},
      }),
 dict(source_id='sos-2018-runoff-county-sharkey',date='2018-11-27',
      office='United States-Senate Unexpired Term',
      candidate_order=['Mike Espy','Cindy Hyde-Smith'],
      candidate_values={
       'Mike Espy':{2:[158,156,180,121,182,67,42,249,2,35,1192]},
       'Cindy Hyde-Smith':{2:[23,91,47,69,184,1,0,14,24,43,496]},
      }),
]
LABELS={stage['source_id']:HEADERS for stage in STAGES}

if __name__=='__main__':build('Sharkey','28125',STAGES,LABELS,10,2,11)
