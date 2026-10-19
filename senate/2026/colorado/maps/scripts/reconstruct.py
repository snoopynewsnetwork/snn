"""Offline exact entity/member reconstruction to a caller-specified temporary path."""
import argparse,io,json,pathlib,zipfile
from acquire import ROOT,body,sha
p=argparse.ArgumentParser();p.add_argument('acquisition_id');p.add_argument('output');p.add_argument('--member');a=p.parse_args();dest=pathlib.Path(a.output).resolve();assert not dest.is_relative_to(ROOT),'do not write into sealed research package';assert not dest.exists(),'do not overwrite an existing file'
r=json.loads((ROOT/'raw'/f'{a.acquisition_id}.receipt.json').read_text());b=body(a.acquisition_id);assert len(b)==r['raw_bytes'] and sha(b)==r['raw_sha256']
if a.member:
 with zipfile.ZipFile(io.BytesIO(b)) as z:assert z.testzip() is None;b=z.read(a.member)
assert len(b)<40000000,'use ordered sub40MB splits for larger temporary reconstructions';dest.write_bytes(b);print(json.dumps(dict(output=str(dest),bytes=len(b),sha256=sha(b),source=a.acquisition_id,member=a.member)))
