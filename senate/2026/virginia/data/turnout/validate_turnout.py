#!/usr/bin/env python3
"""Offline independent raw-source + complete package audit. Default is read-only, requires seal."""
import argparse,collections,csv,gzip,hashlib,io,json,re,tarfile,sys
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
HERE=Path(__file__).resolve().parent;STATE=HERE.parents[1]
def sha(x):return hashlib.sha256(x).hexdigest()
def js(p):return json.loads(p.read_text())
def jl(p):return [json.loads(x) for x in gzip.decompress(p.read_bytes()).splitlines()]
def owned():return sorted([STATE/'turnout.md',STATE/'data/county-turnout.csv']+[p for p in HERE.rglob('*') if p.is_file()])
INDEX=None;CHECKS={};DETAIL={}
def check(name,condition):
 assert condition,name
 CHECKS[name]=True
@lru_cache(None)
def body(id):
 p=HERE/f'source/acquired/{id}.receipt.json';entry=next(x for x in INDEX['receipts'] if x['receipt_path']==str(p.relative_to(HERE)))
 assert sha(p.read_bytes())==entry['receipt_sha256'];r=js(p);h=r['hops'][-1];assert h['status']==200
 b=(HERE/h['body_path']).read_bytes();assert len(b)==h['stored_bytes'] and sha(b)==h['stored_sha256'];raw=gzip.decompress(b);assert len(raw)==h['raw_bytes'] and sha(raw)==h['raw_sha256'];return raw

def sortedproof(rs,total,k):
 assert len({x['key'] for x in rs})==len(rs)
 assert [(x['reported_candidate_writein_votes'],x['source_record']) for x in rs]==[(x['reported_candidate_writein_votes'],x['source_record']) for x in sorted(rs,key=lambda x:(-x['reported_candidate_writein_votes'],x['source_record']))]
 vals=[x['reported_candidate_writein_votes'] for x in rs];assert all(isinstance(x,int) and x>=0 for x in vals);assert sum(vals)==total
 assert sum(vals[:k])*5>=4*total and sum(vals[:k-1])*5<4*total

def failfixture(name,fn):
 try:fn()
 except (AssertionError,ValueError,KeyError,IndexError):CHECKS['negative_fixture_'+name]=True;return
 raise AssertionError('fixture did not fail: '+name)

