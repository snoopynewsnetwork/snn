"""Jeff Davis complete original presidential grids, PDF pages2–3."""
from record_fullgrid_presidential_original import build
H='Kamala D. Harris';O='Chase Oliver';S='Jill Stein';R='Randall Terry'
T='Donald J. Trump';A='Shiva Ayyadurai';C='Claudia De la Cruz'
K='Robert F. Kennedy Jr.';P='Peter Sonski'
B=[None]*4
GRIDS={
 2:{
 H:[57,143,620,52,76,90,70,143,157,359,153],
 O:[0,0,1,0,1,0,0,0,0,0,0],
 S:[0,1,0,0,0,0,0,0,1,0,1],
 R:[0,0,0,0,0,0,0,0,1,1,0],
 T:[56,163,192,136,77,198,186,83,26,163,57],
 A:[0,0,0,0,0,0,1,0,0,0,1],
 C:[0,0,0,0,0,0,0,0,0,1,0],
 K:[0,2,0,0,0,2,2,1,1,0,0],
 P:[0,0,2,0,0,0,0,0,0,0,0],
 },
 3:{
 H:[209,189,220,214,200,89,3041,*B],
 O:[0,0,1,0,0,0,3,*B],
 S:[1,0,0,0,0,0,4,*B],
 R:[0,0,2,0,0,0,4,*B],
 T:[104,201,260,158,59,183,2302,*B],
 A:[1,0,0,1,0,0,4,*B],
 C:[0,0,1,0,0,0,2,*B],
 K:[1,1,3,0,2,1,16,*B],
 P:[0,0,0,0,0,0,2,*B],
 },
}
if __name__=='__main__':
 build('jeff-davis','batch25',GRIDS,17,198)
