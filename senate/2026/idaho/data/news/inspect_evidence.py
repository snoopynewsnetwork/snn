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
assert '"selectedElection":{"id":null}' in raw('kmvt-results') and '"displayTestData":true' in raw('kmvt-results')
assert '2026' in raw('sos-data') and 'precinct' in raw('sos-data').lower()
obs.update(kmvt_empty_test_display=True,official_maps_index_not_download_validation=True)
(ROOT/'inspection.json').write_text(json.dumps(obs,indent=2)+'\n');print(json.dumps(obs,indent=2))
