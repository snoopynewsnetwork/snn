#!/usr/bin/env python3
"""Verify captured response bytes and source-specific preflight observations."""
from pathlib import Path
import gzip,hashlib,json,re
ROOT=Path(__file__).resolve().parent
rows=json.loads((ROOT/'manifest.json').read_text())
for row in rows:
 if 'asset' not in row:continue
 b=(ROOT/row['asset']).read_bytes();assert hashlib.sha256(b).hexdigest()==row['stored_sha256'],row['id']
 raw_bytes=gzip.decompress(b);assert hashlib.sha256(raw_bytes).hexdigest()==row['raw_sha256'],row['id']
def raw(name):
 row=next(r for r in rows if r['id']==name)
 return gzip.decompress((ROOT/row['asset']).read_bytes()).decode(errors='replace')
assert '60951/32341.html' in raw('wgbh-primary-results')
assert '79545/32390.html' in raw('nepm-primary-results')
assert 'webpubcontent.gray.tv/wggb/xml/WMNelections.html' in raw('westernmass-results')
assert '574,030' in raw('westernmass-embed') and '311,151' in raw('westernmass-embed')
assert next(r for r in rows if r['id']=='nepm-primary-ap')['status']==403
result={'gbh_nepm_supplier':'AP','westernmass_observed_contest':'Senate Democratic primary','november_feed_established':False}
result.update(status='pass',retained_assets=sum('asset' in r for r in rows))
(ROOT/'inspection.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
