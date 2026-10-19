"""Amite complete original presidential grids, PDF pages2–4, no OCR aid."""
from record_fullgrid_presidential_original import build
H='Kamala D. Harris';O='Chase Oliver';S='Jill Stein';R='Randall Terry'
T='Donald J. Trump';A='Shiva Ayyadurai';C='Claudia De la Cruz'
K='Robert F. Kennedy Jr.';P='Peter Sonski'
B=[None]*10
GRIDS={
 2:{
 H:[158,195,167,68,114,37,91,52,358,6,114],
 O:[0,2,0,1,0,0,2,0,2,0,1],
 S:[3,1,0,0,0,2,0,2,0,0,1],
 R:[0,2,1,0,1,0,0,1,1,0,0],
 T:[55,92,75,74,249,326,135,116,112,57,406],
 A:[1,0,0,0,2,0,1,0,1,0,0],
 C:[0,0,0,0,1,0,0,0,0,0,0],
 K:[0,2,0,1,2,2,2,0,4,0,1],
 P:[0,0,0,0,1,0,0,0,0,2,1],
 },
 3:{
 H:[38,12,120,115,119,52,67,137,21,145,60],
 O:[0,0,1,1,1,1,0,2,3,0,0],
 S:[0,0,0,1,0,0,0,1,0,0,0],
 R:[1,0,0,2,1,0,0,0,0,0,1],
 T:[287,260,176,281,132,243,409,166,138,403,292],
 A:[0,0,1,0,0,0,1,0,0,0,0],
 C:[0,0,1,0,1,2,1,1,0,0,1],
 K:[2,0,0,0,2,1,0,1,0,3,0],
 P:[1,0,2,0,0,0,0,1,0,0,0],
 },
 4:{
 H:[2246,*B],O:[17,*B],S:[11,*B],R:[11,*B],T:[4484,*B],
 A:[7,*B],C:[8,*B],K:[23,*B],P:[8,*B],
 },
}
if __name__=='__main__':
 build('amite','batch29',GRIDS,22,297)
