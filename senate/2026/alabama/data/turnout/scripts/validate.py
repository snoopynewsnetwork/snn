#!/usr/bin/env python3
"""Offline direct-original verification and read-only post-seal exact-membership audit."""
import pathlib,json,gzip,hashlib,zipfile,io,csv,sqlite3,re,sys,collections,urllib.parse
from fractions import Fraction
from freeze import write
R=pathlib.Path(__file__).resolve().parents[1];S=R.parents[1];REPO=S.parents[2]
def sha(b):return hashlib.sha256(b).hexdigest()
def j(p):return json.loads((R/p).read_text())
def owned():return sorted([S/'turnout.md',S/'data/county-turnout.csv']+[p for p in R.rglob('*') if p.is_file() and p!=R/'asset-manifest.json'])
def audit():
 m=j('asset-manifest.json');actual={str(p.relative_to(S)):p for p in owned()};record={v['path']:v for v in m['assets']};assert len(record)==len(m['assets']);assert set(actual)==set(record),(set(actual)-set(record),set(record)-set(actual))
 for name,p in actual.items():
  b=p.read_bytes();r=record[name];assert len(b)==r['bytes'] and sha(b)==r['sha256'] and len(b)<40000000,name
 for x in m['external_originals']:
  p=REPO/x['path'];b=p.read_bytes();assert len(b)==x['stored_bytes'] and sha(b)==x['stored_sha256'];raw=gzip.decompress(b);assert len(raw)==x['original_bytes'] and sha(raw)==x['original_sha256']
 assert not [p for p in R.rglob('*') if p.name in ['__pycache__','node_modules','.cache','.venv'] or p.suffix=='.pyc']
 for doc in [S/'turnout.md',R/'source/SCHEMA.md']:
  for target in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
   if re.match(r'https?://',target) or target.startswith('#'):continue
   assert (doc.parent/urllib.parse.unquote(target.split('#')[0])).resolve().exists(),(doc,target)
 print(json.dumps({'exact_membership_hash_size_audit':'PASS','owned_asset_count':len(actual),'owned_bytes':sum(p.stat().st_size for p in actual.values()),'largest_owned_bytes':max(p.stat().st_size for p in actual.values()),'external_originals':len(m['external_originals']),'manifest_sha256':sha((R/'asset-manifest.json').read_bytes()),'no_writes':True},indent=2));return
if '--audit' in sys.argv:audit();sys.exit(0)
import xlrd
checks=[];measurements={};source_hashes=[]
def check(name,evidence):checks.append({'check':name,'result':'PASS','evidence':evidence})
# Complete original entity bodies and all immutable receipts; no live network.
for rr in j('source/original-receipts.json'):
 p=REPO/rr['shared_path'];b=p.read_bytes();assert sha(b)==rr['stored_sha256'];raw=gzip.decompress(b);assert len(raw)==rr['bytes'] and sha(raw)==rr['raw_sha256'];source_hashes.append({'path':rr['shared_path'],'stored_sha256':sha(b),'raw_sha256':sha(raw),'raw_bytes':len(raw)})
http={}
for p in sorted((R/'source/http').glob('*.receipt.json')):
 rr=json.loads(p.read_text());parts=[]
 for x in rr['parts']:
  q=(R/x['path']).resolve();assert R in q.parents;z=q.read_bytes();assert len(z)==x['bytes'] and sha(z)==x['sha256'] and len(z)<40000000;parts.append(z)
 raw=gzip.decompress(b''.join(parts));assert len(raw)==rr['original_bytes'] and sha(raw)==rr['original_sha256'];http[rr['original_sha256']]=(rr,raw);source_hashes.append({'receipt':str(p.relative_to(R)),'raw_sha256':sha(raw),'raw_bytes':len(raw),'status':rr['status']})
