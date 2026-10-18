#!/usr/bin/env python3
"""Independent raw JSON/FIPS/positions and native dispatch contract review."""
import collections,csv,datetime,gzip,hashlib,io,json
from pathlib import Path
D=Path(__file__).resolve().parent;ROOT=D.parent;T=D/'turnout';S=T/'source'
def sha(b):return hashlib.sha256(b).hexdigest()
def table(p):
 if p.suffix=='.gz':return list(csv.DictReader(io.StringIO(gzip.decompress(p.read_bytes()).decode())))
 with p.open() as f:return list(csv.DictReader(f))
def text(a):
 values=a or []
 return next((x['text'] for x in values if x.get('languageId')=='en'),values[0]['text'] if values else '')
def val(v):return '' if v is None else str(v)
def pointer(o,p):
 for part in p.strip('/').split('/'):
  key=part.replace('~1','/').replace('~0','~');o=o[int(key)] if isinstance(o,list) else o[key]
 return o

def main():
 body=(T/'priority-set.json').read_bytes();contract_sha=sha(body);assert contract_sha=='1f589d2785d985af2eb33de50adad5a398924ab55f9343deaf79ac5c7378d97a' and len(body)==2293339
 contract=json.loads(body);assert contract['coordinator_formal_acceptance_reference']=='data/coordinator-priority-acceptance.json' and contract['coordinator_accepted'] is False
 data={};raws={};owned=0;shared=0
 for path in S.glob('*.http.json'):
  m=json.loads(path.read_text());p=T/m['asset'];p=p if p.exists() else S/(m['id']+'.body.gz');z=p.read_bytes();b=gzip.decompress(z)
  assert sha(z)==m['stored_sha256'] and len(z)==m['stored_bytes']<40000000 and sha(b)==m['raw_sha256'] and len(b)==m['entity_bytes'];assert m['retrieved_at_utc'] and m['url'] and isinstance(m.get('headers'),dict);owned+=1;raws[m['id']]=b
  if m['status']==200 and b.lstrip().startswith(b'{'):
   try:data[m['id']]=json.loads(b)
   except json.JSONDecodeError:pass
 for fname in ['shared-references.json','source-chain-references.json']:
  for m in json.loads((S/fname).read_text()):
   z=(ROOT/m['path']).read_bytes();b=gzip.decompress(z);assert sha(z)==m['stored_sha256'] and sha(b)==m['raw_sha256'] and len(b)==m['bytes'];shared+=1
   if m['status']==200 and b.lstrip().startswith(b'{'):
    try:data['shared:'+m['id']]=json.loads(b)
    except json.JSONDecodeError:pass
 census=list(csv.DictReader(io.StringIO(raws['county-fips-2020'].decode('utf-8-sig')),delimiter='|'));fips={r['COUNTYNAME']:r['STATEFP']+r['COUNTYFP'] for r in census if r['STATE']=='GA'};assert len(fips)==159
 controls=table(T/'county-controls.csv');assert len(controls)==795
 county_totals=collections.Counter();county_methods=collections.Counter();native_ids=set();native_votes=0;native_ballots=0;native_registration=0;contract_by_fips={c['county_fips']:c for c in contract['coverage']};old_native_unavailable=0
 for row in controls:
  assert fips[row['county_name']]==row['county_fips'];eid=row['election_key'];local=data[row['county_source_id']];state=data[row['state_source_id']];localx=local['ballotItemWithBreakdown'];state_row=pointer(state,row['state_source_pointer'])
  assert row['county_key']=='GA:county:'+row['county_fips'] and row['county_name']==text(state_row['locality']['name'])
  assert int(row['state_summary_option_votes'])==state_row['voteTotal'] and int(row['county_source_all_option_votes'])==localx['voteTotal']
  localopts={text(a['name']):a for a in localx['summaryResults']['ballotOptions']}
  for a in state_row['ballotOptions']:
   other=localopts[text(a['name'])];assert a['voteCount']==other['voteCount'];county_totals[eid]+=a['voteCount']
   sg={text(g['groupName']):g['voteCount'] for g in a['groupResults']};lg={text(g['groupName']):g['voteCount'] for g in other['groupResults']};assert sg==lg and sum(sg.values())==a['voteCount'];county_methods[eid]+=len(sg)
  if eid!='2024NovGen':
   assert not local['precincts'] and not localx['breakdownResults'] and not local['voterTurnout'] and row['ballots_cast_usable']==row['registration_total_usable']=='';old_native_unavailable+=1;continue
  c=contract_by_fips[row['county_fips']];assert c['votes']==int(row['state_summary_option_votes']) and c['parent_ballot_item_id']==localx['id']
  inventory={p['id']:p for p in local['precincts']};breaks=localx['breakdownResults'];assert len(breaks)==len(inventory)==c['constituent_count']==len(c['constituents'])
  known_names={text(a['name']) for a in state_row['ballotOptions']};assert sum(p['voteTotal'] for p in breaks)==localx['voteTotal']
  for unit,p in zip(c['constituents'],breaks):
   ident=p['precinct']['id'];assert ident in inventory and inventory[ident]==p['precinct'];assert unit['native_id']==ident and unit['key']==f'GA:2024NovGen:{row["county_fips"]}:precinct:{ident}' and unit['native_name']==text(p['precinct']['name']) and unit['is_virtual_raw']==p['precinct']['isVirtual']
   assert pointer(local,unit['source_pointer'])==p and unit['source_id']==row['county_source_id'] and unit['source_all_option_votes']==p['voteTotal']
   named=[a['voteCount'] for a in p['ballotOptions'] if text(a['name']) in known_names]
   expected=None if any(v is None for v in named) else sum(named)
   assert unit['state_summary_option_votes']==expected
   assert unit['key'] not in native_ids;native_ids.add(unit['key']);native_votes+=p['voteTotal']
  assert int(row['ballots_cast_usable'])==local['election']['ballotsCast'] and int(row['registration_total_usable'])==local['election']['totalVoters']
  native_ballots+=int(row['ballots_cast_usable']);native_registration+=int(row['registration_total_usable'])
 assert dict(county_totals)=={'2024NovGen':5250047,'2020NovGen':4952175,'2021JanFedRun':4484902,'2022NovGen':3935924,'2022DecGenRun':3541877}
 assert len(native_ids)==2701 and native_votes==5250066 and native_ballots==5297264 and native_registration==7219868 and old_native_unavailable==636
 option_rows=table(T/'candidate-votes.csv.gz');method_rows=table(T/'candidate-method-votes.csv.gz');seen=set();native_nulls=method_nulls=0;known_native=known_methods=0;fields=0
 for r in option_rows:
  k=(r['source_id'],r['source_pointer']);assert k not in seen;seen.add(k);a=pointer(data[r['source_id']],r['source_pointer'])
  assert val(a['id'])==r['option_id'] and val(a['nativeId'])==r['candidate_native_id'] and text(a['name'])==r['candidate_name'] and json.loads(r['localized_candidate_name_json'])==a['name'];fields+=4
  assert val(a['voteCount'])==r['votes'] and type(a['voteCount']).__name__==r['votes_json_type'] and val(a.get('isWriteIn'))==r['is_write_in'] and val(a.get('isQualifiedWriteIn'))==r['is_qualified_write_in'];fields+=4
  if r['unit_level']=='precinct':native_nulls+=a['voteCount'] is None;known_native+=a['voteCount'] or 0
 seen=set()
 for r in method_rows:
  k=(r['source_id'],r['method_pointer']);assert k not in seen;seen.add(k);g=pointer(data[r['source_id']],r['method_pointer']);a=pointer(data[r['source_id']],r['source_pointer'])
  assert val(g['groupId'])==r['method_id'] and text(g['groupName'])==r['method_name'] and val(g['voteCount'])==r['method_votes'] and type(g['voteCount']).__name__==r['method_votes_json_type'] and val(a['voteCount'])==r['votes'];fields+=5
  if r['unit_level']=='precinct':method_nulls+=g['voteCount'] is None;known_methods+=g['voteCount'] or 0
 assert len(option_rows)==15280 and len(method_rows)==61120 and native_nulls==40 and method_nulls==22416 and known_native==5250048 and known_methods==2307296
 ranked=sorted((r for r in controls if r['election_key']=='2024NovGen'),key=lambda r:(-int(r['state_summary_option_votes']),r['county_fips']));order=[r['county_key'] for r in ranked]
 assert contract['complete_ordered_keys']==order and contract['ordered_priority_keys']==order[:44] and contract['remainder_keys']==order[44:]
 proof=json.loads((D/'coordinator-priority-membership-review.json').read_text());assert proof['status']=='pass_exact44_membership_without_imputed_allocation' and proof['proven_membership']==[r['county_name'] for r in ranked[:44]] and set(contract['conditional_full_candidate_minimum_set_unordered_keys'])==set(order[:44])
 assert contract['full_candidate_priority_order'] is None and contract['full_candidate_priority_keys'] is None and contract['native_total']==2701
 assert sha((T/'priority-set.json').read_bytes())==contract_sha,'Contract changed during review'
 peer=json.loads((T/'peer-agreement.json').read_text());assert peer['status']=='pass' and peer['differences']==[]
 result=dict(status='pass_for_historical_dispatch_scope',checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),contract_sha256=contract_sha,contract_bytes=len(body),counties=159,county_election_records=795,source_scoped_native_identities=2701,original_option_rows=len(option_rows),original_method_rows=len(method_rows),original_field_comparisons=fields,native_null_candidate_cells=native_nulls,native_null_method_cells=method_nulls,known_native_candidate_votes=known_native,unallocated_native_candidate_residual=5250066-known_native,known_native_method_votes=known_methods,unallocated_native_method_residual=5250066-known_methods,older_county_native_unavailable_cases=636,owned_originals_hashed=owned,shared_reference_hash_checks=shared,complete_qualified_state_control=5250905,unallocated_qualified_writeins=858,unique_minimum_priority_membership=44,dispatch_order='named-four source descending, not unknown full-candidate order',current_geography_approved=False,live_count_source_approved=False)
 out=D/'coordinator-native-contract-review.json'
 if out.exists():
  old=json.loads(out.read_text())
  if {k:v for k,v in old.items() if k!='checked_utc'}=={k:v for k,v in result.items() if k!='checked_utc'}:result['checked_utc']=old['checked_utc']
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
