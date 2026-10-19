"""Original-only transcription of George's distinct 2018 Senate special stages."""
from record_2018_native_manual_original import build

HEADERS={
 2:['Rocky Creek','Multi Mart','Ward','Shipman','Courthouse','Pine Level',
    'Agricola','Howell','Movella','Multi-Purpose','Basin'],
 3:['Davis','Barton','City Hall','Shady Grove','Bexley','Salem',
    'Middle School','Central','Benndale','Broome','Twin Creek'],
 4:['TOTAL','','','','','','','','','',''],
}
STAGES=[
 dict(source_id='sos-2018-county-george',date='2018-11-06',
      office='United States-Senate Special',
      candidate_order=['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel'],
      candidate_values={
       'Tobey Bernard Bartee':{
        2:[13,7,2,1,3,7,7,5,1,2,11],
        3:[3,10,8,12,6,1,17,3,10,3,7],
        4:[139,None,None,None,None,None,None,None,None,None,None]},
       'Mike Espy':{
        2:[74,21,20,33,18,30,68,29,19,18,130],
        3:[22,62,83,37,59,7,155,17,78,5,16],
        4:[1001,None,None,None,None,None,None,None,None,None,None]},
       'Cindy Hyde-Smith':{
        2:[352,55,120,74,86,146,258,128,110,58,233],
        3:[110,256,228,175,95,31,98,49,143,71,97],
        4:[2973,None,None,None,None,None,None,None,None,None,None]},
       'Chris McDaniel':{
        2:[365,87,77,108,68,115,241,101,99,52,251],
        3:[113,198,205,227,117,27,78,68,146,58,65],
        4:[2866,None,None,None,None,None,None,None,None,None,None]},
      }),
 dict(source_id='sos-2018-runoff-county-george',date='2018-11-27',
      office='United States-Senate Unexpired Term',
      candidate_order=['Mike Espy','Cindy Hyde-Smith'],
      candidate_values={
       'Mike Espy':{
        2:[50,19,9,29,18,23,50,15,12,18,134],
        3:[17,49,67,30,52,10,150,15,102,3,17],
        4:[889,None,None,None,None,None,None,None,None,None,None]},
       'Cindy Hyde-Smith':{
        2:[588,132,179,156,124,224,440,207,175,95,394],
        3:[185,402,356,292,165,50,134,103,248,125,126],
        4:[4900,None,None,None,None,None,None,None,None,None,None]},
      }),
]
LABELS={s['source_id']:HEADERS for s in STAGES}

if __name__=='__main__':build('George','28039',STAGES,LABELS,22,4,1)
