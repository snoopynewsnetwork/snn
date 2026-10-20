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
assert "ELECTION_DATE = 'September 9, 2026'" in raw('journal-election-config')
assert 'UPDATE_INTERVAL_SECONDS = 60' in raw('journal-election-config')
assert 'get-election-results.php' in raw('journal-election-code')
assert 'RI Board of Elections' in raw('journal-primary-results')
assert 'John F. Reed' in raw('journal-statewide-primary')
result={'journal_election_date':'2026-09-09','client_update_seconds':60,'supplier':'RI Board of Elections','usable_november_counts_established':False}
assert next(r for r in rows if r['id']=='nyt-elections')['status']==403
result.update(status='pass',retained_assets=sum('asset' in r for r in rows))
(ROOT/'inspection.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
