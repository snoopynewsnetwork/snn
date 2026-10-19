"""Complete original 2018 Perry Nov6 and Nov27 Senate stage grids."""
from record_2018_native_manual_original import build

HEADERS={
 2:['Arlington 4100','Beaumont District 1\n1030',
    'Beaumont Senior\nCitizens 5120','Courthouse 5110','Deep Creek 5150',
    'Hintonville 4090','Indian Springs 1010','Janice 5140',
    'Miracle Temple\nCOGIC 1040','New Augusta\nCommunity Center','Prospect 2050'],
 3:['Richton Holly Street\n3060','Richton Multi Purpose\n4080',
    'Runnelstown 2040','Thompson Hill 5130','TOTAL','','','','','',''],
}
STAGES=[
 dict(source_id='sos-2018-county-perry',date='2018-11-06',
      office='United States-Senate Special',
      candidate_order=['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel'],
      candidate_values={
       'Tobey Bernard Bartee':{2:[0,6,0,1,2,1,4,5,2,4,1],
                               3:[8,6,2,0,42,None,None,None,None,None,None]},
       'Mike Espy':{2:[55,246,36,17,7,64,98,53,78,81,16],
                    3:[102,66,33,8,960,None,None,None,None,None,None]},
       'Cindy Hyde-Smith':{2:[195,46,66,99,37,90,73,210,8,59,78],
                           3:[346,115,356,25,1803,None,None,None,None,None,None]},
       'Chris McDaniel':{2:[74,26,20,88,11,29,36,111,6,23,65],
                         3:[388,60,238,18,1193,None,None,None,None,None,None]},
      }),
 dict(source_id='sos-2018-runoff-county-perry',date='2018-11-27',
      office='United States-Senate Unexpired Term',
      candidate_order=['Mike Espy','Cindy Hyde-Smith'],
      candidate_values={
       'Mike Espy':{2:[46,294,39,16,10,69,118,49,92,85,14],
                    3:[114,78,33,2,1059,None,None,None,None,None,None]},
       'Cindy Hyde-Smith':{2:[269,51,85,175,45,117,89,289,10,59,143],
                           3:[669,157,552,44,2754,None,None,None,None,None,None]},
      }),
]
LABELS={stage['source_id']:HEADERS for stage in STAGES}

if __name__=='__main__':build('Perry','28111',STAGES,LABELS,15,3,5)
