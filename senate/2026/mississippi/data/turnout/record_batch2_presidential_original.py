"""Seven more complete original-PDF nine-candidate source views.

All37 corrections below were typed while reading each complete original
source raster, after an independent original-pixel OCR pass and before the
post-extraction peer comparison. The frozen peer never supplies vote inputs.
"""
from record_small_presidential_original import build
MANUAL={
 'adams':{(2,1,'Kamala D. Harris'):510,(2,2,'Kamala D. Harris'):415,(2,8,'Kamala D. Harris'):389,(2,10,'Kamala D. Harris'):213,(2,11,'Kamala D. Harris'):443,(3,2,'Kamala D. Harris'):464,(3,5,'Kamala D. Harris'):341,(3,7,'Kamala D. Harris'):311,(3,8,'Kamala D. Harris'):177,(3,9,'Kamala D. Harris'):6743},
 'carroll':{(2,5,'Chase Oliver'):0,(2,5,'Kamala D. Harris'):212,(2,5,'Peter Sonski'):0,(2,5,'Shiva Ayyadurai'):0,(2,6,'Kamala D. Harris'):358,(2,8,'Kamala D. Harris'):18,(2,9,'Kamala D. Harris'):118,(2,9,'Peter Sonski'):0,(3,2,'Shiva Ayyadurai'):0,(3,4,'Jill Stein'):3},
 'clay':{(2,5,'Peter Sonski'):2,(2,9,'Randall Terry'):0,(2,11,'Claudia De la Cruz'):1,(3,1,'Peter Sonski'):0,(3,3,'Robert F. Kennedy Jr.'):5},
 'jefferson':{(2,10,'Shiva Ayyadurai'):1,(2,11,'Donald J. Trump'):11,(3,1,'Jill Stein'):0},
 'quitman':{(3,3,'Kamala D. Harris'):170,(3,6,'Peter Sonski'):1,(3,9,'Robert F. Kennedy Jr.'):3},
 'sharkey':{(2,9,'Kamala D. Harris'):2,(2,11,'Randall Terry'):0},
 'sunflower':{(2,3,'Claudia De la Cruz'):0,(3,2,'Kamala D. Harris'):265,(3,6,'Kamala D. Harris'):552,(3,6,'Shiva Ayyadurai'):0},
}
def main():build(MANUAL,'batch2',96,1188,37)
if __name__=='__main__':main()
