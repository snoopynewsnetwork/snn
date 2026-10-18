from common import *
import argparse,collections,csv,io,re,urllib.parse
ap=argparse.ArgumentParser();ap.add_argument('--manifest-only',action='store_true');args=ap.parse_args()
if args.manifest_only:
 m=js(ROOT/'asset-manifest.json')
 for r in m['owned']:
  p=GA/r['path'];b=p.read_bytes();assert len(b)==r['bytes'] and sha(b)==r['sha256'],r['path']
 md=(GA/'official-results.md').read_text()
 for u in re.findall(r'\[[^\]]+\]\(([^\s)]+)\)',md):
  if not re.match(r'[a-zA-Z]+:',u) and not u.startswith('#'):assert (GA/urllib.parse.unquote(u.split('#')[0])).is_file(),u
 print('Final owned artifact manifest and links verified',len(m['owned']));raise SystemExit
checks={};shared=js(ROOT/'shared-inputs.json');originals={}
for r in shared:
 p=GA/r['path'];b=p.read_bytes();assert len(b)==r['stored_bytes'] and sha(b)==r['stored_sha256'],r['path'];assert len(b)<40000000
 raw=gzip.decompress(b) if b.startswith(b'\x1f\x8b') else b;assert sha(raw)==r['raw_sha256'],r['path']
 size=r.get('raw_bytes',r.get('entity_bytes',r.get('decoded_bytes')))
 if size is not None:assert len(raw)==size,(r['path'],len(raw),size)
 if r['path'].endswith('.body.gz') or 'api-data-selected' in r['path']:
  try:originals[r['path']]=json.loads(raw)
  except (ValueError,UnicodeDecodeError):pass
checks['shared_originals_hash_verified']=len(shared)
for r in js(ROOT/'frozen-inputs.json')+js(ROOT/'shared-derived-inputs.json'):
 b=(GA/r['path']).read_bytes();assert len(b)==r['bytes'] and sha(b)==r['sha256'],r['path']
checks['immutable_final_firstwave_and_acceptance_pins']='pass'
receipts=[js(p) for p in sorted((ROOT/'raw').glob('*.http.json'))];byid={r['id']:r for r in receipts};assert len(byid)==len(receipts)
for r in receipts:
 assert r['url'] and r['retrieved_at_utc'] and r['completed_at_utc'] and 'redirects' in r
 if r.get('status') is not None:
  raw=entity(r);p=GA/r['shared_path'] if 'shared_path' in r else ROOT/r['path'];b=p.read_bytes();assert sha(raw)==r['raw_sha256'] and len(raw)==r['raw_bytes'];assert sha(b)==r['stored_sha256'] and len(b)==r['stored_bytes'];assert len(b)<40000000
checks['owned_request_receipts_hash_verified']=len(receipts)
req=js(ROOT/'requests.json');assert {r['id'] for r in req}==set(byid)
con=js(GA/'data/turnout/priority-set.json');accept=js(GA/'data/coordinator-priority-acceptance.json');assert accept['accepted'] and accept['contract_sha256']==sha((GA/'data/turnout/priority-set.json').read_bytes()) and accept['contract_bytes']==2293339
assert con['ordered_priority_keys']==accept['ordered_dispatch_keys'] and con['full_candidate_priority_order'] is None and con['full_candidate_priority_keys'] is None
assert len(con['coverage'])==159 and len(con['ordered_priority_keys'])==44
csvrows=list(csv.DictReader((GA/'data/official-results-sources.csv').open()));counties=csvrows[1:];assert len(csvrows)==160 and csvrows[0]['record_type']=='state'
assert len({r['county_fips'] for r in counties})==159 and [r['county_key'] for r in counties[:44]]==accept['ordered_dispatch_keys'];assert [r['county_name'] for r in counties[:44]]==accept['priority_names_in_dispatch_order']
assert sum(r['priority44']=='True' for r in counties)==44
assert sum(int(r['native_count_2024']) for r in counties)==2701 and sum(int(r['native_count_2024']) for r in counties[:44])==1938
assert all(r['current_general_election_id']==r['current_senate_contest_id']==r['current_candidate_ids']=='' for r in counties)
checks['county_priority_native_inventory']={'counties':159,'priority':44,'remainder':115,'native':2701,'priority_native':1938,'order':'named-four dispatch only'}
controls=[json.loads(s) for s in gzip.decompress((ROOT/'extracts/county-controls.jsonl.gz').read_bytes()).decode().splitlines()];pos=[json.loads(s) for s in gzip.decompress((ROOT/'extracts/source-positions.jsonl.gz').read_bytes()).decode().splitlines()];native=[json.loads(s) for s in gzip.decompress((ROOT/'extracts/native-identities.jsonl.gz').read_bytes()).decode().splitlines()]
assert len(controls)==795 and len(pos)==76400 and len(native)==2701
assert len({(c['election_key'],c['county_fips']) for c in controls})==795
assert {c['election_key'] for c in controls}=={'2024NovGen','2020NovGen','2021JanFedRun','2022NovGen','2022DecGenRun'}
# Resolve every derivative source pointer into exact original JSON, never only compare implementation totals.
def source(path):
 if path not in originals:originals[path]=json.loads(gzip.decompress((GA/path).read_bytes()))
 return originals[path]
