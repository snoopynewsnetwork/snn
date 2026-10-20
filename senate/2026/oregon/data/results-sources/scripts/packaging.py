"""Self-only manifest, fixed-input seal, complete owned membership."""
from pathlib import Path
from replay_inputs import R,S,sha
import json
MANIFEST='data/results-sources/asset-manifest.json'
def owned():
 p=[S/'official-results.md',S/'data/official-results-sources.csv']+[x for x in R.rglob('*') if x.is_file()]
 assert all(not x.is_symlink() for x in p)
 return {str(x.relative_to(S)):x for x in p}
def validate_members(manifest,payloads):
 assert manifest['excluded']==[MANIFEST]
 rows=manifest['files'];assert len({x['path'] for x in rows})==len(rows)
 assert {x['path'] for x in rows}==set(payloads)-{MANIFEST},'exact full membership excluding self only'
 for x in rows:
  b=payloads[x['path']];assert len(b)==x['bytes']<40000000 and sha(b)==x['sha256'],'full hash/size '+x['path']
 assert 'data/results-sources/finalseal.json' in payloads
 seal=json.loads(payloads['data/results-sources/finalseal.json']);assert 'manifest_sha256' not in seal and 'current_manifest' not in seal
 for r in seal['fixed_inputs']:
  b=payloads[r['path']];assert sha(b)==r['sha256'] and len(b)==r['bytes'],'seal fixed input '+r['path']
 return len(rows)
def audit_members():
 p=owned();data={k:v.read_bytes() for k,v in p.items()};m=json.loads(data[MANIFEST]);return validate_members(m,data)
