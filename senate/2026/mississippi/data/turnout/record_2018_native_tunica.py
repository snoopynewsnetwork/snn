"""Direct complete original 2018 Tunica November6 special / November27 runoff."""
from record_2018_native_manual_original import build

HEADERS={
 2:['Banks/Hambrick','Mhoon Landing','New Sub Park','Prichard',
    'Robinsonville\nCommunity Center','Tunica','Tunica Auditorium',
    'Tunica Co. Supt. of\nEduc.','Two Mile Lake','Westend Store',
    'White Oak Rec.\nCenter'],
 3:['Win Job Center','TOTAL','','','','','','','','',''],
}
STAGES=[
 dict(source_id='sos-2018-county-tunica',date='2018-11-06',
      office='United States-Senate Special',
      candidate_order=['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel'],
      candidate_values={
       'Tobey Bernard Bartee':{2:[2,2,5,3,23,9,13,13,7,0,5],
                               3:[6,88,None,None,None,None,None,None,None,None,None]},
       'Mike Espy':{2:[136,7,173,200,182,178,200,107,236,24,194],
                    3:[88,1725,None,None,None,None,None,None,None,None,None]},
       'Cindy Hyde-Smith':{2:[2,42,98,15,26,158,27,58,53,23,58],
                           3:[26,586,None,None,None,None,None,None,None,None,None]},
       'Chris McDaniel':{2:[0,9,20,5,8,30,5,22,20,7,8],
                         3:[9,143,None,None,None,None,None,None,None,None,None]},
      }),
 dict(source_id='sos-2018-runoff-county-tunica',date='2018-11-27',
      office='United States-Senate Unexpired Term',
      candidate_order=['Mike Espy','Cindy Hyde-Smith'],
      candidate_values={
       'Mike Espy':{2:[133,9,202,222,211,193,253,134,244,30,218],
                    3:[88,1937,None,None,None,None,None,None,None,None,None]},
       'Cindy Hyde-Smith':{2:[2,45,104,14,16,160,16,68,55,24,49],
                           3:[25,578,None,None,None,None,None,None,None,None,None]},
      }),
]
LABELS={stage['source_id']:HEADERS for stage in STAGES}

if __name__=='__main__':build('Tunica','28143',STAGES,LABELS,12,3,2)
