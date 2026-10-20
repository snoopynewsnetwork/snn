"""Offline exact original reconstruction/full-object view, no downloads."""
from acquire import *
import sys
if sys.argv[1]=='materialize':
 target=Path(sys.argv[3]).resolve();assert target.is_relative_to(Path('/tmp').resolve()) or target.is_relative_to(Path('/private/tmp')), 'Use a temporary output path; originals remain once/byhash'
 b=content(sys.argv[2]);target.write_bytes(b);print({'bytes':len(b),'sha256':sha(b),'output':str(target)})
elif sys.argv[1]=='native':
 o=json.loads(content(sys.argv[2]));print(json.dumps(o['features'][int(sys.argv[3])],indent=2,ensure_ascii=False,allow_nan=False))
elif sys.argv[1]=='receipt':print((BASE/'receipts'/f'{sys.argv[2]}.json').read_text())
else:raise SystemExit('materialize RECEIPT /tmp/file | native RECEIPT FEATURE_INDEX | receipt RECEIPT')
