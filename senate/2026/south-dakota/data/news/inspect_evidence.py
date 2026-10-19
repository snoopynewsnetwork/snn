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
import csv,io
rows_csv=list(csv.DictReader(io.StringIO(raw('sos-statewide-export'))))
sen=[r for r in rows_csv if r['RaceID']=='14412']
assert len(sen)==2 and {r['PartyCode'] for r in sen}=={'REP','IND'}
assert all(int(r['CandidateVotes'])==0 for r in sen)
assert 'Testing In Progress' in raw('sos-results-media')
assert '"displayTestData":true' in raw('dakota-results')
obs.update(state_november_setup_test=True,senate_candidates=[{'id':r['CandidateID'],'label':r['CandidateName'],'party':r['PartyCode'],'votes':int(r['CandidateVotes'])} for r in sen])
(ROOT/'inspection.json').write_text(json.dumps(obs,indent=2)+'\n');print(json.dumps(obs,indent=2))
