#!/usr/bin/env python3
"""Read-only independent reconciliation of stable turnout peer outputs to our extraction/originals."""
import csv,gzip,hashlib,io,json,pathlib,collections
R=pathlib.Path(__file__).resolve().parents[1];S=R.parents[1];P=S/'data/turnout'
def rows(p):
 b=p.read_bytes();return list(csv.DictReader(io.StringIO((gzip.decompress(b) if p.suffix=='.gz' else b).decode())))
def en(x):return next((a['text'] for a in (x or []) if a.get('languageId')=='en'),x[0]['text'] if x else '')
def value(x):return '' if x is None else str(x)
def ptr(d,path):
 for k in path.split('/')[1:]:d=d[int(k)] if isinstance(d,list) else d[k]
 return d
references=json.load(open(R/'source/shared-inputs.json'));docs={}
for ref in references:
 if ref['role'] not in ['county-selected','state-selected']:continue
 d=json.loads(gzip.decompress((S/ref['path']).read_bytes()));key=ref['acquisition'].get('id');docs[key]=d
# Explicit peer source ID aliases; these identify the same exact retained entities.
for e,key in [('2024NovGen','sos-2024-general-api-data-selected'),('2021JanFedRun','sos-2021-federal-runoff-api-data-selected'),('2022NovGen','sos-2022-general-api-data-selected'),('2022DecGenRun','sos-2022-runoff-api-data-selected')]:docs['shared:'+key]=docs[key]
docs['state-2020-selected']=docs.get('state-2020-selected') or json.loads(gzip.decompress((P/'source/state-2020-selected.body.gz').read_bytes()))
fail=[];counts=collections.Counter();pins={};qualified=[]
def check(kind,a,b,where):
 counts[kind]+=1
 if value(a)!=value(b):fail.append({'kind':kind,'location':where,'ours_or_original':a,'peer':b})
for filename in ['candidate-votes.csv.gz','candidate-method-votes.csv.gz','county-controls.csv','native-units.csv','rankings.json','candidate-crosswalk.csv','native-candidate-controls.csv','native-method-controls.csv','source-clocks.csv']:
 f=P/filename;pins[filename]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size}
long=rows(R/'candidate-methods.csv.gz');totals=[r for r in long if r['group_name']=='TOTAL'];methods=[r for r in long if r['group_name']!='TOTAL']
def key(r):return (r['election_key'],r['county_fips'],r['unit_level'].replace('native_precinct','precinct'),r['source_pointer'])
ours={key(r):r for r in totals};oursmethod={key(r):r for r in methods};assert len(ours)==len(totals);assert len(oursmethod)==len(methods)
for filename,ismethod in [('candidate-votes.csv.gz',False),('candidate-method-votes.csv.gz',True)]:
 peer=rows(P/filename);check(filename+'_length',len(methods if ismethod else totals),len(peer),'all rows');seen=set()
 for r in peer:
  pointer=r['method_pointer'] if ismethod else r['source_pointer'];k=(r['election_key'],r['county_fips'],r['unit_level'],pointer);assert k not in seen;seen.add(k);o=(oursmethod if ismethod else ours)[k];source=docs[r['source_id']];raw=ptr(source,r['source_pointer']);where=r['source_id']+pointer
  for a,b in [('native_GUID','unit_id'),('native_name','unit_name'),('candidate_GUID','option_id'),('nativeId','candidate_native_id'),('candidate_name','candidate_name'),('candidate_ordinal','option_position'),('party','party_abbreviation'),('isWriteIn','is_write_in'),('isQualifiedWriteIn','is_qualified_write_in')]:check('candidate_'+b,o[a],r[b],where)
  check('candidate_votes',raw['voteCount'],r['votes'],where);check('candidate_json_type',type(raw['voteCount']).__name__,r['votes_json_type'],where)
  check('party_id',(raw.get('party') or {}).get('id'),r['party_id'],where);check('party_name',en((raw.get('party') or {}).get('name')),r['party_name'],where);check('localized_candidate',raw['name'],json.loads(r['localized_candidate_name_json']),where)
  if ismethod:
   m=ptr(source,pointer)
   for a,b in [('group_GUID','method_id'),('group_name','method_name'),('group_ordinal','method_position'),('votes','method_votes')]:check('method_'+b,o[a],r[b],where)
   check('method_type',type(m['voteCount']).__name__,r['method_votes_json_type'],where)
  else:check('own_candidate_votes',o['votes'],r['votes'],where)
