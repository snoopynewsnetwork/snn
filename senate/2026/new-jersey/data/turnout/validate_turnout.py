#!/usr/bin/env python3
"""Meaningful network-free NJ source, arithmetic, identity, coverage and artifact QA."""
from pathlib import Path
import json,gzip,csv,re,hashlib,sys,collections
from fractions import Fraction
D=Path(__file__).resolve().parent;E=D/'extract';S=D/'source';STATE=D.parent.parent
failures=[];checks={}
def check(name,value,detail=None):
 checks[name]=bool(value)
 if not value:failures.append({'check':name,'detail':detail})
def read(p):return json.loads(p.read_text())
def zread(p):return json.loads(gzip.decompress(p.read_bytes()))
def sha(b):return hashlib.sha256(b).hexdigest()
def sourceposition(r):
 try:
  text=gzip.decompress((E/(r['source_id']+'.txt.gz')).read_bytes()).decode();line=text.split('\f')[r['page']-1].splitlines()[r['line']-1];return line==r['source_line']
 except Exception:return False

def main():
 m=read(E/'native-rows.json');b=read(E/'ballot-rows.json');bf=read(E/'ballot-footers.json');tc=read(E/'turnout-controls.json');cp=read(E/'state-candidate-controls.json');co=read(D/'priority-set.json');orders=read(D/'all-source-orders.json');sens=read(D/'sensitivity.json')
 primary=m['2024-senate'];check('ranked_rows575_unique_keys',len(primary)==len({r['key'] for r in primary})==575)
 check('municipal564_administrative11',collections.Counter(r['unit_type'] for r in primary)=={'municipality':564,'administrative':11})
 check('all21_counties',len({r['county_fips'] for r in primary})==21 and len(co['county_coverage'])==21)
 check('primary_source_positions',all(sourceposition(r) for rr in m.values() for r in rr))
 check('ballot_source_positions',all(sourceposition(r) for rr in b.values() for r in rr))
 rec=list(csv.DictReader((E/'candidate-reconciliation.csv').open()))
 check('all588_candidate_county_cells_reconcile',len(rec)==588 and all(int(r['difference_from_state'])==0 and int(r['municipal_sum'])==int(r['published_municipal_footer'])==int(r['state_pdf_county_control']) for r in rec))
 check('all_primary_county_vectors_complete',all(len(c['county_cells'])==21 and len({r['county'] for r in c['county_cells']})==21 and c['sum_counties']==c['published_total'] for cc in cp.values() for c in cc))
 totals={'2024-senate':4031795,'2020-senate':4440540,'2018-senate':3169310,'2024-president':4272725}
 check('whole_state_primary_candidate_universes',all(sum(v for r in m[sc] for v in r['values'] if v is not None)==n for sc,n in totals.items()))
 check('literal_sparse_blank_cells_retained',next(r for r in primary if r['county']=='Cape May' and r['unit_type']=='administrative')['values']==[85,16,3,None,None,None])
 check('zero_vote2018_admin_retained',any(r['county']=='Mercer' and r['unit_type']=='administrative' and r['values']==[0]*8 for r in m['2018-senate']))
 ranked=sorted(primary,key=lambda r:(-sum(v for v in r['values'] if v is not None),r['key']));n=sum(sum(v for v in r['values'] if v is not None) for r in ranked);cum=0;k=None
 for i,r in enumerate(ranked,1):
  cum+=sum(v for v in r['values'] if v is not None)
  if k is None and 5*cum>=4*n:k=i
 check('canonical_full_order',co['complete_ordered_keys']==[r['key'] for r in ranked] and co['complete_ordered_keys']==[r['key'] for r in orders['2024-senate']])
 check('exact_top15',sum(sum(v for v in r['values'] if v is not None) for r in ranked[:15])==co['top15']['votes']==631518 and co['top15']['ordered_keys']==[r['key'] for r in ranked[:15]])
 before=sum(sum(v for v in r['values'] if v is not None) for r in ranked[:k-1]);cross=before+sum(v for v in ranked[k-1]['values'] if v is not None)
 check('minimum_integer80',k==233 and before==3224325 and cross==3229453 and 5*before<4*n<=5*cross and co['minimum80']['preceding_votes']==before and co['minimum80']['votes']==cross)
 check('crossing_source_key',co['minimum80']['crossing_key']=='2024-official-general-results-us-senate-monmouth:p0001:l0016' and ranked[k-1]['native_label']=='Asbury Park City')
 check('priority_and_full_remainder',co['ordered_priority_keys']==[r['key'] for r in ranked[:k]] and co['remainder']['ordered_keys']==[r['key'] for r in ranked[k:]] and co['remainder']['count']==342 and co['remainder']['votes']==n-cross==802342)
 check('weights_sum_exactly_one',sum(Fraction(sum(v for v in r['values'] if v is not None),n) for r in ranked)==1)
 check('no_current_identity_or_acceptance_claim',co['coordinator_acceptance']['accepted'] is False and co['independent_peer']['agent_id']=='61054f9e-a14c-44fc-b6b2-7bbc4c84b449' and co['independent_peer']['derivatives_read'] is True and co['independent_peer']['full_future_final_equality_claimed'] is False and all(c['approved_2026_native_or_geometry_crosswalk'] is False for c in co['county_coverage']))
 allorders=True
 for se in sens:
  rr=orders[se['scope']];tot=sum(r['volume'] for r in rr);pre=0
  if len(rr)!=len({r['key'] for r in rr}) or len(rr)!=se['unit_count'] or tot!=se['total'] or rr!=sorted(rr,key=lambda r:(-r['volume'],r['key'])):allorders=False
  for i,r in enumerate(rr,1):
   if r['rank']!=i or r['cumulative_votes']!=pre+r['volume'] or r['share_denominator']!=tot:allorders=False
   pre+=r['volume']
  i=se['minimum80_count'];pv=sum(r['volume'] for r in rr[:i-1]);cv=pv+rr[i-1]['volume']
  if not(5*pv<4*tot<=5*cv) or pv!=se['preceding_votes'] or cv!=se['minimum80_votes']:allorders=False
 check('all10_source_orders_denominators_crossings',len(sens)==10 and allorders)
 ballotok=True;gaps=[]
 for y,rr in b.items():
  if len(bf[y])!=21 or len(tc[y])!=22:ballotok=False
  for f in bf[y]:
   sub=[r for r in rr if r['county']==f['county']];state=next(r for r in tc[y] if r['county']==f['county'])
   for key in ['registered_voters','ballots_cast','vote_by_mail_ballots_cast','provisional_ballots_cast','election_day_provisional_ballots_cast','early_voting_provisional_ballots_cast']:
    if f[key] is not None and sum(r[key] for r in sub if r[key] is not None)!=f[key]:ballotok=False
   for field in ['registered_voters','ballots_cast']:
    if f[field]!=state[field]:gaps.append((y,f['county'],field,f[field]-state[field]))
 check('all_ballot_registration_method_footer_balances',ballotok)
 check('only_known2022_somerset420_gap',gaps==[('2022','Somerset','ballots_cast',420)],gaps)
 dl=read(D/'discrepancy-ledger.json');check('side_by_side_anomaly_positions',all(sourceposition(r) for rr in dl['monmouth_neptune'].values() for r in rr) and all(sourceposition(r) for r in dl['somerset_2022']['municipal_publication_footer']))
 receipts=list(S.glob('*.receipt.json'));sourceok=True;receiptbounds=True
 for p in receipts:
  a=read(p)
  if not a.get('raw_sha256'):continue
  path=S/a.get('reference_path',a.get('asset'));z=path.read_bytes();raw=gzip.decompress(z)
  if sha(z)!=a['stored_sha256'] or sha(raw)!=a['raw_sha256']:sourceok=False
  if len(z)>=40000000:receiptbounds=False
  if a.get('stored_bytes') is not None and a['stored_bytes']!=len(z):sourceok=False
  if a.get('raw_bytes') is not None and a['raw_bytes']!=len(raw):sourceok=False
 check('all_individual_original_raw_stored_hashes_sizes',sourceok and receiptbounds)
 cl=read(S/'clerk-2020-reference.json');cb=(S/cl['reference_path']).read_bytes();check('independent_clerk_reference_and_vintage_gap',sha(cb)==cl['raw_sha256'] and len(cb)==cl['raw_bytes'] and cl['candidate_controls']=={'Cory Booker':2541178,'Rikin Mehta':1817052})
 be=zread(E/'bergen-senate-native-rows.json.gz');check('bergen_all3250_positions706_totals_suppression',len(be)==3250 and len([r for r in be if r['method']=='Total'])==706 and len({r['native_label'] for r in be if r['method']=='Total'})==706 and sum(any(v=='***' for v in r['candidates'].values()) for r in be)==7 and not any(r['unassigned_words'] for r in be))
 sa=zread(E/'salem-required-native-dom.json.gz');check('salem_native43senate43president_uniqueids',len(sa)==86 and len([r for r in sa if r['native_contest_id']=='2'])==43 and len({r['key'] for r in sa})==86 and all(len(r['rows'])==len({x['native_candidate_key'] for x in r['rows']}) for r in sa))
 mo=zread(E/'morris-required-worksheets.json.gz');check('morris_original2sheets_native_positions_protected',len(mo)==2 and all(len(sh['rows'])==405 for sh in mo) and any(v=='protected' for sh in mo for r in sh['rows'] for v in r['cells'].values()))
 pages=zread(E/'county-required-literal-pages.json.gz');pageok=True
 for p in pages:
  tx=gzip.decompress((E/(p['source_id']+'.txt.gz')).read_bytes()).decode().split('\f')[p['page']-1].splitlines()
  if any(tx[r['line']-1]!=r['literal'] for r in p['lines']):pageok=False
 check('all1240_native_pdf_page_positions_lossless',len(pages)==1240 and pageok)
 check('all21_county_chains_and6finer_originals',len(read(D/'county-chains.json'))==21 and sum(bool(c['finer_original_source_ids']) for c in co['county_coverage'])==6)
 csvrows=list(csv.DictReader((D.parent/'county-turnout.csv').open()));check('compatibility_csv575_source_rows_no_county_substitution',len(csvrows)==575 and [r['key'] for r in csvrows]==[r['key'] for r in ranked] and sum(int(r['contest_votes']) for r in csvrows)==n and all(r['unit_type']!='county' for r in csvrows))
 owned=[STATE/'turnout.md',D.parent/'county-turnout.csv']+[p for p in D.rglob('*') if p.is_file()]
 check('all_owned_assets_strictly_below40million',all(p.stat().st_size<40000000 for p in owned))
 check('no_dependency_or_cache_directories',not any(p.name in ['__pycache__','node_modules','.venv','venv'] for p in D.rglob('*')))
 badlinks=[]
 for p in [STATE/'turnout.md',S/'SCHEMA.md']:
  for href in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   href=href.strip('<>')
   if re.match(r'https?://|#',href):continue
   target=(p.parent/href.split('#',1)[0]).resolve()
   if not target.exists():badlinks.append((str(p),href))
 check('all_report_schema_relative_links_exist',not badlinks,badlinks)
 mf=D/'asset-manifest.json'
 if mf.exists():
  manifest=read(mf);manifestok=True;listed=set()
  for a in manifest['assets']:
   p=STATE/a['path'];listed.add(p.resolve())
   if not p.is_file() or p.stat().st_size!=a['bytes'] or sha(p.read_bytes())!=a['sha256']:manifestok=False
  actual={p.resolve() for p in owned if p!=mf}
  check('complete_owned_asset_manifest_hashes_sizes',manifestok and listed==actual)
 else:check('complete_owned_asset_manifest_hashes_sizes',False,'Manifest must be generated, then this validator rerun.')
 wf=D/'pre-peer-witness.json'
 if wf.exists():
  w=read(wf);frozenok=w['peer_derivatives_read'] is False
  for a in w['frozen_bodies']:
   p=STATE/a['frozen_path'];z=p.read_bytes();raw=gzip.decompress(z)
   if sha(z)!=a['stored_sha256'] or len(z)!=a['stored_bytes'] or sha(raw)!=a['original_sha256'] or len(raw)!=a['original_bytes']:frozenok=False
  for a in w['original_pins']:
   p=STATE/a['path']
   if sha(p.read_bytes())!=a['sha256'] or p.stat().st_size!=a['bytes']:frozenok=False
  check('immutable_pre_peer_bodies_original_pins',frozenok)
 else:check('immutable_pre_peer_bodies_original_pins',False,'Pre-peer witness must be frozen before final QA.')

 rr=D/'reciprocal-review';review=read(rr/'comparison.json')
 check('bounded_actual_peer_core_and_reverse_zero_differences',review['status']=='pass_bounded_fixed_core_reciprocal' and not review['differences'] and review['checks']==82206 and review['reverse_peer_fixed_core_result']['failed']==0 and review['reverse_peer_fixed_core_result']['checks']==40921 and sha((rr/'comparison.json').read_bytes())==co['independent_peer']['comparison_sha256'])
 captureok=True
 for name in ['pre-reciprocal-capture.json','peer-capture.json','peer-return-capture.json']:
  capture=read(rr/name)
  for a in capture['records']:
   if not a.get('capture_path'):continue
   z=(STATE/a['capture_path']).read_bytes();raw=gzip.decompress(z)
   if sha(z)!=a['stored_sha256'] or len(z)!=a['stored_bytes'] or sha(raw)!=a['sha256'] or len(raw)!=a['bytes']:captureok=False
 check('all_pre_reciprocal_and_peer_capture_bodies_hashes_sizes',captureok)
 allowed={'turnout.md','data/turnout/source/SCHEMA.md','data/turnout/build_package.py','data/turnout/validate_turnout.py','data/turnout/reproducibility.json','data/turnout/asset-manifest.json','data/turnout/priority-set.json','data/turnout/validation.json'}
 prior=read(rr/'pre-reciprocal-capture.json');unexpected=[]
 for a in prior['records']:
  p=STATE/a['path']
  if a['path'] not in allowed and (not p.is_file() or sha(p.read_bytes())!=a['sha256'] or p.stat().st_size!=a['bytes']):unexpected.append(a['path'])
 check('all_prior_count_csv_source_order_native_objects_byte_equal',not unexpected,unexpected)
 oldrec=next(a for a in prior['records'] if a['path']=='data/turnout/priority-set.json');oldcontract=json.loads(gzip.decompress((STATE/oldrec['capture_path']).read_bytes()));newcontract=dict(co)
 for metadata in ['status','independent_peer']:
  oldcontract.pop(metadata);newcontract.pop(metadata)
 oldcontract['unresolved']=oldcontract['unresolved'][:3];newcontract['unresolved']=newcontract['unresolved'][:3]
 check('contract_changes_only_explicit_peer_review_metadata',oldcontract==newcontract)
 check('original_witness_digest_preserved',sha((D/'pre-peer-witness.json').read_bytes())=='7e26b6b14d5f881af05800aec84beaa4f38abbeb40b034dad1b49e2a061454f1')
 check('negative_corruption_and_integer_hash_size_fixtures',review['categories']['negative_fixture_rejected']==15)
 fs=D/'final-seal.json'
 sealok=fs.exists()
 if sealok:
  seal=read(fs);sealok=not any(seal['acceptance'].values()) and 'manifest_sha256' not in seal and 'validation_sha256' not in seal
  for a in seal['pins']:
   p=STATE/a['path']
   if not p.is_file() or sha(p.read_bytes())!=a['sha256'] or p.stat().st_size!=a['bytes']:sealok=False
 check('final_seal_hash_pins_false_approvals_no_reverse_digest_cycle',sealok)
 result={'status':'pass_bounded_actual_peer_reciprocal_with_explicit_limits' if not failures else 'incomplete_sealing_or_failed_checks','checks':checks,'failures':failures,'verified_primary_scope':{'counties':21,'2024_senate_source_rows':575,'municipal':564,'administrative':11,'votes':4031795,'top15_votes':631518,'minimum80_count':233,'minimum80_votes':3229453,'preceding_count':232,'preceding_votes':3224325,'remainder_count':342,'remainder_votes':802342},'intentional_limits':['Only captured completed original-first peer core agrees in both directions; later peer final outputs outside claim, coordinator acceptance false.','Six-candidate SOS reported universe; no verified statewide generic/named/eligible writein or under/over tally.','Finer originals recovered for6counties; complete native physical/current legal hierarchy not approved.','Native suppressed/wrapped source fields preserve null/stars/protected and partial specialized PDF extraction; no forced county reconciliation.','Literal Neptune anomaly and Somerset2022+420 source vintage difference remain unallocated.']}
 # A second manifest build after this write pins the deterministic final QA body; final rerun must leave it identical.
 (D/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'passed':sum(checks.values()),'checks':len(checks),'failures':failures},indent=2))
 return 0 if not failures else 1
if __name__=='__main__':sys.exit(main())
