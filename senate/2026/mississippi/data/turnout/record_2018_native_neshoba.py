"""Direct complete-original Neshoba Nov6 special and Nov27 runoff grids.

All source candidates, each of three whole source pages, and the distinct
runoff office are transcribed from original rasters before peer comparison.
"""
from record_2018_native_manual_original import build

HEADERS={
 2:['Arlington','Bogue Chitto','Burnside','Center','County Line','Deemer',
    'Dixon','East Neshoba','Fairview','Forestdale','Fork'],
 3:['Fusky','Hays','Herbert','Hope','House','Mcdonald','Neshoba',
    'North Bend','Northeast\nPhiladelphia','Northwest\nPhiladelphia','Pearl River'],
 4:['SOUTH\nPHILADELPHIA','Southeast\nPhiladelphia','Tucker - District One',
    'Tucker - District\nThree','Zephyrhill','TOTAL','','','','',''],
}
STAGES=[
 dict(source_id='sos-2018-county-neshoba',date='2018-11-06',
      office='United States-Senate Special',
      candidate_order=['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel'],
      candidate_values={
       'Tobey Bernard Bartee':{
        2:[1,1,7,1,2,0,6,9,2,2,1],
        3:[1,0,1,1,0,1,2,1,10,22,2],
        4:[3,9,2,3,6,96,None,None,None,None,None]},
       'Mike Espy':{
        2:[13,23,175,35,20,16,128,148,21,52,16],
        3:[14,38,19,32,31,32,27,21,159,750,136],
        4:[12,129,20,26,46,2139,None,None,None,None,None]},
       'Cindy Hyde-Smith':{
        2:[149,11,79,138,173,90,142,63,84,136,126],
        3:[160,130,143,90,222,278,134,215,670,91,32],
        4:[60,537,11,243,101,4308,None,None,None,None,None]},
       'Chris McDaniel':{
        2:[87,5,37,68,73,26,43,20,21,41,30],
        3:[53,41,55,28,96,97,75,74,193,30,22],
        4:[13,105,7,89,36,1465,None,None,None,None,None]},
      }),
 dict(source_id='sos-2018-runoff-county-neshoba',date='2018-11-27',
      office='United States-Senate Unexpired Term',
      candidate_order=['Mike Espy','Cindy Hyde-Smith'],
      candidate_values={
       'Mike Espy':{
        2:[5,31,196,34,11,7,139,168,22,35,6],
        3:[4,37,8,31,31,16,38,15,152,767,158],
        4:[11,137,34,21,50,2164,None,None,None,None,None]},
       'Cindy Hyde-Smith':{
        2:[204,13,91,196,209,101,201,72,93,168,145],
        3:[193,160,177,109,296,332,183,269,801,89,34],
        4:[71,570,9,303,133,5222,None,None,None,None,None]},
      }),
]
LABELS={stage['source_id']:HEADERS for stage in STAGES}

if __name__=='__main__':build('Neshoba','28099',STAGES,LABELS,27,4,6)
