"""Independent read-only raw schema audit, without admitting current returns."""
from pathlib import Path
from collections import defaultdict
import gzip,hashlib,json,urllib.parse
D=Path(__file__).resolve().parent;S=D.parent;R=D/'results-sources'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))
def read(sid):
 p=R/'receipts'/f'{sid}.json';r=json.loads(p.read_bytes());parts=[]
 for a in r['stored_parts']:
  b=(R/a['path']).read_bytes();assert len(b)==a['bytes']and sha(b)==a['sha256'];parts.append(b)
 raw=gzip.decompress(b''.join(parts));assert len(raw)==r['raw_bytes']and sha(raw)==r['raw_sha256']and r['http_status']==200
 return json.loads(raw)['d'],dict(receipt=pin(p),original_parts=[pin(R/a['path'])for a in r['stored_parts']],raw_bytes=len(raw),raw_sha256=sha(raw),requested_url=r['requested_url'],retrieved_utc=r['retrieved_utc'])
def main():
 county,cp=read('state-current-county-json');assert len(county)==465;groups=defaultdict(list)
 for r in county:groups[r['CountyID'],r['CountyName']].append(r)
 assert len(groups)==93 and all(len(v)==5 for v in groups.values())
 candidates={};schema=set(county[0]);allrows=county[:];parents=[];sources=[cp]
 for r in county:
  c={k:r[k]for k in ['CandidateID','calcCandidate','PartyCode','PartyName','BallotOrder']};key=r['CandidateID']
  if key in candidates:assert candidates[key]==c
  else:candidates[key]=c
 assert set(candidates)=={'3012','3249','3434','3429','3365'}
 expected={cid for cid,name in groups};paths=sorted((R/'receipts').glob('current-native-*.json'));assert len(paths)==58
 for p in paths:
  rows,proof=read(p.stem);sources.append(proof);params=urllib.parse.parse_qs(urllib.parse.urlparse(proof['requested_url']).query)
  assert params['raceID']==['13224']and params['osn']==['102']and params['category']==['PREC']
  local=defaultdict(list)
  for r in rows:
   assert (r['CountyID'],r['CountyName'])in groups and r['CountyID']in expected and params['county']==[r['CountyID']]
   local[r['StatePrecinctID'],r['PrecinctName']].append(r)
  assert all(len(v)==5 and {r['CandidateID']for r in v}==set(candidates)for v in local.values())
  admin=[dict(StatePrecinctID=k[0],PrecinctName=k[1])for k in local if '_TOT'in str(k[0])or '_TOT'in str(k[1])]
  parent=dict(source_id=p.stem,source_county_ID=rows[0]['CountyID'],source_county_name=rows[0]['CountyName'],rows=len(rows),source_contexts=len(local),source_administrative_TOT_contexts=admin,other_source_contexts=len(local)-len(admin),TotalPrecincts_literals=sorted(set(r['TotalPrecincts']for r in rows)),no_historical_or_map_join=True)
  parents.append(parent);allrows+=rows
 for r in allrows:
  assert set(r)==schema and r['RaceID']==13224 and r['OfficeSeqNo']=='102'and r['VoteFor']==1
  assert r['calcCandidateVotes']==0 and r['calcCandidatePercentage']==0 and r['IsReported']is False and r['CurrentDateTime']is None
  assert all(r[k]==candidates[r['CandidateID']][k]for k in ['calcCandidate','PartyCode','PartyName','BallotOrder'])
 for name,contexts,other in [('Douglas',235,234),('Lancaster',200,199)]:
  r=next(p for p in parents if p['source_county_name']==name);assert r['source_contexts']==contexts and r['other_source_contexts']==other
 out=dict(status='pass_bounded_current_official_setup_schema_only',county_rows=465,counties=93,priority_parent_response_files=58,total_raw_records_checked=len(allrows),literal_record_fields=sorted(schema),literal_record_field_count=len(schema),choice_objects=sorted(candidates.values(),key=lambda c:c['BallotOrder']),priority_parent_observations=parents,source_pins=sources,all_raw_candidate_votes_zero=True,all_IsReported_false=True,all_CurrentDateTime_null=True,complete_eligible_writein_universe_approved=False,historical_or_geometry_joins_approved=0,genuine_November_returns_admitted=False,operational_current_choice_key_approval=False,qualification='Observed source-scoped November setup IDs, full raw fields and zero/status/time/nulls are verified. Catalog148 search ID remains distinct. Per-context five named rows do not prove qualified write-in completeness. Administrative TOT contexts are not added to their included units. Native TotalPrecincts1322 is global and distinct from county response denominators. No count/cadence/forecast/current physical crosswalk is admitted.')
 p=D/'coordinator-current-official-setup-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
 print(json.dumps(pin(p)))
if __name__=='__main__':main()
