#!/usr/bin/env python3
"""Verify retained public captures; summarize bounded product inspections."""
from pathlib import Path
import gzip,hashlib,json,re
ROOT=Path(__file__).resolve().parent
rows=json.loads((ROOT/'manifest.json').read_text())
for r in rows:
 if 'asset' not in r:continue
 b=(ROOT/r['asset']).read_bytes();assert hashlib.sha256(b).hexdigest()==r['stored_sha256'],r['id']
 raw=gzip.decompress(b);assert hashlib.sha256(raw).hexdigest()==r['raw_sha256'],r['id']
def raw(name):
 r=next(r for r in rows if r['id']==name);return gzip.decompress((ROOT/r['asset']).read_bytes()).decode(errors='replace')
obs={'captures':len(rows),'verified_assets':sum('asset' in r for r in rows)}
assert '"selectedElection":{"id":null}' in raw('wlbt-results')
assert '"selectedElection":{"id":null}' in raw('wdam-results')
assert 'MS Chancery Court Judicial Races' in raw('wlox-results')
assert all('"displayTestData":true' in raw(n) for n in ('wlbt-results','wlox-results','wdam-results'))
obs.update(local_sources_empty_or_judicial=True,test_display_enabled=True)
for name in ('wtok-results', 'wtva-results'):
 assert '"selectedElection":{"id":null}' in raw(name)
 assert '"displayTestData":true' in raw(name)
obs['additional_current_empty_test_pages']=['wtok-results','wtva-results']
assert 'https://www.branch.vote/embedded-lookup?organization=mpbonline' in raw('mpb-voter-guide')
obs['mpb_voter_guide_is_not_count_publication']=True
assert 'County election officials will continue to process absentee ballots' in raw('mpb-2025-counting-report')
assert 'Preliminary results as of midnight Wed, Nov. 5.' in raw('mpb-2025-counting-report')
obs['mpb_historical_counting_report']={'election':'2025 legislative special','publisher_date':'2025-11-05','not_2026_senate':True}
for name in ('delta-2026-levee-results','delta-washington-administration'):
 assert 'itemprop="articleBody"' in raw(name)
assert '2026-06-10T10:04:00-05:00' in raw('delta-2026-levee-results')
obs['delta_lanes']={'levee_results':'June2026 local election, excluded from Senate counts','registration_administration':'February2026 report, not candidate choices or outstanding votes'}
assert all(name in raw('sos-current-qualifying') for name in ('Scott Colom','Ty Pinkins','Cindy Hyde-Smith'))
assert 'Independent' in raw('sos-current-qualifying') and 'November 3, 2026' in raw('sos-current-qualifying')
obs['current_primary_candidate_list']={'names':['Scott Colom','Ty Pinkins','Cindy Hyde-Smith'],'Pinkins_party':'Independent','scope':'Current qualifying publication, not a signed final ballot certificate or result IDs'}
(ROOT/'inspection.json').write_text(json.dumps(obs,indent=2)+'\n');print(json.dumps(obs,indent=2))
