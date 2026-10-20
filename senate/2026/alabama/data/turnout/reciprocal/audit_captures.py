#!/usr/bin/env python3
"""Read-only complete original-phase and captured-final-peer reconstruction audit."""
import pathlib,tarfile,json,gzip,hashlib,posixpath,io,sys
R=pathlib.Path(__file__).resolve().parents[1];S=R.parents[1];REPO=S.parents[2];D=R/'reciprocal'
def sha(b):return hashlib.sha256(b).hexdigest()
def verify():
 op=json.loads((D/'own-capture-proof.json').read_text());pp=json.loads((D/'peer-capture-proof.json').read_text());ob=(D/'turnout-original-phase.tar.gz').read_bytes();pb=(D/'baseline-actual-final.tar.gz').read_bytes();assert len(ob)==op['archive_bytes'] and sha(ob)==op['archive_sha256'];assert len(pb)==pp['archive_bytes'] and sha(pb)==pp['archive_sha256'];o=tarfile.open(fileobj=io.BytesIO(ob));p=tarfile.open(fileobj=io.BytesIO(pb));om=json.loads(o.extractfile('data/turnout/asset-manifest.json').read());pm=json.loads(p.extractfile('data/baselines/asset-manifest.json').read());assert len(om['assets'])==145 and len(pm['assets'])==306
 assert sha(o.extractfile('data/turnout/asset-manifest.json').read())=='4e2a1f5ab3c66508444c112f9e6430006dce94f795a172837c7b95eaee557207';assert sha(p.extractfile('data/baselines/asset-manifest.json').read())=='13ec2553cbeafdbf4111f1decd6c686e14d5fbfb8c196c70d3e95836f7016254'
 assert len(o.getnames())==len(set(o.getnames()))==146 and set(o.getnames())=={a['path'] for a in om['assets']}|{'data/turnout/asset-manifest.json'}
 external={r['path']:r for r in pp['original_entity_references']};assert len(p.getnames())==306 and len(set(p.getnames()))==306;assert set(p.getnames())|set(external)=={a['path'] for a in pm['assets']}|{'data/baselines/asset-manifest.json'}
 def pread(path):
  if path in external:
   r=external[path];b=(S/path).read_bytes();assert len(b)==r['bytes'] and sha(b)==r['sha256'];raw=gzip.decompress(b);assert len(raw)==r['original_bytes'] and sha(raw)==r['original_sha256'];return b
  return p.extractfile(path).read()
 for archive,manifest in [(o,om),(None,pm)]:
  for a in manifest['assets']:
   b=archive.extractfile(a['path']).read() if archive else pread(a['path']);assert len(b)==a['bytes'] and sha(b)==a['sha256'] and len(b)<40000000,a['path']
 originals=0
 for r in om['external_originals']:
  b=(REPO/r['path']).read_bytes();raw=gzip.decompress(b);assert len(b)==r['stored_bytes'] and sha(b)==r['stored_sha256'];assert len(raw)==r['original_bytes'] and sha(raw)==r['original_sha256'];originals+=1
 # Every complete old turnout history body reconstructs by the path and SHA in its original metadata.
 histories=0
 for name in o.getnames():
  if name.startswith('data/turnout/history/') and name.endswith('.json'):
   r=json.loads(o.extractfile(name).read());b=gzip.decompress(o.extractfile('data/turnout/history/'+r['stored_body']).read());assert len(b)==r['original_bytes'] and sha(b)==r['sha256'];histories+=1
 own_witness=o.extractfile('data/turnout/source/original-first-witness.json').read();assert sha(own_witness)=='b8a4bba1c934beb847166e79d5ca75e1d8b0a5757da5bdbb80abda490b7d7ce5';assert (R/'source/original-first-witness.json').read_bytes()==own_witness
 # All HTTP entity/receipt contexts in actual final peer are verified, including capture-only later/optional originals.
 fresh_receipts=0
 for name in p.getnames():
  if name.startswith('data/baselines/source/http/') and name.endswith('.receipt.json'):
   r=json.loads(pread(name));path=posixpath.normpath('data/baselines/'+r['stored_path_relative_baselines']);b=o.extractfile(path).read() if path.startswith('data/turnout/') else pread(path);assert len(b)==r['stored_bytes'] and sha(b)==r['stored_sha256'];raw=gzip.decompress(b);assert len(raw)==r['original_bytes'] and sha(raw)==r['original_sha256'];fresh_receipts+=1
 nested=tarfile.open(fileobj=io.BytesIO(pread('data/baselines/history/original-first-v1.tar.gz')));found=[n.name for n in nested.getmembers() if n.isfile() and sha(nested.extractfile(n).read())=='941f8c78065a55966c2514b6e99bc1e148ec200d9cc1b269cf461146e83b940d'];assert len(found)==1
 # Peer reverse comparison is proof only of the captured original turnout phase.
 reverse_body=pread('data/baselines/peer-reconciliation.json');assert sha(reverse_body)==next(x['sha256'] for x in pm['assets'] if x['path']=='data/baselines/peer-reconciliation.json');reverse=json.loads(reverse_body);assert reverse['peer_frozen_manifest_sha256']=='4e2a1f5ab3c66508444c112f9e6430006dce94f795a172837c7b95eaee557207' and reverse['own_original_first_v1_sha256']=='941f8c78065a55966c2514b6e99bc1e148ec200d9cc1b269cf461146e83b940d'
 return {'status':'PASS','own_original_manifest_targets_reconstructed':145,'own_complete_original_files_including_manifest':146,'own_original_history_bodies_reconstructed':histories,'own_original_first_witness_sha256':sha(own_witness),'own_external_originals_verified':originals,'peer_actual_final_manifest_targets_reconstructed':306,'peer_complete_files_including_manifest':307,'peer_archive_bodies':306,'peer_large_original_entity_references':len(external),'peer_capture_only_fresh_original_receipts_verified':fresh_receipts,'peer_original_first_v1_witness_sha256':'941f8c78065a55966c2514b6e99bc1e148ec200d9cc1b269cf461146e83b940d','source_scope':'Only frozen exact individual original references and complete captured archive bodies. Peer reverse proof is original-turnout-phase historical evidence, never future/current full-report equality.'}
if __name__=='__main__':
 result=verify()
 if '--audit' not in sys.argv:(D/'capture-reconstruction-validation.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