def pointer(v,p):
 for s in p.strip('/').split('/'):
  s=s.replace('~1','/').replace('~0','~');v=v[int(s)] if isinstance(v,list) else v[s]
 return v
keys=set()
for r in pos:
 key=(r['source_path'],r['source_pointer']);assert key not in keys;keys.add(key)
 node=pointer(source(r['source_path']),r['source_pointer']);assert node['voteCount']==r['votes'] and type(node['voteCount']).__name__==r['raw_vote_type']
 if r['kind']=='TOTAL':assert node['id']==r['candidate_id'] and node.get('nativeId')==r['nativeId'] and node['name']==r['name'] and node.get('party')==r['party']
 else:assert node['groupId']==r['group_id'] and node['groupName']==r['group_name']
checks['original_json_pointers_and_types_verified']=len(pos)
assert {(r['county_fips'],r['native_id']) for r in native}=={(c['county_fips'],u['native_id']) for c in con['coverage'] for u in c['constituents']}
for n in native:
 d=source(n['source_path']);assert d['precincts'][n['inventory_ordinal']]==n['inventory_object'];assert d['ballotItemWithBreakdown']['breakdownResults'][n['breakdown_ordinal']]['precinct']==n['breakdown_precinct_object']
for c in controls:
 d=source(c['source_path']);assert c['election']==d['election'];assert c['response_ballot_id']==d['ballotItemWithBreakdown']['id'];assert c['jurisdiction_id']==d['jurisdiction']['id']
 if c['election_key']!='2024NovGen':assert c['native_count']==0 and c['ballots_cast'] is None and c['registered_voters'] is None
 else:
  assert sum(x['voteTotal'] for x in d['ballotItemWithBreakdown']['breakdownResults'])==c['county_options_sum']
  assert {x['id'] for x in d['voterTurnout']}=={x['id'] for x in d['precincts']}
  assert sum(x['ballotsCast'] for x in d['voterTurnout'])==c['ballots_cast']
  assert sum(x['voterTurnout'] for x in d['voterTurnout'])==c['ballots_cast']
  assert sum(x['voterRegistration'] for x in d['voterTurnout'])==c['registered_voters']
assert sum(c['ballots_cast'] for c in controls if c['election_key']=='2024NovGen')==5297264
assert sum(c['registered_voters'] for c in controls if c['election_key']=='2024NovGen')==7219868
np=[r for r in pos if r['level']=='precinct'];assert sum(r['votes'] is None for r in np if r['kind']=='TOTAL')==40;assert sum(r['votes'] is None for r in np if r['kind']=='METHOD')==22416
assert len({r['county_fips'] for r in np if r['kind']=='METHOD' and r['votes'] is None})==130
hc=js(ROOT/'extracts/history-checks.json');expected={'2024NovGen':5250047,'2020NovGen':4952175,'2021JanFedRun':4484902,'2022NovGen':3935924,'2022DecGenRun':3541877}
assert {e:v['named_state_votes'] for e,v in hc['elections'].items()}==expected
assert hc['native_candidate_residual']==18 and hc['native_method_residual']==2942770
assert hc['elections']['2024NovGen']['county_all_options']==5250066
assert hc['elections']['2024NovGen']['extra_options']=={'Claudia De la Cruz (Ind)':13,'Cornel West (Ind)':6}
checks['five_stage_counts_nulls_and_usable_controls']='pass'
# Recompute the exact named-four ordering from originals, independent of accepted county weights.
state=source(js(ROOT/'extracts/state-controls.json')['2024NovGen']['source_path']);b=state['ballotItemWithBreakdown'];fips={r['county_name']:r['county_fips'] for r in counties};rank=[]
for x in b['breakdownResults']:
 name=next(n['text'] for n in x['locality']['name'] if n['languageId']=='en');rank.append((sum(o['voteCount'] for o in x['ballotOptions']),fips[name]))
