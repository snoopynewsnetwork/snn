"""Independent full-original Union Nov6 special and Nov27 runoff reading."""
from record_2018_native_manual_original import build

HEADERS={
 2:['Macedonia','Blythe','Myrtle','Glenfield','Pinedale','West Union',
    'Sportsplex','Ingomar',"King's Chapel",'Courthouse','Central Maintenance'],
 3:['Beacon Hill','Blue Springs','Hillcrest Church','Center','East Union',
    'NE Community\nCollege','Keownville','Pleasant Ridge','Jericho','TOTAL',''],
}
STAGES=[
 dict(source_id='sos-2018-county-union',date='2018-11-06',
      office='United States-Senate Special',
      candidate_order=['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel'],
      candidate_values={
       'Tobey Bernard Bartee':{
        2:[1,1,8,4,0,1,3,6,5,7,3],
        3:[1,2,9,1,2,6,4,1,2,67,None]},
       'Mike Espy':{
        2:[13,22,119,87,16,28,201,87,39,124,59],
        3:[91,43,161,11,89,228,21,16,18,1473,None]},
       'Cindy Hyde-Smith':{
        2:[119,78,353,268,150,249,317,301,167,321,361],
        3:[268,194,213,162,308,427,237,100,145,4738,None]},
       'Chris McDaniel':{
        2:[59,47,196,87,74,124,131,176,93,86,147],
        3:[120,85,65,72,124,152,104,41,66,2049,None]},
      }),
 dict(source_id='sos-2018-runoff-county-union',date='2018-11-27',
      office='United States-Senate Unexpired Term',
      candidate_order=['Mike Espy','Cindy Hyde-Smith'],
      candidate_values={
       'Mike Espy':{
        2:[7,22,135,108,16,34,239,105,36,129,74],
        3:[88,30,183,13,102,227,26,13,17,1604,None]},
       'Cindy Hyde-Smith':{
        2:[170,119,499,322,212,339,415,433,246,397,488],
        3:[365,281,257,239,417,549,316,133,212,6409,None]},
      }),
]
LABELS={s['source_id']:HEADERS for s in STAGES}

if __name__=='__main__':build('Union','28145',STAGES,LABELS,20,3,10)
