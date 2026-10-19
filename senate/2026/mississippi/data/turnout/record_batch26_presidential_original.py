"""Franklin complete original presidential grids, PDF pages2–3."""
from record_fullgrid_presidential_original import build
H='Kamala D. Harris';O='Chase Oliver';S='Jill Stein';R='Randall Terry'
T='Donald J. Trump';A='Shiva Ayyadurai';C='Claudia De la Cruz'
K='Robert F. Kennedy Jr.';P='Peter Sonski'
B=[None]*7
GRIDS={
 2:{
 H:[101,16,334,42,21,152,51,22,47,88,7],
 O:[0,0,0,0,0,0,0,1,0,0,0],
 S:[0,0,0,0,0,0,0,0,1,0,0],
 R:[0,1,0,0,0,0,0,0,0,0,0],
 T:[173,340,282,197,258,64,118,172,282,279,138],
 A:[0,0,0,0,0,0,0,0,0,0,0],
 C:[0,0,0,0,0,0,0,0,0,1,0],
 K:[3,0,0,0,1,2,0,2,0,0,1],
 P:[0,0,0,0,0,0,0,0,0,2,0],
 },
 3:{
 H:[241,57,34,1213,*B],
 O:[1,0,0,2,*B],
 S:[1,0,0,2,*B],
 R:[0,0,0,1,*B],
 T:[158,113,257,2831,*B],
 A:[0,0,1,1,*B],
 C:[0,0,0,1,*B],
 K:[3,1,0,13,*B],
 P:[0,0,0,2,*B],
 },
}
if __name__=='__main__':
 build('franklin','batch26',GRIDS,14,198)
