#!/usr/bin/env python3
"""Actual corruption fixtures against direct fixed XLS originals and reconstructed historical contracts."""
import pathlib,tarfile,json,gzip,hashlib,io,zipfile,collections,copy,urllib.parse
import xlrd
R=pathlib.Path(__file__).resolve().parents[1];D=R/'reciprocal';F=D/'fixtures';F.mkdir(exist_ok=True)
def sha(b):return hashlib.sha256(b).hexdigest()
t=tarfile.open(D/'turnout-original-phase.tar.gz')
def raw(p):return t.extractfile('data/turnout/'+p).read()
def j(p):
 b=raw(p);return json.loads(gzip.decompress(b) if p.endswith('.gz') else b)
receipts=[json.loads(t.extractfile(n).read()) for n in t.getnames() if n.startswith('data/turnout/source/http/') and n.endswith('.receipt.json')];byhash={r['original_sha256']:r for r in receipts}
source_truth={};body_companion={};member_counts=0
fips=j('source/county-fips.json')['mapping']
for year,prefix in [(2024,'4ecca55'),(2022,'4ea186'),(2020,'471fc54')]:
 rec=next(r for h,r in byhash.items() if h.startswith(prefix));parts=[raw(x['path']) for x in rec['parts']]
 for b,x in zip(parts,rec['parts']):assert sha(b)==x['sha256'] and len(b)==x['bytes']
 body=gzip.decompress(b''.join(parts));assert sha(body)==rec['original_sha256'] and len(body)==rec['original_bytes'];body_companion[year]=rec
 zf=zipfile.ZipFile(io.BytesIO(body));assert len(zf.infolist())==67
 for info in zf.infolist():
  b=zf.read(info);book=xlrd.open_workbook(file_contents=b,formatting_info=True);county=info.filename.split('-General-')[1].removesuffix('.xls');county={'StClair':'St. Clair'}.get(county,county);cf=fips[county]
  for s in book.sheets():
   contest='PRESIDENT AND VICE PRESIDENT OF THE UNITED STATES' if year==2024 else 'UNITED STATES SENATOR';selected=[r for r in range(1,s.nrows) if s.cell_value(r,0).strip()==contest];candidate=[r for r in selected if s.cell_value(r,2).strip() not in ['Under Votes','Over Votes']];admin=[r for r in range(1,s.nrows) if s.cell_value(r,0).strip().startswith(('REGISTERED VOTERS','BALLOTS CAST')) or s.cell_value(r,0).strip()=='STRAIGHT PARTY'];others=[r for r in selected if r not in candidate]
   for col in [c for c in range(3,s.ncols) if str(s.cell_value(0,c)).strip()]:
    label=s.cell_value(0,col);key=f'AL:{year}:general:{cf}:col{col+1:03}:'+urllib.parse.quote(label,safe='')
    def rows(rs):return [{'row_1based':ri+1,'column_1based':col+1,'contest_literal':s.cell_value(ri,0),'party_literal':s.cell_value(ri,1),'candidate_literal':s.cell_value(ri,2),'xls_type':s.cell_type(ri,col),'raw_value':s.cell_value(ri,col),'value':int(s.cell_value(ri,col)) if isinstance(s.cell_value(ri,col),(int,float)) else None} for ri in rs]
    source_truth[key]={'year':year,'county':county,'county_fips':cf,'native_label':label,'native_id':label,'source_member':info.filename,'member_sha256':sha(b),'source_sheet':s.name,'column_1based':col+1,'candidate_votes':rows(candidate),'administrative_fields':rows(admin),'contest_other_fields':rows(others)}
  member_counts+=1
assert member_counts==201 and len(source_truth)==6270
base={'units':{str(y):j(f'native-units-{y}.json') for y in [2024,2022,2020]},'contract':j('priority-set.json'),'summaries':j('native-rank-summary.json'),'canvass':j('canvass-cells.json'),'receipts':{str(y):r for y,r in body_companion.items()}}
source_fields=['row_1based','column_1based','contest_literal','party_literal','candidate_literal','xls_type','raw_value','value'];id_fields=['year','county','county_fips','native_label','native_id','source_member','member_sha256','source_sheet','column_1based']
class Reject(Exception):pass
def require(ok,rule):
 if not ok:raise Reject(rule)
