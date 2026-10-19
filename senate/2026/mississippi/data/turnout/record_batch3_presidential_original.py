"""Four more complete original-PDF presidential source views.

The values below were reread on complete original page rasters after an
independent original-pixel OCR pass. The peer is compared only after the
source ledger is assembled; it supplies no vote inputs.
"""
from record_small_presidential_original import build

MANUAL={
 'calhoun':{(2,3,'Donald J. Trump'):311,(2,5,'Kamala D. Harris'):63,(2,6,'Peter Sonski'):0,(2,7,'Kamala D. Harris'):95,(2,8,'Chase Oliver'):0,(2,10,'Peter Sonski'):0,(2,11,'Chase Oliver'):9,(2,11,'Claudia De la Cruz'):5,(2,11,'Jill Stein'):0,(2,11,'Randall Terry'):7,(2,11,'Shiva Ayyadurai'):3},
 'claiborne':{(2,2,'Chase Oliver'):0,(2,2,'Randall Terry'):0,(2,3,'Peter Sonski'):0,(2,3,'Randall Terry'):0,(2,3,'Robert F. Kennedy Jr.'):0,(2,4,'Jill Stein'):0,(2,4,'Kamala D. Harris'):179,(2,4,'Randall Terry'):0,(2,5,'Jill Stein'):0,(2,5,'Peter Sonski'):0,(2,5,'Randall Terry'):0,(2,6,'Kamala D. Harris'):16,(2,7,'Chase Oliver'):0,(2,8,'Claudia De la Cruz'):0,(2,8,'Kamala D. Harris'):274,(2,8,'Randall Terry'):0,(2,9,'Jill Stein'):1,(2,9,'Randall Terry'):0,(2,11,'Shiva Ayyadurai'):1,(3,1,'Peter Sonski'):0,(3,2,'Claudia De la Cruz'):7,(3,2,'Kamala D. Harris'):2950},
 'smith':{(2,3,'Kamala D. Harris'):39,(2,3,'Robert F. Kennedy Jr.'):1,(2,6,'Peter Sonski'):0,(2,8,'Randall Terry'):2,(2,10,'Peter Sonski'):0,(3,4,'Peter Sonski'):1,(3,4,'Randall Terry'):0,(3,8,'Chase Oliver'):7,(3,8,'Jill Stein'):3},
 'tishomingo':{(3,2,'Kamala D. Harris'):70,(3,5,'Kamala D. Harris'):11,(3,6,'Shiva Ayyadurai'):1,(3,7,'Jill Stein'):0,(3,8,'Jill Stein'):0,(3,9,'Robert F. Kennedy Jr.'):10,(3,10,'Chase Oliver'):1,(3,10,'Donald J. Trump'):461,(3,10,'Jill Stein'):0,(3,10,'Randall Terry'):0,(3,10,'Robert F. Kennedy Jr.'):0,(3,10,'Shiva Ayyadurai'):0,(4,1,'Chase Oliver'):1,(4,1,'Jill Stein'):1,(4,1,'Robert F. Kennedy Jr.'):1,(4,2,'Shiva Ayyadurai'):2,(4,3,'Jill Stein'):10,(4,3,'Peter Sonski'):0},
}

def main():build(MANUAL,'batch3',53,693,60)
if __name__=='__main__':main()
