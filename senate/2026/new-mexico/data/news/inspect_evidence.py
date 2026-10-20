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
assert '2026 Primary' in raw('sos-primary') and '6/23/2026' in raw('sos-primary')
assert '2026-06-10 04:45:24 am' in raw('kvia-full-results')
assert 'U.S. Senator - NM (D)' in raw('kvia-full-results')
assert next(r for r in rows if r['id']=='source-nm-primary')['status']==403
result={'official_observed_election':'June 2 primary','kvia_observed_contest':'New Mexico Senate Democratic primary','usable_november_counts_established':False}
assert next(r for r in rows if r['id']=='nyt-elections')['status']==403
result.update(status='pass',retained_assets=sum('asset' in r for r in rows))
(ROOT/'inspection.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
