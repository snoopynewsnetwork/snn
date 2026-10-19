"""Direct original Noxubee 2018 special and runoff Senate grids."""
from record_2018_native_manual_original import build

SPECIAL=['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel']
RUNOFF=['Mike Espy','Cindy Hyde-Smith']
HEADERS={2:['Brooksville','Cliftonville','District 3 Central','EARL NASH GYM',
            'Mashulaville','Prairie Point','Shuqualak','Summerville','TOTAL','','']}
LABELS={sid:HEADERS for sid in ('sos-2018-county-noxubee','sos-2018-runoff-county-noxubee')}
STAGES=[
 dict(source_id='sos-2018-county-noxubee',date='2018-11-06',office='United States-Senate Special',candidate_order=SPECIAL,candidate_values={
  'Tobey Bernard Bartee':{2:[29,11,24,16,1,15,7,0,103,None,None]},
  'Mike Espy':{2:[502,295,657,620,118,215,364,28,2799,None,None]},
  'Cindy Hyde-Smith':{2:[218,26,130,151,125,86,91,64,891,None,None]},
  'Chris McDaniel':{2:[34,16,20,33,21,22,19,15,180,None,None]},
 }),
 dict(source_id='sos-2018-runoff-county-noxubee',date='2018-11-27',office='United States-Senate Unexpired Term',candidate_order=RUNOFF,candidate_values={
  'Mike Espy':{2:[589,343,752,698,116,263,433,23,3217,None,None]},
  'Cindy Hyde-Smith':{2:[201,24,118,153,135,93,100,76,900,None,None]},
 }),
]

if __name__=='__main__':build('Noxubee','28103',STAGES,LABELS,8,2,9)
