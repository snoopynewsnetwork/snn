"""Native GeoPackage/WKB scanner. No coordinate conversion or precision changes."""
import collections,struct
def wkb_blob(b):
 assert b[:2]==b'GP'; flags=b[3]; env=(flags>>1)&7; size={0:0,1:32,2:48,3:48,4:64}[env]
 return b[8+size:],{'version':b[2],'flags':flags,'envelope_type':env,'empty_flag':bool(flags&16),'extended_flag':bool(flags&32),'srs_id':struct.unpack('<i' if flags&1 else '>i',b[4:8])[0]}

def scan_wkb(b):
 counts=collections.Counter(); dimensions=collections.Counter();coords=0
 def rec(pos):
  nonlocal coords
  endian='<' if b[pos]==1 else '>';typ=struct.unpack_from(endian+'I',b,pos+1)[0];pos+=5
  z=bool(typ&0x80000000);m=bool(typ&0x40000000);sr=bool(typ&0x20000000);t=typ&0x0fffffff
  if t>=3000:z=m=True;t-=3000
  elif t>=2000:m=True;t-=2000
  elif t>=1000:z=True;t-=1000
  if sr:pos+=4
  counts[str(t)]+=1;dimensions['XYZM' if z and m else 'XYZ' if z else 'XYM' if m else 'XY']+=1
  dim=2+int(z)+int(m)
  if t==1:coords+=1;return pos+dim*8
  n=struct.unpack_from(endian+'I',b,pos)[0];pos+=4
  if t in (2,8):coords+=n;return pos+n*dim*8
  if t==3:
   for _ in range(n):
    n2=struct.unpack_from(endian+'I',b,pos)[0];pos+=4+n2*dim*8;coords+=n2
   return pos
  if t in (4,5,6,7,9,10,11,12,15,16):
   for _ in range(n):pos=rec(pos)
   return pos
  raise ValueError('unsupported native WKB type '+str(t))
 end=rec(0);assert end==len(b),(end,len(b));return {'types':dict(counts),'dimensions':dict(dimensions),'coordinate_positions':coords,'curved_types_present':any(int(t) in (8,9,10,11,12) for t in counts)}

