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
from xml.etree import ElementTree as ET
assert '7th%20District%20Democratic%20Primary' in raw('news12-primary')
assert 'Vote 2024' in raw('news12-primary-embed')
assert 'include/races.jsp' in raw('news12-primary-code') and '30000' in raw('news12-primary-code')
x=ET.fromstring(raw('news12-primary-category-list'))
assert any('Senate Class II General New Jersey' in (c.findtext('TITLE') or '') and c.findtext('ID')=='13' for c in x.findall('CATEGORY'))
x=ET.fromstring(raw('news12-senate-general-data'))
assert x.findtext('RACE_DATA/PERCENT')=='98'
assert x.findtext('RACE_DATA/LAST_UPDATED')=='Last updated on Oct 15, 2026 4:09 PM'
c=x.findall('RACE_CANDIDATES/RACE_CANDIDATE');assert len(c)==4
assert sum(int(r.findtext('VOTES_NUM').replace(',','')) for r in c)>0
assert c[0].findtext('LAST')=='Booker' and c[0].findtext('WINNER')=='1'
assert '2026_DE_PRIMARY.html' in raw('fox29-results')
result={'news12_general_label_id':'13','news12_candidates':4,'news12_status':'unvalidated nonzero pre-election/setup counts; no election date/test flag','usable_november_counts_established':False}
assert next(r for r in rows if r['id']=='nyt-elections')['status']==403
result.update(status='pass',retained_assets=sum('asset' in r for r in rows))
(ROOT/'inspection.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
