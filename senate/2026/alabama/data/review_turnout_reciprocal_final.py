"""Coordinator complete old/final capture and metadata-only semantic bridge.
No producer modules, parser import, network or source/producer writes.
"""
from pathlib import Path
import gzip,hashlib,io,json,tarfile,sys
S=Path(__file__).resolve().parents[1];D=S/'data';T=D/'turnout';B=D/'baselines';REPO=S.parents[2];AL=S.name=='alabama';N=0

def ck(v,label=''):
 global N
 N+=1
 assert v,(N,label)
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_bytes())
def pin(p):
 b=p.read_bytes();return {'path':str(p.relative_to(S)),'bytes':len(b),'sha256':sha(b)}
def audit_archive(path,expected,number):
 b=path.read_bytes();ck(sha(b)==expected and len(b)<40000000,'complete archive')
 tf=tarfile.open(fileobj=io.BytesIO(b),mode='r:gz');members={}
 for m in tf:
  ck(m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts,'regular safe body')
  ck(m.name not in members,'unique archive body');members[m.name]=tf.extractfile(m).read();ck(len(members[m.name])==m.size,'full member length')
 ck(len(members)==number,'every member');return members
hist=[]
if AL:
 root=T/'reciprocal';a=read(root/'own-capture-proof.json');p=read(root/'peer-capture-proof.json')
 own=audit_archive(root/'turnout-original-phase.tar.gz',a['archive_sha256'],146)
 peer=audit_archive(root/'baseline-actual-final.tar.gz',p['archive_sha256'],306)
 ck(set(own)==set(a['archive_original_paths']),'every original own path')
 for ref in p['original_entity_references']:
  b=(S/ref['path']).read_bytes();ck(sha(b)==ref['sha256'] and len(b)==ref['bytes'],'complete immutable peer original');raw=gzip.decompress(b);ck(sha(raw)==ref['original_sha256'] and len(raw)==ref['original_bytes']);peer[ref['path']]=b
 ck(len(peer)==307 and {r['path'] for r in p['files']}==set(peer),'complete final peer')
 for ref in p['files']:ck(len(peer[ref['path']])==ref['bytes'] and sha(peer[ref['path']])==ref['sha256'])
 roles=[('own',own,a['manifest_sha256'],root/'turnout-original-phase.tar.gz'),('peer',peer,p['manifest_sha256'],root/'baseline-actual-final.tar.gz')]
 allowed={'peer_agent_id','independent_peer_agreement','dispatch_status','peer_agreement_scope'}
 expectedchanges={'data/turnout/asset-manifest.json','data/turnout/final-seal.json','data/turnout/priority-set.json','data/turnout/scripts/validate.py','data/turnout/source/SCHEMA.md','data/turnout/validation.json','turnout.md'}
 comparison=read(root/'comparison.json');ck(comparison['status']=='PASS' and comparison['independent_peer_agreement'] is True)
 ck(comparison['counts']['members']==201 and comparison['counts']['native_units']==6270 and comparison['counts']['selected_raw_cells']==610064)
 offline=read(root/'offline-reproduction.json');ck(offline['status']=='PASS' and offline['byte_identical_rebuilt_original_targets']==144 and len(offline['route_probes'])==5 and not offline['network_used'] and not offline['mutable_aggregate_used'])
 ck(len(offline['regenerated_audit_only_differences'])==1 and offline['regenerated_audit_only_differences'][0]['captured_original']==16 and offline['regenerated_audit_only_differences'][0]['regenerated']==17)
 negatives=read(root/'corruption-validation.json');ck(negatives['status']=='PASS' and negatives['actual_corruption_fixture_count']==30)
 witness=T/'source/original-first-witness.json';ck(sha(witness.read_bytes())=='b8a4bba1c934beb847166e79d5ca75e1d8b0a5757da5bdbb80abda490b7d7ce5')