rank.sort(key=lambda x:(-x[0],x[1]));assert [f for v,f in rank]==[r['county_fips'] for r in counties]
assert sum(v for v,f in rank)==5250047 and sum(v for v,f in rank[:15])==2939795 and sum(v for v,f in rank[:43])==4199292 and sum(v for v,f in rank[:44])==4222572
full=5250047+858;threshold=(4*full+4)//5;assert full==5250905 and threshold==4200724 and 4199292+858==4200150<threshold and 4222572>=threshold
assert 23258<23280 and 22353+858==23211<23280
checks['named_order_full_universe_priority_bounds']='pass; membership/cardinality only, no full-candidate ordering or allocation'
for r in counties:
 d=json.loads(entity(byid['current-tenant-'+r['county_fips']]));assert d['id'] is None and d['redirectToShortName']=='Georgia' and d['elections']==[]
state_now=json.loads(entity(byid['fresh-jurisdiction']));assert len(state_now['elections'])==117 and not any(x['electionDate']=='2026-11-03' for x in state_now['elections'])
checks['real_current_root_negative_controls']={'county_200_redirect_metadata':159,'state_listed_elections':117,'november_count_admissions':0}
# These are real original negative controls, not fabricated vote sequences.
text=lambda id:gzip.decompress((ROOT/'extracts'/(id+'.pdf.txt.gz')).read_bytes()).decode()
la=text('cobb-november-la');assert 'L&A 11/3/2026' in la and 'Mike Collins (Rep)' in la and '918' in la
walton=text('local-13297-1-child-0');assert '0 of 19 (0.00%)' in walton and '58,734' in walton and 'Official and Complete' in walton
writeins=text('follow-local-13297-2-38');assert 'FINAL LIST OF CERTIFIED WRITE-IN CANDIDATES' in writeins
for n in ['Elbert Arthur Bartell','Christina Clement','Cassandra Easton']:assert n in writeins
checks['test_completion_and_current_ballot_evidence']='L&A rejected despite918nonzero; Walton0/19 not zero votes; FINAL Senate3names verified'
exp=js(ROOT/'extracts/export-controls.json');assert len(exp)==6 and all(x['summary_matches_app'] for x in exp)
e24=next(x for x in exp if x['source_id']=='observed-export-2024NovGen-0-0');assert e24['county_count']==159 and len(e24['sheets'][2]['selected_rows'])==954
assert set(e24['sheets'][2]['labels'])=={'Ballots Cast','Total Votes','Donald J. Trump (Rep)','Kamala D. Harris (Dem)','Chase Oliver (Lib)','Jill Stein (Grn)'}
alt=js(ROOT/'extracts/fulton-alternative-native-nulls.json');assert len(alt['null_cells'])==40 and alt['known_cell_count']==1824 and alt['known_cell_differences']==[] and alt['alternative_sum']==18 and alt['no_frozen_vector_mutation']
assert alt['alternative_candidate_sums']=={'Donald J. Trump (Rep)':7,'Kamala D. Harris (Dem)':11,'Chase Oliver (Lib)':0,'Jill Stein (Grn)':0}
checks['exports_unallocated858_and_distinct_fulton_numeric_alternative']='pass'
assert js(ROOT/'extracts/independent-peer-check.json')['source_positions']==76400
assert len(js(ROOT/'extracts/independent-peer-check.json')['candidate_nativeId_or_party_differences'])==18
assert len(js(ROOT/'gaps.json')['county_vintage_records'])==954
# Author source scripts must parse without writing bytecode/dependency caches.
import ast
for p in (ROOT/'scripts').glob('*.py'):ast.parse(p.read_text(),filename=str(p))
# Relative report links, with exact local existence. External sources retain URL provenance in request/receipt manifests.
md=(GA/'official-results.md').read_text();links=re.findall(r'\[[^\]]+\]\(([^\s)]+)\)',md);local=[]
for u in links:
 if re.match(r'[a-zA-Z]+:',u) or u.startswith('#'):continue
 target=urllib.parse.unquote(u.split('#')[0]);assert (GA/target).is_file() or target in ['data/results-sources/validation.json','data/results-sources/asset-manifest.json'],u;local.append(u)
checks['report_relative_links_verified']=len(local)
files=[p for p in ROOT.rglob('*') if p.is_file() and p.name not in ['validation.json','asset-manifest.json']]+[GA/'official-results.md',GA/'data/official-results-sources.csv'];assert all(p.stat().st_size<40000000 for p in files)
assert not any(p.name=='__pycache__' or p.name=='node_modules' for p in ROOT.rglob('*'))
checks['owned_final_file_count_including_validation_and_manifest']=len(files)+2;checks['largest_stored_owned_bytes']=max(p.stat().st_size for p in files)
checks['status']='pass';checks['scope']='offline research evidence; no live/current/geographic/probability approval';save(ROOT/'validation.json',checks);print(json.dumps(checks,indent=2))
