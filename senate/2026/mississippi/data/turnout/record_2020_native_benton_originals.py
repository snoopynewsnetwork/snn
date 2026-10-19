"""Both Benton 2020 original and amended PDF2s, separately visually read."""
from record_2020_native_manual_original import build
E='Mike Espy';H='Cindy Hyde-Smith';J='Jimmy L. Edwards';B=[None]*5
LABELS={2:['Ashland Precinct\nDistrict 3','Canaan Precinct\nDistrict 1','Floyd Precinct   Dist 4','Hickory Flat Prec\nDist 5','Lamar Precinct\nDistrict 2','TOTAL','','','','','']}
# Each PDF page was separately rendered and reviewed. Identical printed
# numbers remain two source publications, never merged as one source ID.
ORIGINAL={2:{E:[397,468,229,157,617,1868,*B],H:[451,344,562,743,220,2320,*B],J:[22,8,14,39,9,92,*B]}}
AMENDED={2:{E:[397,468,229,157,617,1868,*B],H:[451,344,562,743,220,2320,*B],J:[22,8,14,39,9,92,*B]}}
if __name__=='__main__':
 build('benton','benton',ORIGINAL,LABELS,5)
 build('benton-amended','benton-amended',AMENDED,LABELS,5)
