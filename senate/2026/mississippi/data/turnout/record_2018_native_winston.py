"""Direct original Winston November6 special and November27 runoff grids."""
from record_2018_native_manual_original import build

HEADERS={
 2:['American Legion','County Agent','East Winston','Fairground',
    'Lovorn Tractor','Mars Hill','Mill Creek','Nanih Waiya',
    'New National Guard','Noxapater','Shiloh'],
 3:['Zion Ridge','TOTAL','','','','','','','','',''],
}
STAGES=[
 dict(source_id='sos-2018-county-winston',date='2018-11-06',
      office='United States-Senate Special',
      candidate_order=['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel'],
      candidate_values={
       'Tobey Bernard Bartee':{2:[13,19,9,15,6,10,5,2,4,10,1],
                               3:[13,107,None,None,None,None,None,None,None,None,None]},
       'Mike Espy':{2:[477,545,126,439,137,181,322,156,56,178,81],
                    3:[298,2996,None,None,None,None,None,None,None,None,None]},
       'Cindy Hyde-Smith':{2:[64,112,269,689,138,174,430,489,171,303,164],
                           3:[36,3039,None,None,None,None,None,None,None,None,None]},
       'Chris McDaniel':{2:[23,30,62,142,50,64,125,135,40,116,57],
                         3:[11,855,None,None,None,None,None,None,None,None,None]},
      }),
 dict(source_id='sos-2018-runoff-county-winston',date='2018-11-27',
      office='United States-Senate Unexpired Term',
      candidate_order=['Mike Espy','Cindy Hyde-Smith'],
      candidate_values={
       'Mike Espy':{2:[522,621,130,478,150,197,335,139,72,199,75],
                    3:[329,3247,None,None,None,None,None,None,None,None,None]},
       'Cindy Hyde-Smith':{2:[82,115,306,763,176,225,513,579,185,371,210],
                           3:[34,3559,None,None,None,None,None,None,None,None,None]},
      }),
]
LABELS={stage['source_id']:HEADERS for stage in STAGES}

if __name__=='__main__':build('Winston','28159',STAGES,LABELS,12,3,2)
