"""Holmes complete original presidential grids, PDF pages2–3."""
from record_fullgrid_presidential_original import build
H='Kamala D. Harris';O='Chase Oliver';S='Jill Stein';R='Randall Terry'
T='Donald J. Trump';A='Shiva Ayyadurai';C='Claudia De la Cruz'
K='Robert F. Kennedy Jr.';P='Peter Sonski'
B=[None]*5
GRIDS={
 2:{
 H:[372,163,638,290,326,235,43,174,375,491,830],
 O:[0,1,0,1,0,0,0,0,2,0,3],
 S:[0,0,1,2,1,0,0,1,2,0,2],
 R:[0,0,0,0,0,0,0,0,0,1,2],
 T:[62,23,102,108,57,120,120,65,55,65,134],
 A:[0,1,1,1,0,0,0,0,0,2,1],
 C:[0,0,0,0,1,0,0,0,0,0,0],
 K:[6,3,2,3,1,2,0,0,2,1,2],
 P:[0,0,0,1,0,0,0,1,0,0,0],
 },
 3:{
 H:[204,128,165,248,738,5420,*B],
 O:[0,0,0,0,1,8,*B],
 S:[2,0,0,0,4,15,*B],
 R:[0,0,0,0,0,3,*B],
 T:[32,14,58,142,86,1243,*B],
 A:[0,0,0,0,4,10,*B],
 C:[0,0,0,0,0,1,*B],
 K:[1,1,0,1,2,27,*B],
 P:[0,1,0,0,0,3,*B],
 },
}
if __name__=='__main__':
 build('holmes','batch27',GRIDS,16,198)
