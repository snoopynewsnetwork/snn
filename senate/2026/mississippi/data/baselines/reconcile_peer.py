"""Read-only independent reverse comparison; never writes peer outputs."""
import csv,json
from sources import *
def main():
 own=list(csv.DictReader((OUT/'candidate-votes.csv').open()));pp=BASE/'data/turnout/candidate-votes.csv';peer=list(csv.DictReader(pp.open()));diff=[];n=0
 peer_keys={(r['election_date'],r['fips'],r['office_literal'],r['candidate_literal'],r['party_literal']):r for r in peer};assert len(peer_keys)==len(peer)
 for r in own:
  if r['election_date'].startswith('2018'):continue
  key=tuple(r[k] for k in ['election_date','fips','office_literal','candidate_literal','party_literal']);s=peer_keys.get(key);n+=1
  if s is None or int(s['votes'])!=int(r['votes']):diff.append(dict(key=key,own=r['votes'],peer=None if s is None else s['votes']))
 oc=list(csv.DictReader((BASE/'data/county-baselines.csv').open()));pcpath=BASE/'data/county-turnout.csv';pc=list(csv.DictReader(pcpath.open()));contract=json.loads((OUT/'county-contract.json').read_text());order=[r['fips'] for r in sorted(pc,key=lambda r:int(r['rank']))]
 hpath=BASE/'data/turnout/historical-county-candidate-votes.csv';historical=list(csv.DictReader(hpath.open()));hd=[];hmetadata=[];hn=0;hk={(r['election_date'],r['fips'],r['candidate']):r for r in historical};assert len(hk)==len(historical)==492
 readings={r['source_id']:r for r in json.loads((OUT/'county-2018-readings.json').read_text())['readings']}
 for r in own:
  if not r['election_date'].startswith('2018'):continue
  key=(r['election_date'],r['fips'],r['candidate_literal']);s=hk.get(key);hn+=1
  if s is None:hd.append(dict(key=key,reason='missing_peer'));continue
  pointer=readings[r['source_id']]['source_positions'];fields={'votes':int(r['votes'])==int(s['votes']),'source_id':r['source_id']==s['source_id'],'raw_sha256':readings[r['source_id']]['raw_sha256']==s['raw_sha256'],'page':pointer['page']==int(s['source_page']),'TOTAL_column':pointer['source_column']==int(s['source_TOTAL_column'])}
  if not fields['TOTAL_column']:
   correction=readings[r['source_id']].get('physical_column_correction_history');recognized=correction is not None and int(s['source_TOTAL_column'])==correction['prior_source_positions']['source_column'] and pointer['source_column']==correction['actual_physical_source_column']
   hmetadata.append(dict(key=key,source_id=r['source_id'],owned_fresh_physical_TOTAL_column=pointer['source_column'],peer_observed_TOTAL_column=int(s['source_TOTAL_column']),matches_documented_prior_merged_machine_ordinal=recognized,own_original_correction_evidence=correction))
   if not recognized:hd.append(dict(key=key,checks=fields))
  if not all(v for k,v in fields.items() if k!='TOTAL_column'):hd.append(dict(key=key,checks=fields))
 ppriority=BASE/'data/turnout/priority-set.json';p=json.loads(ppriority.read_text());checks=dict(compared_candidate_rows=n,candidate_differences=diff,all_82_order_match=order==contract['ordered_keys'],priority_order_match=[r['fips'] for r in sorted(pc,key=lambda r:int(r['rank'])) if r['priority'].lower()=='true']==contract['ordered_priority_keys'],minimum80_count=contract['minimum80_count'],crossing_county=contract['crossing_county'],historical_candidate_fields=hn,historical_differences=hd,historical_physical_column_differences=hmetadata,all_historical_physical_TOTAL_ordinals_agree=not hmetadata,peer_candidate_csv_sha256=sha(pp.read_bytes()),peer_county_csv_sha256=sha(pcpath.read_bytes()),peer_priority_sha256=sha(ppriority.read_bytes()),peer_historical_csv_sha256=sha(hpath.read_bytes()),owned_contract_sha256=sha((OUT/'county-contract.json').read_bytes()),scope='Complete county named field/order comparison. Explicit documented later original physical-column corrections are not silently called ordinal agreement. Native/method/generic source scope independently gated; not current legal geography/final contract approval.')
 save(OUT/'peer-reconciliation.json',checks);assert not diff and not hd and checks['all_82_order_match'] and checks['priority_order_match'];print(n,hn,'named fields agree including raw/page; explicit physical ordinal differences',len(hmetadata))
if __name__=='__main__':main()
