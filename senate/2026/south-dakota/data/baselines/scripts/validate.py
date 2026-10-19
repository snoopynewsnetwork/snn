#!/usr/bin/env python3
"""Offline substantive validation; --write saves deterministic validation.json."""
import argparse,csv,gzip,hashlib,io,json,math,re
from pathlib import Path
from collections import defaultdict
from extract import BASE,SRC,DATA,NEWS,PEER,original,js
from calculator import live,live_selected,bounded_shift,selected_unit
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');arg=p.parse_args();checks=[]
 def ck(n,v):checks.append(dict(check=n,passed=bool(v)));assert v,n
 read=lambda name:list(csv.DictReader((BASE/name).open()))
 county=read('../county-baselines.csv');candidates=read('county-candidates.csv');fips=json.loads((SRC/'county-identities.json').read_text());ck('66_county_FIPS_identities',len(fips)==66 and set(fips.values())=={r['county_fips']for r in county})
 controls=json.loads((SRC/'state-controls.json').read_text())
 for y in [2024,2022,2020]:
  rr=[r for r in county if int(r['year'])==y];ck(f'{y}_66_unique_counties',len(rr)==66 and len({r['county_fips']for r in rr})==66)
  cand=[r for r in candidates if int(r['year'])==y];control=controls[str(y)];ck(f'{y}_full_named_candidate_sums',[sum(int(r['votes'])for r in cand if int(r['printed_candidate_column'])==j+1)for j in range(len(control['columns']))]==control['candidate_totals'])
  for r in rr:
   A,B,O,N,P=[int(r[k])for k in ['a_votes','b_votes','other_named_votes','all_named_votes','pair_votes']]
   ck(f'{y}_{r["county"]}_denominators',A+B==P and P+O==N and math.isclose(float(r['pair_participation']),P/N)and math.isclose(float(r['a_pair_share']),A/P))
   ck(f'{y}_{r["county"]}_source_position',int(r['pdf_page'])>0 and int(r['pdf_line'])>0)
 for y,n,tot in [(2024,691,428728),(2022,687,348020),(2020,693,420178)]:
  rr=read('native-2024.csv'if y==2024 else f'native-{y}-public.csv');ck(f'{y}_native_complete_universe',len(rr)==n and len({r['native_key']for r in rr})==n and {r['county_fips']for r in rr}==set(fips.values()))
  ck(f'{y}_native_all_candidate_sum',sum(int(r['all_named_votes'])for r in rr)==tot)
  ck(f'{y}_native_method_and_null_semantics',all(r['method_scope']==('source_label_absentee_unsplit'if'absentee'in r['native_label'].lower()else'unavailable_not_assumed_election_day')and r['official_native_id']=='' and r['current_geometry_join']=='unapproved'for r in rr))
  ck(f'{y}_native_denominators',all(int(r['a_votes'])+int(r['b_votes'])==int(r['pair_votes'])and int(r['pair_votes'])+int(r['other_named_votes'])==int(r['all_named_votes'])for r in rr))
 ck('2022_PDF679_65parents_separate_from687',len(read('native-2022.csv'))==679 and len({r['county_fips']for r in read('native-2022.csv')})==65 and all(r['county']!='Yankton'for r in read('native-2022.csv')))
 balances=json.loads((SRC/'native-2022-balances.json').read_text());ck('2022_PDF_Yankton_gap_2462_340_6051',next(r for r in balances if r['county']=='Yankton')['signed']==[2462,340,6051])
 for k,contract in json.loads((BASE/'priority-contract.json').read_text()).items():
  T=contract['denominator'];n=contract['minimum80_count'];oo=contract['order'];ck(k+'_integer80_minimum',5*contract['before80_votes']<4*T<=5*contract['crossing80_votes']and contract['minimum_integer80_target']==(4*T+4)//5 and contract['priority_keys']==[r['key']for r in oo[:n]])
  ck(k+'_complete_order_and_sum',sum(r['volume']for r in oo)==T and len({r['key']for r in oo})==len(oo)and all(oo[i]['volume']>=oo[i+1]['volume']for i in range(len(oo)-1)))
 ck('distinct_source_and_signed80_thresholds',(4*428728+4)//5==342983 and(4*428922+4)//5==343138 and 342947+194>343138)
 states=json.loads((BASE/'state-targets.json').read_text());settings=json.loads((BASE/'scenario-settings.json').read_text());ck('42_state_targets_21_scenarios',len(states)==42 and len(settings)==21)
 with gzip.open(BASE/'unit-targets.csv.gz','rt')as f:rows=list(csv.DictReader(f))
 groups=defaultdict(list)
 for r in rows:groups[r['scenario'],r['target']].append(r)
 for state in states:
  rr=groups[state['scenario'],state['target']];ss=next(s for s in settings if s['scenario']==state['scenario']);ck(state['scenario']+state['target']+'_all_units',len(rr)==ss['units']and len({r['unit_key']for r in rr})==len(rr))
  ck(state['scenario']+state['target']+'_net_and_weights',math.isclose(sum(float(r['target_net'])for r in rr),state['target_net'],abs_tol=1e-6)and math.isclose(sum(float(r['pair_weight'])for r in rr),1,abs_tol=1e-12)and math.isclose(sum(float(r['all_candidate_weight'])for r in rr),1,abs_tol=1e-12))
  ck(state['scenario']+state['target']+'_complete_named_legal_denominator',math.isclose(sum(state['historical_final_candidate_votes'].values()),state['all_candidate_total'],abs_tol=1e-6))
  ck(state['scenario']+state['target']+'_bounded_and_gain_units',all((r['target_a_share']==''or 0<=float(r['target_a_share'])<=1)and math.isclose(float(r['net_gain_per_one_share_pp']),.02*float(r['pair_volume']))for r in rr))
  ck(state['scenario']+state['target']+'_participation',all(math.isclose(float(r['pair_volume']),float(r['pair_participation'])*float(r['all_candidate_volume']))for r in rr if r['all_candidate_volume']!='0.0'and float(r['all_candidate_volume'])>0))
 with gzip.open(BASE/'selected-unit-break-even.csv.gz','rt')as f:selected=list(csv.DictReader(f))
 ck('17756_unit_and_selected_targets',len(rows)==len(selected)==17756)
 for r in selected:
  if r['status']=='no_positive_pool':continue
  q=float(r['required_share']);T=float(r['selected_pair_volume']);O=float(r['other_fixed_net']);target=float(r['target_net'])
  ck(r['scenario']+r['target']+r['unit_key']+'_selected_only_equation',math.isclose(T*(2*q-1)+O,target,abs_tol=1e-6))
 cases=json.loads((BASE/'live-synthetic-scenarios.json').read_text())
 for e in cases:ck('live_'+e['name']+'_replay',live(e['input'])==e['result']and(e['selected_result']is None or live_selected(e['input'],e['selected_result']['selected_key'])==e['selected_result']))
 cases={c['name']:c for c in cases};ck('live_FINAL_denominator_requirement_1_05',cases['FINAL_denominator_Aplus1']['result']['required_remaining_a_pair_share']==1.05 and cases['FINAL_denominator_Aplus1']['result']['final_pair_denominator']==1000)
 ck('live_other_candidate_can_win',cases['third_candidate_beats_pair_winner']['result']['unique_plurality_winner']=='Illustrative third candidate')
 ck('live_counted_fixed_and_all_denominator',all(e['result'].get('counted_fixed',e['input']['counted'])==e['input']['counted']and('final_candidate_votes'not in e['result']or math.isclose(sum(e['result']['final_candidate_votes'].values()),sum(e['input']['counted'].values())+sum(u['remaining_total']for u in e['input']['remaining'])))for e in cases.values()))
 edges=json.loads((BASE/'bounded-synthetic-scenarios.json').read_text());ck('bounded_cases_explicit',edges[0]['result']['status']=='no_positive_pool'and edges[1]['result']['bounded_shift']<0 and edges[2]['result']['bounded_shift']>edges[2]['result']['unbounded_shift']and edges[3]['result']['status']=='impossible_with_shift_bounds')
 # Every retained original, including ordered parts, verified independently of derived tables.
 refs=json.loads((SRC/'shared-news-receipts.json').read_text());rawverified=0
 for a in refs:
  if 'asset'in a or'asset_parts'in a:original(a,NEWS);rawverified+=1
 for f in [SRC/'peer-original-receipts.json',SRC/'senate-public-original-receipts.json']:
  for a in json.loads(f.read_text()):original(a,PEER);rawverified+=1
 for f in SRC.glob('*.receipt.json'):
  a=json.loads(f.read_text())
  if 'asset'in a:original(a,SRC);rawverified+=1
 ck('raw_originals_and_orderedparts_hashes',rawverified>30)
 for file in list(BASE.rglob('*'))+[DATA/'county-baselines.csv',DATA.parent/'county-partisanship.md']:
  if file.is_file():ck('bounded_asset_'+str(file.relative_to(DATA.parent)),file.stat().st_size<40000000)
 md=[DATA.parent/'county-partisanship.md',SRC/'SCHEMA.md']
 for f in md:
  for link in re.findall(r'\]\(([^)]+)\)',f.read_text()):
   if not re.match(r'https?://|#',link):
    dest=(f.parent/link.split('#')[0]).resolve()
    if arg.write and dest==(BASE/'validation.json').resolve()and not dest.exists():continue # this command creates the linked output; final verify requires it
    ck('relative_link_'+str(f.name)+'_'+link,dest.exists())
 peer=json.loads((BASE/'peer-reconciliation.json').read_text());ck('independent_peer_711_checks',peer['status']=='pass'and peer['checks']==711)
 if not arg.write:
  assets=json.loads((BASE/'asset-manifest.json').read_text())
  for a in assets['owned_assets']:
   f=DATA.parent/a['path'];ck('owned_asset_hash_'+a['path'],f.exists()and f.stat().st_size==a['bytes']and hashlib.sha256(f.read_bytes()).hexdigest()==a['sha256'])
  for a in assets['read_only_references']:
   f=DATA.parent/a['path'];ck('read_only_reference_hash_'+a['path'],f.exists()and f.stat().st_size==a['bytes']and hashlib.sha256(f.read_bytes()).hexdigest()==a['sha256'])
 result=dict(status='pass',checks=len(checks),checks_passed=len(checks),raw_original_entities_verified=rawverified,county_baseline_rows=198,county_candidate_rows=594,complete_native_rows={'2024':691,'2022':687,'2020':693},signed2022PDF_rows=679,signed2022PDF_parents=65,targets=42,unit_targets=17756,selected_targets=17756,peer_checks=711,qualifications=['2024 public minus signed -194 in24counties; unallocated','2020 public minus signed -41 in21counties; unallocated','2022PDFmissingYankton; public2022all66close','certified native minimum80 membership robustness unproved','currentBallot PDF primary web observation succeeds; original download returns404empty','current geometry/collector/probabilities/cadence not established'],comparisons=checks)
 if arg.write:js(BASE/'validation.json',result)
 print(json.dumps({k:v for k,v in result.items()if k!='comparisons'}))
if __name__=='__main__':main()