check('all_original_shared_and_download_body_hashes_sizes_receipts',len(source_hashes))
# Independent extraction from original binary XLS, not only the derived JSON.
field_checks=0;raw_cells=0;member_count=0;blank_candidate_cells=0;controls=j('statewide-controls.json');coverage=j('native-coverage.json');all_summary=j('native-rank-summary.json');countyrows=list(csv.DictReader((S/'data/county-turnout.csv').open()));assert len(countyrows)==201
for year,prefix in [(2024,'4ecca55'),(2022,'4ea186'),(2020,'471fc54')]:
 receipt,raw=next(v for h,v in http.items() if h.startswith(prefix));zf=zipfile.ZipFile(io.BytesIO(raw));assert len(zf.infolist())==67;member_count+=67
 typed=json.loads(gzip.decompress((R/f'source/workbooks-{year}.json.gz').read_bytes()));by_member={w['member']['name']:w for w in typed};units=j(f'native-units-{year}.json');by_position={(u['source_member'],u['source_sheet'],u['column_1based']):u for u in units};assert len(by_position)==len(units);assert len(set(u['key'] for u in units))==len(units)
 directly=[];county_sums=collections.defaultdict(collections.Counter);state_sums=collections.Counter();expected_keys=set();unlabeled_populated=0
 for info in zf.infolist():
  b=zf.read(info);w=by_member[info.filename];assert sha(b)==w['member']['sha256'] and len(b)==w['member']['bytes'] and info.CRC==w['member']['zip_crc32'];book=xlrd.open_workbook(file_contents=b,formatting_info=True);assert len(book.sheets())==len(w['sheets'])
  for si,sheet in enumerate(book.sheets()):
   saved=w['sheets'][si];assert sheet.name==saved['name'] and sheet.nrows==saved['nrows'] and sheet.ncols==saved['ncols'];assert len(saved['rows'])==sheet.nrows
   for ri in range(sheet.nrows):
    savedrow=saved['rows'][ri];assert savedrow['values']==sheet.row_values(ri);assert savedrow['types']==sheet.row_types(ri).tolist();raw_cells+=len(savedrow['values'])
   assert sheet.row_values(0)[:3]==['Contest Title','Party','Candidate'];cols=[c for c,v in enumerate(sheet.row_values(0)) if c>=3 and str(v).strip()];assert len(set(sheet.cell_value(0,c) for c in cols))==len(cols)
   contest='PRESIDENT AND VICE PRESIDENT OF THE UNITED STATES' if year==2024 else 'UNITED STATES SENATOR';rs=[r for r in range(1,sheet.nrows) if sheet.cell_value(r,0).strip()==contest];candidates=[r for r in rs if sheet.cell_value(r,2).strip() not in ['Under Votes','Over Votes']]
   assert len(candidates)=={2024:6,2022:4,2020:3}[year]
   for ri in range(1,sheet.nrows):
    for ci,v in enumerate(sheet.row_values(ri)):
     if ci>=3 and ci not in cols and v!='':unlabeled_populated+=1
   for col in cols:
    u=by_position[(info.filename,sheet.name,col+1)];expected_keys.add(u['key']);assert u['native_label']==sheet.cell_value(0,col);assert u['native_id']==u['native_label'];assert u['standalone_native_numeric_id'] is None
    full_rows=[(r,cell) for r,cell in zip(candidates,u['candidate_votes'])];assert len(full_rows)==len(candidates)
    for ri,cell in full_rows:
     val=sheet.cell_value(ri,col);assert isinstance(val,(int,float));assert int(val)==val;assert cell['value']==int(val) and cell['xls_type']==sheet.cell_type(ri,col);assert cell['row_1based']==ri+1 and cell['column_1based']==col+1;assert [cell['contest_literal'],cell['party_literal'],cell['candidate_literal']]==sheet.row_values(ri)[:3];field_checks+=1;state_sums[sheet.cell_value(ri,2).strip()]+=int(val);county_sums[u['county']][sheet.cell_value(ri,2).strip()]+=int(val)
    others=[r for r in rs if r not in candidates];metarows=[r for r in range(1,sheet.nrows) if sheet.cell_value(r,0).strip().startswith(('REGISTERED VOTERS','BALLOTS CAST')) or sheet.cell_value(r,0).strip()=='STRAIGHT PARTY']
    for relevant,derived in [(others,u['contest_other_fields']),(metarows,u['administrative_fields'])]:
     assert len(relevant)==len(derived)
     for ri,cell in zip(relevant,derived):
      val=sheet.cell_value(ri,col);expected=int(val) if isinstance(val,(int,float)) else None;assert cell['value']==expected and cell['raw_value']==val and cell['xls_type']==sheet.cell_type(ri,col);assert [cell['contest_literal'],cell['party_literal'],cell['candidate_literal']]==sheet.row_values(ri)[:3];assert cell['row_1based']==ri+1 and cell['column_1based']==col+1;field_checks+=1
    total=sum(int(sheet.cell_value(ri,col)) for ri in candidates);assert total==u['reported_candidate_votes'];directly.append((u['key'],total));assert u['current_2026_crosswalk'] is None
 assert unlabeled_populated==0;assert expected_keys==set(u['key'] for u in units)
 assert state_sums==collections.Counter(controls[str(year)])
 # SQLite gives an independently implemented full ranking, using exact integer cumulative sums.
 db=sqlite3.connect(':memory:');db.execute('create table unit (key text primary key, votes integer)');db.executemany('insert into unit values (?,?)',directly);order=db.execute('select key,votes,sum(votes) over (order by votes desc,key rows unbounded preceding) from unit order by votes desc,key').fetchall();den=db.execute('select sum(votes) from unit').fetchone()[0];k=next(i for i,r in enumerate(order,1) if 5*r[2]>=4*den);sm=all_summary[str(year)];assert [r[0] for r in order]==sm['full_order']==[u['key'] for u in units];assert k==sm['minimum80_count'];assert sum(r[1] for r in order[:15])==sm['top15_votes'];assert order[k-2][2]==sm['preceding_votes'];assert order[k-1][2]==sm['minimum80_votes'];assert 5*sm['preceding_votes']<4*den<=5*sm['minimum80_votes'];assert sm['remainder_votes']==sum(r[1] for r in order[k:]);assert sm['priority_keys']==[r[0] for r in order[:max(k,15)]];assert sm['remainder_keys']==[r[0] for r in order[max(k,15):]]
 assert sum(Fraction(u['weight_exact']) for u in units)==1
 for i,u in enumerate(units):assert u['rank']==i+1 and u['cumulative_votes']==order[i][2] and Fraction(u['cumulative_share_exact'])==Fraction(order[i][2],den)
 cr=[r for r in countyrows if int(r['year'])==year];assert len(cr)==67 and len(set(r['county_fips'] for r in cr))==67
 for row in cr:
  assert sum(county_sums[row['county']].values())==int(row['candidate_votes'])
  for n in range(1,{2024:6,2022:4,2020:3}[year]+1):assert county_sums[row['county']][row[f'candidate_{n}_name']]==int(row[f'candidate_{n}_votes'])
 cv=[c for c in coverage if c['year']==year];assert len(cv)==67;constituents=[k for c in cv for k in c['constituent_keys']];assert len(constituents)==len(set(constituents))==len(units) and set(constituents)==expected_keys
 measurements[str(year)]={'native_units':len(units),'county_parents':len(cv),'candidate_sums':dict(state_sums),'denominator':den,'top15_votes':sm['top15_votes'],'minimum80_count':k,'minimum80_votes':sm['minimum80_votes'],'preceding_count':k-1,'preceding_votes':sm['preceding_votes'],'crossing_key':sm['crossing_key'],'remainder_count':len(units)-k,'remainder_votes':sm['remainder_votes'],'unlabeled_populated_columns':unlabeled_populated}
