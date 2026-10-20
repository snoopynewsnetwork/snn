"""Independent coordinator source/hierarchy/current-schema audit; no producer imports."""
from pathlib import Path
import collections,csv,gzip,hashlib,html,io,json,re
S=Path(__file__).resolve().parents[1];R=S/'data/results-sources';N=0;CACHE={};PARSED={}
def ck(v):
 global N
 N+=1
 assert v,N
def sha(b):return hashlib.sha256(b).hexdigest()
def load(path):
 p=S/path
 if str(p) not in PARSED:
  b=p.read_bytes();PARSED[str(p)]=json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
 return PARSED[str(p)]
def exact(r):
 k=(r['path'],r['sha256'])
 if k not in CACHE:
  b=(S/r['path']).read_bytes();ck(len(b)==r['bytes'] and sha(b)==r['sha256']);CACHE[k]=b
 return CACHE[k]
def sem(v):return sha(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def resolve(r):
 exact(r);x=load(r['path'])
 for k in r.get('pointer','').split('/')[1:]:
  k=k.replace('~1','/').replace('~0','~');x=x[int(k)] if isinstance(x,list) else x[k]
 ck(sem(x)==r['full_object_semantic_sha256'] and r['complete_object'] is True);return x
def entity(r):
 b=(S/r['stored_path']).read_bytes();ck(len(b)==r['stored_bytes'] and sha(b)==r['stored_sha256']);b=gzip.decompress(b);ck(len(b)==r['raw_bytes'] and sha(b)==r['raw_sha256']);return b
def lang(x):return ' | '.join(v.get('text') or '' for v in x or [])

m=load('data/results-sources/asset-manifest.json');ck(m['excludes_only_itself'] is True)
actual={str(p.relative_to(S)) for p in R.rglob('*') if p.is_file()}|{'official-results.md','data/official-results-sources.csv'}
listed=m['owned_assets'];ck(len(listed)==len({p['path'] for p in listed})==1236);ck(set(p['path'] for p in listed)==actual-{'data/results-sources/asset-manifest.json'})
for p in listed:exact(p);ck(p['bytes']<40000000)
for p in R.rglob('*'):ck(not {'__pycache__','node_modules','.venv','.pytest_cache'}.intersection(p.parts))
inputs=load('data/results-sources/inputs.json');receipts={};bodies={};status=collections.Counter();redirects=0
for pin in inputs['receipts']:
 r=json.loads(exact(pin));ck(r['id'] not in receipts);receipts[r['id']]=r;ck(r['method']=='GET' and r['submitted_body'] is None and r['retrieved_at_utc'].endswith('+00:00'))
 ck(bool(r['url']) and bool(r['configured_request_headers']) and isinstance(r['redirects'],list));redirects+=len(r['redirects'])
 for hop in r['redirects']:ck(bool(hop['url']) and isinstance(hop['headers'],list) and isinstance(hop['status'],int))
 if r.get('stored_path'):
  ck(r['body_complete'] is True and bool(r['response_headers']));bodies[r['id']]=entity(r);status[r['status']]+=1
 else:ck(r['body_complete'] is False and bool(r['error']));status['nonHTTP']+=1
ck(len(receipts)==336 and status[200]==325 and status[403]==8 and status['nonHTTP']==3)
ext=load('data/results-sources/external-inputs.json');ck(ext['authority_path']=='data/coordinator-priority-acceptance.json')
for r in ext['complete_files']:ck(r['path']!=ext['authority_path']);exact(r)
for r in inputs['reader_representations']:exact(r)

contract=load('data/turnout/priority-set.json');rank=contract['complete_descending_order'];natives=contract['all_source_native_constituents'];parents=contract['municipal_and_administrative_parent_sensitivity']['full_inventory']
rows=load('data/results-sources/derived/all-Senate-hierarchy.json');inv=load('data/results-sources/derived/full-inventory.json');pr=load('data/results-sources/derived/parent-investigations.json')
ck(len(rows)==len(rank)==458 and len(inv)==len(natives)==497 and len(pr)==len(parents)==43)
ck(rows[:242]==load('data/results-sources/derived/priority-investigations.json') and rows[242:]==load('data/results-sources/derived/remainder-investigations.json'))
bykey={p['key']:p for p in pr};ck(len(bykey)==43 and sum(p['directory'] is not None for p in pr)==39 and sum(p['priority_parent'] for p in pr)==37)
for a,b in zip(rows,rank):
 ck(resolve(a['whole_rank'])==b);n=resolve(a['whole_native']);p=resolve(a['whole_parent'])
 ck(n['key']==b['native_key'] and n['key'] in p['native_keys'] and a['dispatch_key']==b['key'] and a['original_anchor']==b['source_anchor'])
 ck(a['current_leaf_mapping'] is None and a['admitted_November'] is False and a['independent_feed_count']==0)
 ck(a['all_historical_candidate_record_keys']==n['contests']['Senator in Congress']['candidate_rows'])
for r,n in zip(inv,natives):ck(resolve(r['whole_native'])==n and r['current_leaf_mapping'] is None and r['Senate_total']==n['contests']['Senator in Congress']['total'])
ck(sum(r['Senate_total'] is None for r in inv)==39 and sum(r['Senate_total']==0 for r in inv)==15)
for p,h in zip(pr,parents):
 ck(resolve(p['historical_whole_parent'])==h);ck(p['current_November_source'] is None and p['current_geometry'] is None and p['exact_outstanding'] is None and p['measured_cadence'] is None)
 expected=[r for r in rank if r['parent_key']==p['key'] or (p['key'].startswith('RI:state-admin:') and r['native_code']==p['key'].split(':')[-1])]
 ck(p['ordered_priority_children']==[r['key'] for r in expected if r['rank']<=242] and p['ordered_remainder_children']==[r['key'] for r in expected if r['rank']>242])
ck(sum(p['historical_Senate_votes'] for p in pr)==491948 and sum(p['historical_Senate_votes'] for p in pr if p['directory'] is None)==1473)
csvrows=list(csv.DictReader(io.StringIO((S/'data/official-results-sources.csv').read_text())));ck(len(csvrows)==45 and len({r['authority_key'] for r in csvrows})==45)
ck({r['authority_key'] for r in csvrows}==set(bykey)|{'RI:state','RI:secretary'})

# Direct original HTML cell slices, every raw directory row and source character position.
directory=load('data/results-sources/derived/municipality-directory.json');text=bodies['board-directory-network'].decode('utf-8');names=[]
for table in directory['tables']:
 for row in table['rows']:
  ck(text[row['character_start']:row['character_end']]==row['raw_html'])
  for cell in row['cells']:ck(text[cell['character_start']:cell['character_end']]==cell['raw_html'])
  if len(table['rows'])==40 and row is not table['rows'][0]:names.append(re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]*>',' ',row['cells'][0]['raw_html']))).strip().replace(' (Block Island)',''))
ck(set(names)=={p['name'] for p in pr if p['directory'] is not None} and len(names)==39)

# Primary API and shared export are whole observed source schemas, never November data.
j=json.loads(bodies['results-jurisdiction']);ck(len(j['elections'])==10 and all(e['electionDate']!='2026-11-03' for e in j['elections']))
state=json.loads(bodies['primary-state-data']);export=json.loads(bodies['primary-shared-export']);ck(len(export['localResults'])==40)
products=load('data/results-sources/derived/primary-products.json');ck(len(products)==40)
local={};api_choices=api_methods=ex_choices=ex_native=ex_methods=0
for key,b in bodies.items():
 if not key.startswith('primary-local-'):continue
 v=json.loads(b);e=v['election'];name=lang(v['jurisdiction']['name']);ck(name not in local);local[name]=v
 ck(e['electionDate']=='2026-09-09' and e['isPrimary'] is True and e['isProduction'] is True and e['isOfficialResults'] is True)
 for item in v['ballotItems']:
  opts=item['summaryResults']['ballotOptions'];ck(sum(o['voteCount'] for o in opts)==item['voteTotal'])
  for o in opts:
   ck(sum(g['voteCount'] for g in o['groupResults'])==o['voteCount']);api_choices+=1;api_methods+=len(o['groupResults'])
ck(len(local)==40 and set(local)=={p['name'] for p in products})
for p in products:
 v=local[p['name']];e=v['election'];ck(p['primary_precinct_objects']==len(v['precincts']) and p['primary_ballot_items']==len(v['ballotItems']))
 for k in ['asOf','lastUpdated','nextUpdateAt','countGroups','groupReportingStatus','precinctReportingStatus','ballotsCast','totalVoters']:ck(p[k]==e[k])
 ck(p['current_leaf_mapping'] is None and p['admitted_November'] is False and p['outstanding_ballots'] is None and p['measured_update_cadence'] is None)
for loc in export['localResults']:
 ck(loc['name'] in local)
 for item in loc['ballotItems']:
  for o in item['ballotOptions'] or []:
   ck(sum(g['voteCount'] for g in o['groupResults'])==o['voteCount']);ex_choices+=1
   if o['precinctResults'] is not None:
    ck(sum(p['voteCount'] for p in o['precinctResults'])==o['voteCount'])
    for p in o['precinctResults']:ck(sum(g['voteCount'] for g in p['groupResults'])==p['voteCount']);ex_native+=1;ex_methods+=len(p['groupResults'])
senate=[]
for item in export['results']['ballotItems']:
 if 'Senator in Congress' not in item['name']:continue
 for o in item['ballotOptions']:
  seen=[]
  for loc in export['localResults']:
   i=[x for x in loc['ballotItems'] if (x['id'],x['name'])==(item['id'],item['name'])];ck(len(i)==1)
   opts=[x for x in i[0]['ballotOptions'] if (x['id'],x['name'],x['politicalParty'])==(o['id'],o['name'],o['politicalParty'])];ck(len(opts)==1);seen.append(opts[0]['voteCount'])
  ck(sum(seen)==o['voteCount']);senate.append({'contest':item['name'],'source_option':o['id'],'literal_name':o['name'],'literal_party':o['politicalParty'],'votes':o['voteCount'],'admitted_November':False})
ck(state['election']['ballotItemCount']==1 and len(state['ballotItems'])==192 and state['election']['ballotsCast']==0)
ck(any(v['election']['ballotsCast']>0 for v in local.values()))
ck(all(g['reportingStatusClientTextKey']=='reporting-status-not-reported' and g['value'] is None for g in state['election']['groupReportingStatus']))
result={'status':'pass_independent_whole_source_current_schema_and_hierarchy_review','checks':N,'manifest_targets':1236,'complete_owned_files':1237,'complete_receipt_objects':336,'final_response_statuses':dict(status),'retained_redirect_metadata_observations':redirects,'redirect_body_scope':'Final whole bodies retained; redirected response headers/status/Location retained, no claim of every redirect intermediate body or full transport framing. Earlier duplicate overwritten receipt metadata is unavailable and candidly retained as a gap.','whole_external_file_pins':len(ext['complete_files']),'full_historical_Senate_objects':458,'priority_objects':242,'remainder_objects':216,'full_inventory':497,'unavailable_Senate':39,'observed_zero':15,'municipal_parents':39,'priority_municipal_parents':37,'separate_admin_parents':4,'all_authority_CSV_rows':45,'whole_current_primary_localities':40,'API_choice_records_checked':api_choices,'API_method_records_checked':api_methods,'export_choice_records_checked':ex_choices,'export_native_choice_rows_checked':ex_native,'export_native_method_rows_checked':ex_methods,'primary_Senate_state_local_vectors':senate,'primary_source_date':'2026-09-09; independently matches retained Secretary calendar, not November3','state_API_asOf':state['election']['asOf'],'export_createdAt':export['createdAt'],'source_inconsistencies_retained':['stateballotItemCount1 versus192fullitems','stateballotsCast0 versuspositivelocalcounts','stateunreportedgroups versusfullyreportedlocals','primarymethodorder distinct historical14slots','oldBoarddirectory2022footer versuscurrentreader/currentHTTP','currentprimaryFederal has four precincts but no historical/current administrative join'],'original_source_bytes_or_producer_writes':False,'current_November_returns_or_ID_mapping_approved':False,'geometry_or_legal_native80_approved':False,'exact_eligible_pool_or_measured_cadence_approved':False,'reviewed_manifest':{'path':'data/results-sources/asset-manifest.json','bytes':(R/'asset-manifest.json').stat().st_size,'sha256':sha((R/'asset-manifest.json').read_bytes())}}
(S/'data/coordinator-official-final-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':result['status'],'checks':N,'all_parents':43,'native_objects':458,'current_primary_localities':40}))
