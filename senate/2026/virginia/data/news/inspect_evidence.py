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
assert '52020/31145.html' in raw('wtop-primary-results')
assert next(r for r in rows if r['id']=='wtop-primary-ap')['status']==403
assert '"displayTestData":true' in raw('whsv-results') and '2026 General Election' in raw('whsv-results')
assert '2026-November-General' in raw('elect-results') and '<app-root' in raw('elect-november-linked')
result={'official_november_link':'published; raw response is application shell only','whsv_selection':'General named, inactive/test display','wtop_supplier':'AP','usable_november_counts_established':False}
assert next(r for r in rows if r['id']=='nyt-elections')['status']==403
result.update(status='pass',retained_assets=sum('asset' in r for r in rows))
(ROOT/'inspection.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
