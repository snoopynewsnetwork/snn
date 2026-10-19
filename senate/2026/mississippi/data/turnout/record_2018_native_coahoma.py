"""Direct original November6 special and November27 runoff Coahoma grids."""
from record_2018_native_manual_original import build

HEADERS={
 2:['Bobo','Cagle Crossing','Clarksdale\nCourthouse','Clarksdale #2',
    'Clarksdale #3','Clarksdale #4','Clarksdale #4 North','Clarksdale #5',
    'Coahoma','Dublin','Farrell'],
 3:['Friars Point','Jonestown','Lula','Lyon','Rena Lara','Roundaway',
    'Sasse Street Fire\nStation','TOTAL','','',''],
}
STAGES=[
 dict(source_id='sos-2018-county-coahoma',date='2018-11-06',
      office='United States-Senate Special',
      candidate_order=['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel'],
      candidate_values={
       'Tobey Bernard Bartee':{2:[1,0,6,8,6,11,3,17,1,1,1],
                               3:[6,3,2,3,2,0,3,74,None,None,None]},
       'Mike Espy':{2:[60,12,275,469,293,779,78,805,149,41,94],
                    3:[381,375,102,248,35,36,344,4576,None,None,None]},
       'Cindy Hyde-Smith':{2:[21,21,150,365,44,27,47,126,8,50,14],
                           3:[29,5,68,416,85,23,10,1509,None,None,None]},
       'Chris McDaniel':{2:[8,9,51,109,14,16,10,39,1,17,7],
                         3:[6,1,17,114,45,0,4,468,None,None,None]},
      }),
 dict(source_id='sos-2018-runoff-county-coahoma',date='2018-11-27',
      office='United States-Senate Unexpired Term',
      candidate_order=['Mike Espy','Cindy Hyde-Smith'],
      candidate_values={
       'Mike Espy':{2:[63,14,307,522,328,865,90,933,171,52,104],
                    3:[397,440,103,273,31,35,383,5111,None,None,None]},
       'Cindy Hyde-Smith':{2:[29,26,175,422,45,29,53,131,9,61,15],
                           3:[22,4,82,492,120,26,7,1748,None,None,None]},
      }),
]
LABELS={stage['source_id']:HEADERS for stage in STAGES}

if __name__=='__main__':build('Coahoma','28027',STAGES,LABELS,18,3,8)
