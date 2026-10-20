"""Read-only final exact-set verification; emits no owned file."""
from acquire import *
ROOT=BASE.parent
m=json.loads((BASE/'asset-manifest.json').read_bytes());expected={e['path'] for e in m['files']};actual={'precinct-maps.md'}|{str(p.relative_to(ROOT)) for p in BASE.rglob('*') if p.is_file() and p!=BASE/'asset-manifest.json'};assert expected==actual,(expected-actual,actual-expected)
for e in m['files']:
 b=(ROOT/e['path']).read_bytes();assert len(b)==e['bytes']<40000000 and sha(b)==e['sha256'],e['path']
s=json.loads((BASE/'final-seal.json').read_bytes())
for e in s['critical_products']:
 b=(ROOT/e['path']).read_bytes();assert len(b)==e['bytes'] and sha(b)==e['sha256']
for p in BASE.rglob('*'):assert p.name not in ['__pycache__','node_modules','.cache'],str(p)
assert not s['manifest_reverse_pin'] and not s['optional_coordinator_proof_dependency']
print(json.dumps({'status':'pass_read_only_exact_self_only_seal','listed_owned_files':len(expected),'plus_manifest':1,'manifest_sha256':sha((BASE/'asset-manifest.json').read_bytes()),'finalseal_sha256':sha((BASE/'final-seal.json').read_bytes())}))