else:
 root=T/'history/captured-final-reciprocal';capture=read(root/'capture.json');roles=[]
 for role in ['own','peer']:
  spec=capture[role];stored=[r for r in spec['records'] if r['storage']=='tar-member'];packed=audit_archive(root/spec['archive'],spec['archive_sha256'],len(stored));allbody={}
  for ref in spec['records']:
   b=packed[ref['member']] if ref['storage']=='tar-member' else (REPO/ref['reference_path']).read_bytes()
   ck(len(b)==ref['bytes'] and sha(b)==ref['sha256'],'exact old path+digest');allbody[ref['path']]=b
  ck(len(allbody)==spec['body_count'] and set(packed)=={r['member'] for r in stored},'all original capture bodies')
  roles.append((role,allbody,spec['manifest_sha256'],root/spec['archive']))
 own=roles[0][1];peer=roles[1][1]
 allowed={'acceptance_status'}
 expectedchanges={'data/turnout/asset-manifest.json','data/turnout/final-seal.json','data/turnout/priority-set.json','data/turnout/report.py','data/turnout/seal.py','data/turnout/source/SCHEMA.md','data/turnout/validate.py','data/turnout/validation.json','turnout.md'}
 comparison=read(T/'reciprocal.json');ck(comparison['status']=='pass' and comparison['checks']==9608341 and comparison['errors']==[])
 offline=read(T/'isolated-replay.json');ck(offline['status']=='pass' and len(offline['outputs'])==49 and not offline['network_allowed'] and not offline['peer_derivatives_allowed'])
 negatives=read(T/'reciprocal-fixtures.json');ck(negatives['status']=='pass' and negatives['negative_cases']==24 and negatives['all_rejected'])
 core=T/'history/original-first-core/core.tar.gz';ck(sha(core.read_bytes())=='b23716c17084a5a49a3534f1d494667818a36d0c27ec397f6bc9ba08bca2cf3f')
for role,bodies,mfsha,archive in roles:
 path='data/'+('turnout' if role=='own' else 'baselines')+'/asset-manifest.json';mb=bodies[path];mf=json.loads(mb);ck(sha(mb)==mfsha)
 ck(set(bodies)=={r['path'] for r in mf['assets']}|{path},'complete original manifest scope')
 for ref in mf['assets']:
  b=bodies[ref['path']];ck(len(b)==ref['bytes'] and sha(b)==ref['sha256'],'every old manifest target')
  if role=='peer':ck(b==(S/ref['path']).read_bytes(),'captured completed peer remains exact')
 hist.append({'role':role,'archive':pin(archive),'complete_original_files':len(bodies),'old_manifest_sha256':mfsha})
changes=[]
for path,b in own.items():
 if b!=(S/path).read_bytes():changes.append(path)
ck(set(changes)==expectedchanges,'only explicit authorized old body changes')
old=json.loads(own['data/turnout/priority-set.json']);new=read(T/'priority-set.json')
ck(set(old)-set(allowed)<=set(new),'no nonmetadata field dropped')
for k in set(old)|set(new):
 if k not in allowed:ck(k in old and k in new and old[k]==new[k],'entire nonmetadata contract field '+k)
ck(own['data/county-turnout.csv']==(D/'county-turnout.csv').read_bytes(),'native/county compatibility CSV unchanged')
current=read(T/'asset-manifest.json');rows=current['assets'];actual={str(p.relative_to(S)) for p in T.rglob('*') if p.is_file()}|{'turnout.md','data/county-turnout.csv'}
ck(len(rows)==(295 if AL else 1065) and {r['path'] for r in rows}==actual-{'data/turnout/asset-manifest.json'})
for r in rows:ck(pin(S/r['path'])=={k:r[k] for k in ['path','bytes','sha256']} and r['bytes']<40000000,'every final target')
result={'status':'pass_complete_capture_history_and_metadata_only_reciprocal_bridge','checks':N,'current_manifest':pin(T/'asset-manifest.json'),'old_and_peer_complete_captures':hist,'whole_old_body_count':len(own),'whole_final_peer_bodies':len(peer),'old_bodies_unchanged':len(own)-len(changes),'only_changed_old_paths':sorted(changes),'allowed_contract_metadata_fields':sorted(allowed),'all_other_full_contract_objects_exact':True,'compatibility_CSV_unchanged':True,'comparison_proof':pin(T/('reciprocal/comparison.json' if AL else 'reciprocal.json')),'original_source_scope':comparison.get('counts',comparison.get('coverage')),'isolated_rebuild_scope':{'byte_identical_old_targets':144,'regenerated_audit_history_count':{'old':16,'regenerated':17},'denied_route_probes':5} if AL else {'byte_identical_old_products':49,'network':False,'peer_inputs':False},'negative_fixtures':30 if AL else 24,'root_prior_original_math_and_CLI_reviews_remain_immutable':True,'worker_or_peer_writes':False,'current_legal_geometry_feed_calculator_outcome_or_future_equality_claim':False}
out=D/'coordinator-turnout-reciprocal-final-review.json';body=(json.dumps(result,indent=2)+'\n').encode()
if '--check' in sys.argv:ck(out.read_bytes()==body,'same bridge evidence')
else:out.write_bytes(body)
print(json.dumps({k:v for k,v in result.items() if k not in ['original_source_scope','old_and_peer_complete_captures','only_changed_old_paths']}))
