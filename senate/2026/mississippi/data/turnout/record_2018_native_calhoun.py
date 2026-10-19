"""Direct complete original Calhoun 2018 special and runoff p2 grids."""
from record_2018_native_manual_original import build

HEADERS={2:['Banner','Bruce #3','Calhoun City #1','Calhoun City 4',
            'Derma # 4','Derma #5','Northeast Calhoun','Pittsboro #1',
            'Pittsboro #2','Vardaman','TOTAL']}
STAGES=[
 dict(source_id='sos-2018-county-calhoun',date='2018-11-06',
      office='United States-Senate Special',
      candidate_order=['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel'],
      candidate_values={
       'Tobey Bernard Bartee':{2:[2,13,4,4,4,2,6,12,5,8,60]},
       'Mike Espy':{2:[37,155,283,183,57,67,78,282,100,140,1382]},
       'Cindy Hyde-Smith':{2:[192,382,173,454,174,222,317,58,180,275,2427]},
       'Chris McDaniel':{2:[77,123,58,126,45,46,130,20,85,62,772]},
      }),
 dict(source_id='sos-2018-runoff-county-calhoun',date='2018-11-27',
      office='United States-Senate Unexpired Term',
      candidate_order=['Mike Espy','Cindy Hyde-Smith'],
      candidate_values={
       'Mike Espy':{2:[33,178,311,193,63,74,76,315,106,166,1515]},
       'Cindy Hyde-Smith':{2:[254,472,201,534,215,269,424,66,258,353,3046]},
      }),
]
LABELS={stage['source_id']:HEADERS for stage in STAGES}

if __name__=='__main__':build('Calhoun','28013',STAGES,LABELS,10,2,11)
