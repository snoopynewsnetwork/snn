"""Keep literal historical native source fields, masks and unallocated controls."""
from pathlib import Path
import collections,csv,gzip,hashlib,io,json
DATA=Path(__file__).resolve().parent
NEWS=DATA/'news'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 manifest={r['id']:r for r in json.loads((NEWS/'manifest.json').read_bytes())};pins={}
 def body(sid):
  r=manifest[sid];z=(NEWS/r['asset']).read_bytes();b=gzip.decompress(z);assert len(b)==r['bytes']and sha(b)==r['raw_sha256']and sha(z)==r['stored_sha256'];pins[sid]=r;return b
 controls={};legacy={}
 for sid,tag,scope in [('sos-2020-federal-csv','2020-senate','United States Senator'),('sos-2022-statewide-csv','2022-governor','Governor and Lieutenant Governor')]:
  selected=[r for r in csv.DictReader(io.StringIO(body(sid).decode('utf-8-sig')))if r['RaceName']==scope];assert len(selected)==3
  for r in selected:assert int(r['CandidateVotes'])==sum(int(r[k])for k in ['CandidateAbsenteeVotes','CandidateElectionDayVotes','CandidateEarlyVotes'])
  legacy[tag]=selected
 contests=[];whole=collections.Counter();keysets={};keyrows={}
 for tag,sid in [('2020-senate','elstats-observed-2020-senate-native-csv'),('2022-governor','elstats-observed-2022-governor-native-csv'),('2024-president','elstats-observed-2024-president-native-csv'),('2024-senate','elstats-2024-senate-linked-csv')]:
  rows=list(csv.reader(io.StringIO(body(sid).decode('utf-8-sig'))));headers=rows[:2];width=len(rows[0]);assert rows[0][-2:]==['Total Votes Cast','Total Ballots Cast'];state=rows[2];assert state[:2]==['State','New Mexico'];statevalues=[int(v)for v in state[2:]];counties=[];native=[];current=None;masks=collections.Counter();allfields=[];keys=set()
  for ordinal,row in enumerate(rows[2:],3):
   assert len(row)==width and row[0]in ['State','County','Precinct'];parsed=[]
   for col,value in enumerate(row[2:],3):
    assert value.isdigit()or value=='*';number=int(value)if value.isdigit()else None;parsed.append(number)
    if number is None:masks[rows[0][col-1]]+=1
    allfields.append(dict(CSV_record_ordinal=ordinal,CSV_column_ordinal=col,source_scope=row[0],literal_header=rows[0][col-1],raw_value=value,parsed_value=number))
   if row[0]=='State':assert ordinal==3
   elif row[0]=='County':
    assert all(v is not None for v in parsed);current=dict(literal_county=row[1],CSV_record_ordinal=ordinal,raw_row=row,source_controls=parsed,native_rows=[]);counties.append(current)
   else:
    assert current is not None;key=(current['literal_county'],row[1]);assert key not in keys;keys.add(key)
    r=dict(literal_county=current['literal_county'],literal_native_label=row[1],CSV_record_ordinal=ordinal,raw_row=row,parsed_values=parsed,masked_literals=[dict(CSV_column_ordinal=i+3,literal_header=rows[0][i+2],literal=value)for i,value in enumerate(row[2:])if value=='*'],source_VoterPrivacy_administrative_row=row[1]=='Voter Privacy');native.append(r);current['native_rows'].append(r)
  assert len(counties)==33 and len({c['literal_county']for c in counties})==33
  assert [sum(c['source_controls'][i]for c in counties)for i in range(width-2)]==statevalues
  for c in counties:
   c['known_native_sums_including_privacy_rows']=[sum(r['parsed_values'][i]for r in c['native_rows']if r['parsed_values'][i]is not None)for i in range(width-2)]
   c['unallocated_county_minus_known_native']=[a-b for a,b in zip(c['source_controls'],c['known_native_sums_including_privacy_rows'])]
   c['masked_native_cells_by_column']=[sum(r['parsed_values'][i]is None for r in c['native_rows'])for i in range(width-2)];c['source_native_rows']=len(c['native_rows']);del c['native_rows']
  assert sum(r['source_VoterPrivacy_administrative_row']for r in native)==33
  if tag in legacy:
   # Candidate spelling/party source forms differ; retain the explicit party-index mapping.
   mp={'DEM':'Democratic','REP':'Republican','LIB':'Libertarian'}
   for r in legacy[tag]:
    indices=[i for i,v in enumerate(rows[1][2:-2])if v==mp[r['PartyCode']]];assert len(indices)==1;assert statevalues[indices[0]]==int(r['CandidateVotes'])
  view='elstats-observed-'+tag+'-view'if tag!='2024-senate'else'elstats-2024-senate';body(view)
  if tag!='2024-senate':
   for suffix in ['document','canvass-original']:body('elstats-observed-'+tag+'-'+suffix)
  record=dict(contest=tag,literal_header_rows=headers,original_CSV_rows=rows,state_controls=statevalues,candidate_names=rows[0][2:-2],candidate_party_source_row=rows[1][2:-2],county_controls=counties,native_source_rows=native,native_context_count=len(native),source_privacy_aggregate_rows=33,nonprivacy_source_rows=len(native)-33,masked_fields_by_literal_column=dict(masks),masked_field_total=sum(masks.values()),masked_candidate_fields=sum(v for k,v in masks.items()if k not in ['Total Votes Cast','Total Ballots Cast']),legacy_state_candidate_method_rows=legacy.get(tag),explicit_native_method_columns_available=False,downloaded_original_canvass_HTTP_status=manifest.get('elstats-observed-'+tag+'-canvass-original',manifest['elstats-2024-state-canvass-original'])['status'],all_original_numeric_and_mask_positions=allfields)
  contests.append(record);whole['native_source_contexts_across_distinct_contests']+=len(native);whole['retained_candidate_control_positions_including_masks']+=len(allfields);whole['masked_fields']+=sum(masks.values());keysets[tag]=keys;keyrows[tag]={(r['literal_county'],r['literal_native_label']):r for r in native}
 diagnostic=[]
 for tag,other in [('2024-president','2024-senate'),('2024-senate','2024-president')]:
  for key in sorted(keysets[tag]-keysets[other]):diagnostic.append(dict(present_in=tag,absent_in=other,literal_county=key[0],literal_native_label=key[1],present_source_row=keyrows[tag][key],absent_contest_values='unavailable_not_inferred_zero'))
 out=dict(status='pass_original_historical_county_state_controls_with_explicit_native_privacy_gaps',source_pins=pins,contests=contests,counts=dict(whole),same2024_two_contest_literal_key_presence_diagnostics_only=diagnostic,qualification='Every original table header, party/category string, scope, row, candidate/control cell, asterisk and source position survives. All33 county/state candidate vectors reconcile;2020/2022 legacy statewide method totals agree after explicit source-party/name mapping. Masks are unavailable, never0, and privacy aggregates remain administrative rows, not physical precincts. Known sums and county residuals are source arithmetic only; even a zero residual does not restore hidden geographic cells. TotalBallotsCast equals candidate scope in state/county export controls and is not admitted as uniform actual whole ballots. Historical method totals and completion headlines remain separate from native rows;2020 legacy1925/1925 versus1959native source rows including33privacy is not forced into a geographic crosswalk. The2024Senate/president literal presence diagnostic is not a join or an absent-contest zero. Actual embedded original canvasses remain403 even with the public viewer as normalReferer; all complete error bodies/receipts are retained and deduplicated. No independent question-worker extraction, valid-write-in completeness, certification chronology, exactpriority, currentcandidate/resultIDs/geography/cadence or livefeed is approved.',formal_priority_accepted=False,current_geography_approved=False)
 p=DATA/'coordinator-historical-native-preflight.json';p.write_text(json.dumps(out,indent=2)+'\n');assert p.stat().st_size<40_000_000
 print(json.dumps(dict(status=out['status'],bytes=p.stat().st_size,sha256=sha(p.read_bytes()),counts=dict(whole),contests=[dict(contest=r['contest'],native_rows=r['native_context_count'],privacy_rows=r['source_privacy_aggregate_rows'],masked_fields=r['masked_field_total'],masked_candidate_fields=r['masked_candidate_fields'],residual_counties=[c['literal_county']for c in r['county_controls']if any(c['unallocated_county_minus_known_native'])])for r in contests],presence_diagnostics=diagnostic)))
if __name__=='__main__':main()
