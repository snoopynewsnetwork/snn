"""Coordinator-only fixed-body audit of the narrow producer packaging/input repair."""
import gzip,hashlib,json
from pathlib import Path
S=Path(__file__).resolve().parents[1]; R=S/'data/baselines'
def sha(b):return hashlib.sha256(b).hexdigest()
checks=0
def ck(x):
 global checks
 assert x
 checks+=1
m=json.loads((R/'asset-manifest.json').read_bytes());ck(m['self_hash_exclusions']==['data/baselines/asset-manifest.json'])
actual={str(p.relative_to(S)) for p in R.rglob('*') if p.is_file()}|{'county-partisanship.md','data/county-baselines.csv'}
listed=[x['path'] for x in m['assets']];ck(len(listed)==len(set(listed))==599);ck(set(listed)==actual-{'data/baselines/asset-manifest.json'});ck(len(actual)==600)
for row in m['assets']:
 b=(S/row['path']).read_bytes();ck(len(b)==row['bytes']<40000000 and sha(b)==row['sha256'])
freeze=json.loads((R/'source/history/seal-input-repair-v1/inventory.json').read_bytes()); old={};changed=[];same=[]
for row in freeze['owned_files']+freeze['external_read_only_evidence']:
 stored=(R/row['body']).read_bytes();ck(len(stored)==row['stored_bytes'] and sha(stored)==row['stored_sha256']);raw=gzip.decompress(stored);ck(len(raw)==row['bytes'] and sha(raw)==row['sha256'])
 if row in freeze['owned_files']:old[row['path']]=raw
for path,body in old.items():
 if body==(S/path).read_bytes():same.append(path)
 else:changed.append(path)
allowed={'data/baselines/scripts/originals.py','data/baselines/scripts/validate.py','data/baselines/scripts/seal.py','data/baselines/scripts/reproduce.py','data/baselines/source/SCHEMA.md','data/baselines/validation.json','data/baselines/seal.json','data/baselines/asset-manifest.json'}
ck(set(changed)==allowed and len(old)==296 and len(same)==288)
for row in json.loads(old['data/baselines/asset-manifest.json'])['assets']:ck(len(old[row['path']])==row['bytes'] and sha(old[row['path']])==row['sha256'])
for path,pin in {'county-partisanship.md':'bd7889a3078cdcf4d5f9b9fc924c590c9124a38380d23dbf61fa11aca5c90e0b','data/county-baselines.csv':'fed7a77bb7181697189c67a51b59abe39960da11d18ce91b4bd3d28e61a8f4db','data/baselines/scripts/calculator.py':'36974be4ce787e70385868548dc675ceefe2eec0241b851f05c035c84452c38c','data/baselines/source/pre-peer-witness.json':'208a3ad98dfb055eea0f895c0c0faf9881f684214e7d5a34c41e01f4df123b7f'}.items():ck(sha((S/path).read_bytes())==pin)
seal=json.loads((R/'seal.json').read_bytes());ck('manifest_sha256' not in seal)
for row in seal['pins']:
 b=(S/row['path']).read_bytes();ck(len(b)==row['bytes'] and sha(b)==row['sha256']);ck(row['path']!='data/baselines/asset-manifest.json')
proof=json.loads((R/'source/repair-proofs/original-rebuild.json').read_bytes());ck(proof['before_after_identical'] and proof['original_entity_texts']==113 and proof['ZIP_members']==72);ck(len(proof['mutable_routes_denied'])==5 and all(x['denied'] for x in proof['mutable_routes_denied']))
for path,pin in proof['unchanged_output_hashes'].items():ck(sha((R/path).read_bytes())==pin)
negative=json.loads((R/'source/repair-proofs/packaging-negatives.json').read_bytes());ck(len(negative['negative_checks'])==3 and all(x['correctly_rejected'] for x in negative['negative_checks']))
for x in ['current_source_accepted','geography_accepted','coordinator_accepted']:ck(seal[x] is False)
result={'status':'pass_narrow_repair_review','checks':checks,'owned_files':600,'manifest_entries':599,'excludes_only':'data/baselines/asset-manifest.json','old_complete_bodies_reconstructed':296,'unchanged_previous_payloads':288,'changed_only_authorized_packaging_files':changed,'immutable_reader_guarded_rebuild':{'entities_texts':113,'ZIP_members':72,'denied_mutable_routes':5},'packaging_negative_fixtures':3,'pins':[{ 'path':str(p.relative_to(S)), 'bytes':p.stat().st_size, 'sha256':sha(p.read_bytes())} for p in [R/'asset-manifest.json',R/'seal.json',R/'validation.json',R/'source/history/seal-input-repair-v1/inventory.json',R/'source/inputs/original-receipts-v1.json']],'scope':'Complete body preservation, immutable input reader and self-only manifest repair. Historical sources, model, orders, scenarios and calculator unchanged; no renewed math/live/current approval.'}
(S/'data/coordinator-baseline-repair-review.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps({'status':result['status'],'checks':checks,'unchanged':len(same),'changed_packaging':len(changed)}))
