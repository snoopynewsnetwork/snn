#!/usr/bin/env python3
"""Verify retained public captures; summarize bounded product inspections."""
from pathlib import Path
from collections import Counter
import datetime,gzip,hashlib,json,re
ROOT=Path(__file__).resolve().parent
rows=json.loads((ROOT/'manifest.json').read_text())
for r in rows:
 if 'asset' not in r:continue
 b=(ROOT/r['asset']).read_bytes();assert hashlib.sha256(b).hexdigest()==r['stored_sha256'],r['id']
 raw=gzip.decompress(b);assert hashlib.sha256(raw).hexdigest()==r['raw_sha256'],r['id']
def raw(name):
 r=next(r for r in rows if r['id']==name);return gzip.decompress((ROOT/r['asset']).read_bytes()).decode(errors='replace')
obs={'captures':len(rows),'verified_assets':sum('asset' in r for r in rows)}
x=json.loads(raw('kmbc-primary-widget'));assert len(x['results'])==40 and x['last_updated']=='2026-08-05T03:55:26+00:00'
assert all(r['source']=='hearst' for r in x['results'])
assert '"displayTestData":true' in raw('wibw-results') and '2026 Kansas Primary' in raw('wibw-results')
obs.update(kmbc_historical_items=40,kmbc_timestamp=x['last_updated'],wibw_test_display=True)
assert '../data/KS_S_8_4_2026.json' in raw('npr-primary') and '../data/KS_S_8_4_2026_counties.json' in raw('npr-primary')
assert 'Sources: Electoral results from the AP.' in raw('npr-primary')
state=json.loads(raw('npr-senate-primary'))['races'];county=json.loads(raw('npr-senate-primary-counties'))['races']
assert len(state)==len(county)==2
controls=[]
for race in state:
 assert (race['date'],race['state'],race['type'],race['office'],race['seat'],race['test'])==('8/4/2026','KS','Primary','S','2',False)
 other=next(r for r in county if r['id']==race['id'])
 assert all(other[k]==race[k] for k in ('date','state','type','office','seat','party','test'))
 rows=other['results'];assert len(rows)==len({r['fips'] for r in rows})==105
 assert all(re.fullmatch(r'20\d{3}',r['fips']) for r in rows)
 top,=race['results'];sums=Counter();candidates={c['id']:c for c in top['candidates']}
 for row in rows:
  assert {c['id'] for c in row['candidates']}==set(candidates)
  assert sum(c['votes'] for c in row['candidates'])==row['total']
  sums.update({c['id']:c['votes'] for c in row['candidates']})
 assert all(sums[cid]==c['votes'] for cid,c in candidates.items())
 assert sum(sums.values())==top['total']==sum(r['total'] for r in rows)
 assert sum(r['precincts'] for r in rows)==top['precincts']==4150
 reporting=sum(r['reporting'] for r in rows)
 assert top['reporting']==4149 and reporting==({'Dem':4137,'GOP':4149}[race['party']])
 controls.append({'party':race['party'],'race_id':race['id'],'county_rows':105,'displayed_candidate_count':len(candidates),'displayed_total':top['total'],
                  'state_reporting':top['reporting'],'county_reporting_sum':reporting,'state_eevp':top['eevp'],
                  'source_updated_utc_from_epoch':datetime.datetime.fromtimestamp(top['updated']/1000,datetime.timezone.utc).isoformat(),
                  'incomplete_counties':[{k:r[k] for k in ('fips','county','reporting','precincts','eevp')} for r in rows if r['reporting']!=r['precincts']]})
obs['NPR_AP_August_primary']={'controls':controls,'scope':'All displayed candidate/county sums reconcile. State/county reporting scopes differ; EEVP is separate. No certified all-candidate universe, November result admission or measured release cadence established.'}
(ROOT/'inspection.json').write_text(json.dumps(obs,indent=2)+'\n');print(json.dumps(obs,indent=2))
