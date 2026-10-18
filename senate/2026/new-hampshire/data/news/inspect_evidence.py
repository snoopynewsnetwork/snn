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
assert 'September 8, 2026' in raw('nh-results-primary') and re.search(r'local\s+volunteers', raw('nh-results-primary'))
assert '1970 to 2024' in raw('nhpr-database')
assert '128298/32161.html' in raw('nhpr-primary')
assert 'https://ehub.htvapps.com/wmur/wp-json/election-hub/v1/widget/775' in raw('wmur-local-embed')
widget=json.loads(raw('wmur-local-widget'))
assert len(widget['results'])==8 and {r['source'] for r in widget['results']}=={'hearst'}
senate=[r for r in widget['results'] if 'U.S. Senate' in r['title']]
assert len(senate)==2
controls=[]
for race in senate:
 assert sum(c['votes_total'] for c in race['candidates'])==race['total_votes']
 assert race['precincts_reporting']==race['precincts_total']==318
 assert race['last_updated']=='2026-09-24T20:56:18+00:00'
 controls.append({k:race[k] for k in ['id','title','total_votes','precincts_reporting','precincts_total','last_updated','source']})
obs['WMUR_September_primary_widget']={'items':8,'senate_controls':controls,'scope':'Displayed candidate sums only, no town rows or certification reconciliation. Source label hearst does not establish original count gathering. No November admission or measured publication cadence.'}
obs.update(volunteer_primary_not_official=True,nhpr_database_historical_through_2024=True)
assert 'As Nov. 3 election nears, a look at some Coos County ballots' in raw('berlin-sun-home')
assert '2026-09-08T14:32:00-04:00' in raw('laconia-belmont-primary')
assert 'state Primary Election' in raw('laconia-belmont-primary')
assert 'By News Release' in raw('indepth-absentee-report')
obs['additional_regional_channels']={
 'Berlin':'Current homepage200 links Coos ballot reporting; exact linked article429, no downloaded article or November scoreboard claim.',
 'Laconia':'Current elections parent200 and September8 Belmont primary original reporting200; publisher timestamps distinguish historical primary from November.',
 'CaledonianRecord':'Homepage200 covers multiple states; inspected StJohnsbury mail headline is Vermont and excluded as NH counting evidence.',
 'InDepthNH':'Current homepage200 and October14 absentee article200; By News Release attribution means republished administration guidance, not independent count confirmation.'}
(ROOT/'inspection.json').write_text(json.dumps(obs,indent=2)+'\n');print(json.dumps(obs,indent=2))
