#!/usr/bin/env python3
"""Offline audit originals→source rows→complete ranks; integrity/links/bounds and scoped acceptance gates."""
from pathlib import Path
import json,csv,gzip,hashlib,io,collections,re,datetime
from fractions import Fraction
O=Path(__file__).resolve().parent;ST=O.parents[1];N=O.parent/'news'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text())
def jl(p):return [json.loads(x)for x in gzip.decompress(p.read_bytes()).splitlines()]
def main():
 checks={};shared=load(O/'source/shared-source-pins.json');shared_by={x['id']:x for x in shared};owned=load(O/'source/acquisition.json');inputs=[]
 for r in shared:
  path=O/'source'/r['reference_path'];z=path.read_bytes();b=gzip.decompress(z);assert sha(z)==r['stored_sha256']and sha(b)==r['raw_sha256']and len(b)==r['bytes'];assert len(z)<40000000;inputs.append(dict(id=r['id'],path=str(path.resolve().relative_to(ST)),raw_sha256=sha(b),stored_sha256=sha(z),bytes=len(z)))
 for r in owned:
  z=(O/'source'/r['asset']).read_bytes();b=gzip.decompress(z);assert sha(z)==r['stored_sha256']and sha(b)==r['raw_sha256']and len(b)==r['raw_bytes']and len(z)==r['stored_bytes'];assert len(z)<40000000
 checks['shared_original_hashes']=len(shared);checks['fresh_HTTP_entity_hashes']=len(owned)
 source_rows=jl(O/'extracts/historical-source-rows.jsonl.gz');catalog=load(O/'extracts/candidate-universes.json');full=load(O/'extracts/native-rankings.json');county=load(O/'extracts/county-candidate-rankings.json');control=load(O/'extracts/county-turnout-registration.json');proof=jl(O/'extracts/independent-candidate-controls.jsonl.gz');fips=load(O/'extracts/county-fips.json')['mapping']
 assert len(fips)==64 and len(set(fips.values()))==64 and all(re.fullmatch('08[0-9]{3}',v)for v in fips.values())
 years={};candidate_positions=0;numeric_positions=0
 for y,kind,expected_n in [(2024,'president',3199),(2022,'senate',3232),(2020,'senate',3205)]:
  sid=f'sos-history-observed-{y}-{kind}-table-csv';m=shared_by[sid];rr=list(csv.reader(io.StringIO(gzip.decompress((N/m['asset']).read_bytes()).decode('utf-8-sig'))));h,party=rr[:2];rs=[r for r in source_rows if r['year']==y];assert len(rs)==len(rr)-2
  # Compare every literal raw field and native/county/state source object, without build helpers.
  parent=None;groups=collections.defaultdict(list);parents={};state=None
  for ordinal,(r,z)in enumerate(zip(rr[2:],rs),3):
   assert r==z['raw_fields']and ordinal==z['source_record']and z['source_id']==sid
   assert z['candidate_values']==[int(v)for v in r[2:-2]]
   assert sum(z['candidate_values'])==z['candidate_votes']==int(r[-2])==int(r[-1])
   assert z['source_TOTAL_VOTES']==int(r[-2])and z['source_TOTAL_BALLOTS']==int(r[-1])
   assert z['method']is None and all(z[f]is None for f in ['blank','undervote','overvote','administrative_ballots','registration'])
   if r[0]=='State':assert state is None;state=z
   elif r[0]=='County':parent=r[1];assert parent not in parents;parents[parent]=z
   else:assert r[0]=='Precinct'and parent==z['county_literal'];groups[parent].append(z)
   if z['county_literal']is not None:assert z['county_fips']==fips[z['county_literal']]
   numeric_positions+=len(r)-2
  assert len(groups)==len(parents)==64 and state is not None
  native=[x for x in rs if x['level_literal']=='Precinct'];assert len(native)==expected_n and len({x['key']for x in native})==expected_n;candidate_positions+=expected_n*(len(h)-4)
  for c,children in groups.items():
   assert all(sum(x['candidate_values'][j]for x in children)==parents[c]['candidate_values'][j]for j in range(len(h)-4))
  assert all(sum(x['candidate_values'][j]for x in parents.values())==state['candidate_values'][j]for j in range(len(h)-4))
  assert sum(x['candidate_votes']for x in native)==state['candidate_votes']
  assert sum((Fraction(x['candidate_votes'],state['candidate_votes'])for x in native),Fraction(0))==1
  assert h==catalog[str(y)]['header']and party==catalog[str(y)]['party_header']
  objects=catalog[str(y)]['page_properties']['contest']['candidates'];assert len(objects)==len(h)-2 and len({x['id']for x in objects})==len(objects)
  for x in objects:assert x['nVotes']==int(rr[2][h.index(x['displayName'])])
  fresh=gzip.decompress((O/'source'/f'current-{y}-{kind}-csv.body.gz').read_bytes());assert sha(fresh)==m['raw_sha256']
  ordered=full[str(y)]['full_order'];assert {x['key']for x in ordered}=={x['key']for x in native};lookup={x['key']:x for x in native}
  for x in ordered:assert x['candidate_values']==lookup[x['key']]['candidate_values']and x['source_record']==lookup[x['key']]['source_record']
  years[y]=dict(native=len(native),county=64,candidate_columns=len(h)-4,total=state['candidate_votes'],zero_rows=sum(x['candidate_votes']==0 for x in native))
 checks['all_source_objects_fields_and_candidate_balances']=years;checks['native_candidate_positions']=candidate_positions;checks['all_selected_numeric_positions']=numeric_positions
 assert candidate_positions==99514 and numeric_positions==121191
 # Prefix minimality and complete order checked for all candidate and volume universes.
 def audit_rank(r,field):
  a=r['full_order'];assert len(a)==r['unit_count'];assert len({x['key']for x in a})==len(a)
  assert [(x[field],x['key'])for x in a]==sorted([(x[field],x['key'])for x in a],key=lambda z:(-z[0],z[1]))
  s=0
  for i,x in enumerate(a,1):s+=x[field];assert x['rank']==i and x['cumulative_votes']==s and x['share_numerator']==x[field]and x['share_denominator']==r['total']
  assert s==r['total'];k=r['minimum80_count'];assert k>0 and 5*a[k-1]['cumulative_votes']>=4*s and (k==1 or 5*a[k-2]['cumulative_votes']<4*s)
  assert r['preceding_count']==k-1 and r['preceding_votes']==(a[k-2]['cumulative_votes']if k>1 else 0)
  assert a[k-1]['key']==r['crossing_key']and a[k-1][field]==r['crossing_votes']
  assert sum(x[field]for x in a[:15])==r['top15_votes'];assert sum(x[field]for x in a[:k])==r['priority_votes'];assert sum(x[field]for x in a[k:])==r['remainder_votes']and len(a[k:])==r['remainder_count']
  assert sum((Fraction(x[field],s)for x in a),Fraction(0))==1
 for r in list(full.values())+list(county.values()):audit_rank(r,'candidate_votes')
 sens=load(O/'extracts/sensitivities.json')
 for r in sens.values():audit_rank(r,'value')
 checks['complete_orders_integer_minimum80_and_exact_weights']=len(full)+len(county)+len(sens)
 contract=load(O/'priority-set.json');rank=full['2024'];assert contract['full_order']==rank['full_order'];k=rank['minimum80_count'];a=rank['full_order'];assert contract['ordered_priority_keys']==[x['key']for x in a[:k]]and contract['ordered_top15_keys']==[x['key']for x in a[:15]]and contract['ordered_remainder_keys']==[x['key']for x in a[k:]]
 hier=contract['county_native_hierarchy'];assert len(hier)==64
 assert {x for p in hier for x in p['all_native_keys']}=={x['key']for x in a};assert sum(p['all_count']for p in hier)==3199
 assert [x for x in a if x['county_literal']=='Summit'and x['native_id_literal']=='2081359007'][0]['candidate_votes']==870
 assert len(contract['ordered_priority_keys'])==1992 and contract['priority_votes']==2554233 and contract['preceding_votes']==2553363
 assert contract['current_geography_approved']is False
 with (O/'native-unit-order.csv').open()as f:export=list(csv.DictReader(f))
 assert len(export)==3199
 for e,r in zip(export,a):
  assert e['key']==r['key']and int(e['rank'])==r['rank']and int(e['candidate_votes'])==r['candidate_votes']and int(e['cumulative_votes'])==r['cumulative_votes']
  for fld in ['stats_active','stats_total','stats_ballots','stats_published_active','stats_published_total','stats_published_ballots']:assert e[fld]==(''if r[fld]is None else str(r[fld]))
 checks['dispatch_contract_full_hierarchy_order_remainder_and_CSV_export']=True
 native_stats=jl(O/'extracts/2024-native-statistics.jsonl.gz');assert len(native_stats)==3183 and len({(x['comparison_county'],x['native_id_literal'])for x in native_stats})==3183
 sl={(x['comparison_county'],x['native_id_literal']):x for x in native_stats};kl={(x['county_literal'],x['native_id_literal'])for x in a};assert sl.keys()<=kl;assert len(kl-sl.keys())==16
 assert len([x for x in native_stats if x['ballots']is None])==2
 for x in native_stats:
  assert x['county_literal']==x['comparison_county']or(x['county_literal']=='Weld 'and x['comparison_county']=='Weld')
  for f,col in [('active','C'),('inactive','D'),('total','E'),('ballots','F')]:
   cell=x['cells'].get(col+str(x['source_row']));assert (cell is None and x[f]is None)or(cell is not None and str(x[f])==cell['decoded'])or(cell is not None and x[f]is None and re.fullmatch(r'[0-9]+\*',cell['decoded']))
   if cell is not None and re.fullmatch(r'[0-9]+\*',cell['decoded']):
    ann=x['annotated_counts'][f];assert ann['literal']==cell['decoded']and ann['source_type']=='s'and ann['raw_v']==cell['value']and ann['parsed_count']==int(cell['decoded'][:-1])==x['published_'+f]
   else:assert x['published_'+f]==x[f]
  if all(x[f]is not None for f in ['active','inactive','total']):assert x['active']+x['inactive']==x['total']
 for x in a:
  ss=sl.get((x['county_literal'],x['native_id_literal']));assert x['statistics_source_row']==(ss['source_row']if ss else None)
  if ss is None:assert x['candidate_votes']==0 and all(x['stats_'+f]is None for f in ['active','inactive','total','ballots'])
  else:
   for f in ['active','inactive','total','ballots']:assert x['stats_'+f]==ss[f]and x['stats_published_'+f]==ss['published_'+f]
   assert x['stats_annotations']==ss['annotated_counts']
 tail=load(O/'extracts/2024-workbook-footnotes-tail.json');assert sum(tail['cached_error_only_tail'].values())==1043548;assert any('school district question'in str(x)for x in tail['other_rows'])
 stats_diag=load(O/'extracts/2024-statistics-county-reconciliation.json');assert {x['county']for x in stats_diag if any(x['known_minus_abstract'].values())}=={'Montezuma'}
 assert sum(x['ballots']for x in native_stats if x['ballots']is not None)==3239261
 assert sum(x['published_ballots']for x in native_stats)==3241155 and sum(x['published_active']for x in native_stats)==4074612 and sum(x['published_total']for x in native_stats)==4583280
 assert all(not any(x['published_minus_abstract'].values())for x in stats_diag)
 correction=load(O/'source/montezuma-annotated-count-correction.json');assert [r['source_row']for r in correction['source_rows']]==[2632,2633]
 checks['native_stats_plain_lane_annotations_nulls_alias_coverage_tail_no_residual_allocation']=True
 # Original independent candidate-position comparisons span every candidate and county.
 assert collections.Counter(x['year']for x in proof)=={2024:896,2022:576,2020:512}
 for y in [2024,2022,2020]:
  pp=[x for x in proof if x['year']==y];assert len({(x['county'],x['header'])for x in pp})==len(pp)
  assert {x['county']for x in pp}==set(fips)
 checks['independent_primary_candidate_controls']=1984
 # Complete county CSV checks: denominator separation + per-candidate controls + source governor universe.
 with (O.parent/'county-turnout.csv').open()as f:county_csv=list(csv.DictReader(f))
 assert len(county_csv)==64 and len({r['county_fips']for r in county_csv})==64
 for y in ['2024','2022','2020']:
  assert sum(int(r[y+'_contest_votes'])for r in county_csv)==full[y]['total']
  for r in county_csv:
   assert sum(int(v)for key,v in r.items()if key.startswith(y+'_candidate::'))==int(r[y+'_contest_votes'])
   for fld in ['blank','undervote','overvote']:assert r[y+'_'+fld]==''
   for fld in ['ballots','active','registered']:assert int(r[y+'_'+fld])==control[y][r['county']][fld]
   assert int(r[y+'_ballots_minus_candidate_votes_unclassified'])==int(r[y+'_ballots'])-int(r[y+'_contest_votes'])
 assert sum(int(r['2022_governor_votes'])for r in county_csv)==2508830
 for r in county_csv:assert sum(int(v)for f,v in r.items()if f.startswith('2022_governor_candidate::'))==int(r['2022_governor_votes'])
 checks['64_county_compatibility_CSV_candidate_ballot_registration_separation']=True
 coverage=list(csv.DictReader((O/'county-native-coverage.csv').open()));assert len(coverage)==64 and sum(int(x['native_records'])for x in coverage)==3199 and sum(int(x['priority_native_records'])for x in coverage)==1992 and sum(int(x['candidate_votes'])for x in coverage)==3192745 and sum(int(x['priority_candidate_votes'])for x in coverage)==2554233
 checks['64_county_native_coverage_map']=True
 v=load(O/'source/visual-review.json')
 for r in v:
  b=(ST/r['reference_path']).read_bytes();assert sha(b)==r['sha256']and len(b)==r['bytes']
 checks['independent_complete_original_page_visual_pins']=len(v)
 # Links in every owned Markdown file must exist; relative targets cannot escape repository.
 repo=ST.parents[2];mds=[ST/'turnout.md']+list(O.rglob('*.md'));links=[]
 for p in mds:
  for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   t=target.strip('<>').split('#',1)[0]
   if not t or re.match(r'^[a-z]+:',t):continue
   q=(p.parent/t).resolve();assert q.is_relative_to(repo)and(q.exists()or q in [O/'validation.json',O/'asset-manifest.json']),(p,target);links.append(dict(document=str(p.relative_to(ST)),target=target))
 checks['all_relative_Markdown_links']=len(links)
 # Manifest owns only the assigned report/CSV/tree. It excludes itself to avoid circular hashing.
 gate=load(O/'peer-agreement.json')if (O/'peer-agreement.json').exists()else dict(status='pending_no_actual_Colorado_peer_launched',peer_id=None)
 if gate.get('status')=='pass_bounded_reciprocal_original_source_QA':
  capture=load(O/gate['capture']);assert capture['peer_id']==gate['peer_id']
  for r in capture['files']:
   pp=ST/r['peer_path']if r['storage']=='original_hash_reference'else O/r['captured_path'];bb=pp.read_bytes();assert len(bb)==r['bytes']and sha(bb)==r['sha256']
  frozen=load(O/gate['frozen_own']);bb=(O/'history/sealed-v1'/frozen['archive']).read_bytes();assert len(bb)==frozen['archive_bytes']and sha(bb)==frozen['archive_sha256']
  recomputed=load(O/'peer-comparison/proof-v1/peer-raw-recomputed-rankings.json')
  for yy,rr in recomputed.items():
   assert rr['denominator']==full[yy]['total']and rr['native_count']==full[yy]['unit_count']
   assert [x['key']for x in rr['full_order']]==[x['key']for x in full[yy]['full_order']]
  assert contract['formal_coordinator_acceptance']is False and contract['peer_agreement']['peer_id']==gate['peer_id']
  checks['bounded_reciprocal_peer_inputs_frozen_archive_and_current_orders']=dict(peer_id=gate['peer_id'],captured_files=len(capture['files']),status=gate['status'],scope=gate['scope'])
 status='pass_offline_and_bounded_reciprocal_QA_formal_acceptance_pending'if gate.get('status')=='pass_bounded_reciprocal_original_source_QA'else'pass_offline_source_and_arithmetic_QA_peer_and_coordinator_pending'
 out=dict(status=status,checked_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),checks=checks,priority=dict(total=3192745,top15=39005,minimum80_count=1992,preceding_count=1991,preceding_votes=2553363,crossing_key=contract['crossing_key'],crossing_votes=870,selected_votes=2554233,remainder_count=1207,remainder_votes=638512),peer_agreement=gate,coordinator_acceptance='pending; this worker cannot confer acceptance',current_geography_approved=False,material_gaps=['No native voting-method/ballot-style/central-group disaggregation in selected statewide exports','No extracted statewide blank/under/over or generic invalid-write-in controls','16zero-candidateCSV-only statisticcontexts unavailable; Montezuma literal starred source counts separately parsed, no allocation; other absent inactive cells remain unknown','No finer2022/2020 native administrative ballot/registration allocation in selected originals','No November2026 native identity/geometry approval or measured live outstanding inventory'],manifest_self_exclusion='asset-manifest.json cannot hash itself; validation.json does not record its own hash',read_only_shared_input_pins=inputs)
 (O/'validation.json').write_text(json.dumps(out,indent=2)+'\n')
 files=[ST/'turnout.md',O.parent/'county-turnout.csv']+[p for p in O.rglob('*')if p.is_file()and p.name!='asset-manifest.json']
 assets=[]
 for p in sorted(files):
  assert '__pycache__'not in p.parts and p.stat().st_size<40000000
  b=p.read_bytes();assets.append(dict(path=str(p.relative_to(ST)),bytes=len(b),sha256=sha(b)))
 manifest=dict(scope='only turnout.md,data/county-turnout.csv,data/turnout/**',self_exclusion='asset-manifest.json only; all other owned assets including validation and scripts enumerated',assets=assets,shared_originals='source/shared-source-pins.json; exact raw/stored hashes and read-only paths',shared_visuals='source/visual-review.json;8wholepages read-only hash references',maximum_stored_bytes=max(x['bytes']for x in assets),all_assets_strictly_below_40000000=True)
 (O/'asset-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 for r in assets:assert sha((ST/r['path']).read_bytes())==r['sha256']
 for link in links:assert ((ST/link['document']).parent/link['target'].split('#',1)[0]).exists()
 print(json.dumps(dict(status=out['status'],checks=checks,owned_assets=len(assets),maximum_stored_bytes=manifest['maximum_stored_bytes']),indent=2))
if __name__=='__main__':main()
