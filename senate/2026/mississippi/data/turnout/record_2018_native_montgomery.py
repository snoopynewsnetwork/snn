"""Direct complete-original Montgomery 2018 special and runoff grids."""
from record_2018_native_manual_original import build

SPECIAL=['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel']
RUNOFF=['Mike Espy','Cindy Hyde-Smith']
HEADERS={
 2:['DUCK HILL','EAST WINONA','KILMICHAEL','Lodi','Mt. Pisgah',
    'NORTH DUCK HILL','NORTH KILMICHAEL','NORTH MT PISGAH\nSWEETHOME',
    'NORTH WINONA','Nations','Poplar Creek'],
 3:['SOUTH WINONA','SOUTHEAST WINONA','Stewart','WEST WINONA','TOTAL']+['']*6,
}
LABELS={sid:HEADERS for sid in ('sos-2018-county-montgomery','sos-2018-runoff-county-montgomery')}
STAGES=[
 dict(source_id='sos-2018-county-montgomery',date='2018-11-06',office='United States-Senate Special',candidate_order=SPECIAL,candidate_values={
  'Tobey Bernard Bartee':{2:[4,10,6,1,0,3,2,0,2,1,1],3:[20,3,0,2,55]+[None]*6},
  'Mike Espy':{2:[135,244,165,101,11,88,52,38,101,26,7],3:[460,51,7,96,1582]+[None]*6},
  'Cindy Hyde-Smith':{2:[160,143,178,33,83,64,14,47,411,117,56],3:[160,56,42,282,1846]+[None]*6},
  'Chris McDaniel':{2:[50,29,34,12,23,15,0,19,69,32,11],3:[38,14,15,54,415]+[None]*6},
 }),
 dict(source_id='sos-2018-runoff-county-montgomery',date='2018-11-27',office='United States-Senate Unexpired Term',candidate_order=RUNOFF,candidate_values={
  'Mike Espy':{2:[144,277,165,118,11,88,58,43,104,20,5],3:[514,55,4,103,1709]+[None]*6},
  'Cindy Hyde-Smith':{2:[176,140,196,38,115,64,10,51,437,145,70],3:[154,68,56,316,2036]+[None]*6},
 }),
]

if __name__=='__main__':build('Montgomery','28097',STAGES,LABELS,15,3,5)
