#!/usr/bin/env python3
"""Independent structural/arithmetic/hash validation; offline, no source or peer writes."""
import sys
sys.dont_write_bytecode=True
import argparse,collections,csv,gzip,hashlib,json,math,re
from pathlib import Path
from calculator import targets,live
BASE=Path(__file__).resolve().parent;STATE=BASE.parent.parent
def jl(p):return [json.loads(x)for x in gzip.decompress(p.read_bytes()).splitlines()]
def sha(b):return hashlib.sha256(b).hexdigest()
def close(a,b,tol=1e-6):assert math.isclose(a,b,rel_tol=1e-10,abs_tol=tol),(a,b)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check-manifest',action='store_true');args=ap.parse_args();checks={}
 t=json.loads((BASE/'extracts/state-controls.json').read_text());assert len(t)==11
 for key,table in t.items():
  assert len(table['county'])==93
  assert [sum(v[i]for v in table['county'].values())for i in range(len(table['columns']))]==table['state']
 checks['county_vectors']=1023;checks['state_vectors']=11
 candidates=list(csv.DictReader((BASE/'county-candidates.csv').open()));assert len(candidates)==1860
 assert len({(r['county_fips'],r['contest'],r['column_ordinal'])for r in candidates})==1860
 assert all(r['party_literal']=='By Petition'for r in candidates if r['contest']=='senate2024regular'and r['candidate']=='Dan Osborn')
 assert all(r['party_literal']=='Write-In'for r in candidates if r['contest']=='senate2020'and r['candidate']=='Preston Love Jr.')
 native=jl(BASE/'extracts/native-special.jsonl.gz');assert len(native)==len({r['key']for r in native})==1326
 assert [r['key']for r in native]==[r['key']for r in sorted(native,key=lambda x:(-x['pair_votes'],x['key']))]
 assert sum(r['A']for r in native)==349902 and sum(r['B']for r in native)==585103
 assert all(r['A']+r['B']==r['pair_votes']for r in native)
 for county,v in t['senate2024special']['county'].items():
  rr=[r for r in native if r['county']==county];assert[sum(r['B']for r in rr),sum(r['A']for r in rr)]==v
  assert len(rr)==t['registration2024']['county'][county][0]
 fips={r['county']:r['county_fips']for r in native};assert fips['McPherson']=='31117'and fips['Madison']=='31119'
 priority=[r for r in native if r['priority']];assert len(priority)==765 and sum(r['pair_votes']for r in priority)==748190
 assert sum(r['pair_votes']for r in priority[:-1])==747645
 assert 5*747645<4*935005<=5*748190;assert len(native)-len(priority)==561
 close(sum(r['weight']for r in native),1)
 assert len(jl(BASE/'extracts/administrative-partial-alternatives.jsonl.gz'))==329
 checks.update(county_candidates=1860,native=1326,exact_min80=765,remainder=561,administrative_partial=329)
 rows=jl(BASE/'scenarios/unit-targets.jsonl.gz');state=json.loads((BASE/'scenarios/state-targets.json').read_text());assert len(rows)==11676 and len(state)==46
 groups=collections.defaultdict(list)
 for r in rows:groups[r['scenario'],r['target']].append(r)
 for s in state:
  rr=groups[s['scenario'],s['target']];assert len(rr)==(93 if s['geography']=='county' else 1326)
  assert len({r['key']for r in rr})==len(rr)
  close(sum(r['T']for r in rr),s['pair_volume']);close(sum(r['weight']for r in rr),1)
  close(sum(r['target_net']for r in rr),s['target_net']);close(sum(r['baseline_net']for r in rr),s['baseline_net'])
  for r in rr:
   assert 0<=r['target_share']<=1 and 0<=r['q']<=1
   close(r['target_gain'],r['target_net']-r['baseline_net']);close(r['net_gain_for_one_share_pp'],.02*r['T'])
   q=r['selected_only_required_share_unbounded']
   if q is not None:close(r['selected_only_other_units_net']+r['T']*(2*q-1),s['target_net'])
  if s['anchor']=='senate2024special':assert s['anchor_all_source_votes']is None and s['anchor_pair_participation']is None and s['all_candidate_cushion_if_held_at_historical_participation_pp']is None
 for sid in {s['scenario']for s in state}:
  pair=[s for s in state if s['scenario']==sid];assert len(pair)==2;tie=next(s for s in pair if s['target']=='tie');plus=next(s for s in pair if s['target']!='tie');close(plus['unbounded_shift_share_pp']-tie['unbounded_shift_share_pp'],.5)
 checks.update(historical_state_targets=46,historical_unit_targets=11676)
 modern=json.loads((BASE/'scenarios/current-five-choice.json').read_text());assert len(modern)==54
 expected={'Dan Osborn','Pete Ricketts','Chuck Conboy','Mike Marvin','Robin Richards'}
 for s in modern:
  scores=s['candidate_totals'];assert set(scores)==expected;close(sum(scores.values()),s['final_all_candidate_denominator']);close(scores['Dan Osborn']+scores['Pete Ricketts'],s['pair_volume'])
  close(100*(scores['Dan Osborn']-scores['Pete Ricketts'])/s['pair_volume'],s['pair_margin_pp']);close(100*(scores['Dan Osborn']-scores['Pete Ricketts'])/s['final_all_candidate_denominator'],s['all_candidate_margin_pp'])
  if s['target']=='Osborn_plus1_pair':close(s['pair_margin_pp'],1)
  if s['target']=='Osborn_plus1_all_candidate':close(s['all_candidate_margin_pp'],1)
  if 'stress_Conboy55percent'in s['scenario']:assert s['unique_highest']=='Chuck Conboy'and s['legal_pair_share_boundary']>1 and s['legal_bounded_shift']['status']=='impossible_target_margin'
 assert len(jl(BASE/'scenarios/current-five-choice-units.jsonl.gz'))==27216
 checks.update(current_five_choice_scenarios=54,current_five_choice_units=27216)
 synthetic=json.loads((BASE/'scenarios/live-results.json').read_text());assert len(synthetic)==16
 byname={s['name']:s for s in synthetic}
 for s in synthetic:
  result=live(s['input']);assert result==s['output']
  if all(k in result for k in ['counted_A','counted_B','counted_others']):assert all(result[k]==s['input'][k]for k in ['counted_A','counted_B','counted_others'])
  assert result.get('probability')is None
  if result.get('final_A')is not None and result.get('final_others')is not None:close(result['final_A']+result['final_B']+sum(result['final_others'].values()),result['final_all_candidate_denominator'])
 assert byname['unknown_pool']['output']['status']=='unknown_remaining_pool'
 assert byname['negative_pool']['output']['status']=='invalid_negative_or_nonfinite_remaining_pool'
 assert byname['impossible']['output']['tie_remaining_share']>1 and byname['secured']['output']['tie_remaining_share']<0
 assert byname['clip_high']['output']['remaining_A_share_used']==1 and byname['clip_low']['output']['remaining_A_share_used']==0
 assert byname['third_candidate_wins_despite_pair_lead']['output']['unique_plurality_winner']=='Chuck Conboy'
 # Genuine final denominator test: a boundary computed from U alone would fail this.
 inp=byname['nonzero_other_remaining_final_denominator']['input'];out=byname['nonzero_other_remaining_final_denominator']['output'];q=out['A_plus1_final_all_share']
 out2=live({**inp,'remaining_A_share':q});close(out2['final_all_margin_pp'],1)
 assert out['final_all_candidate_denominator']==1200
 for case in json.loads((BASE/'scenarios/target-edge-cases.json').read_text()):assert targets(case['rows'],case['margin'])==case['output']
 checks.update(live_synthetic_cases=16,target_edge_cases=7,counted_totals_fixed=True,final_denominator_includes_counted_and_remaining_others=True)
 u=json.loads((BASE/'candidate-universe.json').read_text());assert u['nine_county_total']==1117 and u['selected_native_observed_generic_marks']==1078 and u['selected_native_unknown_generic_contexts']==895
 checks.update(nine_county_generic_marks=1117,scan_contexts=46,text_summary_contexts=12,eligible_writein_universe_complete=False,priority_eligible_membership_robustness_proven=False)
 registration=json.loads((BASE/'extracts/registration-source-disagreements.json').read_text());assert len(registration['observations'])==6
 assert {r['county']:r['difference']for r in registration['observations']}==dict(Nemaha=-4,Clay=12,Nance=3,Gosper=-1,Lancaster=164,Deuel=1)
 checks['registration_disagreements_preserved']=6
 dc=json.loads((BASE/'extracts/douglas-summary-controls.json').read_text());assert dc['candidate_fields_checked']==21
 d2020=next(r for r in dc['source_volume_observations']if r['year']==2020);assert d2020['state_canvass_TotalVoting']==278518 and d2020['PDF_minus_state']==58 and d2020['BIFF_minus_state']==48
 checks['Douglas_PDF_candidate_fields']=21;checks['Douglas_2020_additional_ballot_disagreement_preserved']=True
 # All original source and required reference files are verified individually.
 source_count=0
 for receiptfile in [BASE/'source/reused-originals.json',BASE/'source/extra-original-references.json']:
  obj=json.loads(receiptfile.read_text());receipts=obj['receipts']if isinstance(obj,dict)else obj
  for r in receipts:
   path=STATE/r['shared_path'];z=path.read_bytes();raw=gzip.decompress(z)
   assert sha(z)==r['stored_sha256']and sha(raw)==r['raw_sha256']and len(raw)==r['bytes'];source_count+=1
 for r in json.loads((BASE/'source/acquisition.json').read_text()):
  if 'asset'in r:
   z=(BASE/r['asset']).read_bytes();raw=gzip.decompress(z);assert sha(z)==r['stored_sha256']and sha(raw)==r['raw_sha256']and len(raw)==r['raw_bytes'];source_count+=1
 checks['original_receipts_checked']=source_count
 for p in [STATE/'county-partisanship.md',BASE/'source/SCHEMA.md']:
  for href in re.findall(r'\[[^\]]*\]\(([^)]+)\)',p.read_text()):
   if re.match(r'https?://',href):continue
   target=p.parent/href.split('#')[0]
   if not args.check_manifest and target.name in ['validation.json','asset-manifest.json']:continue
   assert target.exists(),(p,href)
 checks['relative_links']=True
 for p in [STATE/'county-partisanship.md',BASE.parent/'county-baselines.csv',*BASE.rglob('*')]:
  if p.is_file():assert p.stat().st_size<40000000,(str(p),p.stat().st_size)
 assert not any(p.name in['__pycache__','node_modules','.venv']for p in BASE.rglob('*'))
 checks['stored_assets_strictly_below_40000000']=True
 if args.check_manifest:
  m=json.loads((BASE/'asset-manifest.json').read_text())
  for a in m['assets']+m['references']:
   p=STATE/a['path'];b=p.read_bytes();assert sha(b)==a['sha256']and len(b)==a['bytes'],a['path']
  actual={str(p.relative_to(STATE))for p in [STATE/'county-partisanship.md',BASE.parent/'county-baselines.csv',*BASE.rglob('*')]if p.is_file()and p.name!='asset-manifest.json'}
  assert {a['path']for a in m['assets']}==actual
  print(json.dumps(dict(status='pass',checks=checks,manifest_assets=len(m['assets']),manifest_references=len(m['references']))));return
 result=dict(status='pass',scope='Complete historical named source scope, not eligible-writein or current-geography approval',checks=checks,
  gaps=['Special generic/eligible named write-in universe unavailable statewide; exact named935005 priority is not proven robust for an eligible all-candidate universe.','Native statewide coverage complete for priority special only; other native comparators remain source-scoped local extracts.','2026 later withdrawals/write-ins/signed instrument/unique result IDs not audited; no current counts/geography/feed admission.','Douglas ballot reconstruction disagreements and six local/state registration differences retained and unallocated.','Six initial restricted-shell DNS failures produced no HTTP bodies; exact first-failure timestamps unavailable, per source/acquisition-attempt-note.md.','No remaining-vote estimates, turnout projection, model calibration, live collector or cadence claim.'])
 (BASE/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status='pass',checks=checks)))
if __name__=='__main__':main()