def validate(b):
 global counted
 counted=0;allkeys=[]
 for y,us in b['units'].items():
  expected={k:v for k,v in source_truth.items() if str(v['year'])==y};keys=[u['key'] for u in us];require(len(keys)==len(set(keys)) and set(keys)==set(expected),'native_universe_uniqueness_coverage')
  for u in us:
   tr=expected[u['key']];require(all(u.get(k)==tr[k] for k in id_fields),'literal_header_native_identity_member_source_position')
   for field in ['candidate_votes','administrative_fields','contest_other_fields']:
    require(len(u.get(field,[]))==len(tr[field]),'missing_candidate_or_admin_source_row')
    for c,tc in zip(u[field],tr[field]):require(all(k in c and c[k]==tc[k] for k in source_fields),'source_candidate_admin_party_type_null_value_companion');counted+=len(source_fields)
   require(u['reported_candidate_votes']==sum(c['value'] for c in tr['candidate_votes']),'source_candidate_total_residual_allocation')
   require(u['current_2026_crosswalk'] is None and u['standalone_native_numeric_id'] is None and u['named_valid_writein_allocation'] is None,'unestablished_current_crosswalk_id_writein_admission')
   def get(field,name):return next((c['value'] for c in tr[field] if c['candidate_literal'].strip()==name),None)
   for out,field,label in [('ballots_cast_source','administrative_fields','Ballots Cast - Total'),('blank_ballots_source','administrative_fields','Ballots Cast - Blank'),('registration_source','administrative_fields','Registered Voters - Total'),('under_votes_source','contest_other_fields','Under Votes'),('over_votes_source','contest_other_fields','Over Votes')]:require(out in u and u[out]==get(field,label),'separate_source_field_missing_null_or_value')
  truth_order=sorted(expected,key=lambda k:(-sum(c['value'] for c in expected[k]['candidate_votes']),k));require(keys==truth_order,'descending_full_order');den=sum(u['reported_candidate_votes'] for u in us);cum=0
  for rank,u in enumerate(us,1):cum+=u['reported_candidate_votes'];require((u['rank'],u['cumulative_votes'])==(rank,cum),'rank_cumulative_integer_control')
  sm=b['summaries'][y];k=next(i for i,u in enumerate(us,1) if 5*u['cumulative_votes']>=4*den)
  require(sm['full_order']==keys and sm['denominator']==den and sm['minimum80_count']==k,'minimum80_full_order_denominator')
  require(sm['minimum80_votes']==us[k-1]['cumulative_votes'] and sm['preceding_votes']==us[k-2]['cumulative_votes'] and sm['crossing_key']==us[k-1]['key'],'crossing_preceding_control')
  require(sm['priority_keys']==keys[:max(k,15)] and sm['remainder_keys']==keys[max(k,15):] and sm['remainder_votes']==sum(u['reported_candidate_votes'] for u in us[max(k,15):]),'complete_priority_remainder_partition')
  require(b['receipts'].get(y)==body_companion[int(y)],'complete_original_body_receipt_context_companion_metadata');allkeys+=keys
 # PDF null/dash observations are immutable source scoped evidence, not native0 imputation.
 expected_canvass=j('canvass-cells.json');require(b['canvass']==expected_canvass,'PDF_source_null_dash_or_position_imputed')
 c=b['contract'];sm=b['summaries']['2024'];require(c['units']==b['units']['2024'],'contract_full_native_fields_context')
 require(c['full_order']==sm['full_order'] and c['certified_statewide_native_order']==sm['full_order'] and c['top15_keys']==sm['full_order'][:15],'contract_full_native_order_or_county_substitution')
 require(c['ordered_priority_keys']==sm['priority_keys'] and c['priority_keys']==sm['priority_keys'] and c['remainder_keys']==sm['remainder_keys'],'contract_priority_remainder_arrays')
 groups=collections.defaultdict(list)
 for u in b['units']['2024']:groups[u['county_fips']].append(u)
 require(len(c['parents'])==67 and {p['county_fips'] for p in c['parents']}==set(groups),'all67parent_coverage')
 for parent in c['parents']:
  full=sorted(u['key'] for u in groups[parent['county_fips']]);pk=set(sm['priority_keys']);require(parent['constituent_keys']==full and parent['priority_constituent_keys']==[k for k in full if k in pk] and parent['remainder_constituent_keys']==[k for k in full if k not in pk],'parent_disjoint_source_constituent_priority_remainder')
 require(c['coordinator_acceptance'] is False and c['legal_geographic_approval_2026'] is False and c['current_2026_crosswalk_complete'] is False,'current_coordinator_legal_geography_admission')
 require(c['unavailable_cases']==base['contract']['unavailable_cases'] and c['source_chain']==base['contract']['source_chain'],'source_context_and_unavailable_companion_metadata')
 return counted
