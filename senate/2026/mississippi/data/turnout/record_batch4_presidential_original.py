"""Eight complete original-PDF presidential views after direct glyph review.

An independent original-pixel pass preceded selection of the thirty-six
exception cells. The values below were read on complete original page rasters;
peer data are compared only after the source transcript has been assembled.
"""
from record_small_presidential_original import build

MANUAL={
 'union':{(2,1,'Kamala D. Harris'):13,(2,1,'Peter Sonski'):0,(2,3,'Peter Sonski'):0,(2,3,'Robert F. Kennedy Jr.'):2,(2,4,'Randall Terry'):1,(2,7,'Peter Sonski'):0,(2,9,'Donald J. Trump'):420,(2,9,'Peter Sonski'):0,(3,5,'Kamala D. Harris'):113},
 'stone':{(2,1,'Kamala D. Harris'):9,(2,7,'Claudia De la Cruz'):0,(2,10,'Peter Sonski'):1,(3,2,'Jill Stein'):0},
 'george':{(2,5,'Kamala D. Harris'):30,(3,4,'Kamala D. Harris'):81,(3,5,'Kamala D. Harris'):22,(3,7,'Kamala D. Harris'):28,(3,8,'Kamala D. Harris'):99,(3,10,'Kamala D. Harris'):39},
 'lowndes':{(2,3,'Peter Sonski'):0,(2,4,'Chase Oliver'):7,(2,6,'Chase Oliver'):1,(3,10,'Randall Terry'):13},
 'panola':{(2,1,'Kamala D. Harris'):557,(2,3,'Kamala D. Harris'):275},
 'monroe':{(3,5,'Kamala D. Harris'):101,(3,9,'Jill Stein'):1,(4,1,'Shiva Ayyadurai'):1,(4,3,'Donald J. Trump'):404,(4,4,'Kamala D. Harris'):483,(4,6,'Kamala D. Harris'):5090},
 'prentiss':{},
 'newton':{(2,2,'Kamala D. Harris'):115,(2,3,'Peter Sonski'):0,(3,1,'Peter Sonski'):0,(3,3,'Peter Sonski'):0,(3,7,'Claudia De la Cruz'):2},
}

def main():build(MANUAL,'batch4',155,1683,36)
if __name__=='__main__':main()
