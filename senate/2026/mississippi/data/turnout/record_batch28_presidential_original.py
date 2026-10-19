"""Choctaw complete original presidential grids, PDF pages2–3."""
from record_fullgrid_presidential_original import build
H='Kamala D. Harris';O='Chase Oliver';S='Jill Stein';R='Randall Terry'
T='Donald J. Trump';A='Shiva Ayyadurai';C='Claudia De la Cruz'
K='Robert F. Kennedy Jr.';P='Peter Sonski'
B=[None]*9
GRIDS={
 2:{
 H:[35,135,143,160,39,20,8,75,75,8,191],
 O:[0,0,0,1,2,1,0,0,1,0,1],
 S:[2,0,0,0,0,2,1,0,0,0,0],
 R:[1,1,1,0,0,0,0,0,0,0,1],
 T:[137,375,687,59,259,186,244,139,231,343,59],
 A:[0,0,2,0,1,0,0,0,0,0,0],
 C:[0,0,0,0,0,0,0,0,0,0,0],
 K:[1,2,5,4,4,1,0,0,1,0,2],
 P:[0,0,0,0,1,0,0,0,0,0,0],
 },
 3:{
 H:[76,965,*B],
 O:[1,7,*B],
 S:[2,7,*B],
 R:[0,4,*B],
 T:[162,2881,*B],
 A:[1,4,*B],
 C:[0,0,*B],
 K:[1,21,*B],
 P:[0,1,*B],
 },
}
if __name__=='__main__':
 build('choctaw','batch28',GRIDS,12,198)