ourscounty={(r['election_key'],r['county_fips']):r for r in rows(R.parent/'county-baselines.csv')}
for r in rows(P/'county-controls.csv'):
 o=ourscounty[(r['election_key'],r['county_fips'])];d=docs[r['county_source_id']];where=r['county_source_id'];q=d['ballotItemWithBreakdown']
 for a,b in [('county_name','county_name'),('named_valid_option_votes','state_summary_option_votes'),('source_alloption_votes','county_source_all_option_votes')]:check('county_'+b,o[a],r[b],where)
 for a,b in [('ballotsCast','ballots_cast_raw'),('totalVoters','registration_total_raw')]:check('county_'+b,d['election'].get(a),r[b],where)
 check('county_election_date',d['election']['electionDate'],r['election_date'],where);check('county_contest',en(q['name']),r['contest_name'],where)
 if d['jurisdiction']['id']!=r['jurisdiction_id'] and d['jurisdiction']['id'].lower()==r['jurisdiction_id'].lower():qualified.append({'kind':'GUID_hex_letter_case_only','source_id':where,'county_payload':d['jurisdiction']['id'],'peer_returned_state_locality':r['jurisdiction_id'],'resolution':'same UUID hexadecimal value; original strings retained'})
 else:check('county_jurisdiction',d['jurisdiction']['id'],r['jurisdiction_id'],where)
 check('county_precinct_count',len(d['precincts']),r['native_row_count'],where)
 for a,b in [('underVoteCount','under_votes_source'),('overVoteCount','over_votes_source')]:check('county_'+b,q.get(a),r[b],where)
 check('ballots_usable',float(o['ballots_cast']) if o['ballots_cast'] else None,float(r['ballots_cast_usable']) if r['ballots_cast_usable'] else None,where);check('registration_usable',float(o['registered_voters']) if o['registered_voters'] else None,float(r['registration_total_usable']) if r['registration_total_usable'] else None,where)
our_native={(r['county_fips'],r['native_GUID']):r for r in rows(R/'native-baselines.csv.gz')}
peer_native=rows(P/'native-units.csv');check('native_count',len(our_native),len(peer_native),'state')
for r in peer_native:
 o=our_native[(r['county_fips'],r['native_id'])];d=docs[r['source_id']];raw=ptr(d,r['source_pointer']);z=raw['precinct'];v=ptr(d,r['turnout_pointer']);where=r['source_id']+r['source_pointer']
 for a,b in [('native_name','native_name'),('source_voteTotal','source_all_option_votes')]:check('native_'+b,o[a],r[b],where)
 if o['named_valid_option_votes']!='':check('native_named_sum',o['named_valid_option_votes'],r['state_summary_option_votes'],where)
 else:qualified.append({'kind':'redacted_native_options_raw_total_available','source_id':where,'candidate_sum':None,'raw_voteTotal':raw['voteTotal'],'resolution':'native source voteTotal is distinct from unavailable candidate sums; no assignment'})
 for a,b in [('id','native_id'),('precinctOrder','precinct_order'),('isVirtual','is_virtual_raw'),('mapFeatureId','map_feature_id'),('reportingStatus','reporting_status_raw')]:check('native_'+b,z.get(a),r[b],where)
 check('native_localized_name',z['name'],json.loads(r['localized_native_name_json']),where);check('native_position',int(o['source_pointer'].split('/')[-1]),r['native_source_position'],where)
 check('native_inventory_position',next(i for i,x in enumerate(d['precincts']) if x['id']==z['id']),r['inventory_source_position'],where)
 for a,b in [('ballotsCast','ballots_cast_source'),('voterTurnout','voter_turnout_source'),('voterRegistration','voter_registration_source')]:check('native_'+b,v.get(a),r[b],where)
