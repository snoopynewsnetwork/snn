"""Exact complete owned membership; only the manifest itself is excluded."""
import gzip,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];STATE=R.parent.parent
EXCLUSION='data/baselines/asset-manifest.json'
MUTABLE_OLD={'data/baselines/scripts/originals.py','data/baselines/scripts/validate.py','data/baselines/scripts/seal.py','data/baselines/scripts/reproduce.py','data/baselines/source/SCHEMA.md','data/baselines/validation.json','data/baselines/seal.json',EXCLUSION}
def sha(b):return hashlib.sha256(b).hexdigest()
def owned(state=STATE):
 r=state/'data/baselines'
 return sorted([p for p in r.rglob('*') if p.is_file()]+[state/'county-partisanship.md',state/'data/county-baselines.csv'])
def payload(state=STATE):return [p for p in owned(state) if str(p.relative_to(state))!=EXCLUSION]
def verify(state=STATE,read=None):
 read=read or (lambda p:p.read_bytes());r=state/'data/baselines';manifest=json.loads(read(r/'asset-manifest.json'))
 assert manifest['self_hash_exclusions']==[EXCLUSION],'manifest exclusion must be itself only'
 assets=manifest['assets'];keys=[x['path'] for x in assets];expected={str(p.relative_to(state)) for p in payload(state)}
 assert len(keys)==len(set(keys)) and set(keys)==expected,('manifest membership mismatch',expected-set(keys),set(keys)-expected)
 assert 'data/baselines/seal.json' in expected
 for row in assets:
  b=read(state/row['path']);assert len(b)==row['bytes']<40000000 and sha(b)==row['sha256'],('asset changed',row['path'])
 seal=json.loads(read(r/'seal.json'));assert 'manifest_sha256' not in seal,'reverse current manifest digest forbidden'
 for row in seal['pins']:
  b=read(state/row['path']);assert len(b)==row['bytes'] and sha(b)==row['sha256'],('seal fixed input changed',row['path'])
 assert all(seal[x] is False for x in ['current_source_accepted','geography_accepted','coordinator_accepted'])
 return {'assets':len(assets),'exclusions':[EXCLUSION],'manifest_sha256':sha(read(r/'asset-manifest.json')),'seal_sha256':sha(read(r/'seal.json')),'validation_sha256':sha(read(r/'validation.json'))}
def historical_integrity():
 h=R/'source/history/seal-input-repair-v1/inventory.json';freeze=json.loads(h.read_bytes());same=[];changed=[]
 for row in freeze['owned_files']+freeze['external_read_only_evidence']:
  b=(R/row['body']).read_bytes();assert len(b)==row['stored_bytes'] and sha(b)==row['stored_sha256'];raw=gzip.decompress(b);assert len(raw)==row['bytes'] and sha(raw)==row['sha256']
 for row in freeze['owned_files']:
  p=STATE/row['path'];assert p.is_file();current=sha(p.read_bytes())
  if current==row['sha256']:same.append(row['path'])
  else:assert row['path'] in MUTABLE_OLD,('substantive payload changed',row['path']);changed.append(row['path'])
 # Original prior manifest coverage is reconstructable entirely from frozen bodies.
 bypath={x['path']:x for x in freeze['owned_files']};oldmf=json.loads(gzip.decompress((R/bypath[EXCLUSION]['body']).read_bytes()))
 for row in oldmf['assets']:assert bypath[row['path']]['sha256']==row['sha256'] and bypath[row['path']]['bytes']==row['bytes']
 return {'old_owned_files':len(freeze['owned_files']),'all_old_bodies_reconstruct':True,'unchanged_old_files':len(same),'changed_packaging_only_files':changed,'unchanged_paths':same,'freeze_inventory_sha256':sha(h.read_bytes())}
