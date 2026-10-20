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
x=json.loads(raw('spotlight-primary-data'))
assert x['electionDate']=='2026-09-15' and len(x['contests'])==33
assert x['reporting']['reported']==x['reporting']['total']==530
assert x['fetchedAt']=='2026-09-16T11:59:14.621Z'
assert 'pollIntervalMs: 20000' in raw('spotlight-primary-config')
assert 'state = {' in raw('spotlight-primary-app') and '...data' in raw('spotlight-primary-app')
for contest in x['contests']:
 for c in contest['candidates']:
  assert c['votes']==c.get('machineVotes',0)+c.get('absenteeVotes',0)+c.get('earlyVotes',0)
assert '30,896' in raw('wboc-senate-primary') and '9,052' in raw('wboc-senate-primary')
result={'election_date':x['electionDate'],'contests':len(x['contests']),'districts_reported':530,'client_poll_ms':20000,'november_feed_established':False}
result.update(status='pass',retained_assets=sum('asset' in r for r in rows))
(ROOT/'inspection.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
