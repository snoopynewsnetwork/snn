"""Webster complete original presidential grids, PDF pages2–3, no OCR aid."""
from record_fullgrid_presidential_original import build
H='Kamala D. Harris';O='Chase Oliver';S='Jill Stein';R='Randall Terry'
T='Donald J. Trump';A='Shiva Ayyadurai';C='Claudia De la Cruz'
K='Robert F. Kennedy Jr.';P='Peter Sonski'
B=[None]*7
GRIDS={
 2:{
 H:[37,11,23,45,387,66,18,40,110,27,50],
 O:[0,1,0,1,1,0,0,1,0,0,0],
 S:[0,0,3,0,0,0,1,0,0,0,0],
 R:[0,2,0,0,0,0,0,0,1,0,0],
 T:[325,181,505,277,474,208,123,226,381,335,205],
 A:[0,0,0,0,1,0,0,0,0,0,0],
 C:[0,0,0,0,1,0,0,0,0,0,0],
 K:[0,2,0,2,2,0,1,0,0,0,2],
 P:[0,0,0,0,0,0,0,0,0,1,1],
 },
 3:{
 H:[24,16,18,872,*B],
 O:[0,0,1,5,*B],
 S:[0,1,0,5,*B],
 R:[0,1,0,4,*B],
 T:[294,341,320,4195,*B],
 A:[0,0,1,2,*B],
 C:[0,0,0,1,*B],
 K:[0,0,0,9,*B],
 P:[0,0,0,2,*B],
 },
}
if __name__=='__main__':
 build('webster','batch24',GRIDS,14,198)
