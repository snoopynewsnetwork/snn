"""Direct original Quitman 2018 special and runoff Senate source columns."""
from record_2018_native_manual_original import build

SPECIAL=['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel']
RUNOFF=['Mike Espy','Cindy Hyde-Smith']
HEADERS={2:['Crenshaw','Crowder','Darling','District 3 North','District 3 South',
            'Lambert','North West Marks','Sledge','South West Marks','West Lambert','TOTAL']}
LABELS={sid:HEADERS for sid in ('sos-2018-county-quitman','sos-2018-runoff-county-quitman')}
STAGES=[
 dict(source_id='sos-2018-county-quitman',date='2018-11-06',office='United States-Senate Special',candidate_order=SPECIAL,candidate_values={
  'Tobey Bernard Bartee':{2:[4,3,2,4,3,6,8,10,9,6,55]},
  'Mike Espy':{2:[72,35,92,181,174,206,284,239,183,177,1643]},
  'Cindy Hyde-Smith':{2:[2,120,21,116,125,32,62,31,42,50,601]},
  'Chris McDaniel':{2:[1,33,10,25,17,4,20,11,6,14,141]},
 }),
 dict(source_id='sos-2018-runoff-county-quitman',date='2018-11-27',office='United States-Senate Unexpired Term',candidate_order=RUNOFF,candidate_values={
  'Mike Espy':{2:[95,31,110,160,151,225,322,279,201,214,1788]},
  'Cindy Hyde-Smith':{2:[1,157,25,127,129,38,72,31,54,50,684]},
 }),
]

if __name__=='__main__':build('Quitman','28119',STAGES,LABELS,10,2,11)