clean_cells=validate(base)
# Tiny ordered patches reconstruct each complete bad input from fixed complete captured bodies.
recipes=[]
def add(name,path,op='delete',value=None):recipes.append({'name':name,'base_archive_sha256':sha((D/'turnout-original-phase.tar.gz').read_bytes()),'path':path,'operation':op,'value':value})
# Select actual blank registration and Walker unknown under/over contexts, not made-up geographies.
blank_idx=next(i for i,u in enumerate(base['units']['2024']) if u['registration_source'] is None);walker_idx=next(i for i,u in enumerate(base['units']['2024']) if u['county']=='Walker');pdf_idx=next(i for i,r in enumerate(base['canvass']) if r['county']=='Wilcox' and r['source']=='sos-2024-canvass-original');pdf_cell=base['canvass'][pdf_idx]['candidate_names_in_order'].index('Jill Stein')
add('missing-native',['units','2024',0]);add('duplicate-native-key',['units','2024',1,'key'],'set',base['units']['2024'][0]['key']);add('missing-candidate-row',['units','2024',0,'candidate_votes',0]);add('missing-administrative-row',['units','2024',0,'administrative_fields',0]);add('missing-source-party',['units','2024',0,'candidate_votes',0,'party_literal']);add('wrong-header',['units','2024',0,'native_label'],'set','ABSENTEE_RENAMED');add('missing-source-member-hash',['units','2024',0,'member_sha256']);add('wrong-source-column',['units','2024',0,'column_1based'],'set',999);add('changed-native-type',['units','2024',0,'candidate_votes',0,'xls_type'],'set',1);add('zero-for-blank-registration',['units','2024',blank_idx,'registration_source'],'set',0);add('zero-for-missing-under',['units','2024',walker_idx,'under_votes_source'],'set',0);add('PDF-null-imputed-zero',['canvass',pdf_idx,'cells',pdf_cell,'value'],'set',0);add('residual-allocation-candidate',['units','2024',0,'candidate_votes',0,'value'],'set',base['units']['2024'][0]['candidate_votes'][0]['value']+180);add('residual-allocation-contest-total',['units','2024',0,'reported_candidate_votes'],'set',base['units']['2024'][0]['reported_candidate_votes']+180);add('wrong80count',['summaries','2024','minimum80_count'],'set',886);add('wrong-cumulative',['units','2024',0,'cumulative_votes'],'set',0);add('wrong-full-order',['units','2024'],'swap-first-two');add('missing-remainder-key',['summaries','2024','remainder_keys',0]);add('missing-parent',['contract','parents',0]);add('missing-parent-constituent',['contract','parents',0,'constituent_keys',0]);add('county-dispatch-substitution',['contract','ordered_priority_keys'],'set',j('county-rank-sensitivity.json')['2024']['priority_keys']);add('current-geometry-admission',['contract','legal_geographic_approval_2026'],'set',True);add('coordinator-admission',['contract','coordinator_acceptance'],'set',True);add('current-crosswalk-admission',['units','2024',0,'current_2026_crosswalk'],'set','assumed2026');add('valid-named-writein-admission',['units','2024',0,'named_valid_writein_allocation'],'set',{'invented':8738});add('missing-context-companion',['contract','unavailable_cases','polling_method_splits_within_ordinary_columns']);add('missing-original-receipt-headers',['receipts','2024','headers']);add('changed-source-election-context',['units','2024',0,'year'],'set',2026);add('missing-receipt-part-hash',['receipts','2024','parts',0,'sha256']);add('wrong-contract-complete-source-field',['contract','units',0,'administrative_fields',0,'value'],'set',123456)
results=[]
for recipe in recipes:
 (F/(recipe['name']+'.input.json')).write_text(json.dumps(recipe,indent=2)+'\n');subject=copy.deepcopy(base);parent=subject
 for part in recipe['path'][:-1]:parent=parent[part]
 leaf=recipe['path'][-1]
 if recipe['operation']=='delete':del parent[leaf]
 elif recipe['operation']=='set':parent[leaf]=recipe['value']
 elif recipe['operation']=='swap-first-two':parent[leaf][0],parent[leaf][1]=parent[leaf][1],parent[leaf][0]
 try:validate(subject)
 except (Reject,KeyError) as e:out={'name':recipe['name'],'result':'REJECTED','rule':str(e)}
 else:raise AssertionError('Corruption accepted: '+recipe['name'])
 (F/(recipe['name']+'.result.json')).write_text(json.dumps(out,indent=2)+'\n');results.append(out)
proof={'status':'PASS','clean_input_passed':True,'direct_original_members':member_counts,'direct_original_native_units':len(source_truth),'direct_source_field_positions_checked_in_clean_input':clean_cells,'actual_corruption_fixture_count':len(results),'results':results,'scope':'Actual complete in-memory source/contract records reconstructed from immutable original-phase bodies plus retained exact ordered patch. Direct XLS source identities/types/values/party/header/administrative rows and relationships supply truth; stored success flags do not establish acceptance.','no_network_peer_calculator_or_mutable_aggregate':True}
(D/'corruption-validation.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items() if k!='results'},indent=2))
