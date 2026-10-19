#!/usr/bin/env python3
"""Reconstruct complete originals without duplicating frozen stored evidence.
python3 reconstruct.py --owned lincoln-ballot --output /tmp/lincoln.pdf
python3 reconstruct.py --shared sos-2020-general-county-canvass --output /tmp/sd2020.pdf
No output path: verify full stream only. Every ordered part and original is checked.
"""
import sys
sys.dont_write_bytecode=True
from common import *
import argparse,zlib

def reconstruct(which,id,output=None):
 if which=='owned':
  e=json.loads((ROOT/'raw'/f'{id}.receipt.json').read_text());parts=e['stored_parts'];base=ROOT;rawhash=e['raw_sha256'];rawlen=e['raw_bytes']
 else:
  e=next(x for x in json.loads((STATE/'data/news/manifest.json').read_text()) if x['id']==id);base=STATE/'data/news';rawhash=e['raw_sha256'];rawlen=e['bytes'];parts=e.get('asset_parts') or [{'asset':e['asset'],'sha256':e['stored_sha256']}]
 dec=zlib.decompressobj(16+zlib.MAX_WBITS);h=hashlib.sha256();n=0;gz=hashlib.sha256();gn=0;f=open(output,'wb') if output else None
 try:
  for part in parts:
   name=part.get('path',part.get('asset'));b=(base/name).read_bytes();assert hashlib.sha256(b).hexdigest()==part.get('sha256',part.get('stored_sha256'))
   if 'bytes' in part:assert len(b)==part['bytes']
   gz.update(b);gn+=len(b);d=dec.decompress(b);h.update(d);n+=len(d)
   if f:f.write(d)
  d=dec.flush();h.update(d);n+=len(d)
  if f:f.write(d)
  assert dec.eof and not dec.unused_data
  assert n==rawlen and h.hexdigest()==rawhash
  if which=='shared' and 'asset_parts' in e:assert gz.hexdigest()==e['stored_sha256']
 finally:
  if f:f.close()
 return {'id':id,'raw_bytes':n,'raw_sha256':h.hexdigest(),'stored_bytes':gn,'stored_sha256':gz.hexdigest(),'parts':len(parts)}
if __name__=='__main__':
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--owned');g.add_argument('--shared');p.add_argument('--output');a=p.parse_args();print(json.dumps(reconstruct('owned' if a.owned else 'shared',a.owned or a.shared,a.output),indent=2))
