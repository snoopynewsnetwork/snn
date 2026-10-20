"""Offline audits, with complete/partial source scope distinguished. No source repairs."""
import argparse,csv,gzip,hashlib,json,math,re,subprocess,tempfile,zipfile
from pathlib import Path
from urllib.parse import unquote
from county import R,COUNTIES,SPECS,js
from immutable_sources import restore_zip,receipts as fixed_receipts,receipt_bytes,metadata_bytes
from packaging import verify as verify_package,historical_integrity
STATE=R.parent.parent

def sha(b):return hashlib.sha256(b).hexdigest()
def strict(b):return json.loads(b,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('nonfinite JSON')))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();checks=[]
 def check(name,ok,detail=None):
  checks.append({'check':name,'passed':bool(ok),'detail':detail});assert ok,(name,detail)
 wide=list(csv.DictReader((R.parent/'county-baselines.csv').open()));long=list(csv.DictReader((R/'county-candidates.csv').open()));state=strict((R/'state-controls.json').read_bytes());units=strict((R/'native-units.json').read_bytes());rec=strict((R/'native-reconciliation.json').read_bytes())
 check('all36_parents_in_every_required_contest',all({r['county'] for r in wide if r['contest']==ct}==set(COUNTIES) for ct in SPECS) and len(wide)==144)
 check('unique_county_candidate_source_positions',len(long)==864==len({(r['contest'],r['county'],r['source_candidate_column']) for r in long}))
 for ct,spec in SPECS.items():
  check(ct+'_all_candidate_columns_balance',all(sum(int(r['votes']) for r in long if r['contest']==ct and int(r['source_candidate_column'])==j+1)==v for j,v in enumerate(state[ct]['values'])))
 for r in wide:
  A,B,O,N,G,V,T=[int(r[k]) for k in ['A_votes','B_votes','other_reported_votes','named_candidate_votes','generic_Misc_votes','reported_all_choice_votes','pair_votes']];assert A+B==T and T+O==V and N+G==V and A>=0 and B>=0 and O>=0
  assert abs(float(r['A_pair_share'])-A/T)<1e-14 and abs(float(r['pair_participation_in_reported_all_choice'])-T/V)<1e-14
 check('all_county_denominators_and_pair_participation',True)
 participation=list(csv.DictReader((R/'participation-controls.csv').open()))
 for y in ['2020','2022','2024']:
  for group in {r['group_source'] for r in participation if r['year']==y}:
   rows=[r for r in participation if r['year']==y and r['group_source']==group];foot=next(r for r in rows if r['county']=='Total');assert {r['county'] for r in rows if r['county']!='Total'}==set(COUNTIES)
   for field in ['Number Eligible','Ballots Returned']:assert sum(int(r[field]) for r in rows if r['county']!='Total')==int(foot[field])
 check('all_county_party_participation_columns_balance',True)
 monthly=list(csv.DictReader((R/'monthly-registration.csv').open()))
 for y in ['2020','2022','2024']:
  rows=[r for r in monthly if r['year']==y];foot=next(r for r in rows if r['county']=='Total');assert {r['county'] for r in rows if r['county']!='Total'}==set(COUNTIES)
  for field in ['this_month','last_month','prior_year_month']:assert sum(int(r[field]) for r in rows if r['county']!='Total')==int(foot[field])
 check('separate_monthly_registration_county_columns_balance',True)
 check('native_source_keys_unique_nonblank',len(units)==len({r['unit_key'] for r in units}) and all(isinstance(r['unit_key'],str) and r['unit_key'].strip() for r in units))
 check('native_current_geographic_flags_false',all(r['current_source_accepted'] is False and r['geography_accepted'] is False for r in units))
 check('all36_native_parent_gaps_explicit',all({r['county'] for r in rec if r['contest']==ct}==set(COUNTIES) for ct in SPECS))
 for r in rec:
  if r['column_closed']:assert not r['units_missing_columns'] and all(v==0 for v in r['differences'].values())
 check('closed_native_candidate_columns_only',True,{ct:sorted({r['county'] for r in rec if r['contest']==ct and r['column_closed']}) for ct in SPECS})
 controls=list(csv.DictReader((R/'known-native-controls.csv').open()));check('known2024_native510_ballot_nonvote_controls_balance',len(controls)==510 and all(float(r['balance'])==0 for r in controls))
 for scope in ['county','known-native']:
  rows=list(csv.DictReader((R/f'{scope}-priority-order.csv').open())) if scope=='county' else list(csv.DictReader((R/'known-native-order.csv').open()));v=[int(r['votes']) for r in rows];den=sum(v);target=(4*den+4)//5;cross=next(i for i,r in enumerate(rows,1) if int(r['cumulative_votes'])>=target)
  assert all(v[i]>=v[i+1] for i in range(len(v)-1));assert sum(v[:cross-1])*5<4*den<=sum(v[:cross])*5;assert all(int(r['cumulative_votes'])==sum(v[:i]) for i,r in enumerate(rows,1));assert abs(sum(float(r['weight']) for r in rows)-1)<1e-12
  check(scope+'_full_order_exact80_predecessor_weights',True,{'denominator':den,'threshold_ceiling_integer':target,'crossing_count':cross,'crossing_votes':sum(v[:cross]),'preceding_votes':sum(v[:cross-1]),'top15_votes':sum(v[:15]),'remainder_votes':sum(v[cross:])})
 priority=strict((R/'priority-contract.json').read_bytes());check('canonical_statewide_native_priority_unavailable',all(priority[k] is None for k in ['canonical_statewide_native_order','canonical_top15','canonical_minimum80']) and len(priority['unclosed_native_parents'])==31 and priority['accepted'] is False)
 scenarios=strict((R/'historical-scenarios.json').read_bytes());check('26_scenarios_all36_no_omission',len(scenarios)==26 and all({r['key'] for r in s['result']['units']}==set(COUNTIES) for s in scenarios))
 for s in scenarios:
  r=s['result'];assert len(r['units'])==36 and r['bounded_feasible'];assert abs(sum(x['weight'] for x in r['units'])-1)<1e-12;assert all(0<=x['target_share']<=1 for x in r['units']);assert abs(sum(x['target_net_votes'] for x in r['units'])-r['target_net_votes'])<=max(1e-7,r['pair_volume']*1e-12);assert abs(r['residual_net_votes'])<=max(1e-7,r['pair_volume']*1e-12)
  assert abs(s['historical_volume']-sum(x['reported_all_choice_volume'] for x in s['county_volume_and_full_field']))<1e-6
  for x,f in zip(r['units'],s['county_volume_and_full_field']):assert abs(x['pair_volume']-f['reported_all_choice_volume']*f['pair_participation'])<1e-7
  if s['scenario_id'].endswith('-tie'):
   p=next(x for x in scenarios if x['scenario_id']==s['scenario_id'].removesuffix('-tie')+'-Aplus1');assert abs(p['result']['unbounded_share_shift_points']-r['unbounded_share_shift_points']-.5)<1e-12
 check('weights_participation_clipped_bounds_roots_and_half_share_point',True)
 selected=list(csv.DictReader((R/'county-selected-targets.csv').open()))
 for r in selected:
  q=float(r['unbounded_required_share']);t=float(r['selected_pair_volume']);o=float(r['other_net_votes_fixed']);scenario=next(s for s in scenarios if s['scenario_id']==r['scenario_id']);target=scenario['result']['target_net_votes'];assert abs(o+t*(2*q-1)-target)<1e-6;assert 0<=float(r['required_share'])<=1
 check('all_selected_county_only_equations_all_other_units_fixed',len(selected)==936)
 fixture=strict((R/'fixtures/results.json').read_bytes());oracle=strict((R/'bounded-root-oracle.json').read_bytes());check('actual_CLI_positive_unknown_negative_regressions',len(fixture)==63 and all(r['passed'] for r in fixture));check('independent_analytic_bounded_root_checks',len(oracle)==120 and all(r['passed'] for r in oracle))
 inventory=strict((R/'source/independent-original-inventory.json').read_bytes())
 for r in inventory:
  b=(R/r['text_path']).read_bytes();assert sha(b)==r['text_stored_sha256'];raw=gzip.decompress(b);assert len(raw)==r['text_bytes'] and sha(raw)==r['text_raw_sha256']
 check('all113_original_text_derivative_hashes',len(inventory)==113)
 # Re-audit original ZIP bytes and every retained member against our own independent inventory.
 for y in [2020,2022]:
  with tempfile.TemporaryFile() as f:
   restore_zip(y,f);f.seek(0)
   with zipfile.ZipFile(f) as z:
    assert z.testzip() is None and len(z.infolist())==36
    for i,info in enumerate(z.infolist()):
     inv=next(r for r in inventory if r['source_key']==f'{y}-{i:02}');body=z.read(info);assert sha(body)==inv['raw_sha256'] and len(body)==inv['raw_bytes'] and info.filename==inv['origin']['member'] and info.CRC==inv['origin']['CRC']
  check(str(y)+'_whole_original_ZIP_CRC_all36_member_hashes',True)
 # Every receipt metadata/body pin, including complete failed responses and ordered parts.
 shared={}
 assert (R/'source/original-read-receipts.json').read_bytes()==receipt_bytes()
 receipts=fixed_receipts()
 for item in receipts:
  s=item['source']
  if 'response_entities' in s:
   parent=(STATE/item['receipt_path']).parent;rp=STATE/item['receipt_path'];metadata=metadata_bytes(item);shared[str(rp.relative_to(STATE))]=sha(metadata)
   for e in s['response_entities']:
    path=parent/e['asset'];stored=path.read_bytes();assert sha(stored)==e['stored_sha256'];b=gzip.decompress(stored);assert sha(b)==e['raw_sha256'] and len(b)==e['raw_bytes'];shared[str(path.relative_to(STATE))]=sha(stored)
  elif 'asset' in s:
   path=R.parent/'news'/s['asset'];stored=path.read_bytes();assert sha(stored)==s['stored_sha256'];b=gzip.decompress(stored);assert sha(b)==s['raw_sha256'] and len(b)==s['bytes'];shared[str(path.relative_to(STATE))]=sha(stored)
  elif 'asset_parts' in s:
   for e in s['asset_parts']:
    path=R.parent/'news'/e['asset'];b=path.read_bytes();assert sha(b)==e['sha256'] and len(b)==e['bytes']<40000000;shared[str(path.relative_to(STATE))]=sha(b)
 for r in strict((R/'source/authority-chain-references.json').read_bytes()):
  p=STATE/r['path']
  if r['path']=='data/turnout/source/shared-original-pins.json':
   body=(json.dumps([x['source'] for x in receipts if 'id' in x['source']],indent=2)+'\n').encode()
  else:body=p.read_bytes()
  assert len(body)==r['bytes'] and sha(body)==r['sha256'];shared[r['path']]=r['sha256']
 for r in strict((R/'source/ocr-pins.json').read_bytes()):
  p=STATE/r['path'];assert p.stat().st_size==r['bytes'] and sha(p.read_bytes())==r['sha256'];shared[r['path']]=r['sha256']
 for r in strict((R/'source/visual-readings.json').read_bytes()):
  for e in r['evidence']:assert sha((R/e['raster']).read_bytes())==e['sha256']
 check('original_receipt_body_OCR_visual_pins',True,{'shared_assets':len(shared)})
 # Preserve the historical shared-assets output byte-for-byte. Metadata paths are
 # verified against their own captured receipt serialization, never current peer metadata.
 old_shared=strict((R/'source/shared-assets.json').read_bytes());assert {x['path']:x['sha256'] for x in old_shared}==shared
 for r in strict((R/'source/pre-peer-body-map.json').read_bytes()):
  b=(R/r['frozen_body']).read_bytes();assert sha(b)==r['stored_sha256'] and sha(gzip.decompress(b))==r['raw_sha256']
 check('immutable_pre_peer_bodies_reproduce_witness',sha((R/'source/pre-peer-witness.json').read_bytes())=='208a3ad98dfb055eea0f895c0c0faf9881f684214e7d5a34c41e01f4df123b7f')
 peer=strict((R/'peer-reconciliation.json').read_bytes());check('full_county_and510_native_candidate_order_peer_comparison',not any(peer[k] for k in ['county_differences','county_control_differences','participation_differences','monthly_registration_differences','known_native_candidate_differences','native_raw_CSV_method_differences']) and peer['known_native_complete_descending_contract_order_equal'])
 for p in peer['pins']:
  body=(R/p['frozen_path']).read_bytes();assert sha(body)==p['stored_sha256'] and sha(gzip.decompress(body))==p['raw_sha256']
 check('peer_captured_bodies_stable_not_used_as_source_repairs',True,{'unresolved_candidate_differences':peer['native_shared_candidate_differences'],'unresolved_control_differences':peer['native_shared_control_differences'],'coverage_differences':peer['coverage']})
 for p in (R/'source/current').glob('*.receipt.json'):
  receipt=strict(p.read_bytes())
  for hop in receipt['hops']:
   b=(p.parent/hop['asset']).read_bytes();assert sha(b)==hop['stored_sha256'] and sha(gzip.decompress(b))==hop['raw_sha256']
 check('fresh_authority_success_failed_and_local_error_receipts',True)
 payload=[p for p in R.rglob('*') if p.is_file()]+[R.parent/'county-baselines.csv',STATE/'county-partisanship.md'];check('every_owned_asset_strictly_under40million_bytes',all(p.stat().st_size<40000000 for p in payload),{'max_bytes':max(p.stat().st_size for p in payload)})
 check('no_owned_dependency_or_cache_directories',not any(p.is_dir() and p.name in ['__pycache__','node_modules','.venv'] for p in R.rglob('*')))
 for p in R.rglob('*.json'):
  if p.name in ['nan.input.json','inf.input.json','minusinf.input.json']:continue
  strict(p.read_bytes())
 check('strict_JSON_outputs_nonfinite_inputs_separately_invalid_fixtures',True)
 links=[]
 for p in [STATE/'county-partisanship.md',R/'source/SCHEMA.md']:
  for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   if re.match(r'https?://|mailto:',target):continue
   target=unquote(target.split('#')[0]);links.append(str((p.parent/target).resolve()));assert (p.parent/target).is_file(),(p,target)
 check('all_relative_report_links_resolve',True,{'links_checked':len(links)})
 stable=strict((R/'source/repair-proofs/unchanged-payloads.json').read_bytes())
 for row in stable['files']:
  b=(STATE/row['path']).read_bytes();assert len(b)==row['bytes'] and sha(b)==row['sha256']
 check('every_unaffected_previous_payload_byte_identical',stable['unchanged_count']==288 and stable['all_exact'])
 history=historical_integrity();check('pre_repair296_bodies_reconstruct_and_unchanged_substantive_pins',True,{'old_owned_files':history['old_owned_files'],'all_old_bodies_reconstruct':history['all_old_bodies_reconstruct'],'freeze_inventory_sha256':history['freeze_inventory_sha256']})
 proof=strict((R/'source/repair-proofs/original-rebuild.json').read_bytes());check('guarded_immutable_original_reader113_texts72_members_unchanged',proof['before_after_identical'] and proof['original_entity_texts']==113 and proof['ZIP_members']==72 and len(proof['mutable_routes_denied'])==5)
 negatives=strict((R/'source/repair-proofs/packaging-negatives.json').read_bytes());check('missing_changed_seal_and_omitted_history_rejected',len(negatives['negative_checks'])==3 and all(x['correctly_rejected'] for x in negatives['negative_checks']))
 if not args.write:
  audit=verify_package();check('complete_manifest_self_only_exclusion_seal_first',True,audit)
 result={'status':'passed_complete_available_historical_scopes_with_explicit_gaps','checks':checks,'current_source_accepted':False,'geography_accepted':False,'coordinator_accepted':False,'material_gaps':{'canonical_statewide2024_native_priority':None,'unclosed2024_native_parents':31,'historical_native_coverage':'partial; all36 county controls complete; inspect reconciliation/source-method gaps','unclosed_Douglas2022_peer_candidate_differences':peer['native_shared_candidate_differences'],'unclosed_Douglas2022_peer_control_differences':peer['native_shared_control_differences'],'valid_named_writein_scope':None,'complete_statewide_canvass_ballots_blank_under_over_series':None,'actual2026_final_ballot_mapping':None,'current_geometry_feed_cadence_and_calibration':None}}
 if args.write:js('validation.json',result)
 print(json.dumps({'status':result['status'],'checks':len(checks),'failed':sum(not x['passed'] for x in checks),'canonical_native_priority_available':False}))
if __name__=='__main__':main()
