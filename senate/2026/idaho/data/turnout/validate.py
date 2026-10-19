#!/usr/bin/env python3
"""Independent offline checks against pinned original source rows and complete dispatch.
No network, no Git, no preflight code imports, no changes to peer/coordinator files.
"""
from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction
import ast,csv,gzip,hashlib,io,json,re,sys,tarfile,zipfile,xml.etree.ElementTree as E
D=Path(__file__).resolve().parent;S=D.parent.parent;H=lambda b:hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_bytes())
def rows(p):return list(csv.DictReader(p.open()))
def original_rows(raw,worksheet):
 z=zipfile.ZipFile(io.BytesIO(raw));assert z.testzip()is None;ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
 ss=[''.join(n.itertext())for n in E.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns)]if'xl/sharedStrings.xml'in z.namelist()else[]
 out={}
 for r in E.fromstring(z.read(worksheet)).findall('s:sheetData/s:row',ns):
  cells={}
  for c in r:
   v=c.find('s:v',ns);v=None if v is None else v.text
   if c.get('t')=='s'and v is not None:v=ss[int(v)]
   cells[re.sub(r'\d','',c.get('r'))]=v
  out[int(r.get('r'))]=cells
 return out

def main():
 if '--verify-assets'in sys.argv:
  m=load(D/'asset-manifest.json');expected={(S/x['path']).resolve()for x in m['owned_assets']};actual={S/'turnout.md',D.parent/'county-turnout.csv'}|{p for p in D.rglob('*')if p.is_file()and p.name!='asset-manifest.json'}
  assert expected==actual,(expected-actual,actual-expected)
  for r in m['owned_assets']:
   b=(S/r['path']).read_bytes();assert len(b)==r['bytes']<40000000 and H(b)==r['sha256'],r['path']
  print(f"PASS complete asset manifest: {len(expected)} owned files, exact SHA256/bytes, every object <40,000,000 bytes.");return
 checks=[]
 def check(name,fn,detail=None):
  try:r=fn();assert r is not False;checks.append(dict(name=name,pass_check=True,detail=detail if detail is not None else r))
  except Exception as e:checks.append(dict(name=name,pass_check=False,error=repr(e)));raise
 refs=load(D/'source/reused-originals.json');raws={}
 for r in refs:
  b=(D/r['reused_path']).read_bytes();raw=gzip.decompress(b);assert H(b)==r['stored_sha256']and H(raw)==r['raw_sha256']and len(raw)==r['bytes'];raws[r['id']]=raw
  if raw.startswith(b'PK'):assert zipfile.ZipFile(io.BytesIO(raw)).testzip()is None
 check('original_news_complete_hashes_lengths_and_archive_CRC',lambda:dict(originals=len(refs),all_valid=True))
 for r in load(D/'source/requests.json'):
  b=(D/r['asset']).read_bytes();raw=gzip.decompress(b);assert H(b)==r['stored_sha256']and H(raw)==r['original_sha256']and len(raw)==r['original_bytes'];assert len(b)<40000000
 check('new_acquisition_entity_and_stored_hashes',lambda:True)
 for r in load(D/'source/reused-national-originals.json'):
  root=D.parents[2];b=(root/r['original_asset_path']).read_bytes();raw=gzip.decompress(b);assert H(b)==r['stored_sha256']and H(raw)==r['original_sha256'];assert H((root/r['original_record_path']).read_bytes())==r['original_metadata_sha256'];assert H((root/r['headers_record_path']).read_bytes())==r['headers_sha256']
 check('reused_national_originals_read_only_hashes',lambda:True)
 cur=S/'data/news/coordinator-oct19-recheck/current-ballot-original-review.json'
 if cur.exists():
  r=load(cur);rec=r['original_source'];b=(S/rec['asset_path']).read_bytes();assert H(b)==rec['stored_sha256']and H(gzip.decompress(b))==rec['raw_sha256'];assert len(gzip.decompress(b))==592959;assert not r['all_official_statewide_eligible_writeins_or_later_signed_ballot_scope_exhausted'];check('bounded_current_sample_original_preserved_no_scope_expansion',lambda:True)
 q=load(D/'priority-set.json');a=rows(D/'native-order.csv');source=original_rows(raws['sos-2024-all-races-xlsx'],'xl/worksheets/sheet1.xml');native=defaultdict(dict);sourcepositions=[]
 for row,x in source.items():
  if x.get('D')=='United States President':
   k=(x['A'],x['B']);ck=(x.get('E'),x['F']);assert ck not in native[k];native[k][ck]=int(x['G']);sourcepositions.append(row)
 assert len(native)==985 and len(sourcepositions)==12805 and len(set(c for c,p in native))==44
 check('raw_2024_native_universe_and_candidate_key_uniqueness',lambda:True)
 ps=rows(D/'native-2024-candidate-positions.csv');assert len(ps)==12805
 for r in ps:
  o=source[int(r['source_row'])];assert [r['county'],r['literal_precinct'],r['literal_party']or None,r['literal_candidate'],int(r['value'])]==[o['A'],o['B'],o.get('E'),o['F'],int(o['G'])];assert r['cell']=='G'+r['source_row']
 check('all_12805_selected_category_positions_match_original_cells',lambda:True)
 units={r['key']:r for r in a};assert len(units)==985;assert {(r['county'],r['literal_precinct'])for r in a}==set(native)
 for r in a:
  v=native[(r['county'],r['literal_precinct'])];assert int(r['candidate_votes'])==sum(n for(p,c),n in v.items()if c not in ['Overvotes','Undervotes']);assert int(r['overvotes'])==v[(None,'Overvotes')];assert int(r['undervotes'])==v[(None,'Undervotes')]
 votes=sorted(units,key=lambda k:(-int(units[k]['candidate_votes']),k));assert votes==[r['key']for r in a]==[r['key']for r in q['complete_order']];assert sum(int(r['candidate_votes'])for r in a)==905057
 weights=sum((Fraction(int(r['weight_numerator']),int(r['weight_denominator']))for r in a),Fraction());assert weights==1
 cum=0
 for i,r in enumerate(a,1):
  cum+=int(r['candidate_votes']);assert int(r['rank'])==i and int(r['cumulative_votes'])==cum;assert r['minimum80_priority']==str(i<=528)
 assert sum(int(r['candidate_votes'])for r in a[:15])==65391
 assert sum(int(r['candidate_votes'])for r in a[:527])==723753
 assert sum(int(r['candidate_votes'])for r in a[:528])==724515
 assert 5*723753<4*905057<=5*724515
 assert a[527]['literal_precinct']=='Osburn'and a[527]['county']=='Shoshone County'and int(a[527]['candidate_votes'])==762
 assert q['ordered_priority_keys']==votes[:528]and q['ordered_remainder_keys']==votes[528:]and len(votes[528:])==457
 assert sum(int(r['candidate_votes'])for r in a[528:])==180542
 check('full_native_order_exact_weights_top15_minimum80_predecessor_crossing_remainder',lambda:dict(total=905057,top15=65391,k=528,votes=724515,predecessor=723753,remainder=180542))
 assert len(q['all_county_constituents'])==44
 allchild=[];prichild=[];remchild=[]
 for c in q['all_county_constituents']:
  k=c['key'];full=q['ordered_child_keys_by_parent'][k];pri=q['ordered_priority_child_keys_by_parent'][k];rem=q['ordered_remainder_child_keys_by_parent'][k]
  assert full==[v for v in votes if units[v]['county_fips']==k];assert pri==[v for v in full if v in set(votes[:528])];assert rem==[v for v in full if v not in set(votes[:528])];assert {r['key']for r in c['president_contexts']}==set(full)
  allchild+=full;prichild+=pri;remchild+=rem
 assert len(allchild)==len(set(allchild))==985 and len(prichild)==528 and len(remchild)==457 and set(prichild).isdisjoint(remchild)
 check('44_parent_full_ordered_priority_remainder_child_maps_disjoint_complete',lambda:dict(parents=44,children=985,priority=528,remainder=457,priority_parents=sum(bool(v)for v in q['ordered_priority_child_keys_by_parent'].values())))
 # Independent original statistical totals and footer comparison.
 rawstats=original_rows(raws['sos-2024-turnout-xlsx'],'xl/worksheets/sheet1.xml');ss=defaultdict(Counter);foot={};statkeys=set()
 for pos,x in rawstats.items():
  if pos==1:continue
  c=x['A']
  if x['B']=='Total':foot[c]=x
  else:
   assert(c,x['B'])not in statkeys;statkeys.add((c,x['B']))
   for col in 'CDEF':ss[c][col]+=int(x[col])
   assert int(x['C'])+int(x['D'])==int(x['E'])
 for c in foot:assert all(ss[c][col]==int(foot[c][col])for col in 'CDEF')
 assert len(statkeys)==986 and statkeys-set(native)=={('Bingham County','BONNEVILLE 27')}and not(set(native)-statkeys)
 extra=next(x for x in rawstats.values()if x.get('A')=='Bingham County'and x.get('B')=='BONNEVILLE 27');assert all(int(extra[col])==0 for col in 'CDEF')
 assert [sum(ss[c][col]for c in ss)for col in 'CDEF']==[1057735,121015,1178750,917469]
 residual=[]
 for c,p in native:
  r=next(x for x in rawstats.values()if x.get('A')==c and x.get('B')==p);diff=int(r['F'])-sum(native[(c,p)].values())
  if diff:residual.append((c,p,diff))
 assert len(residual)==7 and {c for c,p,d in residual}=={'Boundary County'}and sum(d for c,p,d in residual)==3
 assert next(d for c,p,d in residual if p=='Absentee')==-2721
 assert sum(d for c,p,d in residual if p!='Absentee')==2724
 check('2024_stats986_44_footers_registration_balance_and_exact7_residuals',lambda:dict(statistics_ballots=917469,race_allcategory=917466,net=3,stats_only_zero=True))
 county=rows(D.parent/'county-turnout.csv');assert len(county)==44
 sums=defaultdict(Counter)
 for(c,p),v in native.items():
  for ck,n in v.items():sums[c][ck]+=n
 for r in county:
  assert int(r['president_2024_candidate_votes'])==sum(n for(p,c),n in sums[r['county']].items()if c not in ['Overvotes','Undervotes']);assert int(r['ballots_2024'])==ss[r['county']]['F']
 assert [int(r['president_2024_candidate_votes'])for r in county]==sorted((int(r['president_2024_candidate_votes'])for r in county),reverse=True)
 assert sum(int(r['president_2024_candidate_votes'])for r in county[:15])==758271 and sum(int(r['president_2024_candidate_votes'])for r in county[:12])==722749 and sum(int(r['president_2024_candidate_votes'])for r in county[:13])==735838
 assert q['county_sensitivity']['ordered_priority_keys']==[r['county_fips']for r in county[:15]]
 check('county44_aggregation_and_separate13_15_sensitivity',lambda:True)
 # Every saved historical candidate position checked against original ZIP member XML.
 hp=json.loads(gzip.decompress((D/'historical-candidate-positions.json.gz').read_bytes()));hb={};workbooks=json.loads(gzip.decompress((D/'source/historical-workbook-rows.json.gz').read_bytes()))
 for b in workbooks:
  z=zipfile.ZipFile(io.BytesIO(raws[b['source_id']]));raw=z.read(b['archive_member']);assert H(raw)==b['original_sha256']
  for sh in b['sheets']:hb[(b['source_id'],b['archive_member'],sh['sheet'])]=original_rows(raw,sh['member'])
 for r in hp:
  o=hb[(r['source_id'],r['archive_member'],r['sheet'])][r['source_row']];col=re.sub(r'\d','',r['cell']);assert r['raw_resolved_value']==o.get(col)and r['raw_cell_present']==(col in o)
  if r['value']is not None:assert int(o[col])==r['value']
 hist=json.loads(gzip.decompress((D/'historical-native.json.gz').read_bytes()));hc=rows(D/'historical-county-candidate-controls.csv');hcounters=defaultdict(Counter)
 for r in hp:
  if r['role']=='native'and r['value']is not None:hcounters[(r['year'],r['contest'],r['county'])][r['county_candidate_header']]+=r['value']
 for r in hc:assert int(r['votes'])==hcounters[(int(r['year']),r['contest'],r['county'])][r['literal_candidate']]==int(r['native_known_sum'])
 for y,contest,rows_expected,total_expected,null_expected in [(2020,'Senate_Class_II',974,859827,8),(2020,'President',974,867281,42),(2022,'Senate_Class_III',999,590890,0),(2022,'Governor',999,592624,0)]:
  nn=[r for r in hist if r['year']==y and r['contest']==contest];assert len(nn)==rows_expected and len({r['county']for r in nn})==44;assert sum(r['candidate_votes_known_sum']for r in nn)==total_expected;assert sum(v is None for r in nn for v in r['candidate_values'])==null_expected
 check('historical_every_saved_candidate_position_original_cell_and_all44_controls',lambda:dict(candidate_positions=len(hp),native2020=974,native2022=999,Senate2020=859827,President2020=867281,Senate2022=590890,Governor2022=592624,nulls2020Senate=8,nulls2020President=42))
 for paths in [q['source_object_paths'].values(),[q['historical_native_path'],q['historical_administrative_path']]]:
  for rel in paths:assert(D/rel).is_file(),rel
 for filename in ['native-rankings.json','rankings.json']:
  for name,r in load(D/filename).items():
   order=r['full_order'];assert len(order)==r['unit_count']and len({o['key']for o in order})==len(order);assert sum(x['votes']for x in order)==r['denominator'];assert order==sorted(order,key=lambda x:(-x['votes'],x['key']));k=r['minimum80_count'];pre=sum(x['votes']for x in order[:k-1]);cross=sum(x['votes']for x in order[:k]);assert 5*pre<4*r['denominator']<=5*cross;assert pre==r['preceding_votes']and cross==r['minimum80_votes'];assert sum(x['votes']for x in order[k:])==r['remainder_votes']
 check('all_sensitivity_orders_and_exact_integer_minimum_thresholds',lambda:True)
 st20=json.loads(gzip.decompress((D/'native-2020-stats.json.gz').read_bytes()));assert len(st20)==974
 sums20=defaultdict(Counter)
 for r in st20:
  o=hb[(r['source_id'],r['archive_member'],r['sheet'])][r['source_row']]
  for col,field in zip('DEFG',['cutoff','election_day','registered','ballots']):
   assert r[field]==(None if o.get(col)is None else int(o[col]))
   if r[field]is not None:sums20[r['county']][field]+=r[field]
 for r in county:
  assert [sums20[r['county']][field]for field in ['cutoff','election_day','registered','ballots']]==[int(r[field])for field in ['registration_2020_cutoff','registration_2020_election_day','registration_2020_total','ballots_2020']]
 assert [sum(r[field]is None for r in st20)for field in ['cutoff','election_day','registered','ballots']]==[32,35,33,9]
 assert sum(r['county']=='Boise County'and r['literal_precinct']=='90 Absentee'for r in st20)==3
 check('native2020_statistics_all_original_fields_44_controls_nulls_and_duplicate_labels',lambda:True)
 st22=json.loads(gzip.decompress((D/'stats2022.json.gz').read_bytes()));method22=[r for r in st22 if r['table']=='general_method'];assert len(method22)==45
 assert sum(r['absentee']for r in method22 if r['literal_county']!='GRAND TOTAL')==129210
 assert sum(r['early']for r in method22 if r['literal_county']!='GRAND TOTAL'and r['early']is not None)==61048
 assert all(r['early']is None for r in method22 if r['raw_early']=='-')
 check('2022_actual_general_ballot_method_controls_and_literal_dash_nulls',lambda:True)
 pdf=load(D/'source/pdf-primary-controls.json');assert pdf['all_presidential_categories_equal_OOXML']and pdf['all_4_statistical_integer_columns_equal_OOXML']and pdf['printed_presidential_native_vectors']==985
 fec=(D/'source/fec-pres-2024.txt').read_text();assert re.search(r'^ID\s+3\s+905,057\s*$',fec,re.M)
 clerk=(D/'source/house-clerk-2024.txt').read_text();idaho=clerk.split('IDAHO',1)[1].split('FOR UNITED STATES REPRESENTATIVE',1)[0];assert'11,194'in idaho and'1,215'in idaho and'245'in idaho
 check('independent_printed_state_vectors_and_national_scope_controls',lambda:True)
 peerqa=None
 if (D/'peer-qa/comparison.json').exists():
  pq=D/'peer-qa';peerqa=load(pq/'comparison.json');assert peerqa['status']=='pass_shared_original_fields_with_explicit_presentation_differences'and not peerqa['unresolved_differences']
  snap=load(pq/'peer-snapshot-manifest.json')
  for r in snap['files']:
   b=(D/r['snapshot']).read_bytes();assert len(b)==r['bytes']and H(b)==r['sha256']
  w=load(pq/'pre-peer-witness.json');b=(D/w['archive']).read_bytes();assert H(b)==w['archive_sha256'];t=tarfile.open(fileobj=io.BytesIO(gzip.decompress(b)))
  for r in w['files']:
   b=t.extractfile(r['path']).read();assert len(b)==r['bytes']and H(b)==r['sha256']
  pre={r['path']:r for r in w['files']}
  for rel in ['data/county-turnout.csv','data/turnout/native-order.csv','data/turnout/native-2024-candidate-positions.csv','data/turnout/historical-candidate-positions.json.gz']:
   assert H((S/rel).read_bytes())==pre[rel]['sha256']
  check('immutable_actual_peer_bodies_and_prepeer_owned_witness_original_data_unchanged',lambda:dict(peer_agent=snap['peer_agent_id'],peer_bodies=len(snap['files']),prepeer_bodies=len(w['files'])))
  peer_map=json.loads(gzip.decompress((pq/'source-position-map.json.gz').read_bytes()));assert len(peer_map)==985
  peerpos=json.loads(gzip.decompress((pq/'peer-snapshot/source/native-units.json.gz').read_bytes()));pu={r['unit_id']:r for r in peerpos if r['contest']=='2024-president'}
  mapped=[]
  for r in peer_map:
   p=pu[r['peer_unit_id']];assert r['source_rows']==p['source_rows']and r['literal_label']==p['label']and r['county']==p['county'];assert r['original_sha256']=='7bb35774f2521b3b75f8bc0c7b188c0cccde2399700841210c67d050e84fc65e'
   mapped.append((sum(x['votes']for x in p['candidates']),r['turnout_source_position_key']))
  mapped.sort(key=lambda r:(-r[0],r[1]));assert [r[1]for r in mapped]==[r['key']for r in a]
  assert [r[0]for r in mapped]==[int(r['candidate_votes'])for r in a]
  assert q['peer_agreement']['comparison_sha256']==H((pq/'comparison.json').read_bytes())and q['peer_agreement']['coordinator_acceptance']is False
  check('independent_peer_counts_reconstruct_all985_canonical_ranks_and_priority_maps',lambda:dict(full_order=985,minimum80=528,remainder=457,parents=44))
  assert len(peerqa['earlier_peer_literal_order_reordered_ranks'])==12 and len(peerqa['method_lexical_flag_differences'])==5
  assert [r['source_row']for r in peerqa['owned_additional_stats2020_admin_headings']]==[1147,1151]
  assert peerqa['null_native_candidate_cells']=={'2020-senate-II':8,'2020-president':42}
  assert peerqa['total_field_checks']==sum(peerqa['comparison_counts'].values())and peerqa['total_field_checks']>=508514
  check('peer_exact_raw_header_null_admin_stat_method_checks_and_explicit_exceptions',lambda:dict(field_comparisons=peerqa['total_field_checks'],unresolved_source_values=0,reordered_tied_ranks=12,method_flag_presentations=5,additional_nonnumeric_heading_objects=2))
 attribution=None
 if (D/'source/2022-writein-scope-disagreement.json').exists():
  attribution=load(D/'source/2022-writein-scope-disagreement.json');proof=load(D/'attribution-history/repair-proof.json');w=load(D/'attribution-history/pre-repair-witness.json');b=(D/w['archive']).read_bytes();assert H(b)==w['archive_sha256'];history=tarfile.open(fileobj=io.BytesIO(gzip.decompress(b)))
  for r in w['files']:
   bb=history.extractfile(r['path']).read();assert len(bb)==r['bytes']and H(bb)==r['sha256']
  for r in proof['byte_identical_existing_objects']:
   bb=(S/r['path']).read_bytes();assert len(bb)==r['bytes']and H(bb)==r['sha256']
  oldcontract=json.loads(history.extractfile('data/turnout/priority-set.json').read());now=json.loads(json.dumps(q));now.pop('source_scope_attribution_review');now['source_object_paths'].pop('writein2022_scope_disagreement');assert now==oldcontract
  assert q['source_scope_attribution_review']['sha256']==H((D/'source/2022-writein-scope-disagreement.json').read_bytes())
  assert ast.dump(ast.parse(history.extractfile('data/turnout/build.py').read()))==ast.dump(ast.parse((D/'build.py').read_text()))
  oldvalidation=json.loads(history.extractfile('data/turnout/validation.json').read());assert oldvalidation['passed']==19 and oldvalidation['failed']==0
  assert attribution['HTML']['stage']is None and attribution['HTML']['header_literal']==['Counties','Lisa Marie','Garth Gaylord','Steve R. Johnson']and attribution['HTML']['grand_total_literal']==['GRAND TOTAL','46','2,753','9,025']
  assert attribution['HTML']['complete_table0_literal']==json.loads(gzip.decompress((D/'source/stats2022-tables.json.gz').read_bytes()))[0]
  assert attribution['general_governor']['votes']==67 and sum(int(r['votes'])for r in attribution['general_governor']['complete44_county_candidate_controls'])==67
  pr=attribution['distinct_primary']['receipt'];pp=S/attribution['distinct_primary']['reused_original_path'];pb=pp.read_bytes();assert len(pb)==pr['stored_bytes']and H(pb)==pr['stored_sha256'];pd=gzip.decompress(pb);assert len(pd)==pr['raw_bytes']and H(pd)==pr['raw_sha256']
  assert attribution['distinct_primary']['candidate_vector']=={'Ryan Cole':22,'David Reilly':21,'Shelby Rognstad':6712}
  assert load(D/'peer-qa/comparison.json')['total_field_checks']==561023
  for r in proof['exact_old_new_claim_changes']:
   bb=(S/r['path']).read_bytes();assert H(bb)==r['new_sha256'];assert r['old']not in bb.decode()and r['new']in bb.decode()
  assert 'unexplained publication/scope disagreement'in(S/'turnout.md').read_text()and'**primary** write-in table'not in(S/'turnout.md').read_text()
  check('narrow_stage_attribution_repair_prior19groups561023_witness_and_all_vote_semantics_unchanged',lambda:dict(byte_identical_prior_objects=proof['byte_identical_existing_count'],all_preexisting_contract_fields_equal=True,build_AST_identical=True,HTML46_stage=None,general67_unchanged=True,distinct_primary_vector_unchanged=True,no_original_duplication=True,old_peer_checks_are_snapshot_scoped=True))
 relcount=0
 for f in [S/'turnout.md',D/'source/SCHEMA.md']:
  for target in re.findall(r'\]\(([^)]+)\)',f.read_text()):
   if re.match(r'[a-z]+://',target)or target.startswith('#'):continue
   target=target.split('#')[0];resolved=(f.parent/target).resolve();assert resolved.exists() or resolved==D/'validation.json',(f,target);relcount+=1
 assets=[S/'turnout.md',D.parent/'county-turnout.csv']+[p for p in D.rglob('*')if p.is_file()];assert all(p.stat().st_size<40000000 for p in assets);assert not[p for p in D.rglob('*')if p.name in ['__pycache__','node_modules','.cache']]
 check('owned_asset_bounds_and_all_report_relative_links',lambda:dict(relative_links=relcount,owned_files=len(assets),maximum_bytes=max(p.stat().st_size for p in assets)))
 out=dict(status='pass_offline_actual_peer_fields_reconciled_coordinator_acceptance_pending'if peerqa else'pass_offline_pending_independent_peer_and_coordinator_acceptance',primary_geography='985 original2024presidential native contexts across44 county parents',checks=checks,passed=len(checks),failed=0,peer_agreement='Actual independent peer original fields and canonical full985/528/457 maps agree after explicit source-position mapping; earlier literal tie-order and lexical/admin object exceptions retained.'if peerqa else'pending actual peer launch/stable files; coordinator preflight is not a peer',coordinator_acceptance=False,known_source_gaps=['Boundary literal method/stat scope and net3 ballot discrepancy unresolved; no allocation','Sparse2020 candidate/stat cells remain null despite known-sum closure','No current approved historical/native/geometry/timezone crosswalk','2026 county LD24 sample is bounded; statewide/later eligible write-in completeness and result choice IDs not established','Native operational candidate-method partition and polling places not supplied']+(['2022 HTML Write-In Totals Lisa Marie46 versus general Lisa Marie(W/I)IND67: publication/scope unexplained, HTML stage unestablished']if attribution else[]),prior_peer_check_scope='561023 original-field comparisons and prior19groups remain dated immutable-snapshot evidence; later final peer bodies are not asserted byte-equal',narrow_attribution_repair_verified=attribution is not None,asset_manifest_verification='Run asset_manifest.py, then validate.py --verify-assets; separate check includes this completed validation file and does not rewrite it.')
 (D/'validation.json').write_text(json.dumps(out,indent=2)+'\n');print(f'PASS {len(checks)} offline check groups; actual peer fields reconciled={peerqa is not None}; coordinator acceptance pending.')
if __name__=='__main__':main()
