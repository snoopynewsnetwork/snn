"""Direct original Kemper special and runoff Senate source grids."""
from record_2018_native_manual_original import build

HEADERS={
 2:['Band Building','Courthouse','Farmers Market','Fort Stevens',
    'Kellis Store','Kemper Springs','LITTLE ROCK\nCOMMUNITY CENTER',
    'Lynville','Lynwood','Mount Nebo','Porterville'],
 3:['Preston','Scooba A-L','Scooba M-Z','TOTAL','','','','','','',''],
}
STAGES=[
 dict(source_id='sos-2018-county-kemper',date='2018-11-06',
      office='United States-Senate Special',
      candidate_order=['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel'],
      candidate_values={
       'Tobey Bernard Bartee':{2:[10,20,2,1,5,2,10,4,3,7,9],
                               3:[2,12,6,93,None,None,None,None,None,None,None]},
       'Mike Espy':{2:[158,277,45,22,90,87,212,90,51,128,258],
                    3:[163,142,130,1853,None,None,None,None,None,None,None]},
       'Cindy Hyde-Smith':{2:[82,114,29,52,19,10,128,117,142,78,78],
                           3:[112,60,65,1086,None,None,None,None,None,None,None]},
       'Chris McDaniel':{2:[32,47,7,27,7,5,28,36,63,23,28],
                         3:[27,33,26,389,None,None,None,None,None,None,None]},
      }),
 dict(source_id='sos-2018-runoff-county-kemper',date='2018-11-27',
      office='United States-Senate Unexpired Term',
      candidate_order=['Mike Espy','Cindy Hyde-Smith'],
      candidate_values={
       'Mike Espy':{2:[201,342,49,25,122,102,238,94,69,155,275],
                    3:[180,192,163,2207,None,None,None,None,None,None,None]},
       'Cindy Hyde-Smith':{2:[95,124,35,72,20,10,147,142,177,92,84],
                           3:[123,70,79,1270,None,None,None,None,None,None,None]},
      }),
]
LABELS={stage['source_id']:HEADERS for stage in STAGES}

if __name__=='__main__':build('Kemper','28069',STAGES,LABELS,14,3,4)
