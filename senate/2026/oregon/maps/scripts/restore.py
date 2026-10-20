"""Restore complete map original bytes or an exact ZIP member to temporary output."""
from common import *
from acquire import body_of
import argparse,zipfile
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('request');ap.add_argument('--member');ap.add_argument('--output',required=True);args=ap.parse_args();r=load(args.request);b=body_of(r)
 if args.member:
  with zipfile.ZipFile(io.BytesIO(b)) as z:b=z.read(args.member)
 target=Path(args.output).resolve();assert target.is_relative_to(Path('/tmp').resolve()) or target.is_relative_to(Path('/private/tmp'));target.write_bytes(b);print(json.dumps({'bytes':len(b),'sha256':sha(b)}))
