"""Direct original-page Sharkey 2020 Senate grids, both publications separately."""
from record_2020_native_manual_original import build

E='Mike Espy';H='Cindy Hyde-Smith';J='Jimmy L. Edwards'
LABELS={2:[
    'Anguilla Fifth District','Anguilla Fourth District','Cary Second District',
    'Delta City Fifth District','Rolling Fork First District',
    'Rolling Fork Fourth District','Rolling Fork Second District',
    'Rolling Fork Third District','Spanish Fort First District',
    'Straight Bayou Fourth District','TOTAL',
]}
GRIDS={2:{
    E:[176,185,228,150,267,100,48,321,3,33,1511],
    H:[30,119,80,88,243,4,0,20,30,49,663],
    J:[2,1,0,0,1,1,0,2,0,0,7],
}}
if __name__=='__main__':
    build('sharkey','sharkey-original',GRIDS,LABELS,10)
    build('sharkey-amended','sharkey-amended',GRIDS,LABELS,10)
