"""External historical dispatch authority; never approves current reporting joins."""
import datetime,hashlib,json,pathlib
HERE=pathlib.Path(__file__).resolve().parent
STATE=HERE.parent
EXPECTED='0c056e0ebfdb393d4fcb59676805122d8442f444200b9edaf7f4c979c5e9a173'
def pin(path):
 b=path.read_bytes();return {'path':str(path.relative_to(STATE)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def check(path,witness):
 b=path.read_bytes();assert len(b)==witness['bytes'] and hashlib.sha256(b).hexdigest()==witness['sha256'],str(path)
def main():
 path=HERE/'turnout/priority-set.json';contract_pin=pin(path)
 assert contract_pin['sha256']==EXPECTED and contract_pin['bytes']==23823926
 contract=json.loads(path.read_bytes())
 assert contract['coordinator_acceptance_path']=='data/coordinator-priority-acceptance.json'
 assert contract['coordinator_accepted'] is False
 counties=contract['all_unit_order'];assert len(counties)==67
 gulf=next(c for c in counties if c['name']=='Gulf')
 assert gulf['ordinary_poll_close_2026_utc'] is None and gulf['ordinary_election_admin_clock'] is None
 assert len(contract['ordered_priority_keys'])==22
 cumulative=0
 primary=json.loads((HERE/'coordinator-primary-table-review.json').read_text())
 for county,expected in zip(counties,primary['primary_order']):
  cumulative+=county['votes']
  assert county['rank']==expected['rank'] and county['name'].casefold()==expected['county_literal'].casefold()
  assert county['votes']==expected['candidate_votes'] and county['cumulative_votes']==cumulative
 assert cumulative==10757428 and counties[20]['cumulative_votes']==8572752 and counties[21]['cumulative_votes']==8734473
 native=json.loads((HERE/'coordinator-native-original-review.json').read_text())
 assert native['all_frozen_contract_constituents_checked']==23532 and native['contract_sha256']==EXPECTED
 # Original/source/native values were independently rederived; the documented repair changes only two current-clock metadata fields.
 repair=json.loads((HERE/'turnout/priority-freeze-repair.json').read_text())
 reviews=[]
 for name in ['coordinator-primary-table-review.json','coordinator-native-original-review.json','coordinator-target-review.json']:
  value=json.loads((HERE/name).read_text());assert value['status'].startswith('pass')
  reviews.append(pin(HERE/name))
 output=HERE/'coordinator-priority-acceptance.json'
 if output.exists():
  old=json.loads(output.read_text());assert old['contract']==contract_pin
  for witness in old['peer_witnesses']:check(STATE/witness['path'],witness)
  print('Existing immutable historical acceptance verified.');return
 proofs=[]
 for name in ['turnout/peer-agreement.json','baselines/peer-agreement.json']:
  path=HERE/name;body=path.read_bytes();witness=json.loads(body)
  assert witness['status'].startswith('pass')
  if name.startswith('turnout'):
   assert witness['raw19_source_positions']==211874 and witness['raw_fields_compared']==4025606
   assert witness['primary_county_candidate_cells']==2479 and witness['native_contexts']==23532
   for relative,expected in witness['peer_files'].items():check(HERE/'baselines'/relative,expected)
  else:
   assert witness['raw_selected_source_rows']==211874 and witness['native_contexts']==23532
   assert witness['minimum80_total']==8734473 and witness['prior_total']==8572752
   for expected in witness['pinned_assets']:check(STATE/expected['path'],expected)
   contract_witness=next(x for x in witness['pinned_assets'] if x['path']=='data/turnout/priority-set.json')
   assert contract_witness==contract_pin
  assert path.read_bytes()==body
  proofs.append((name,body))
 folder=HERE/'coordinator-witnesses';folder.mkdir(exist_ok=True);witnesses=[]
 for name,body in proofs:
  target=folder/(name.split('/')[0]+'-peer-agreement.json');assert not target.exists();target.write_bytes(body);witnesses.append(pin(target))
 record={'status':'accepted_historical_dispatch_only','accepted':True,'accepted_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'coordinator_agent_id':'d0fc3534-1613-4883-b48b-21a233fcfd9e','actual_first_pair':{'turnout':'f67a9af9-f5bd-47d5-8ebf-ed23594aa3e0','partisanship':'1df5579b-5d40-46b9-a7af-17fdb1a2398d'},'contract':contract_pin,'independent_reviews':reviews,'peer_witnesses':witnesses,'denominator':10757428,'integer_threshold':8605943,'top15_votes':7373225,'minimum80_count':22,'minimum80_votes':8734473,'previous_votes':8572752,'crossing':{'name':'Escambia','fips':'12033','votes':161721},'remainder_count':45,'remainder_votes':2022955,'ordered_priority_keys':contract['ordered_priority_keys'],'ordered_priority':counties[:22],'retained_native_contexts':{'2024_senate':5710,'2024_president':5712,'2022_senate':6013,'2020_president':6097},'metadata_repair':pin(HERE/'turnout/priority-freeze-repair.json'),'scope_limits':['Historical 2024 valid/named Senate county priority only; no current candidate/result identifiers or physical/reporting approval.','Official valid/named county counts differ from unadjusted compiled native marks/vintages; no valid named native write-in allocation.','No explicit method field in original19; EAVS participation methods are separate county administrative observations, not candidate allocation.','Gulf current operational clocks remain null pending source-specific official review; no precinct timezone mapping.','Second-pair dispatch still requires actual worker completion/free slot; this acceptance neither launches workers nor marks assignments complete.']}
 output.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({'status':record['status'],'contract':contract_pin,'priority_count':22,'witnesses':len(witnesses)}))
if __name__=='__main__':main()
