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
for name in ('wrdw-results','wtoc-results','walb-results'):
 assert '"displayTestData":true' in raw(name) and '"selectedElection":{"id":null}' in raw(name)
assert '"displayTestData":true' in raw('wtvm-results') and '"name":"AUBURN CITY ELECTIONS 2026"' in raw('wtvm-results')
assert '"id":"2649","isActive":false' in raw('wtvm-results')
for layout in ('110246/32468.html','110246/32439.html'):
 assert layout in raw('wtvm-georgia') and layout in raw('wtoc-georgia')
assert 'https://www.13wmaz.com/elections' in raw('wmaz-home')
assert '2026-midterm-elections-georgia-how-ballots-are-counted' in raw('wmaz-elections')
assert '2026 General Primary Runoff' in raw('accg-results') and '900000' in raw('accg-results')
assert 'Mon Jul 13 16:30:01 EDT 2026' in raw('fox5-embed')
obs.update(wrdw_wtoc_walb_empty_test_display=True,wtvm_selected='Inactive Auburn Alabama city election2649; test display enabled',wtvm_wtoc_same_AP_layouts=True,wmaz_scope='Actual linked current election hub; no established November count payload',accg_selected='2026 June primary runoff',fox5_embed_timestamp='2026-07-13')
(ROOT/'inspection.json').write_text(json.dumps(obs,indent=2)+'\n');print(json.dumps(obs,indent=2))
