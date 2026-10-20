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
assert '"displayTestData":true' in raw('kait-results')
assert 'arkansas.tally-enr.com' in raw('sos-home')
assert next(r for r in rows if r['id']=='advocate-primary')['status']==403
result={'kait_selection':'unselected/test display','official_linked_vendor':'Tally; November identity/status not validated','usable_november_counts_established':False}
assert next(r for r in rows if r['id']=='nyt-elections')['status']==403
result.update(status='pass',retained_assets=sum('asset' in r for r in rows))
(ROOT/'inspection.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
