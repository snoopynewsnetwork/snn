#!/usr/bin/env python3
"""Offline independent assertions over original entities, extracted fields, ranks and assets."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'source'))
from common import *
from fractions import Fraction
from invariants import source_guard,order_guard,admission_guard
from compare_peer import frozen,own
from urllib.parse import unquote

def main():
 checks=[]
 def check(name,condition,details=None):
  assert condition,(name,details);checks.append(dict(check=name,passed=True,details=details))
 a=json.loads((D/'original-extract.json').read_text());b=json.loads((D/'ballot-registration-extract.json').read_text());c=json.loads((D/'canvass-controls.json').read_text());stock=json.loads((D/'registration-stocks.json').read_text());s=json.loads((D/'sensitivity.json').read_text());p=json.loads((D/'priority-set.json').read_text());geo=json.loads((D/'county-identifiers.json').read_text())
 source_guard(a);order_guard(s);admission_guard(p);check('source_order_admission_guards',True)
 source_receipts=manifest();check('source_ids_unique',len({r['id']for r in source_receipts})==len(source_receipts))
 sharedassets={}
 for receipt in source_receipts:
  raw=body(receipt['id']);check('raw_and_stored_source_hash:'+receipt['id'],sha(raw)==receipt['raw_sha256']and len(raw)==receipt['bytes']);check('source_asset_bound:'+receipt['id'],(STATE/receipt['asset']).stat().st_size<40_000_000)
  sharedassets[receipt['asset']]=dict(path=receipt['asset'],sha256=sha((STATE/receipt['asset']).read_bytes()),bytes=(STATE/receipt['asset']).stat().st_size,read_only_reference=not receipt['asset'].startswith('data/turnout/'))
  for hop in receipt.get('redirects',[]):
   if 'asset'in hop:
    path=STATE/hop['asset'];bb=path.read_bytes();check('redirect_entity_hash:'+receipt['id']+':'+hop['url'],sha(bb)==hop['stored_sha256']and sha(gzip.decompress(bb))==hop['raw_sha256']);sharedassets[hop['asset']]=dict(path=hop['asset'],sha256=sha(bb),bytes=len(bb),read_only_reference=not hop['asset'].startswith('data/turnout/'))
 check('no_missing_provenance_parents',all(r.get('parent_source_id')is None or r['parent_source_id']in {z['id']for z in source_receipts}for r in source_receipts))
 all_native=0
 for tag,v in a.items():
  rr=list(csv.reader(io.StringIO(body(v['source_id']).decode('utf-8-sig'))));check('complete_csv_row_and_field_positions:'+tag,len(rr)==len(v['rows'])+2 and rr[:2]==v['header_rows']and all(rr[r['source_row_1based']-1]==r['raw_row']and [f['literal']for f in r['fields']]==r['raw_row'][2:]for r in v['rows']))
  check('source_keys_unique:'+tag,len({r['key']for r in v['rows']})==len(v['rows']))
  counties=[r for r in v['rows']if r['level']=='County'];native=[r for r in v['rows']if r['level']=='Precinct'];all_native+=len(native);n=v['candidate_count'];state=v['rows'][0]
  check('all33_fips_and_parents:'+tag,len(counties)==33 and {r['native_label']for r in counties}==set(geo)and all(r['county_literal']in geo for r in native))
  check('county_all_candidate_and_printed_control_state_balances:'+tag,all(sum(r['fields'][j]['value']for r in counties)==state['fields'][j]['value']for j in range(n+2)))
  check('candidate_universe_state_denominator:'+tag,state['candidate_votes']==sum(f['value']for f in state['fields'][:n])==state['fields'][-2]['value'])
  check('33_administrative_rows:'+tag,sum(r['administrative']for r in native)==33 and all(r['native_label']=='Voter Privacy'for r in native if r['administrative']))
  check('masked_candidates_remain_unavailable:'+tag,all((r['candidate_votes']is None)==any(f['value']is None for f in r['fields'][:n])for r in native))
  check('no_mask_reconstruction:'+tag,all((f['literal']=='*'and f['value']is None)or(f['literal'].isdigit()and int(f['literal'])==f['value'])for r in native for f in r['fields']))
  check('county_residual_equations_no_allocation:'+tag,all(all(x['value']==z+k for x,z,k in zip(next(r for r in counties if r['native_label']==q['county'])['fields'],q['known_sums'],q['county_minus_known']))for q in v['reconciliation']))
  check('source_known_weights_scoped:'+tag,sum(Fraction(r['candidate_votes'],state['candidate_votes'])for r in counties)==1)
 check('native_total_coverage_count',all_native==8558,all_native)
 for tag,year in [('2024-senate','2024'),('2020-senate','2020'),('2022-governor','2022')]:
  v=a[tag];ct=[r for r in v['rows']if r['level']=='County'];pdf=c['county_controls'][year]
  check('independent_primary_pdf_all_county_candidates:'+tag,len(pdf['candidate_rows'])==v['candidate_count']and all(z['county_values']==[r['fields'][i]['value']for r in ct]and z['state']==v['rows'][0]['fields'][i]['value']for i,z in enumerate(pdf['candidate_rows'])))
 ct=[r for r in a['2024-president']['rows']if r['level']=='County'];check('independent_primary_pdf_all33_all7_presidential_tickets',len(c['president_2024_county_controls'])==7 and all(z['county_values']==[r['fields'][z['csv_column_1based']-3]['value']for r in ct]for z in c['president_2024_county_controls']))
 for year,v in b.items():
  check('turnout_native_identity_uniqueness:'+year,len({r['key']for r in v['native_rows']})==len(v['native_rows']))
  check('whole_ballots_native_county_state:'+year,sum(r['ballots_cast']for r in v['native_rows'])==sum(r['ballots_cast_native_sum']for r in v['counties'])==v['state_ballots_cast'])
  check('eligible_native_county_state_signed_literals:'+year,sum(r['eligible_voters']for r in v['native_rows'])==sum(r['eligible_voters_native_sum']for r in v['counties'])==v['state_eligible_voters'])
  raw=body(v['source_id'])
  check('native_source_byte_spans:'+year,all(r['native_label'].encode()in raw[r['source_byte_start']:r['source_byte_end']]and r['ballots_cast_literal'].encode()in raw[r['source_byte_start']:r['source_byte_end']]for r in v['native_rows']))
 check('signed_registration_anomaly_retained',[(r['county_literal'],r['native_label'],r['eligible_voters'])for r in b['2022']['native_rows']if r['eligible_voters']<0]==[('Sandoval','PCT 051',-3)])
 check('primary_ballot_vintage_difference_retained',c['county_controls']['2020']['pdf_ballots_minus_portal']==-58 and len(c['county_controls']['2020']['pdf_ballots_vs_portal_discrepancies'])==7)
 check('2022_2024_ballot_versions_agree',all(c['county_controls'][y]['pdf_ballots_minus_portal']==0 and not c['county_controls'][y]['pdf_ballots_vs_portal_discrepancies']for y in ['2022','2024']))
 for tag,methods in c['statewide_candidate_methods'].items():
  check('candidate_method_totals:'+tag,all(z['early']+z['absentee']+z['election_day']==z['total']for z in methods['numeric_rows'])and sorted(z['total']for z in methods['numeric_rows'])==sorted(f['value']for f in a[tag]['rows'][0]['fields'][:a[tag]['candidate_count']]))
  if tag in ['2020-senate','2022-governor']:
   id='sos-2020-federal-csv'if tag=='2020-senate'else 'sos-2022-statewide-csv';ll=json.loads((D/'legacy-methods.json').read_text())[id]['required_rows'];lookup={int(z['fields']['CandidateVotes']):z['fields']for z in ll}
   check('independent_legacy_candidate_method_agreement:'+tag,all(z['early']==int(lookup[z['total']]['CandidateEarlyVotes'])and z['absentee']==int(lookup[z['total']]['CandidateAbsenteeVotes'])and z['election_day']==int(lookup[z['total']]['CandidateElectionDayVotes'])for z in methods['numeric_rows']))
 for month,v in stock.items():
  check('registration_stock_all33_and_counties:'+month,len([r for r in v['state']['rows']if r['label_literal']!='TOTAL'])==33 and len([r for r in v['county']['rows']if r['scope']=='county_total'])==33)
  coords={(r['page'],r['line_1based'])for r in v['county']['rows']}
  missing=[]
  for pn,page in enumerate((D/'source'/f'registration-{month}-county.txt').read_text().split('\f'),1):
   for ln,l in enumerate(page.splitlines(),1):
    if len(re.findall(r'-?\d[\d,]*',l))>=9 and not l.startswith('Grand Total')and(pn,ln)not in coords:missing.append((pn,ln))
  check('registration_all_numeric_source_rows_retained:'+month,not missing,missing)
  check('registration_native_party_and_total_preservation:'+month,all(sum(r['counts'])==r['total']for r in v['county']['rows']))
  check('registration_source_discrepancies_not_rescaled:'+month,v['county_report_county_totals_sum']!=v['state_report_total']and sum(r['printed_minus_native']for r in v['county_native_reconciliation'])==v['county_report_county_totals_sum']-v['county_report_native_sum'])
 for key,v in s.items():
  rows=v['order'];den=v['denominator'];k=v['minimum80_count'];cum=0
  check('descending_order_and_unique_keys:'+key,len({r['key']for r in rows})==len(rows)and all(rows[i]['votes']>=rows[i+1]['votes']for i in range(len(rows)-1)))
  for r in rows:cum+=r['votes'];assert cum==r['cumulative_votes']
  check('integer_minimum_crossing_and_preceding:'+key,5*rows[k-1]['cumulative_votes']>=4*den and (k==1 or 5*rows[k-2]['cumulative_votes']<4*den)and v['preceding_count']==k-1 and v['preceding_votes']==(rows[k-2]['cumulative_votes']if k>1 else 0))
  check('top15_fraction_and_remainder:'+key,Fraction(sum(r['votes']for r in rows[:15]),den)==Fraction(v['top15_exact_fraction'])and v['remainder_votes']==den-v['minimum80_votes']and v['ordered_remainder_keys']==[r['key']for r in rows[max(15,k):]])
  weights=sum(Fraction(r['votes'],den)for r in rows);check('weights_and_denominator_scope:'+key,weights==(Fraction(v['observed_votes'],den)))
  if key!='native-2024-senate-known-rows-state-denominator':check('complete_observed_universe_weights_one:'+key,weights==1)
 native=[r for r in a['2024-senate']['rows']if r['level']=='Precinct'];keys={r['key']for r in native};table=list(csv.DictReader((STATE/'data/county-turnout.csv').open()));check('compatibility_csv_all_native_rows',len(table)==2201 and {r['key']for r in table}==keys)
 csvbykey={r['key']:r for r in table};check('csv_all_candidate_and_total_literals_preserved',all([csvbykey[r['key']][k]for k in ['candidate_1_literal','candidate_2_literal','printed_total_votes_literal','printed_total_ballots_literal']]==[f['literal']for f in r['fields']]for r in native))
 check('csv_unknown_rank_and_candidate_sum_empty',all(csvbykey[r['key']]['complete_candidate_votes']==''and csvbykey[r['key']]['observed_complete_row_rank']==''and csvbykey[r['key']]['certified_full_universe_rank']==''for r in native if r['candidate_votes']is None))
 check('priority_complete_constituents_order_and_counties',len(p['constituents'])==2201 and {r['key']for r in p['constituents']}==keys==set(p['complete_coverage_order'])and len(p['complete_coverage_order'])==2201 and len(p['county_contexts'])==33 and set(k for c in p['county_contexts']for k in c['source_native_constituent_keys'])==keys)
 check('privacy_dispatch_qualifier_enforced',p['accepted_for_dispatch']is False and p['ordered_priority_keys']==[]and p['certified_native_minimum80']is None and p['certified_native_full_order']is None and p['certified_native_top15']is None)
 review=json.loads((D/'peer-reconciliation.json').read_text());check('actual_captured_peer_source_agreement',p['peer_agent_id']=='9a904675-c599-4e28-8862-663c3496078e'and p['peer_agreement']=='agreed_bounded_immutable_captured_source_core'and review['status']=='passed_bounded_source_core'and not review['mismatches'])
 check('captured_peer_no_future_or_calculator_admission',p['peer_review']['future_final_byte_equality']is False and p['peer_review']['calculator_validation_admitted']is False and p['peer_review']['coordinator_acceptance']is False)
 check('unmatched_otero_not_senate_zero',p['same_year_unmatched_contexts']['president_only']==[['Otero','18']]and p['same_year_unmatched_contexts']['senate_only']==[])
 check('all_native_coverage_counts_and_masks',p['source_coverage']==dict(county_count=33,native_rows=2201,administrative_rows=33,complete_candidate_rows=2181,candidate_unavailable_rows=20,masked_candidate_cells=30,masked_control_cells=6))
 witness=json.loads((D/'original-first-witness-v2.json').read_text());check('frozen_original_first_witness_hashes',not witness['peer_derivatives_read']and sha((D/'original-first-witness-v2.json').read_bytes())=='427ad9e10b16e85cc675f6479796f09813afa5a72845b1199d4dd6b4e8ae7c51'and all(sha(frozen('turnout-pre-peer','data/turnout/'+name))==z['sha256']for name,z in witness['files'].items()))
 for name in ['original-extract.json','legacy-methods.json','ballot-registration-extract.json','canvass-controls.json','registration-stocks.json','native-inventory.json','sensitivity.json','county-summary.csv']:
  check('current_source_core_unchanged:'+name,(D/name).read_bytes()==frozen('turnout-pre-peer','data/turnout/'+name))
 check('native_csv_unchanged',(STATE/'data/county-turnout.csv').read_bytes()==frozen('turnout-pre-peer','data/county-turnout.csv'))
 old=own('priority-set.json');projection=dict(p);projection.pop('peer_review',None)
 for k in ['status','peer_agent_id','peer_agreement']:projection[k]=old[k]
 check('contract_only_review_annotations_changed',projection==old)
 negative=json.loads((D/'negative-fixtures.json').read_text());check('independent_negative_fixtures',negative['status']=='passed'and len(negative['fixtures'])==13 and all(z['rejected']for z in negative['fixtures']))
 check('grand_total_extension_original_evidence',all(z['raw_lines'][0]in(D/'source'/f"registration-{month}-county.txt").read_text()and sum(z['counts'])==z['total']for month,z in json.loads((D/'registration-grand-controls.json').read_text()).items()))
 # Check links in every owned Markdown; all are in-source citations or resolvable state-relative files.
 broken=[]
 for path in [STATE/'turnout.md']+list(D.rglob('*.md')):
  for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
   if target.startswith(('http://','https://','#','mailto:')):continue
   file=unquote(target.split('#')[0].split(':')[0]);resolved=path.parent/file
   if file and not resolved.exists()and resolved not in [D/'validation.json',D/'asset-manifest.json',D/'final-seal.json']:broken.append(dict(path=str(path),target=target))
 check('all_relative_markdown_links_resolve',not broken,broken)
 owned=[STATE/'turnout.md',STATE/'data/county-turnout.csv']+[f for f in D.rglob('*')if f.is_file()and f.name not in ['asset-manifest.json','validation.json']]
 check('all_owned_assets_strictly_under_40million',all(f.stat().st_size<40_000_000 for f in owned),max(f.stat().st_size for f in owned))
 check('no_retained_dependency_or_cache_directories',not any(p.name in ['__pycache__','node_modules','.venv','venv']for p in D.rglob('*')if p.is_dir()))
 out=dict(status='offline_pass_qualified_research_scope',passed_checks=len(checks),checks=checks,primary_reconciliation='all33 county candidate vectors independently match original PDFs for all4 contests; all county/native/state portal ballots and eligible controls exact; source differences explicitly retained',peer_agreement='agreed_bounded_immutable_captured_source_core',peer_comparison_checks=review['comparison_checks'],coordinator_acceptance='pending',coverage=p['source_coverage'],gaps=['Certified complete-native ordering and membership unavailable under privacy masks','No private-cell allocation or zero substitution','Bounded captured-peer source-core agreement complete; calculator/scenarios/report equality and later-final bytes excluded; coordinator acceptance pending','Native methods/blank/under/over/generic write-in completeness unavailable','2020 PDF and portal ballot versions differ58; source-scoped','Dated registration report native/counties/run-time differences retained','No approved current geography or crosswalk'])
 dump(D/'validation.json',out)
 print(json.dumps(dict(status=out['status'],passed_checks=out['passed_checks'],peer_comparison_checks=review['comparison_checks'],peer='bounded_source_core_agreed',acceptance='pending')))
if __name__=='__main__':main()
