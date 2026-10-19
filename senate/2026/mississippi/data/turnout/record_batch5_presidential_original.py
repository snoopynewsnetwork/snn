"""Direct original presidential glyph readings for four complete source views."""
from record_small_presidential_original import build

MANUAL={
 'walthall':{(2,1,'Jill Stein'):0,(2,2,'Kamala D. Harris'):69,(2,5,'Kamala D. Harris'):110,(3,1,'Peter Sonski'):0,(3,10,'Claudia De la Cruz'):3,(3,10,'Peter Sonski'):4},
 'jasper':{(2,1,'Jill Stein'):0,(2,3,'Shiva Ayyadurai'):1},
 'yalobusha':{(2,1,'Donald J. Trump'):575,(2,1,'Jill Stein'):0,(2,5,'Chase Oliver'):0,(2,5,'Shiva Ayyadurai'):0,(3,2,'Peter Sonski'):3,(3,2,'Robert F. Kennedy Jr.'):40,(3,2,'Shiva Ayyadurai'):4},
 'washington':{(2,1,'Kamala D. Harris'):211,(2,11,'Kamala D. Harris'):730,(3,1,'Peter Sonski'):0,(3,1,'Shiva Ayyadurai'):1,(3,8,'Jill Stein'):1,(3,9,'Shiva Ayyadurai'):11},
}

def main():build(MANUAL,'batch5',63,792,21)
if __name__=='__main__':main()
