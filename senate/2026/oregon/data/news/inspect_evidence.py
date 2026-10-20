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
assert '2026 Oregon May Primary' in raw('kptv-results') and '"displayTestData":true' in raw('kptv-results')
assert '2026-05-28 08:33:58 am' in raw('ktvz-results-embed')
assert '0/17' in raw('ktvz-results-embed')
assert 'Welcome Page' in raw('sos-results')
result={'kptv_observed_election':'May primary with test display','ktvz_observed_update':'2026-05-28 08:33:58 am; timezone unverified','familiar_results_root':'generic SOS welcome redirect','usable_november_counts_established':False}
assert next(r for r in rows if r['id']=='nyt-elections')['status']==403
result.update(status='pass',retained_assets=sum('asset' in r for r in rows))
(ROOT/'inspection.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
