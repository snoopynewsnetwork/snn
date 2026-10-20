import pathlib,json,hashlib,gzip,tarfile,io
B=pathlib.Path('/Users/tqbf/codebase/snn/senate/2026/alabama');P=B/'data/baselines';T=pathlib.Path('/private/tmp/al-reciprocal')
def sha(b):return hashlib.sha256(b).hexdigest()
mf=P/'asset-manifest.json';body=mf.read_bytes();assert len(body)==60279 and sha(body)=='13ec2553cbeafdbf4111f1decd6c686e14d5fbfb8c196c70d3e95836f7016254';m=json.loads(body);expected={x['path']:x for x in m['assets']};actual={str(p.relative_to(B)):p for p in P.rglob('*') if p.is_file()};actual['county-partisanship.md']=B/'county-partisanship.md';actual['data/county-baselines.csv']=B/'data/county-baselines.csv';assert len(expected)==306 and len(actual)==307 and set(actual)==set(expected)|{'data/baselines/asset-manifest.json'}
for name,r in expected.items():
 b=actual[name].read_bytes();assert len(b)==r['bytes'] and sha(b)==r['sha256'] and len(b)<40000000,name
archive=T/'baseline-actual-final.tar.gz'
with tarfile.open(archive,'w:gz',compresslevel=9) as tf:
 for name,p in sorted(actual.items()):tf.add(p,arcname=name,recursive=False)
assert archive.stat().st_size<40000000
with tarfile.open(archive,'r:gz') as tf:
 assert set(tf.getnames())==set(actual)
 for name,p in actual.items():assert tf.extractfile(name).read()==p.read_bytes()
v1=P/'history/original-first-v1.tar.gz';found=[]
with tarfile.open(v1,'r:gz') as tf:
 for item in tf.getmembers():
  if item.isfile():
   b=tf.extractfile(item).read()
   if sha(b)=='941f8c78065a55966c2514b6e99bc1e148ec200d9cc1b269cf461146e83b940d':found.append({'path_in_archive':item.name,'bytes':len(b),'sha256':sha(b)})
assert len(found)==1
proof={'status':'PASS','scope':'All actual-final baseline bodies captured BEFORE comparison; no peer scripts executed, writer contacted or report/model outcomes adopted.','manifest_sha256':sha(body),'manifest_bytes':len(body),'manifest_target_count':306,'complete_files_including_manifest':307,'archive_sha256':sha(archive.read_bytes()),'archive_bytes':archive.stat().st_size,'old_original_first_v1_witness':found,'files':[dict(path=n,bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for n,p in sorted(actual.items())]}
(T/'peer-capture-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items() if k!='files'},indent=2))
# Own originals/MF were already verified and losslessly captured before this script existed.
O=B/'data/turnout/reciprocal';O.mkdir(exist_ok=True)
for n in ['turnout-original-phase.tar.gz','own-capture-proof.json','baseline-actual-final.tar.gz','peer-capture-proof.json','capture_start.py']:
 (O/n).write_bytes((T/n).read_bytes())
