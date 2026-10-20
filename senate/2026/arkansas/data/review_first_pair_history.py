"""Coordinator full archive-member/initial witness/captured peer preservation audit."""
from pathlib import Path
import gzip,hashlib,json,tarfile,sys
S=Path(__file__).resolve().parents[1];D=S/'data';N=0

def sha(b):return hashlib.sha256(b).hexdigest()
def ck(v,msg):
 global N
 N+=1
 if not v:raise AssertionError(msg)
def read(p):return json.loads(p.read_bytes())
archives=[]
for role,rel,expected in [('turnout','history/original-first-core','b23716c17084a5a49a3534f1d494667818a36d0c27ec397f6bc9ba08bca2cf3f'),('baselines','history/original-first','037de259b4abfd81806db94a5ca4aeadbe41fb56e893944c322310019f13a24a')]:
 root=D/role/rel;sn=read(root/'snapshot.json');raw=(root/'core.tar.gz').read_bytes();ck(sha(raw)==expected==sn['archive_sha256'],'whole independently frozen original-first archive')
 with tarfile.open(root/'core.tar.gz')as tf:
  expectedrows={r['path']:r for r in sn['members']};ck({m.name for m in tf if m.isfile()}==set(expectedrows),'all exact original snapshot members')
  for name,r in expectedrows.items():
   b=tf.extractfile(name).read();ck(sha(b)==r['sha256']and len(b)==r['bytes'],'whole original-first body '+name)
 archives.append({'role':role,'archive':str((root/'core.tar.gz').relative_to(S)),'bytes':len(raw),'sha256':sha(raw),'complete_members':len(sn['members'])})
# Captured baseline peer semantics are explicitly limited to47 exact input bodies.
root=D/'baselines/history/peer-frozen';sn=read(root/'receipts.json')
with tarfile.open(root/'reviewed-bodies.tar.gz')as tf:
 members={m.name:tf.extractfile(m).read()for m in tf if m.isfile()}
 ck(len(members)==len(sn['paths'])==47,'whole actual peer capture input scope')
 for r in sn['paths']:
  p=Path(r['path']);choices=[name for name in members if name==str(p.relative_to(D.resolve()))]
  ck(len(choices)==1,'unambiguous exact archived peer body role')
  b=members[choices[0]];ck(sha(b)==r['sha256']and len(b)==r['bytes'],'whole captured peer historical body')
  ck(sha(p.read_bytes())==r['sha256'],'frozen peer remains current exact original phase')
# Every other history body remains a sealed raw artifact; inspect compressed bodies
# and retain checksums without coercing raw invalid fixture/report/script formats.
items=[]
for role in ['turnout','baselines']:
 for p in sorted((D/role/'history').rglob('*')):
  if not p.is_file():continue
  b=p.read_bytes();r={'path':str(p.relative_to(S)),'bytes':len(b),'sha256':sha(b)}
  if p.suffix=='.gz':
   decoded=gzip.decompress(b);r.update({'complete_reconstructed_bytes':len(decoded),'complete_reconstructed_sha256':sha(decoded)})
  items.append(r)
peer=read(D/'baselines/peer-reconciliation.json');ck(peer['checks']==peer['passing']==162714 and peer['errors']==[],'expanded final complete raw comparator succeeded')
for role in ['turnout','baselines']:
 mf=read(D/role/'asset-manifest.json');paths={r['path']for r in mf['assets']}
 ck(all(r['path']in paths for r in items if r['path'].startswith('data/'+role+'/')),'every history included by current manifest')
out={'status':'pass_complete_original_first_and_captured_peer_history_reconstruction','checks':N,'original_first_archives':archives,'complete_reviewed_peer_bodies':47,'complete_current_history_files':items,'expanded_peer_checks':162714,'prior_partial_normalized_raw_projection':120916,'partial_scope_superseded_without_source_or_calculator_count_repair':True,'producer_writes_or_future_byte_equality_claim':False}
body=(json.dumps(out,indent=2)+'\n').encode();p=D/'coordinator-first-pair-history-review.json'
if '--check'in sys.argv:ck(p.read_bytes()==body,'exact old history proof replay')
else:p.write_bytes(body)
print(json.dumps({k:v for k,v in out.items()if k!='complete_current_history_files'}))
