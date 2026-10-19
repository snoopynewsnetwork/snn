"""Direct original Smith 2018 special and runoff native Senate grids."""
from record_2018_native_manual_original import build

SPECIAL=['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel']
RUNOFF=['Mike Espy','Cindy Hyde-Smith']
HEADERS={
 2:['Ag-Complex','Burns','Cedar Grove','Center Ridge','Clear Springs-\nPineville',
    'Lorena - Spinola','Mize','North Raleigh','Polkville','Shady Grove','Summerland'],
 3:['Sylvarena','Taylorsville','Union-New Home','Warren Hill','West Raleigh',
    'White Oak','Zion Hill - New Haven','TOTAL','','',''],
}
LABELS={sid:HEADERS for sid in ('sos-2018-county-smith','sos-2018-runoff-county-smith')}
STAGES=[
 dict(source_id='sos-2018-county-smith',date='2018-11-06',office='United States-Senate Special',candidate_order=SPECIAL,candidate_values={
  'Tobey Bernard Bartee':{2:[4,2,0,0,0,1,0,6,1,0,14],3:[0,2,6,1,1,1,4,43,None,None,None]},
  'Mike Espy':{2:[39,50,44,19,14,32,20,172,26,10,333],3:[13,72,105,269,20,7,125,1370,None,None,None]},
  'Cindy Hyde-Smith':{2:[216,104,51,121,110,137,185,227,277,168,102],3:[75,257,113,21,154,177,211,2706,None,None,None]},
  'Chris McDaniel':{2:[136,41,33,138,61,79,188,99,58,92,92],3:[65,320,133,17,72,73,208,1905,None,None,None]},
 }),
 dict(source_id='sos-2018-runoff-county-smith',date='2018-11-27',office='United States-Senate Unexpired Term',candidate_order=RUNOFF,candidate_values={
  'Mike Espy':{2:[43,55,47,17,10,39,27,204,25,13,357],3:[15,65,123,297,20,14,125,1496,None,None,None]},
  'Cindy Hyde-Smith':{2:[341,144,80,216,176,204,342,276,322,233,157],3:[135,514,220,31,201,233,355,4180,None,None,None]},
 }),
]

if __name__=='__main__':build('Smith','28129',STAGES,LABELS,18,3,8)
