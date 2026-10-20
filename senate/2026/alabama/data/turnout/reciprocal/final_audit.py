#!/usr/bin/env python3
"""Final read-only exact membership, all history/source/context/type/link and captured reciprocal audit."""
import pathlib,json,gzip,hashlib,urllib.parse,re,subprocess,sys,tarfile,collections
R=pathlib.Path(__file__).resolve().parents[1];S=R.parents[1];REPO=S.parents[2]
def sha(b):return hashlib.sha256(b).hexdigest()
def strict(b):return json.loads(b,parse_constant=lambda v:(_ for _ in ()).throw(ValueError(v)))
# These modes recompute proof content and never write validation/peer/capture output.
for script,args in [(R/'scripts/validate.py',['--audit']),(R/'reciprocal/audit_captures.py',['--audit']),(R/'reciprocal/compare_captured.py',['--audit'])]:
 if '--preseal' in sys.argv and script==R/'scripts/validate.py':continue
 a=subprocess.run([sys.executable,str(script)]+args,capture_output=True,env={**__import__('os').environ,'PYTHONDONTWRITEBYTECODE':'1'});assert a.returncode==0,(str(script),a.stdout.decode(),a.stderr.decode())
manifest=strict((R/'asset-manifest.json').read_bytes());before={p:sha(p.read_bytes()) for p in [S/'turnout.md',S/'data/county-turnout.csv']+[p for p in R.rglob('*') if p.is_file()]};jsons=gzips=history=urls=links=0
for p in before:
 b=p.read_bytes();assert len(b)<40000000,p;assert not p.is_symlink(),p
 if p.suffix=='.json':strict(b);jsons+=1
 if p.suffix=='.gz':gzip.decompress(b);gzips+=1
for p in (R/'history').glob('*.json'):
 h=strict(p.read_bytes());raw=gzip.decompress((p.parent/h['stored_body']).read_bytes());assert len(raw)==h['original_bytes'] and sha(raw)==h['sha256'];history+=1
for p in [S/'turnout.md',R/'source/SCHEMA.md']:
 for url in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if url.startswith('#'):continue
  parsed=urllib.parse.urlsplit(url)
  if parsed.scheme:
   assert parsed.scheme in ['https','http'] and parsed.hostname and not any(c.isspace() for c in url),(p,url);urls+=1
  else:
   target=(p.parent/urllib.parse.unquote(parsed.path)).resolve();assert target.exists() and (target==S or S in target.parents),(p,url);links+=1
for p in (R/'source/http').glob('*.receipt.json'):
 r=strict(p.read_bytes());assert set(['requested_url','final_url','retrieved_at_utc','status','headers','redirects','original_sha256','original_bytes','parts']).issubset(r);assert type(r['status']) is int;parts=[]
 for part in r['parts']:
  q=(R/part['path']).resolve();assert R in q.parents;b=q.read_bytes();assert len(b)==part['bytes'] and sha(b)==part['sha256'];parts.append(b)
 body=gzip.decompress(b''.join(parts));assert len(body)==r['original_bytes'] and sha(body)==r['original_sha256']
 for field in ['requested_url','final_url']:
  parsed=urllib.parse.urlsplit(r[field]);assert parsed.scheme=='https' and parsed.hostname and not any(x.isspace() for x in r[field]);urls+=1
