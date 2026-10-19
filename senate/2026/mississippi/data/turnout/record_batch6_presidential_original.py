"""Direct full-original presidential readings for four more SEMS views.

The independent original-pixel OCR and complete source renders predate the
post-extraction peer comparison. Prior OCR errors remain in the reading ledger.
"""
from record_small_presidential_original import build

MANUAL={
 'montgomery':{(5,1,'Shiva Ayyadurai'):1,(5,5,'Peter Sonski'):0,(5,6,'Donald J. Trump'):21,(5,8,'Shiva Ayyadurai'):0,(6,4,'Shiva Ayyadurai'):3},
 'tallahatchie':{(2,1,'Chase Oliver'):0,(2,2,'Kamala D. Harris'):68,(2,3,'Jill Stein'):0,(2,4,'Jill Stein'):0,(2,4,'Kamala D. Harris'):483,(2,6,'Jill Stein'):0,(2,8,'Kamala D. Harris'):12,(2,9,'Claudia De la Cruz'):2,(2,9,'Peter Sonski'):0,(2,10,'Jill Stein'):0,(2,10,'Peter Sonski'):0,(2,10,'Robert F. Kennedy Jr.'):1,(3,9,'Peter Sonski'):2},
 'lawrence':{(2,1,'Jill Stein'):0,(2,2,'Randall Terry'):0,(2,2,'Shiva Ayyadurai'):0,(2,3,'Randall Terry'):0,(2,5,'Donald J. Trump'):457,(2,9,'Kamala D. Harris'):170,(2,10,'Donald J. Trump'):154,(2,10,'Kamala D. Harris'):217,(2,10,'Peter Sonski'):0,(2,11,'Peter Sonski'):0,(2,11,'Randall Terry'):0,(3,2,'Claudia De la Cruz'):0,(3,3,'Donald J. Trump'):4113,(3,3,'Jill Stein'):3,(3,3,'Kamala D. Harris'):1899,(3,3,'Randall Terry'):2,(3,3,'Shiva Ayyadurai'):2},
 'copiah':{(2,5,'Claudia De la Cruz'):1,(2,5,'Peter Sonski'):0,(2,8,'Jill Stein'):0,(2,9,'Randall Terry'):1,(3,1,'Kamala D. Harris'):669,(3,8,'Chase Oliver'):14,(3,8,'Claudia De la Cruz'):7,(3,8,'Donald J. Trump'):6134,(3,8,'Jill Stein'):8,(3,8,'Kamala D. Harris'):5426,(3,8,'Peter Sonski'):11,(3,8,'Randall Terry'):9,(3,8,'Robert F. Kennedy Jr.'):50,(3,8,'Shiva Ayyadurai'):6},
}

def main():build(MANUAL,'batch6',64,792,49)
if __name__=='__main__':main()