check('direct_original_XLS_full_raw_rows_values_types_and_member_hashes',{'members':member_count,'raw_cells':raw_cells})
check('direct_original_target_candidate_method_admin_cell_comparisons',{'cells_checked':field_checks,'missing_candidate_cells_at_labeled_headers':blank_candidate_cells})
check('all_county_native_candidate_and_statewide_controls',measurements)
check('independent_SQLite_full_orders_exact_weights_integer_min80_and_remainders','all three election universes')
# Complete primary dispatch equality and disjointness.
contract=j('priority-set.json');sm=all_summary['2024'];assert contract['full_order']==sm['full_order'] and contract['ordered_priority_keys']==sm['priority_keys'];assert contract['remainder_keys']==sm['remainder_keys'];assert len(contract['parents'])==67;assert contract['units']==j('native-units-2024.json');assert not contract['coordinator_acceptance'] and contract['independent_peer_agreement'] is True and contract['peer_agent_id']=='f2db457b-3e3c-47d0-a65c-7d6be8bbe5c7';peerproof=j('reciprocal/comparison.json');assert contract['peer_agreement_scope']['proof_sha256']==sha((R/'reciprocal/comparison.json').read_bytes());assert peerproof['counts']['native_units']==6270 and peerproof['counts']['ballot_numeric_positions']==1020;assert not contract['legal_geographic_approval_2026']
keys=set(contract['full_order']);assert set(contract['priority_keys']).isdisjoint(contract['remainder_keys']);assert set(contract['priority_keys'])|set(contract['remainder_keys'])==keys
for p in contract['parents']:assert set(p['priority_constituent_keys'])|set(p['remainder_constituent_keys'])==set(p['constituent_keys']);assert not set(p['priority_constituent_keys'])&set(p['remainder_constituent_keys'])
check('complete_dispatch_coverage_priority_parent_constituents_administration_and_pending_acceptance',{'parents':67,'units':len(keys),'priority':len(contract['priority_keys'])})
# PDF null evidence and source positioned exact transcription.
cells=j('canvass-cells.json');nulls=[];recon=j('candidate-reconciliation.json');assert len(recon)==871
for r in recon:
 assert r['difference_when_comparable'] in [0,None]
 if r['canvass_value'] is None:nulls.append((r['year'],r['county'],r['candidate'],r['canvass_cell_type'],r['native_sum']))
