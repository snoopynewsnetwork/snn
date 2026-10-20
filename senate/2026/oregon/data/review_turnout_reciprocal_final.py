"""Coordinator final immutable-body/metadata preservation review; original-source checks separate."""
from pathlib import Path
import tarfile,json,gzip,hashlib
S=Path(__file__).resolve().parents[1];T=S/'data/turnout';N=0

def sha(b):return hashlib.sha256(b).hexdigest()
def ck(x,why):
 global N
 N+=1
 if not x:raise AssertionError(why)

def load(p):return json.loads(p.read_bytes())
def snapshot(folder):
 inv=load(folder/'inventory.json');archives={};result={}
 for a in inv['archives']:
  p=folder/a['path'];b=p.read_bytes();ck(len(b)==a['bytes'] and sha(b)==a['sha256'],'whole snapshot archive hash');archives[a['path']]=tarfile.open(p,'r:gz')
 for r in inv['entries']:
  b=archives[r['archive']].extractfile(r['member']).read() if 'archive' in r else (S/r['immutable_original_path']).read_bytes();ck(len(b)==r['bytes'] and sha(b)==r['sha256'],'complete frozen prior body '+r['path']);ck(r['path'] not in result,'unique snapshot identity');result[r['path']]=b
 for f in archives.values():f.close()
 return result
old=snapshot(T/'source/history/pre-reciprocal-v1');peer=snapshot(T/'source/peer-capture-v1');ck(len(old)==4343 and len(peer)==600,'complete snapshot memberships')
oldmf=json.loads(old['data/turnout/asset-manifest.json']);witness=json.loads(old['data/turnout/pre-peer-witness-v1.json'])
for r in oldmf['owned_assets']+witness['pinned_files']:ck(len(old[r['path']])==r['bytes'] and sha(old[r['path']])==r['sha256'],'every old MF/witness target reconstructed')
for path,b in peer.items():ck((S/path).read_bytes()==b,'captured final peer unchanged at review '+path)
current=load(T/'asset-manifest.json');actual={str(p.relative_to(S)) for p in T.rglob('*') if p.is_file()}|{'turnout.md','data/county-turnout.csv'};listed=[r['path'] for r in current['owned_assets']];ck(len(listed)==len(set(listed))==4367 and actual==set(listed)|{'data/turnout/asset-manifest.json'},'current complete MF only-self exclusion')
for r in current['owned_assets']+current['shared_assets']:
 b=(S/r['path']).read_bytes();ck(len(b)==r['bytes']<40000000 and sha(b)==r['sha256'],'current exact stored body '+r['path'])
changed=[path for path,b in old.items() if (S/path).read_bytes()!=b]
expected={'turnout.md','data/turnout/asset-manifest.json','data/turnout/priority-set.json','data/turnout/scripts/validate.py','data/turnout/source/SCHEMA.md','data/turnout/validation.json'}
ck(set(changed)==expected,'only explicit report/metadata/validator changes '+str(changed));before=json.loads(old['data/turnout/priority-set.json']);after=load(T/'priority-set.json');changed_fields=[k for k in set(before)|set(after) if before.get(k)!=after.get(k)];ck(changed_fields==['peer_agreement'],'only contract peer_agreement metadata changed')
ck(sha((S/'data/county-turnout.csv').read_bytes())=='709d5f6ed17343347fcc486d60022f3a3f9cb6698c8d80c6475b5504dfad351f','native CSV unchanged');ck(sha((T/'pre-peer-witness-v1.json').read_bytes())=='d2b433035d5671178fda01261f0d35a6d13d95ab9c9a2204192ea138eda291b9','original-first witness unchanged')
proof=load(T/'peer-reconciliation.json');e=proof['full_evidence'];z=(T/e['path']).read_bytes();ck(sha(z)==e['stored_sha256'] and len(z)==e['stored_bytes'],'complete source-core stored evidence');b=gzip.decompress(z);ck(sha(b)==e['raw_sha256'] and len(b)==e['raw_bytes'],'complete source-core raw evidence');full=json.loads(b);c=proof['counts'];ck(c['candidate_differences']==1 and c['control_differences']==17,'bounded unclosed Douglas differences explicit');ck(c['known_native_rows']==510 and c['county_orders']==14 and c['unique_raw_CSV_fields']==25483,'captured shared order/raw source scope')
rebuild=load(T/'source/offline-rebuild.json');ck(rebuild['status']=='pass' and rebuild['reconstructed_bodies']==4343 and rebuild['all_original_first_bodies_identical'],'nine-script original rebuild proof');negative=load(T/'source/corruption-fixtures.json');ck(negative['negative_fixtures']==14 and negative['exact_boundary_positive'],'meaningful corruption and exact80 fixtures')
seal=load(T/'finalseal.json')
for r in seal['pins']:
 b=(S/r['path']).read_bytes();ck(sha(b)==r['sha256'] and len(b)==r['bytes'],'fixed seal pin')
ck(sha((T/'asset-manifest.json').read_bytes()).encode() not in (T/'finalseal.json').read_bytes() and sha((T/'asset-manifest.json').read_bytes()).encode() not in (T/'validation.json').read_bytes(),'acyclic current seal/validation')
for k in ['complete_order','ordered_priority_keys','top15','minimum80','remainder']:ck(after[k] is None,'unavailable canonical native '+k)
ck(after['canonical_certified_native_priority_available'] is False,'no canonical priority acceptance')
result={'status':'pass_final_bounded_reciprocal_source_core_preservation','checks':N,'complete_current_owned_files':4368,'manifest_entries':4367,'source_assets':61,'old_own_bodies_reconstructed':4343,'captured_final_peer_bodies_verified':600,'changed_only_packaging_and_peer_metadata_paths':changed,'contract_changed_only_peer_agreement':True,'all_other_original_count_source_order_control_hierarchy_bodies_unchanged':True,'bounded_peer_counts':c,'coverage_differences':proof['coverage'],'canonical_native_priority':None,'unclosed_2024native_parents':31,'complete_evidence_pins':e,'reviewed_manifest_sha256':sha((T/'asset-manifest.json').read_bytes()),'future_peer_calculator_scenario_report_equality_claim':False,'current_or_geographic_approval':False}
(S/'data/coordinator-turnout-reciprocal-final-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'checks':N,'changed_paths':changed,'original_bodies':4343,'peer_bodies':600}))
