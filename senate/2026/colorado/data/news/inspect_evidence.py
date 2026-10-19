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
assert 'June 30, 2026 Primary' in raw('denver7-results')
assert '20251104' in raw('denver7-results')
assert '"displayTestData":true' in raw('kktv-results')
assert '2026 Colorado Primary' in raw('kktv-results')
assert '113508/30468.html' in raw('sun-primary-results')
assert next(r for r in rows if r['id']=='sun-primary-ap')['status']==403
result={'primary_test_selection':'2026 Colorado Primary','sun_supplier':'AP','november_feed_established':False}
result.update(status='pass',retained_assets=sum('asset' in r for r in rows))
(ROOT/'inspection.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
