"""Recover exact original bytes or complete frozen objects, never a vote projection.
python -B reconstruct.py --id minnehaha-county-PDF /private/tmp/map.pdf
python -B reconstruct.py --pointer /all_units/303 /private/tmp/crossing.json
python -B reconstruct.py --original-2020-county /private/tmp/2020-counties.pdf
"""
from common import *
import argparse,zlib
def main():
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--id');g.add_argument('--pointer');g.add_argument('--original-2020-county',action='store_true');p.add_argument('output');a=p.parse_args();out=Path(a.output)
 assert not out.exists(),'Refusing to overwrite an existing reconstruction'
 if a.pointer is not None:
  ref=load('qa/dependencies.json')['contract'];x=json.loads(check(ref))
  for part in a.pointer.split('/')[1:]:x=x[int(part)] if isinstance(x,list) else x[part.replace('~1','/').replace('~0','~')]
  out.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
 elif a.original_2020_county:
  d=load('qa/dependencies.json');e=next(x for x in d['full_original_streams'] if x['raw_bytes']==149141181);refs={p['path']:p for p in d['exact_references']};dec=zlib.decompressobj(31);h=hashlib.sha256();n=0
  with out.open('xb') as f:
   for path in e['paths']:
    b=dec.decompress(check(refs[path]));f.write(b);h.update(b);n+=len(b)
   b=dec.flush();f.write(b);h.update(b);n+=len(b)
  assert dec.eof and n==149141181 and h.hexdigest()==e['raw_sha256']
 else:
  es=load('source/reused-receipts.json')+[json.loads(p.read_bytes()) for p in (MAPS/'raw').glob('*.receipt.json')];e=next(x for x in es if x['id']==a.id);b=original(e);out.write_bytes(b)
 print(str(out),out.stat().st_size,sha(out.read_bytes()))
if __name__=='__main__':main()