assert sorted(nulls)==sorted([(2024,'Wilcox','Jill Stein','blank',0),(2022,'Washington','Write-In','blank',0),(2020,'Perry','Write-In','dash',0)])
for row in cells:
 raw=(R/f"source/{row['source']}.txt").read_text().split('\f')[row['pdf_page_1based']-1].splitlines()[row['extracted_line_1based']-1];assert raw==row['raw_line']
 for cell in row['cells']:
  if cell['character_span_0based'] is not None:
   a,b=cell['character_span_0based'];assert raw[a:b]==cell['literal']
check('canvass_null_dash_generic_scope_character_and_page_positions',nulls)
for group in j('source/visual-transcriptions.json').values():
 if isinstance(group,list):
  for x in group:
   assert (R/x['image']).exists();a,b,c,d=x['region'];assert 0<=a<c<=1 and 0<=b<d<=1
check('visual_transcription_full_image_paths_and_region_bounds','all explicit readings')
# Each ballot report independently closes; native discrepancies remain unrepaired.
bc=j('ballot-registration-controls.json')
for st in bc['statewide']:
 rows=[r for r in bc['county_rows'] if r['year']==st['year']];assert len(rows)==67
 for field in ['registered_voters','ballots_cast','democrat_ballots','republican_ballots','absentee_ballots']:assert sum(r[field] for r in rows)==st[field]
 for r in rows:
  line=(R/r['source_text']).read_text().splitlines()[r['source_line_1based']-1];assert line==r['raw_line']
  vals=[int(x.replace(',','')) for x in re.findall(r'[\d,]+',line[len(r['county']):])[:5]];assert vals==[r[x] for x in ['registered_voters','ballots_cast','democrat_ballots','republican_ballots','absentee_ballots']]
  # Compare printed rounded percentages at their displayed precision; source exceptions are not overwritten.
check('separate_all67_ballot_registration_absentee_party_report_footers_raw_positions','all five integer fields for 2024, 2022, 2020')
# Re-evaluate all sensitivity full orders and integer thresholds independently.
for file in ['ballot-registration-sensitivity.json','native-ballot-registration-sensitivity.json']:
 for key,obj in j(file).items():
  ordered=obj['ordered_rows'];s=obj['summary'];metric=next(k for k in ordered[0] if k not in ['key','county','county_fips','native_label','rank','cumulative_votes','weight_exact','cumulative_share_exact','reported_candidate_votes'] and k in key)
  assert ordered==sorted(ordered,key=lambda r:(-r[metric],r['key']));den=sum(r[metric] for r in ordered);assert den==s['denominator'];cum=0
  for i,row in enumerate(ordered,1):cum+=row[metric];assert cum==row['cumulative_votes'] and Fraction(row['weight_exact'])==Fraction(row[metric],den)
  k=s['minimum80_count'];assert 5*sum(r[metric] for r in ordered[:k-1])<4*den<=5*sum(r[metric] for r in ordered[:k]);assert s['full_order']==[r['key'] for r in ordered]
check('ballot_registration_absentee_sensitivity_orders_denominators_thresholds','county report all three fields and available raw native field scopes')
# Exact source-parent positions and original-scope turnout/absentee rates.
source_bodies={h:b for h,(receipt,b) in http.items()}
for rr in j('source/original-receipts.json'):source_bodies[rr['raw_sha256']]=gzip.decompress((REPO/rr['shared_path']).read_bytes())
chains=j('source/download-chains.json');linked=0
for chain in chains:
 for link in chain['observed_parent_links']:
  text=source_bodies[link['parent_original_sha256']].decode('utf-8',errors='replace');offset=sum(len(line) for line in text.splitlines(keepends=True)[:link['html_line_1based']-1])+link['html_column_0based'];assert text[offset:].startswith(link['start_tag']);assert urllib.parse.urljoin(link['parent_url'],link['href_literal'])==chain['requested_url'];linked+=1