# Compare full descending order and integer crossing, not just membership.
ourrank=json.load(open(R/'rankings.json'));peerrank=json.load(open(P/'rankings.json'))
for e,o in ourrank.items():
 p=peerrank[e];check('rank_order',[f"GA:county:{r['county_fips']}" for r in o['rows']],p['ordered_keys'],e)
 for a,b in [('denominator','denominator'),('minimum_count','minimum_count'),('first_k_minus_1','preceding_votes'),('first_k','priority_votes'),('top15','top15_votes')]:check('rank_'+b,o[a],p[b],e)
# Compare every published clock and redaction/completion flag to the raw county entity.
metadata={ref['acquisition']['id']:ref['acquisition'] for ref in references if ref['acquisition'] and ref['role']=='county-selected'}
clockrows=rows(P/'source-clocks.csv');check('source_clock_rows',795,len(clockrows),'all county elections')
for r in clockrows:
 d=docs[r['source_id']];e=d['election'];where=r['source_id']
 for a,b in [('id','election_id'),('electionDate','date'),('asOf','as_of'),('lastUpdated','last_updated'),('isOfficialResults','is_official'),('isProduction','is_production'),('redactingPrecinctCountGroups','redacting_precinct_count_groups'),('precinctResultsProtected','precinct_results_protected'),('hidePrecincts','hide_precincts'),('includePrecinctResults','include_precinct_results'),('includePrecinctStatuses','include_precinct_statuses')]:check('source_clock_'+b,e.get(a),r[b],where)
 check('source_clock_jurisdiction',d['jurisdiction']['id'],r['jurisdiction_id'],where);check('source_clock_retrieved',metadata[where]['retrieved_at_utc'],r['retrieved_utc'],where)
# Compare each residual from raw numeric cells to peer residual ledgers.
for fname,method in [('native-candidate-controls.csv',False),('native-method-controls.csv',True)]:
 data=rows(P/fname)
 check('residual_control_rows',2552 if method else 638,len(data),fname)
 ledger=collections.defaultdict(list);county_ledger={}
 for x in methods if method else totals:
  k=(x['source_id'],x['candidate_name'],x['group_name'] if method else 'TOTAL')
  if x['unit_level']=='native_precinct':ledger[k].append(x['votes'])
  if x['unit_level']=='county':county_ledger[k]=x['votes']
 for x in data:
  k=(x['source_id'],x['candidate_name'],x['method_name'] if method else 'TOTAL');cells=ledger[k];known=sum(int(z) for z in cells if z!='');nulls=sum(z=='' for z in cells);control=int(county_ledger[k]);where='|'.join(k)
  for a,b in [(control,x['county_method_votes'] if method else x['county_votes']),(known,x['native_observed_method_sum'] if method else x['native_known_sum']),(nulls,x['native_null_cells']),(len(cells)-nulls,x['native_numeric_cells']),(control-known,x['county_minus_known_sum'])]:check('residual_'+fname,a,b,where)
result={'status':'pass_with_explicit_scope_qualifications' if not fail else 'FAIL','peer_artifact_pins':pins,'checks_by_kind':dict(counts),'check_count':sum(counts.values()),'disagreements':fail,'qualified_representation_differences':qualified,'scope':'Original bytes independently extracted first; all15280 candidate and61120 method rows,795 county controls,2701 native identities/raw turnout,5 complete county orders and exact80 arithmetic. Redactions remain null; no acceptance/current geometry implied.'}
(R/'peer-reconciliation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'checks':result['check_count'],'failures':len(fail),'sample':fail[:5]},indent=2))
assert not fail
