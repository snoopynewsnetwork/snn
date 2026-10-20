"""Complete offline owned QA. Default is read-only; --write writes the owned QA result.
--manifest also verifies exact owned membership and every byte pin. No network or producer code.
"""
from common import *
from boundary_guard import admission,exact_remainder,allowed_public_url
from schema_samples import tree_schema,xlsx
import xml.etree.ElementTree as ET
from collections import Counter
from zoneinfo import ZoneInfo
import copy,sys

def owned_files():
 return sorted([STATE/'official-results.md',STATE/'data/official-results-sources.csv']+[p for p in HERE.rglob('*') if p.is_file() and p!=HERE/'asset-manifest.json'])
def verify_order(rows,keys,lookup):
 assert len(rows)==len(keys) and [x['key'] for x in rows]==keys and len(set(keys))==len(keys)
 for r,k in zip(rows,keys):assert sem(r['complete_historical_native_source_object'])==sem(lookup[k])
def fails(f):
 try:f()
 except (AssertionError,ValueError,KeyError):return True
 return False
def main(write_output=False,manifest=False):
 import replay_frozen
 frozen=replay_frozen.main(False)
 a=parsefile(ACCEPTANCE);p=parsefile(STATE/a['frozen_contract']['path']);lookup={x['key']:x for x in p['native_constituents']}
 priority=parsefile(HERE/'investigations-priority.jsonl.gz');remainder=parsefile(HERE/'investigations-remainder.jsonl.gz');rows=priority+remainder
 verify_order(priority,a['ordered_priority_keys'],lookup);verify_order(remainder,a['ordered_remainder_keys'],lookup);verify_order(rows,a['ordered_full_keys'],lookup)
 assert len(priority)==5540 and len(remainder)==4522 and len(rows)==10062
 for rank,r in enumerate(rows,1):
  assert r['historical_rank']==rank and r['historical_parent_key']==p['native_to_authority_parent_map'][r['key']]
  assert r['november_returns_admitted'] is False and r['current_geography_join'] is None and r['current_navigation_election_contest_choice_unit_mapping'] is None and r['unknown_remaining_ballots'] is None
  assert (STATE/r['parent_investigation_path']).is_file()
 pp=p['primary_priority'];vals=[lookup[k]['printed_known_recorded_sum'] for k in a['ordered_full_keys']]
 assert sum(vals)==5592368 and sum(vals[:15])==29572
 assert sum(vals[:5539])==4473789 and vals[5539]==523 and sum(vals[:5540])==4474312 and sum(vals[5540:])==1118056
 assert sum(vals[:5539])*5<sum(vals)*4<=sum(vals[:5540])*5
 assert rows[5539]['key']=='il:2024:authority:88:label:O%20FALLON%203'
 admins=[x for x in lookup.values() if x['administrative_only']];assert len(admins)==4
 for x in admins:assert x['printed_observed_sum'] is None and x['printed_known_recorded_sum']==0 and all(v is None for v in x['printed_candidate_votes'].values())
 kennedy=[x for x in lookup.values() if not x['administrative_only'] and x['printed_candidate_votes']['Robert F. Kennedy Jr.'] is None];assert len(kennedy)==15
 zeros=[x for x in lookup.values() if x['printed_candidate_votes']['Kamala D. Harris']==0 and x['printed_candidate_votes']['Donald J. Trump']==0];assert len(zeros)==745
 assert sum(len(x['source_contexts']) for x in lookup.values())==11535
 counts=[];baseline_seal=next(s for s in a['producer_seals'] if 'baselines/' in s['path']);original_refs=parsefile(STATE/baseline_seal['path'])[baseline_seal['original_reference_field']]
 for year,n in [(2024,59623),(2022,31797),(2020,54950)]:
  original=parsefile(STATE/f'data/baselines/extract/{year}-raw-rows.csv.gz');assert len(original)==n+1 and all(len(r)==15 for r in original)
  source_id=original[1][1];ref=next(v for v in original_refs if v.get('source_id')==source_id);rb=(STATE/'data/baselines'/ref['path']).read_bytes();rb=gzip.decompress(rb) if rb.startswith(b'\x1f\x8b') else rb;raw=list(csv.reader(io.StringIO(rb.decode('utf-8-sig'))));assert len(raw)==len(original) and original[0][3:]==raw[0]
  for i,r in enumerate(original[1:],2):assert r[:3]==[str(year),source_id,str(i)] and r[3:]==raw[i-1]
  assert len(raw[0])==12;counts.append(n)
 assert sum(counts)==146370
 hierarchy=parsefile(HERE/'historical-parent-hierarchy.json.gz');directory=parsefile(HERE/'current-authority-directory.json');idx=parsefile(HERE/'hierarchy-index.json')
 assert len(hierarchy)==len(directory)==108 and len(p['authority_inventory'])==108
 ids={str(i) for i in range(1,103)}|{'104','105','106','107','108','110'};assert {r['current_directory_selector_value'] for r in directory}==ids
 directory_body=HTML(body(parsefile(HERE/'receipts/state-directory-all.json')).decode()).summary();rawrows=[r for r in directory_body['rows'] if len(r['cells'])==7 and r['cells'][0]['text'] not in ['Jurisdiction','']]
 assert [r['complete_directory_row'] for r in directory]==rawrows
 bydir={r['current_directory_selector_value']:r for r in directory};flat=[];priorityparents=0;localparents=0
 for i,h in enumerate(hierarchy):
  old=p['authority_inventory'][i];aid=old['authority_id'];d=parsefile(HERE/'parents'/f'{aid}.json')
  assert d['complete_historical_parent_object']==h['complete_historical_parent_object']==old
  assert d['current_directory_research_association']==bydir[aid]
  assert d['current_leaf_matches'] is None and d['admitted_november_returns'] is False and d['exact_outstanding_eligible_ballots'] is None and d['measured_cadence'] is None
  keys=[k for k in a['ordered_full_keys'] if p['native_to_authority_parent_map'][k]==old['key']]
  assert keys==d['historical_child_keys_ordered']==h['full_ordered_children'];flat+=keys
  assert d['priority_child_keys_ordered']==[k for k in a['ordered_priority_keys'] if k in set(keys)]
  assert d['remainder_child_keys_ordered']==[k for k in a['ordered_remainder_keys'] if k in set(keys)]
  priorityparents+=bool(d['priority_child_keys_ordered']);localparents+=bool(d['local_requests'])
  dr=parsefile(STATE/d['directory_detail_receipt']['receipt_path']);assert dr['complete'] and dr['status']==200
 assert priorityparents==97 and localparents==103 and len(flat)==len(set(flat))==10062 and set(flat)==set(a['ordered_full_keys'])
 assert idx['ordered_full_keys']==a['ordered_full_keys'] and idx['ordered_priority_keys']==a['ordered_priority_keys'] and idx['ordered_remainder_keys']==a['ordered_remainder_keys']
 csvrows=list(csv.DictReader(io.StringIO((STATE/'data/official-results-sources.csv').read_text())));assert len(csvrows)==108
 for r in csvrows:assert json.loads(r['directory_fields_json'])==bydir[r['current_selector_value']]['complete_directory_row']
 receipts={};receipt_files=list(sorted((HERE/'receipts').glob('*.json')));complete=0;redirects=0;aliases=[]
 for q in receipt_files:
  m=parsefile(q);receipts[m['id']]=m
  if q.stem!=m['id']:aliases.append(dict(path=str(q.relative_to(STATE)),original_receipt_id=m['id'],complete=m['complete'],error=m.get('error')))
  for k in ['id','url','parent','literal_href','method','request_body','retrieved_at_utc','finished_at_utc','complete']:assert k in m,(q,k)
  assert m['method'] in ['GET','POST']
  if m['complete']:
   z=(STATE/m['path']).read_bytes();b=gzip.decompress(z);assert len(z)==m['stored_bytes'] and sha(z)==m['stored_sha256'] and len(b)==m['raw_bytes'] and sha(b)==m['raw_sha256'];complete+=1
   assert ('headers' in m and 'redirects' in m) or 'raw_headers_latin1' in m
   if 'curl_info' in m:assert m['curl_info'].get('num_redirects',0)==0 # every curl observation actually had no redirects
   for v in m.get('redirects',[]):assert all(k in v for k in ['url','status','headers','body_hex']);redirects+=1
  else:assert m.get('error')
  parsed=parsefile(HERE/'parsed'/f"{m['id']}.json.gz")
  if m['complete'] and not body(m).startswith((b'%PDF',b'PK',b'\x89PNG',b'\xff\xd8')):assert parsed==HTML(body(m).decode('utf8',errors='replace')).summary()
 assert len(aliases)==4 and all(not x['complete'] and 'sandbox-dns' in x['path'] and x['error'] for x in aliases)
 schemas=parsefile(HERE/'source-schema-inventory.json');assert len(schemas)==77
 for s in schemas:
  m=receipts[s['receipt_id']];b=body(m);obj=parsefile(STATE/s['sample_path']);sid=s['receipt_id']
  if s['format']=='complete JSON':expected=json.loads(b)
  elif sid in ['state-candidate-file-tsv','hancock-primary-csv','macoupin-primary-csv']:
   rr=list(csv.reader(io.StringIO(b.decode('utf-8-sig')),delimiter='\t' if sid.endswith('tsv') else ','));expected=dict(complete_header_in_order=rr[0],complete_rows=rr[1:],row_width_distribution={str(k):v for k,v in Counter(map(len,rr)).items()},source_delimiter='TAB' if sid.endswith('tsv') else ',')
  elif sid=='state-candidate-file-xml':
   root=ET.fromstring(b);expected=dict(root_tag=root.tag,root_attributes=root.attrib,complete_rows=[dict(tag=r.tag,attributes_in_source_order=[list(v) for v in r.attrib.items()],text=r.text,children=[ET.tostring(c,encoding='unicode') for c in r]) for r in root])
  elif sid=='logan-elected-register-xlsx':expected=xlsx(b)
  else:expected=HTML(b.decode()).summary()
  expected=json.loads(json.dumps(expected,ensure_ascii=False,allow_nan=False))
  assert sem(obj)==sem(expected),(sid,'full sample');assert sem(s['schema'])==sem(tree_schema(expected)),sid
 # Negative controls catch complete-object loss, reordered/duplicate membership and null-to-zero tampering.
 tests=[]
 for label,mutate in [('duplicate key',lambda v:v.__setitem__(1,copy.deepcopy(v[0]))),('wrong order',lambda v:v.reverse()),('null to zero',None)]:
  v=copy.deepcopy(rows)
  if mutate:mutate(v)
  else:
   j=next(i for i,r in enumerate(v) if r['complete_historical_native_source_object']['administrative_only']);v[j]['complete_historical_native_source_object']['printed_observed_sum']=0
  assert fails(lambda:verify_order(v,a['ordered_full_keys'],lookup));tests.append(label)
 fixtures=parsefile(HERE/'negative-fixtures.json');base=dict(election_date='2026-11-03',contest='U.S. Senate',stage='synthetic QA only',votes=1)
 for k in ['navigation_verified','contest_keys_verified','choice_keys_verified','unit_keys_verified','all_source_fields_preserved','eligible_scope_verified','genuine_november_returns','coordinator_approval']:base[k]=True
 assert admission(base)['admitted'] # synthetic control only; no actual source approval is written
 for f in fixtures['admission_mutations']:
  v={**base,**f['set']};assert not admission(v)['admitted'];tests.append(f['label'])
 for n in [float('nan'),float('inf'),float('-inf')]:assert not admission({**base,'votes':n})['admitted'];tests.append('nonfinite '+str(n))
 for u in fixtures['blocked_urls']:assert not allowed_public_url(u);tests.append('deny '+u)
 assert allowed_public_url('https://www.elections.il.gov/ElectionOperations/ElectionResults.aspx')
 for v in fixtures['remainder_rejections']:assert exact_remainder(v) is None;tests.append('reject unproven remainder '+str(v))
 assert exact_remainder(dict(count=0,eligible=True,unprocessed=True,explicit_official_status=True))==0
 excluded=parsefile(HERE/'discovery-scope-findings.json')['excluded'];assert len(excluded)==24 and {v['receipt_id'] for v in excluded}=={m['id'] for m in receipts.values() if not allowed_public_url(m['url'])}
 # Real observed counterexamples remain closed even though their HTTP bodies are complete.
 observed=[]
 for sid,stage in [('state-results-search','primary'),('authority-19-platinum-1','setup')]:
  assert sid in receipts
  m=receipts[sid];v={**base,'stage':stage,'genuine_november_returns':False};assert not admission(v)['admitted'];observed.append(dict(receipt=sid,stage=stage,status=m['status'],admitted=False))
 assert datetime.datetime(2026,11,3,19,tzinfo=ZoneInfo('America/Chicago')).astimezone(datetime.timezone.utc).isoformat()=='2026-11-04T01:00:00+00:00'
 statutes=parsefile(HERE/'operative-statutes-complete.json');assert len(statutes)==32
 for s in statutes:
  m=receipts[s['receipt_id']];assert m['status']==200 and m['complete'];assert s['complete_text']==' '.join(HTML(body(m).decode('utf8' if s['encoding']=='UTF-8' else 'cp1252')).text)
 files=owned_files();assert all(q.stat().st_size<40000000 for q in files);assert not list(HERE.rglob('__pycache__'))
 assert all(not any(k in q.parts for k in ['node_modules','.cache','.venv']) for q in files)
 # External authority is path-only: neither literal acceptance digest nor complete body can occur in any owned byte stream.
 authority=ACCEPTANCE.read_bytes();authority_digest=sha(authority).encode()
 for q in files:
  b=q.read_bytes();assert authority_digest not in b and b!=authority,q
 if manifest:
  seal=parsefile(HERE/'asset-manifest.json');assert set(v['path'] for v in seal['owned_assets'])=={str(q.relative_to(STATE)) for q in files}
  for v in seal['owned_assets']:
   b=(STATE/v['path']).read_bytes();assert len(b)==v['bytes'] and sha(b)==v['sha256']
  assert seal['excluded_owned_paths']==['data/results-sources/asset-manifest.json']
 result=dict(status='pass',scope='bounded owned source research QA; no current geography, legal native80 robustness, live return, cadence, remainder or probability approval',complete_recursive_source_objects=frozen['complete_recursive_source_objects'],frozen_checks=frozen['checks'],complete_root_fields=31,complete_companions=116,original_asset_pins=1209,full_historical_children=10062,priority_children=5540,remainder_children=4522,full_historical_parents=108,priority_parents=97,current_directory_rows=108,parents_with_local_requests=localparents,original_12_field_records=146370,presentation_contexts_2024=11535,complete_structured_samples=77,receipts=len(receipt_files),unique_receipt_ids=len(receipts),retained_initial_sandbox_failure_aliases=aliases,complete_entities=complete,redirect_observations=redirects,operative_code_sections=32,negative_cases=len(tests),negative_case_labels=tests,real_source_rejection_controls=observed,all_owned_objects_strictly_below_40000000_bytes=True,external_authority_path_only=True,producer_code_executed=False,november_returns_admitted=0)
 if write_output:write(HERE/'validation.json',result)
 print(json.dumps({k:v for k,v in result.items() if not isinstance(v,(list,dict))}));return result
if __name__=='__main__':main('--write' in sys.argv,'--manifest' in sys.argv)
