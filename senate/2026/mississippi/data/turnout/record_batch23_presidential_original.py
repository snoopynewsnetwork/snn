"""Leflore complete original PDF pages5–6, every printed presidential glyph.

Each array is in physical source-column order. PDF page6 has seven native
columns, TOTAL in column8, and three visually blank template columns.
"""
from record_fullgrid_presidential_original import build

H='Kamala D. Harris';O='Chase Oliver';S='Jill Stein';R='Randall Terry'
T='Donald J. Trump';A='Shiva Ayyadurai';C='Claudia De la Cruz'
K='Robert F. Kennedy Jr.';P='Peter Sonski'
BLANK=[None,None,None]
GRIDS={
 5:{
  H:[210,912,63,19,74,136,548,662,767,353,92],
  O:[1,2,0,0,0,0,0,8,2,0,0],
  S:[1,2,0,0,0,0,0,4,0,0,0],
  R:[0,0,1,1,0,0,0,3,0,0,0],
  T:[43,27,81,88,52,20,119,1757,70,13,117],
  A:[0,1,0,0,0,0,0,0,0,0,0],
  C:[1,0,0,0,0,0,0,1,0,0,0],
  K:[0,5,1,0,0,1,1,14,3,3,0],
  P:[0,0,0,0,0,0,0,2,1,0,0],
 },
 6:{
  H:[143,206,212,980,258,16,825,6476,*BLANK],
  O:[1,1,1,1,1,0,0,18,*BLANK],
  S:[0,1,0,4,0,0,0,12,*BLANK],
  R:[1,0,1,1,0,0,1,9,*BLANK],
  T:[54,4,50,155,7,20,177,2854,*BLANK],
  A:[0,0,0,1,0,0,0,2,*BLANK],
  C:[0,0,0,1,1,0,1,5,*BLANK],
  K:[2,2,0,5,0,1,3,41,*BLANK],
  P:[0,0,0,0,0,0,1,4,*BLANK],
 },
}
if __name__=='__main__':
    build('leflore','batch23',GRIDS,18,198)