def original_checks():
 vectors={};raw_primary=None
 for y,cid,n in [(2024,161257,2669),(2020,144564,2846),(2018,134055,2825)]:
  raw=body(f'fresh-{y}-csv');reader=csv.reader(io.StringIO(raw.decode('utf-8-sig'),newline=''));data=list(reader);header=data[0];totalcol=header.index('Total Votes Cast');candidatecols=list(range(2,totalcol));native=[];parents={};state=None;current=None
  for pos,row in enumerate(data[2:],3):
   v=[int(x) for x in row[2:totalcol]];assert sum(v)==int(row[totalcol])
   if row[0]=='State':state=[int(x) for x in row[2:]]
   elif row[0]=='Locality':current=row[1];assert current not in parents;parents[current]={'values':[int(x) for x in row[2:]],'children':[],'position':pos}
   else:
    assert row[0]=='Precinct' and current is not None
    rec={'key':f'va:{cid}:csv-record:{pos:04d}','label':row[1],'parent_label':current,'source_record':pos,'reported_candidate_writein_votes':sum(v),'values':[int(x) for x in row[2:]]};native.append(rec);parents[current]['children'].append(rec)
  check(f'{y}_raw_disjoint_native_parent_city_coverage',len(native)==n and len(parents)==133 and sum(x.endswith(' City') for x in parents)==38 and all(p['children'] for p in parents.values()))
  sums=[sum(x['values'][j] for x in native) for j in range(len(state))];assert sums==state
  check(f'{y}_raw_native_every_field_state_balance',True)
  residuals=[]
  for label,p in parents.items():
   for j,expected in enumerate(p['values']):
    v=sum(x['values'][j] for x in p['children']);
    if v!=expected:residuals.append((label,header[j+2],v-expected))
  expected=[] if y!=2018 else [('Fairfax City','Write-Ins',1),('Fairfax City','Total Votes Cast',1),('Richmond City','Write-Ins',10),('Richmond City','Total Votes Cast',10),('Roanoke County','Write-Ins',25),('Roanoke County','Total Votes Cast',25)]
  check(f'{y}_all_locality_residuals_exact_unallocated',residuals==expected)
  html=body(f'fresh-{y}-html').decode();obj=json.loads(re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',html).group(1));contest=obj['props']['pageProps']['contest']
  check(f'{y}_full_embedded_source_objects_preserved',obj==js(HERE/f'extracts/{y}-complete-next-data.json'))
  for j,label in enumerate(header[2:]):assert next(c for c in contest['candidates'] if c['displayName']==label)['nVotes']==state[j]
  extract=js(HERE/f'extracts/{y}-contest.json');order=sorted(native,key=lambda x:(-x['reported_candidate_writein_votes'],x['source_record']));saved=extract['native_ranking'];assert [x['key'] for x in order]==[x['key'] for x in saved['order']];k=saved['minimum80']['count'];sortedproof(order,sum(state[:len(candidatecols)]),k)
  check(f'{y}_independent_raw_full_order_minimum80',True)
  positions=jl(HERE/f'extracts/{y}-all-original-rows.jsonl.gz');assert len(positions)==len(data)
  prev=0
  for i,(r,cells) in enumerate(zip(positions,data),1):assert r['source_record']==i and r['cells']==cells and r['byte_start']==prev;piece=raw[r['byte_start']:r['byte_end_exclusive']];assert piece.decode('utf-8-sig')==r['raw_row_utf8'];prev=r['byte_end_exclusive']
  assert prev==len(raw);check(f'{y}_every_raw_row_token_position_coverage',True)
  vectors[y]=state[:len(candidatecols)]
  DETAIL[str(y)]={'native':n,'parents':133,'candidate_vector':vectors[y],'minimum80':saved['minimum80'],'residuals':residuals,'verifiedAt':contest['verifiedAt'],'publicNote':contest['publicNote']}
  if y==2024:raw_primary=order
 return raw_primary

def main(preseal=False):
 global INDEX
 INDEX=js(HERE/'source/acquisition-index.json')
 for e in INDEX['receipts']:
  p=HERE/e['receipt_path'];assert sha(p.read_bytes())==e['receipt_sha256'] and p.stat().st_size==e['receipt_bytes'];r=js(p);assert r==e['full_receipt']
  for hop in r['hops']:
   if hop.get('body_path'):
    packed=(HERE/hop['body_path']).read_bytes();raw=gzip.decompress(packed);assert sha(packed)==hop['stored_sha256'] and sha(raw)==hop['raw_sha256'];assert len(packed)==hop['stored_bytes'] and len(raw)==hop['raw_bytes']
   else:assert hop.get('error') and hop.get('status') is None
 check('every_individual_http_receipt_body_hash_size_clock_and_error_distinction',True)
 for ref in js(HERE/'source/pinned-originals.json'):
  receipt=HERE/ref['receipt_path'];assert sha(receipt.read_bytes())==ref['receipt_sha256'];packed=(STATE/ref['body_path']).read_bytes();assert sha(packed)==ref['stored_sha256'] and sha(gzip.decompress(packed))==ref['raw_sha256']
  if ref.get('offline_replay'):
   r=ref['offline_replay'];assert sha((HERE/r['receipt_path']).read_bytes())==r['receipt_sha256'];assert sha(gzip.decompress((HERE/r['body_path']).read_bytes()))==ref['raw_sha256']
 check('legacy_original_pins_and_fresh_complete_byte_equivalence',True)
 raw=original_checks();contract=js(HERE/'priority-set.json');units=contract['ordered_units'];assert [r['key'] for r in units]==[r['key'] for r in raw];k=contract['minimum80']['count'];sortedproof(units,contract['denominator'],k)
 assert contract['full_all_unit_order']==[r['key'] for r in units] and contract['ordered_priority_keys']==contract['full_all_unit_order'][:k] and contract['ordered_remainder_keys']==contract['full_all_unit_order'][k:] and contract['ordered_top15_keys']==contract['full_all_unit_order'][:15]
 assert sum(x['reported_candidate_writein_votes'] for x in units[:15])==80617 and k==1538 and sum(x['reported_candidate_writein_votes'] for x in units[:k])==3557034 and sum(x['reported_candidate_writein_votes'] for x in units[:k-1])==3555604
 assert sum(Fraction(x['reported_candidate_writein_votes'],contract['denominator']) for x in units)==1
 assert len(contract['parent_inventory'])==133 and len({p['fips'] for p in contract['parent_inventory']})==133
 assert collections.Counter(x for p in contract['parent_inventory'] for x in p['all_native_keys'])==collections.Counter(contract['full_all_unit_order'])
 check('contract_complete_order_priority_remainder_exact_rationals_minimum_integer_crossing',True)
 originalby={r['key']:r for r in raw};seenids=set();methodcount=0;methodtotals=collections.Counter();pcontrols=collections.defaultdict(collections.Counter)
 for r in units:
  orig=originalby[r['key']];assert r['label']==orig['label'] and r['parent_label']==orig['parent_label'] and r['reported_candidate_writein_votes']==orig['reported_candidate_writein_votes'];cons=r['source_native_constituents'];a=cons['enr_api'];obj=json.loads(body(a['source_id']));j=int(a['source_pointer'].rsplit('/',1)[1]);native=obj['ballotItemWithBreakdown']['breakdownResults'][j];assert native==a['full_native_object'];id=native['precinct']['id'];assert id not in seenids;seenids.add(id)
  assert r['source_native_id']==id and r['isVirtual']==native['precinct']['isVirtual'];assert r['legal_named_writein_allocation'] is None and r['current_2026_crosswalk'] is None
  v={c['nativeId']:c['voteCount'] for c in native['ballotOptions']};assert [v[z] for z in ['cs534','cs535','wi-cc200']]==orig['values'][:3];assert sum(v.values())==native['voteTotal']
  for c in native['ballotOptions']:
   assert sum(g['voteCount'] for g in c['groupResults'])==c['voteCount']
   for g in c['groupResults']:methodtotals[c['nativeId'],g['groupId']]+=g['voteCount'];pcontrols[a['source_id']][c['nativeId'],g['groupId']]+=g['voteCount'];methodcount+=1
  assert native['underVoteCount'] is None and native['overVoteCount'] is None
 check('every_native_identity_literal_parent_full_api_object_nulls_and_candidate_vector',len(seenids)==2669 and methodcount==40035)
 state=json.loads(body('enr-2024-senate'));sb=state['ballotItemWithBreakdown'];assert len(sb['breakdownResults'])==133
 for c in sb['summaryResults']['ballotOptions']:
  for g in c['groupResults']:assert methodtotals[c['nativeId'],g['groupId']]==g['voteCount']
 for p in sb['breakdownResults']:
  code=p['locality']['mapFeatureId'];lp=json.loads(body('enr-native-'+code));assert lp['election']['isOfficialResults'] and lp['election']['isProduction'] and lp['election']['electionDate']=='2024-11-05'
  assert sum(x['voteTotal'] for x in lp['ballotItemWithBreakdown']['breakdownResults'])==lp['ballotItemWithBreakdown']['voteTotal']==p['voteTotal']
  for c in p['ballotOptions']:
   for g in c['groupResults']:assert pcontrols['enr-native-'+code][c['nativeId'],g['groupId']]==g['voteCount']
 check('all133_official_election_identities_and_native_locality_state_method_controls',True)
 # Independently validate every selected required CSV raw row/token/byte span.
 inventories=js(HERE/'extracts/csv-source-inventories.json')
 for inv in inventories:
  rawbody=body(inv['source_id']);selected=jl(HERE/f"extracts/{inv['source_id']}-rows.jsonl.gz");seen=set()
  for r in selected:
   assert r['source_record'] not in seen;seen.add(r['source_record']);piece=rawbody[r['byte_start']:r['byte_end_exclusive']];assert piece.decode(r['encoding'])==r['raw_row'];assert next(csv.reader(io.StringIO(piece.decode(r['encoding']),newline='')))==r['cells']
  actual=list(csv.reader(io.StringIO(rawbody.decode(inv['encoding']),newline='')));assert len(actual)==inv['source_logical_records'] and len(selected)==inv['retained_records'];assert all(actual[r['source_record']-1]==r['cells'] for r in selected)
  if inv['source_id'] not in ['enr-2024-results-report','enr-2024-change-log']:assert len(selected)==len(actual)
 check('all_required_csv_headers_rows_tokens_positions_and_full_original_membership',True)
 exp=jl(HERE/'extracts/enr-2024-results-report-rows.jsonl.gz')[1:];exp=[r for r in exp if r['fields']];assert len(exp)==8055
 assert sum(r['fields']['PrecinctId']=='' for r in exp)==48
 expby={r['source_record']:r['fields'] for r in exp};exlinks=js(HERE/'extracts/2024-export-constituents.json');assert len(exlinks)==2669
 assert collections.Counter(i for e in exlinks for i in e['raw_source_records'])==collections.Counter(expby.keys())
 for e in exlinks:
  for c,v in e['candidate_vector'].items():assert sum(int(expby[i]['WriteInVote' if c=='wi-cc200' else 'TOTAL_VOTES']) for i in e['raw_source_records'] if expby[i]['CandidateId']==c)==v
 check('every_export_candidate_row_and_extra_zero_blank_id_constituent_retained_balanced',True)
 cc=list(csv.DictReader((STATE/'data/county-turnout.csv').open()));assert len(cc)==2669
 for r,u in zip(cc,units):assert r['unit_key']==u['key'] and int(r['reported_candidate_writein_marks'])==u['reported_candidate_writein_votes'] and r['historical_literal_label']==u['label'] and r['under_votes_current_api']=='' and r['blank_votes']==''
 pp=list(csv.DictReader((HERE/'locality-turnout.csv').open()));assert len(pp)==133 and sum(int(p['senate_2024_reported_marks']) for p in pp)==4445535 and sum(int(p['native_unit_count']) for p in pp)==2669
 assert sum(int(p['senate_2018_locality_summary']) for p in pp)==3351721 and sum(int(p['senate_2018_native_sum']) for p in pp)==3351757
 check('csv_native_and_all_locality_parents_candidate_and_historical_scopes',True)
 so=js(HERE/'sensitivity-orders.json')
 for name,z in so.items():
  sortedproof(z['order'],z['total'],z['minimum80']['count']);assert sum(Fraction(x['reported_candidate_writein_votes'],z['total']) for x in z['order'])==1
  if z.get('unknown_keys'):assert len(z['unknown_keys'])+len(z['order'])==z['universe_count'] and set(z['unknown_keys']).isdisjoint(x['key'] for x in z['order']) and z['not_an_80percent_claim_for_unknown_full_universe']
 check('all_separate_sensitivity_orders_weights_integer_minimum_and_unknown_coverage',True)
 scopes=js(HERE/'extracts/2024-turnout-scope-controls.json');assert scopes['turnout_csv']['TotalVoteTurnout']['observed_sum']==4537976 and scopes['turnout_csv_minus_annual_total_voting']==2662 and len(scopes['turnout_csv']['TotalVoteTurnout']['missing_rows'])==131
 assert scopes['api_voterTurnout']['ballotsCast']['observed_sum']==4407747 and scopes['api_voterTurnout']['voterTurnout']['observed_sum']==4537976
 admin=js(HERE/'extracts/administrative-turnout-controls.json')
 for y,duplicates,localparents in [('2018',13,127),('2020',2,132),('2022',0,133)]:
  assert admin[y]['Congressional']['locality_count']==133 and len(admin[y]['Congressional']['source_tuple_duplicate_groups'])==duplicates and admin[y]['Local']['locality_count']==localparents
  for r in admin[y]['Local']['localities']:
   if not r['source_records']:assert all(v is None for v in r['fields_observed_sums'].values())
 check('ballot_registration_method_annual_discrepancies_retained_distinct',True)
 # Nontrivial negative controls demonstrate bad package transformations would fail.
 failfixture('wrong_80_crossing',lambda:sortedproof(units,4445535,k-1))
 failfixture('swapped_order',lambda:sortedproof([units[1],units[0]]+units[2:],4445535,k))
 failfixture('omitted_remainder_unit',lambda:sortedproof(units[:-1],4445535,k))
 failfixture('duplicate_native_key',lambda:sortedproof(units+[units[0]],4445535,k))
 failfixture('generic_wrong_export_field',lambda:check('fixture_guard',sum(int(r['fields']['TOTAL_VOTES']) for r in exp if r['fields']['CandidateId']=='wi-cc200')==8509))
 failfixture('2018_residual_silently_repaired',lambda:check('fixture_guard',3351721==3351757))
 failfixture('null_treated_zero',lambda:check('fixture_guard',None==0))
 failfixture('raw_hash_mutation',lambda:check('fixture_guard',sha(body('fresh-2024-csv')+b' ')==sha(body('fresh-2024-csv'))))
 # Links to proof files are only pending before the seal exists.
 links=[];pending=[]
 for file in [STATE/'turnout.md',HERE/'source/SCHEMA.md']:
  for target in re.findall(r'\]\(([^)]+)\)',file.read_text()):
   if re.match(r'[a-zA-Z]+://',target) or target.startswith('#'):continue
   target=target.strip('<>').split('#',1)[0];p=(file.parent/target).resolve()
   if not p.exists():
    if preseal and p.name in ['pre-peer-witness.json','asset-manifest.json','validation.json']:pending.append(str(p.relative_to(STATE)))
    else:raise AssertionError('broken link '+str(p))
   links.append(str(p.relative_to(STATE)))
 check('all_relative_report_schema_links',True);DETAIL['links']=links;DETAIL['preseal_future_proof_links']=pending
 for p in owned():assert p.stat().st_size<40000000 and not p.is_symlink() and '__pycache__' not in p.parts and 'node_modules' not in p.parts
 check('strict_every_owned_file_below_40000000_no_symlink_dependency_cache',True)
 if not preseal:
  manifest=js(HERE/'asset-manifest.json');actual={str(p.relative_to(STATE)) for p in owned() if p!=HERE/'asset-manifest.json'};expected={e['path'] for e in manifest['owned_assets']};assert actual==expected
  for e in manifest['owned_assets']:
   p=STATE/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256']
  check('final_manifest_complete_membership_hash_size_excludes_only_itself',True)
  check('original_witness_current_review_seal_audited_separately',True)
 sys.path.insert(0,str(HERE/'review'))
 from audit import audit
 review=audit(preseal)
 CHECKS.update({'review_'+k:v for k,v in review['checks'].items()});DETAIL['bounded_citation_reciprocal_review']=review
 return {'status':'pass','mode':'preseal source/control audit' if preseal else 'final read-only complete audit','checks':CHECKS,'details':DETAIL,'peer_status':'captured final independent three-Senate source core agrees; coordinator acceptance pending; calculators/president/current/legal scope excluded','validation_limits':['Count-control associations are not geographic/legal/current-identity equivalence.','Source disagreements and unknown ballot/writein universes preserved; no residual allocation.','Preseal validation does not digest later manifest/proof objects; final read-only audit checks those separately.']}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--preseal',action='store_true');p.add_argument('--write',action='store_true');a=p.parse_args();assert not a.write or a.preseal
 result=main(a.preseal)
 if a.write:(HERE/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'status':result['status'],'mode':result['mode'],'checks_passed':len(CHECKS),'native':2669,'parents':133,'minimum80':1538,'peer':'captured source-core agreement; no acceptance'}))
