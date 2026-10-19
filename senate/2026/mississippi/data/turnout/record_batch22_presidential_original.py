"""Tippah: four OCR corrections and nine printed TOTALs read on original PDF 3–4."""
from record_small_presidential_original import build

MANUAL={'tippah':{
 (3,6,'Robert F. Kennedy Jr.'):0,
 (4,3,'Claudia De la Cruz'):0,
 (4,5,'Shiva Ayyadurai'):0,
 (4,8,'Kamala D. Harris'):15,
 (4,11,'Kamala D. Harris'):1547,
 (4,11,'Chase Oliver'):11,
 (4,11,'Jill Stein'):5,
 (4,11,'Randall Terry'):9,
 (4,11,'Donald J. Trump'):7984,
 (4,11,'Shiva Ayyadurai'):4,
 (4,11,'Claudia De la Cruz'):4,
 (4,11,'Robert F. Kennedy Jr.'):27,
 (4,11,'Peter Sonski'):0,
}}
if __name__=='__main__':
    build(MANUAL,'batch22',21,198,13)