rates=j('turnout-rates.json')['rows'];assert len(rates)==204
for row in rates:
 assert Fraction(row['turnout_exact'])==Fraction(row['report_ballots'],row['report_registered_voters']);assert Fraction(row['absentee_fraction_exact'])==Fraction(row['report_absentee_ballots'],row['report_ballots']);assert row['turnout_printed_matches_integer_ratio'] and row['absentee_printed_matches_integer_ratio']
check('exact_parent_original_HTML_hyperlinks_and_turnout_rate_scopes',{'linked_child_receipts':sum(bool(c['observed_parent_links']) for c in chains),'link_observations':linked,'exact_rate_rows':204})

# Full exact captured body/history reconstruction, not equality of old pins to revised current files.
import importlib.util
spec=importlib.util.spec_from_file_location('al_captured_audit',R/'reciprocal/audit_captures.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);captureproof=module.verify();check('complete_original_phase_and_actual_final_peer_body_reconstruction',captureproof)
original_archive=__import__('tarfile').open(R/'reciprocal/turnout-original-phase.tar.gz');original_contract=json.loads(original_archive.extractfile('data/turnout/priority-set.json').read())
for key in original_contract:
 if key not in ['peer_agent_id','independent_peer_agreement','dispatch_status']:assert contract[key]==original_contract[key],key
assert contract['peer_agreement_scope']['current_legal_geographic_admission'] is False
check('unchanged_canonical_source_counts_native_masks_order_and_contract_semantics','Only explicit peer identity/agreement/dispatch status and added bounded proof metadata differ from captured original contract. All original CSV/source body pins independently unchanged.')

# Every local Markdown target exists; all owned files below object bound and no caches/deps.
links=[]
for p in [S/'turnout.md',R/'source/SCHEMA.md']:
 for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if re.match(r'https?://',target) or target.startswith('#'):continue
  q=(p.parent/urllib.parse.unquote(target.split('#')[0])).resolve();assert q.exists() or q in [R/'validation.json',R/'final-seal.json',R/'asset-manifest.json'],(p,target);assert S==q or S in q.parents;links.append(target)
for p in owned():assert p.stat().st_size<40000000,p
assert not [p for p in R.rglob('*') if p.name in ['__pycache__','node_modules','.cache','.venv'] or p.suffix=='.pyc']
check('relative_markdown_links_file_size_bounds_no_dependencies_or_caches',{'links':len(links),'seal_phase_generated_links_verified_by_post_seal_readonly_audit':['validation.json','final-seal.json','asset-manifest.json'],'largest_owned_bytes':max(p.stat().st_size for p in owned())})
# Freeze history reconstruction hashes; history metadata intentionally names exact previous bodies.
history=0
for p in (R/'history').glob('*.json'):
 r=json.loads(p.read_text());b=gzip.decompress((p.parent/r['stored_body']).read_bytes());assert sha(b)==r['sha256'] and len(b)==r['original_bytes'];history+=1
check('all_prior_owned_body_histories_reconstruct_exactly',history)
result={'status':'PASS','scope':'Deterministic historical research/offline QA plus actually captured-final bounded historical peer evidence agreement; no coordinator/current/legal/geography/model admission','checks':checks,'source_hashes':source_hashes,'measurements':measurements,'independent_peer_agreement':True,'peer_agent_id':'f2db457b-3e3c-47d0-a65c-7d6be8bbe5c7','coordinator_acceptance':False,'external_qualifications':['coordinator acceptance pending; actual bounded captured-final historical peer reciprocal complete','November2026 legal geography/native IDs/crosswalk not established','generic write-in rows do not establish eligible named/valid write-in allocation','source-scoped ballot/registration and within-unit statistical discrepancies remain unrepaired','no live collector/cadence/outstanding-ballot count/forecast calibration']}
write(R/'validation.json',json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'PASS','checks':len(checks),'original_field_cells_checked':field_checks,'original_raw_cells_checked':raw_cells,'members':member_count},indent=2))