contract=strict((R/'priority-set.json').read_bytes());allkeys=[];field_positions=0
for year in [2024,2022,2020]:
 units=strict((R/f'native-units-{year}.json').read_bytes());keys=[u['key'] for u in units];assert len(keys)==len(set(keys));allkeys+=keys
 for u in units:
  cf=u['county_fips'];assert len(cf)==5 and cf.isdigit() and cf.startswith('01');assert type(u['column_1based']) is int;expected=f"AL:{year}:general:{cf}:col{u['column_1based']:03}:"+urllib.parse.quote(u['native_label'],safe='');assert u['key']==expected
  for c in u['candidate_votes']+u['administrative_fields']+u['contest_other_fields']:
   assert type(c['row_1based']) is int and type(c['column_1based']) is int and type(c['xls_type']) is int;assert c['column_1based']==u['column_1based'];assert c['value'] is None or type(c['value']) is int;assert all(type(c[x]) is str for x in ['contest_literal','party_literal','candidate_literal']);field_positions+=1
  for out,rows,name in [('ballots_cast_source','administrative_fields','Ballots Cast - Total'),('blank_ballots_source','administrative_fields','Ballots Cast - Blank'),('registration_source','administrative_fields','Registered Voters - Total'),('under_votes_source','contest_other_fields','Under Votes'),('over_votes_source','contest_other_fields','Over Votes')]:assert u[out]==next((c['value'] for c in u[rows] if c['candidate_literal'].strip()==name),None)
  assert u['current_2026_crosswalk'] is None and u['named_valid_writein_allocation'] is None
assert len(allkeys)==6270 and len(set(allkeys))==6270
for r in strict((R/'source/visual-transcriptions.json').read_bytes()).values():
 if isinstance(r,list):
  for c in r:
   assert (R/c['image']).is_file();a,b,x,y=c['region'];assert 0<=a<x<=1 and 0<=b<y<=1
for field in ['archive_receipt','canvass_receipt','original_first_witness']:assert (R/contract['source_chain'][field]).is_file()
assert (R/contract['peer_agreement_scope']['proof_path']).is_file();assert contract['peer_agreement_scope']['proof_sha256']==sha((R/contract['peer_agreement_scope']['proof_path']).read_bytes());assert not contract['coordinator_acceptance'] and not contract['legal_geographic_approval_2026'] and not contract['current_2026_crosswalk_complete']
# Every canonical old target except explicit status/audit/seal paths is still the original body.
with tarfile.open(R/'reciprocal/turnout-original-phase.tar.gz') as tf:
 om=strict(tf.extractfile('data/turnout/asset-manifest.json').read());allowed={'turnout.md','data/turnout/source/SCHEMA.md','data/turnout/priority-set.json','data/turnout/validation.json','data/turnout/final-seal.json','data/turnout/scripts/validate.py'}
 for asset in om['assets']:
  original=tf.extractfile(asset['path']).read();assert sha(original)==asset['sha256']
  if asset['path'] not in allowed:assert sha((S/asset['path']).read_bytes())==asset['sha256'],asset['path']
 oldcontract=strict(tf.extractfile('data/turnout/priority-set.json').read())
 for key in oldcontract:
  if key not in ['peer_agent_id','independent_peer_agreement','dispatch_status']:assert contract[key]==oldcontract[key],key
assert not [p for p in R.rglob('*') if p.name in ['__pycache__','node_modules','.cache','.venv'] or p.suffix=='.pyc']
after={p:sha(p.read_bytes()) for p in before};assert before==after
print(json.dumps({'status':'PASS','mode':'PRESEAL_READONLY_STATIC_SOURCE_CHECK' if '--preseal' in sys.argv else 'READ_ONLY_NO_OWNED_WRITES','owned_files_including_manifest':len(before),'manifest_targets':len(manifest['assets']),'current_manifest_sha256':sha((R/'asset-manifest.json').read_bytes()),'total_owned_manifest_target_bytes':sum(a['bytes'] for a in manifest['assets']),'largest_stored_owned_bytes':max(p.stat().st_size for p in before),'all_history_bodies_verified':history,'strict_json_files':jsons,'lossless_gzip_files':gzips,'relative_markdown_targets':links,'absolute_primary_URL_positions':urls,'native_units':6270,'typed_native_candidate_admin_positions':field_positions,'all_original145_self146_and_peer306_self307_reconstructions':'PASS','all_canonical_source_CSV_masks_counts_order_and_remaining_contract_semantics':'UNCHANGED','bounded_captured_peer_agreement':True,'coordinator_current_legal_geometry_feed_pool_collector_probability_admission':False},indent=2))
